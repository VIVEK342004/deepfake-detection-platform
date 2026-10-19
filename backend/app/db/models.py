import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Text,
)
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    analyses = relationship("Analysis", back_populates="owner")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    owner = relationship("User", back_populates="analyses")
    media_type = Column(String(20), nullable=False, index=True)  # image, video, audio
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    file_sha256 = Column(String(64), nullable=False, index=True)
    mime_type = Column(String(100), nullable=False)

    status = Column(
        String(30),
        nullable=False,
        default="queued",
        index=True
    )  # queued, processing, completed, failed, model_unavailable

    overall_prediction = Column(
        String(30),
        nullable=False,
        default="unprocessed"
    )  # likely_synthetic, likely_authentic, inconclusive, unprocessed

    overall_confidence = Column(Float, nullable=False, default=0.0)
    risk_level = Column(String(20), nullable=False, default="unknown")  # low, medium, high, critical, unknown

    summary_findings = Column(JSON, nullable=True, default=dict)
    media_metadata = Column(JSON, nullable=True, default=dict)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    retention_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship to individual modalities
    modality_results = relationship(
        "ModalityResult",
        back_populates="analysis",
        cascade="all, delete-orphan",
        order_by="ModalityResult.created_at"
    )

class ModalityResult(Base):
    __tablename__ = "modality_results"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    modality = Column(String(30), nullable=False)  # visual, audio, multimodal_sync

    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    status = Column(
        String(30),
        nullable=False,
        default="completed"
    )  # model_ready, model_unavailable, completed, failed

    is_synthetic = Column(Boolean, nullable=True)
    confidence_score = Column(Float, nullable=False, default=0.0)
    raw_scores = Column(JSON, nullable=True, default=dict)  # {"real": 0.12, "fake": 0.88}
    artifacts = Column(JSON, nullable=True, default=dict)  # frames, bounding_boxes, spectrogram_peaks
    execution_time_seconds = Column(Float, nullable=False, default=0.0)
    limitations_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    analysis = relationship("Analysis", back_populates="modality_results")

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    modality = Column(String(30), nullable=False)
    checkpoint_path = Column(String(255), nullable=True)
    architecture = Column(String(100), nullable=False)
    is_ready = Column(Boolean, default=False, nullable=False)
    parameters_count = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    license = Column(String(100), nullable=True)
    last_checked_at = Column(DateTime(timezone=True), default=utc_now)

