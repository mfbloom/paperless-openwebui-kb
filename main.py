import typer
from config import settings
import logging
from pathlib import Path
import asyncio

from paperless import PaperlessClient
from exporter import export_all
from owui import OWUIClient
from uploader import Uploader

app = typer.Typer()

def setup_logging():
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

@app.command()
def run(
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

    async def _run():
        logger.info("Starting export from Paperless -> %s", md_dir)
        processed = await export_all(pc, Path(out_dir), limit_docs=limit_docs)
        logger.info("Exported %d documents", processed)
        logger.info("Starting upload (parallel=%d)", par_j)
        await upl.upload_all(md_dir)
        logger.info("Done.")

    asyncio.run(_run())

if __name__ == "__main__":
    typer.run(run)
