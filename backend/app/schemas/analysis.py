from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from backend.app.schemas.modality import ModalityResultResponse

class AnalysisCreateResponse(BaseModel):
    id: str
    media_type: str
    original_filename: str
    status: str
    message: str
    created_at: datetime

class AnalysisSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    media_type: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    status: str
    overall_prediction: str
    overall_confidence: float
    risk_level: str
    created_at: datetime
    completed_at: Optional[datetime] = None

class AnalysisDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    media_type: str
    original_filename: str
    file_size_bytes: int
    file_sha256: str
    mime_type: str
    status: str
    overall_prediction: str
    overall_confidence: float
    risk_level: str
    summary_findings: Dict[str, Any] = Field(default_factory=dict)
    media_metadata: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    retention_expires_at: Optional[datetime] = None
    modality_results: List[ModalityResultResponse] = Field(default_factory=list)

class AnalysisReportResponse(BaseModel):
    analysis_id: str
    report_generated_at: str
    media_type: str
    file_info: Dict[str, Any]
    verdict: Dict[str, Any]
    modality_evaluations: List[Dict[str, Any]]
    forensic_indicators: List[str]
    model_metadata: List[Dict[str, Any]]
    limitations_and_disclaimer: str

class AnalysisListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[AnalysisSummaryResponse]
