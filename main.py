import typer
from config import settings, elastic
import logging
from pathlib import Path
import asyncio
from fastapi import FastAPI, Request
import uvicorn
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM


from paperless import PaperlessClient
from exporter import export_all
from owui import OWUIClient
from uploader import Uploader

apm = make_apm_client(
    {
        "SERVICE_NAME": elastic.service_name,
        "SECRET_TOKEN": elastic.secret,
        "SERVER_URL": elastic.apm_url,
        "ENVIRONMENT": elastic.environment,
    }
)

app = typer.Typer()
fastapi_app = FastAPI()
fastapi_app.add_middleware(ElasticAPM,client=apm)


def setup_logging():
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )


@app.command()
async def manual(
    page_size: int = settings.PAGE_SIZE,
    par_j: int = settings.PAR_J,
    limit_docs: int = settings.LIMIT_DOCS,
):
    setup_logging()
    logger = logging.getLogger("main")
    out_dir = settings.OUT_DIR
    md_dir = Path(out_dir) / "md"
    mark_dir = Path(out_dir) / ".uploaded"
    md_dir.mkdir(parents=True, exist_ok=True)
    pc = PaperlessClient(settings.PNGX_BASE, settings.PNGX_TOKEN, page_size=page_size)
    ow = OWUIClient(settings.OWUI_BASE, settings.OWUI_TOKEN)
    upl = Uploader(ow, settings.KB_ID, mark_dir, concurrency=par_j)

    logger.info("Starting export from Paperless -> %s", md_dir)
    processed = await export_all(pc, Path(out_dir), limit_docs=limit_docs)
    logger.info("Exported %d documents", processed)
    logger.info("Starting upload (parallel=%d)", par_j)
    await upl.upload_all(md_dir)
    logger.info("Done.")

@app.command()
def serve(host: str = "0.0.0.0", port: int = 8081):
    
    @fastapi_app.post("/sync")
    async def trigger(request: Request):        
        await manual(limit_docs=1)
        return {"status": "success"}

    uvicorn.run(fastapi_app, host=host, port=port)

if __name__ == "__main__":
    app()
