import httpx
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import AsyncIterator, Dict, Any
from config import settings
import logging

logger = logging.getLogger(__name__)

class PaperlessClient:
    def __init__(self, base: str, token: str, page_size: int = 100, timeout: int = 30):
        self.base = base.rstrip("/")
        self.token = token
        self.page_size = page_size
        self.timeout = timeout
        self._headers = {"Authorization": f"Token {self.token}"} if token else {}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def _get(self, client: httpx.AsyncClient, url: str) -> Dict[str, Any]:
        resp = await client.get(url, headers=self._headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    async def iter_documents(self, limit: int = 0) -> AsyncIterator[Dict[str, Any]]:
        url = f"{self.base}/api/documents/?page_size={self.page_size}&fields=id,title,created,archive_serial_number,correspondent,tags,content,detail_url,ocr_text"
        processed = 0
        async with httpx.AsyncClient() as client:
            while url:
                logger.debug("Fetching %s", url)
                page = await self._get(client, url)
                results = page.get("results", [])
                for doc in results:
                    yield doc
                    processed += 1
                    if limit and processed >= limit:
                        return
                url = page.get("next")
