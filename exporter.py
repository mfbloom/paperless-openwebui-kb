from paperless import PaperlessClient
from config import settings
from pathlib import Path
import yaml, re, hashlib
from slugify import slugify
import logging
from typing import Optional

logger = logging.getLogger(__name__)

FRONTMATTER_TEMPLATE = {"source": "paperless"}

def compute_sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def read_existing_hash(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    m = re.search(r"""content_sha256:\s*['"]?([0-9a-f]{64})['"]?""", text)
    return m.group(1) if m else None

def make_slug(title: str) -> str:
    return slugify(title, lowercase=True)

def md_filename(base: str, slug: str) -> str:
    safe = f"{base}-{slug}".strip("-")
    return safe + ".md"

async def export_all(paperless_client: PaperlessClient, out_dir: Path, limit_docs: int = 0):
    md_dir = out_dir / "md"
    md_dir.mkdir(parents=True, exist_ok=True)
    processed = 0
    async for doc in paperless_client.iter_documents(limit=limit_docs):
        doc_id = str(doc.get("id", ""))
        title = doc.get("title") or f"document-{doc_id}"
        created = doc.get("created", "")
        asn = doc.get("archive_serial_number") or ""
        correspondent = doc.get("correspondent") or ""
        tags = doc.get("tags") or []
        content = doc.get("content") or doc.get("ocr_text") or ""
        base = asn if asn else doc_id
        slug = make_slug(title) or f"doc-{doc_id}"
        fname = md_dir / md_filename(base, slug)
        newhash = compute_sha256(content)
        oldhash = read_existing_hash(fname)
        if oldhash == newhash:
            logger.debug("Unchanged: %s", fname)
        else:
            front = FRONTMATTER_TEMPLATE.copy()
            front.update({
                "id": doc_id,
                "asn": asn,
                "title": title,
                "created": created,
                "correspondent": correspondent,
                "tags": tags,
                "content_sha256": newhash,
                "paperless_url": doc.get("detail_url", ""),
            })
            fm = yaml.safe_dump(front, sort_keys=False)
            md = f"---\n{fm}---\n\n# {title}\n\n{content}\n"
            fname.write_text(md, encoding="utf-8")
            logger.info("Wrote: %s", fname)
        processed += 1
        if limit_docs and processed >= limit_docs:
            break
    return processed
