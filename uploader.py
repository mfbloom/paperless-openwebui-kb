import asyncio
from owui import OWUIClient
from pathlib import Path
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def read_hash_from_md(path: Path) -> Optional[str]:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"""content_sha256:\s*['"]?([0-9a-f]{64})['"]?""", text)
    return m.group(1) if m else None

class Uploader:
    def __init__(self, owui_client: OWUIClient, kb_id: str, mark_dir: Path, concurrency: int = 4):
        self.client = owui_client
        self.kb_id = kb_id
        self.mark_dir = mark_dir
        self.mark_dir.mkdir(parents=True, exist_ok=True)
        self.sem = asyncio.Semaphore(concurrency)

    async def _upload_one(self, path: Path):
        h = read_hash_from_md(path)
        if not h:
            logger.warning("No content_sha256 in %s — skipping", path)
            return
        mark_file = self.mark_dir / h
        if mark_file.exists():
            logger.debug("Already uploaded (hash present): %s", path)
            return
        async with self.sem:
            logger.info("Uploading: %s", path)
            res = await self.client.upload_file(str(path))
            file_id = str(res.get("id") or res.get("pk") or res.get("file_id"))
            if not file_id:
                logger.error("No file id returned for %s -> %s", path, res)
                raise RuntimeError("No file id")
            await self.client.attach_to_kb(self.kb_id, file_id)
            mark_file.write_text("", encoding="utf-8")
            logger.info("Attached %s (file_id=%s)", path.name, file_id)

    async def upload_all(self, doc_dir: Path):
        tasks = [asyncio.create_task(self._upload_one(path)) for path in sorted(doc_dir.glob("*.md"))]
        if not tasks:
            logger.info("No files to upload in %s", doc_dir)
            return
        await asyncio.gather(*tasks)
