from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class FrameAnalysisResult(BaseModel):
    frame_index: int
    timestamp_seconds: float
    face_detected: bool
    face_box: Optional[List[int]] = None  # [x, y, w, h]
    confidence_fake: float
    confidence_real: float
    is_anomaly: bool = False

class AudioSegmentResult(BaseModel):
    start_seconds: float
    end_seconds: float
    confidence_fake: float
    confidence_real: float
    spectral_flatness: Optional[float] = None
    spectral_centroid: Optional[float] = None

class ModalityResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_id: str
    modality: str  # visual, audio, multimodal_sync
    model_name: str
    model_version: str
    status: str
    is_synthetic: Optional[bool] = None
    confidence_score: float
    raw_scores: Dict[str, Any] = Field(default_factory=dict)
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    execution_time_seconds: float
    limitations_notes: Optional[str] = None
    created_at: datetime
