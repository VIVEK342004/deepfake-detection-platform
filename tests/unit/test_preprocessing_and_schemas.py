import pytest
import numpy as np
from pydantic import ValidationError
from backend.app.core.security import sanitize_filename, compute_sha256
from backend.app.schemas.analysis import AnalysisCreateResponse, AnalysisReportResponse
from ml.preprocessing.face_detector import FaceDetector

def test_sanitize_filename_prevents_traversal():
    bad_name = "../../../etc/passwd"
    clean = sanitize_filename(bad_name)
    assert "/" not in clean
    assert ".." not in clean
    assert clean == "passwd"

def test_sanitize_filename_strips_special_characters():
    name = "my evil<>:;*?| file.jpg"
    clean = sanitize_filename(name)
    assert "<" not in clean
    assert "?" not in clean
    assert clean == "my_evil________file.jpg"

def test_face_detector_no_face_dummy():
    detector = FaceDetector()
    blank_img = np.zeros((200, 200, 3), dtype=np.uint8)
    crop, box, count = detector.crop_primary_face(blank_img)
    assert crop is None
    assert box is None
    assert count == 0

def test_analysis_create_response_schema():
    from datetime import datetime, timezone
    resp = AnalysisCreateResponse(
        id="test-123",
        media_type="image",
        original_filename="sample.jpg",
        status="queued",
        message="Queued successfully",
        created_at=datetime.now(timezone.utc)
    )
    assert resp.id == "test-123"
    assert resp.media_type == "image"
