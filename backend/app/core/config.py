from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_DB_PATH = (_BACKEND_DIR / "data" / "soilsense.db").resolve()
_UPLOAD_PATH = (_BACKEND_DIR / "data" / "uploads").resolve()
_THRESHOLDS_PATH = (_BACKEND_DIR / "config" / "default_thresholds.json").resolve()
_DEMO_PATH = (_BACKEND_DIR / "data" / "demo" / "madurai_demo_samples.csv").resolve()


class Settings(BaseSettings):
    APP_NAME: str = "SoilSense"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = f"sqlite:///{_DB_PATH.as_posix()}"
    ACTIVE_STANDARD: str = "TNAU"
    UPLOAD_DIR: str = str(_UPLOAD_PATH)
    THRESHOLDS_SEED_FILE: str = str(_THRESHOLDS_PATH)
    DEMO_DATA_FILE: str = str(_DEMO_PATH)
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> object:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


settings = Settings()


def get_settings() -> Settings:
    return settings
