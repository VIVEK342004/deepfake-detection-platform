from datetime import datetime, timezone
import torch
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.schemas.health import HealthResponse, SystemStatusResponse, ModelStatusItem
from ml.inference.engine import engine

router = APIRouter(prefix="/health", tags=["Health & System Status"])

@router.get("", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    """Health check for API, database connection, and storage accessibility."""
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    storage_ok = settings.uploads_dir.exists() and os.access(settings.uploads_dir, os.W_OK)

    return HealthResponse(
        status="healthy" if db_connected and storage_ok else "degraded",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="0.1.0",
        database_connected=db_connected,
        storage_accessible=storage_ok
    )

import os

@router.get("/models", response_model=SystemStatusResponse)
def get_models_health():
    """Returns runtime model readiness, GPU status, and processing limits."""
    models_info = engine.get_models_status()

    gpu_available = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if gpu_available else None

    # Compute overall status
    any_ready = any(m["is_ready"] for m in models_info)
    all_ready = all(m["is_ready"] for m in models_info)

    if all_ready:
        system_status = "operational"
    elif any_ready:
        system_status = "partially_available"
    else:
        system_status = "models_unloaded"

    return SystemStatusResponse(
        status=system_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        device="cuda" if gpu_available else "cpu",
        gpu_available=gpu_available,
        gpu_name=gpu_name,
        models=[ModelStatusItem(**m) for m in models_info],
        limits={
            "max_upload_size_mb": round(settings.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024), 1),
            "max_video_duration_seconds": settings.MAX_VIDEO_DURATION_SECONDS,
            "max_audio_duration_seconds": settings.MAX_AUDIO_DURATION_SECONDS,
            "max_sampled_frames": settings.MAX_VIDEO_FRAMES_SAMPLE
        }
    )
