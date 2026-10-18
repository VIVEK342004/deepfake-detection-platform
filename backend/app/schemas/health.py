from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    version: str
    database_connected: bool
    storage_accessible: bool

class ModelStatusItem(BaseModel):
    name: str
    modality: str
    architecture: str
    status: str  # "model_ready", "model_loading", "model_unavailable", "inference_failed"
    is_ready: bool
    device: str
    checkpoint_found: bool
    checkpoint_path: Optional[str] = None
    parameters_count: Optional[int] = None
    description: str
    limitations: List[str]

class SystemStatusResponse(BaseModel):
    status: str
    timestamp: str
    device: str
    gpu_available: bool
    gpu_name: Optional[str] = None
    models: List[ModelStatusItem]
    limits: Dict[str, Any]
