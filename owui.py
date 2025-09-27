import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class OWUIClient:
    def __init__(self, base: str, token: str, timeout: int = 60):
        self.base = base.rstrip("/")
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"} if token else {}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def upload_file(self, file_path: str) -> Dict[str, Any]:
        url = f"{self.base}/api/v1/files/"
        async with httpx.AsyncClient(timeout=5) as client:
            with open(file_path, "rb") as fh:
                files = {"file": (file_path, fh)}
                resp = await client.post(url, headers=self.headers, files=files)
            resp.raise_for_status()
            logger.info(f"Uploaded {file_path}.")
            return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def attach_to_kb(self, kb_id: str, file_id: str) -> Dict[str, Any]:
        url = f"{self.base}/api/v1/knowledge/{kb_id}/file/add"
        payload = {"file_id": file_id}

        logger.info(f"{file_id}")

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                url,
                headers={**self.headers, "Content-Type": "application/json"},
                json=payload
            )
            resp.raise_for_status()
            return resp.json()