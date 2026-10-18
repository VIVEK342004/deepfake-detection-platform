import os
from pathlib import Path
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_ENV: str = "development"
    APP_NAME: str = "Deepfake Detection Platform"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "development-secret-key-32-chars-minimum-security"
    API_V1_STR: str = "/api/v1"

    HOST: str = "127.0.0.1"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    DATABASE_URL: str = "sqlite:///./deepfake_detection.db"

    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_ALWAYS_EAGER: bool = True

    STORAGE_DIR: str = str(BASE_DIR / "storage")
    MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB
    MAX_VIDEO_DURATION_SECONDS: int = 120  # 2 minutes
    MAX_AUDIO_DURATION_SECONDS: int = 300  # 5 minutes
    MAX_VIDEO_FRAMES_SAMPLE: int = 32
    RETENTION_DAYS: int = 7

    ML_DEVICE: str = "auto"
    ML_BATCH_SIZE: int = 8
    ML_CHECKPOINTS_DIR: str = str(BASE_DIR / "ml" / "checkpoints")
    FACE_DETECTION_CONFIDENCE: float = 0.85
    VISUAL_MODEL_NAME: str = "efficientnet_b0"
    AUDIO_MODEL_NAME: str = "spectral_cnn"

    @property
    def uploads_dir(self) -> Path:
        path = Path(self.STORAGE_DIR) / "uploads"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def thumbnails_dir(self) -> Path:
        path = Path(self.STORAGE_DIR) / "thumbnails"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def processed_dir(self) -> Path:
        path = Path(self.STORAGE_DIR) / "processed"
        path.mkdir(parents=True, exist_ok=True)
        return path

settings = Settings()
