import os
from datetime import datetime, timezone
from typing import Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    BackgroundTasks,
    Query,
    status
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.db.session import get_db
from backend.app.db.models import Analysis, ModalityResult
from backend.app.schemas.analysis import (
    AnalysisCreateResponse,
    AnalysisSummaryResponse,
    AnalysisDetailResponse,
    AnalysisReportResponse,
    AnalysisListResponse
)
from backend.app.services.storage import storage_service
from backend.app.services.media_validator import media_validator, MediaValidationError
from backend.app.core.security import detect_media_type_and_validate, sanitize_filename
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.workers.tasks import execute_analysis_pipeline, process_analysis_task

router = APIRouter(prefix="/analyses", tags=["Analyses"])

@router.post(
    "",
    response_model=AnalysisCreateResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_analysis(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Validates uploaded media, creates an analysis record, and enqueues inference.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename cannot be empty.")

    clean_filename = sanitize_filename(file.filename)

    # Step 1: Save upload securely
    try:
        stored_name, sha256_hash, file_size, dest_path = storage_service.save_upload_file(file)
    except ValueError as ve:
        raise HTTPException(status_code=413, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to store uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to store uploaded file securely.")

    # Step 2: Validate file signature and MIME type
    try:
        media_type, mime_type = detect_media_type_and_validate(dest_path, clean_filename)
    except ValueError as ve:
        storage_service.delete_file(stored_name)
        raise HTTPException(status_code=400, detail=str(ve))

    # Step 3: Inspect media dimensions/duration
    try:
        if media_type == "image":
            media_meta = media_validator.inspect_image(dest_path)
        elif media_type == "video":
            media_meta = media_validator.inspect_video(dest_path)
        elif media_type == "audio":
            media_meta = media_validator.inspect_audio(dest_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported media format.")
    except MediaValidationError as me:
        storage_service.delete_file(stored_name)
        raise HTTPException(status_code=422, detail=str(me))

    # Step 4: Persist DB record
    analysis = Analysis(
        media_type=media_type,
        original_filename=clean_filename,
        stored_filename=stored_name,
        file_size_bytes=file_size,
        file_sha256=sha256_hash,
        mime_type=mime_type,
        status="queued",
        overall_prediction="unprocessed",
        overall_confidence=0.0,
        risk_level="unknown",
        media_metadata=media_meta
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Step 5: Enqueue processing task
    # If Celery eager or standalone, run in background_tasks or celery
    try:
        if settings.CELERY_ALWAYS_EAGER:
            background_tasks.add_task(execute_analysis_pipeline, analysis.id)
        else:
            process_analysis_task.delay(analysis.id)
    except Exception as e:
        logger.warning(f"Could not dispatch via Celery ({e}), falling back to FastAPI background tasks.")
        background_tasks.add_task(execute_analysis_pipeline, analysis.id)

    return AnalysisCreateResponse(
        id=analysis.id,
        media_type=analysis.media_type,
        original_filename=analysis.original_filename,
        status=analysis.status,
        message="Media successfully uploaded and queued for deepfake analysis.",
        created_at=analysis.created_at
    )

@router.get("", response_model=AnalysisListResponse)
def list_analyses(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    media_type: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    risk_level: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Lists analyses with pagination, filtering, and search."""
    query = db.query(Analysis)

    if media_type:
        query = query.filter(Analysis.media_type == media_type)
    if status_filter:
        query = query.filter(Analysis.status == status_filter)
    if risk_level:
        query = query.filter(Analysis.risk_level == risk_level)
    if search:
        query = query.filter(Analysis.original_filename.ilike(f"%{search}%"))

    total = query.count()
    items = query.order_by(desc(Analysis.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return AnalysisListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )

@router.get("/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieves full analysis record and modality results."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis with ID '{analysis_id}' not found.")
    return analysis

@router.get("/{analysis_id}/report", response_model=AnalysisReportResponse)
def get_analysis_report(analysis_id: str, db: Session = Depends(get_db)):
    """Generates structured forensic intelligence report."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis with ID '{analysis_id}' not found.")

    evaluations = []
    models_used = []
    forensic_indicators = []

    for mod in analysis.modality_results:
        evaluations.append({
            "modality": mod.modality,
            "status": mod.status,
            "is_synthetic": mod.is_synthetic,
            "confidence_score": mod.confidence_score,
            "execution_time_seconds": mod.execution_time_seconds,
            "limitations_notes": mod.limitations_notes,
            "raw_scores": mod.raw_scores
        })
        models_used.append({
            "model_name": mod.model_name,
            "model_version": mod.model_version,
            "modality": mod.modality
        })
        if mod.is_synthetic:
            forensic_indicators.append(f"Synthetic signatures flagged in {mod.modality} pipeline.")

    disclaimer = (
        "IMPORTANT FORENSIC NOTICE: The predictions in this report are probabilistic outputs generated "
        "by artificial neural networks and statistical heuristic algorithms. These findings do not "
        "constitute incontrovertible legal proof of authenticity or manipulation. Results should be "
        "reviewed by qualified human forensic examiners alongside provenance metadata."
    )

    return AnalysisReportResponse(
        analysis_id=analysis.id,
        report_generated_at=datetime.now(timezone.utc).isoformat(),
        media_type=analysis.media_type,
        file_info={
            "original_filename": analysis.original_filename,
            "file_size_bytes": analysis.file_size_bytes,
            "file_sha256": analysis.file_sha256,
            "mime_type": analysis.mime_type,
            "media_metadata": analysis.media_metadata
        },
        verdict={
            "status": analysis.status,
            "overall_prediction": analysis.overall_prediction,
            "overall_confidence": analysis.overall_confidence,
            "risk_level": analysis.risk_level,
            "summary_findings": analysis.summary_findings
        },
        modality_evaluations=evaluations,
        forensic_indicators=forensic_indicators,
        model_metadata=models_used,
        limitations_and_disclaimer=disclaimer
    )

@router.get("/{analysis_id}/media")
def get_analysis_media(analysis_id: str, db: Session = Depends(get_db)):
    """Serves media file securely for playback and review."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    try:
        file_path = storage_service.get_file_path(analysis.stored_filename)
        return FileResponse(
            path=str(file_path),
            media_type=analysis.mime_type,
            filename=analysis.original_filename
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Underlying media file was not found on storage.")
