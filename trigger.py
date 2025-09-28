from fastapi import FastAPI, Request
import asyncio
import logging
from main import run

app = FastAPI()
logger = logging.getLogger(__name__)

@app.post("/trigger")
async def trigger(request: Request):
    logger.info("Webhook triggered")
    loop = asyncio.get_event_loop()
    loop.create_task(run())  # fire and forget
    return {"status": "started"}