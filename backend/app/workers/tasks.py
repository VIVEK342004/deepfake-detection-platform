import os
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.db.models import Analysis, ModalityResult
from backend.app.services.storage import storage_service
from backend.app.core.logging import logger
from backend.app.workers.celery_app import celery_app
from ml.inference.engine import engine

def to_serializable(val):
    """Recursively converts numpy types and non-serializable objects into native python types."""
    if isinstance(val, dict):
        return {str(k): to_serializable(v) for k, v in val.items()}
    elif isinstance(val, (list, tuple)):
        return [to_serializable(v) for v in val]
    elif hasattr(val, "item"):
        return val.item()
    return val

def execute_analysis_pipeline(analysis_id: str):
    """
    Core pipeline logic that retrieves the file, runs inference via engine,
    persists ModalityResult records, and updates the Analysis status.
    Can be run via Celery worker or FastAPI BackgroundTasks.
    """
    db: Session = SessionLocal()
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            logger.error(f"Analysis '{analysis_id}' not found in database.")
            return

        analysis.status = "processing"
        db.commit()

        file_path = storage_service.get_file_path(analysis.stored_filename)

        # Run model inference based on media type
        if analysis.media_type == "image":
            results = engine.analyze_image(file_path)
        elif analysis.media_type == "video":
            results = engine.analyze_video(file_path)
        elif analysis.media_type == "audio":
            results = engine.analyze_audio(file_path)
        else:
            raise ValueError(f"Unknown media_type '{analysis.media_type}'")

        # Save Visual Result if produced
        visual = results.get("visual")
        if visual:
            modality_res = ModalityResult(
                analysis_id=analysis.id,
                modality="visual",
                model_name="VisualDeepfakeClassifier",
                model_version="1.0.0",
                status=visual.get("status", "completed"),
                is_synthetic=visual.get("is_synthetic"),
                confidence_score=float(visual.get("confidence_score", 0.0)),
                raw_scores=to_serializable(visual.get("raw_scores", {})),
                artifacts=to_serializable(visual.get("artifacts", {})),
                execution_time_seconds=float(visual.get("execution_time_seconds", 0.0)),
                limitations_notes=visual.get("limitations_notes")
            )
            db.add(modality_res)

        # Save Audio Result if produced
        audio = results.get("audio")
        if audio:
            modality_res = ModalityResult(
                analysis_id=analysis.id,
                modality="audio",
                model_name="AudioDeepfakeClassifier",
                model_version="1.0.0",
                status=audio.get("status", "completed"),
                is_synthetic=audio.get("is_synthetic"),
                confidence_score=float(audio.get("confidence_score", 0.0)),
                raw_scores=to_serializable(audio.get("raw_scores", {})),
                artifacts=to_serializable(audio.get("artifacts", {})),
                execution_time_seconds=float(audio.get("execution_time_seconds", 0.0)),
                limitations_notes=audio.get("limitations_notes")
            )
            db.add(modality_res)

        # Save Multimodal Sync Result if produced
        sync = results.get("multimodal_sync")
        if sync:
            modality_res = ModalityResult(
                analysis_id=analysis.id,
                modality="multimodal_sync",
                model_name="MultimodalSyncAnalyzer",
                model_version="1.0.0",
                status=sync.get("status", "completed"),
                is_synthetic=sync.get("is_synthetic"),
                confidence_score=float(sync.get("confidence_score", 0.0)),
                raw_scores=to_serializable(sync.get("raw_scores", {})),
                artifacts=to_serializable(sync.get("artifacts", {})),
                execution_time_seconds=float(sync.get("execution_time_seconds", 0.0)),
                limitations_notes=sync.get("limitations_notes")
            )
            db.add(modality_res)

        # Synthesize final verdict
        verdict = engine.synthesize_verdict(results)
        analysis.status = verdict["status"]
        analysis.overall_prediction = verdict["overall_prediction"]
        analysis.overall_confidence = float(verdict["overall_confidence"])
        analysis.risk_level = verdict["risk_level"]
        analysis.summary_findings = to_serializable(verdict["summary_findings"])
        analysis.completed_at = datetime.now(timezone.utc)

        db.commit()
        logger.info(f"Analysis '{analysis_id}' finished with status '{analysis.status}'.")

    except Exception as e:
        logger.exception(f"Error during analysis pipeline for '{analysis_id}': {e}")
        try:
            db.rollback()
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                analysis.status = "failed"
                analysis.error_message = str(e)
                analysis.completed_at = datetime.now(timezone.utc)
                db.commit()
        except Exception as db_err:
            logger.error(f"Failed to record failure state for analysis: {db_err}")
    finally:
        db.close()


@celery_app.task(name="process_analysis_task", bind=True, max_retries=1)
def process_analysis_task(self, analysis_id: str):
    """Celery task entrypoint."""
    execute_analysis_pipeline(analysis_id)

