from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class Settings:
    PNGX_BASE: str = os.getenv("PNGX_BASE", "")
    PNGX_TOKEN: str = os.getenv("PNGX_TOKEN", "")
    OWUI_BASE: str = os.getenv("OWUI_BASE", "")
    OWUI_TOKEN: str = os.getenv("OWUI_TOKEN", "")
    KB_ID: str = os.getenv("KB_ID", "")
    OUT_DIR: Path = Path(os.getenv("OUT_DIR", "/data"))
    PAGE_SIZE: int = int(os.getenv("PAGE_SIZE", "100"))
    PAR_J: int = int(os.getenv("PAR_J", "4"))
    LIMIT_DOCS: int = int(os.getenv("LIMIT_DOCS", "0"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
