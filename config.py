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
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", "/tmp/processed"))
    PAGE_SIZE: int = int(os.getenv("PAGE_SIZE", "100"))
    PAR_J: int = int(os.getenv("PAR_J", "4"))
    LIMIT_DOCS: int = int(os.getenv("LIMIT_DOCS", "0"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

@dataclass
class ElasticAgentSettings:
    
    secret: str = os.getenv("ELASTIC_SECRET", "")
    service_name: str = os.getenv("ELASTIC_SERVICE_NAME", "sync-server")
    apm_url: str = os.getenv("ELASTIC_APM_URL", "http://apm-server:8200")
    environment: str = os.getenv("ELASTIC_ENVIRONMENT", "development")

settings = Settings()
elastic = ElasticAgentSettings()
