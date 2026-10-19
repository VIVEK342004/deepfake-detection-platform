import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging, logger
from backend.app.db.session import engine
from backend.app.db.base import Base
import backend.app.db.models  # Ensure models are registered with Base
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.analyses import router as analyses_router
from backend.app.api.v1.auth import router as auth_router
from ml.inference.engine import engine as ml_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Setup logging, ensure storage dirs, create db tables
    setup_logging()
    logger.info("Initializing Deepfake Detection Platform...")
    
    # Create DB tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database schemas verified.")

    # Verify storage directories
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.thumbnails_dir.mkdir(parents=True, exist_ok=True)
    settings.processed_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Storage directories initialized at: {settings.STORAGE_DIR}")

    # Inspect ML models readiness
    status = ml_engine.get_models_status()
    for m in status:
        logger.info(f"Model [{m['name']}] - Status: {m['status']} (Device: {m['device']})")

    yield

    # Shutdown
    logger.info("Deepfake Detection Platform shutting down gracefully.")

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Production-Oriented Multimodal AI Deepfake Detection Platform.\n\n"
        "Analyzes images, sampled video frames, and acoustic speech for synthetic manipulation indicators."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register versioned API routers
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(analyses_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to Deepfake Detection Platform API",
        "documentation": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "model_status": f"{settings.API_V1_STR}/health/models"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)

