import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np

from backend.app.main import app

client = TestClient(app)

def create_synthetic_image_bytes() -> bytes:
    """Generates valid JPEG byte stream for test uploads."""
    img = Image.new("RGB", (128, 128), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_health_endpoint():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "database_connected" in data
    assert "storage_accessible" in data

def test_models_health_endpoint():
    resp = client.get("/api/v1/health/models")
    assert resp.status_code == 200
    data = resp.json()
    assert "models" in data
    assert len(data["models"]) >= 2
    for model in data["models"]:
        assert "status" in model
        assert "architecture" in model
        assert "limitations" in model

def test_upload_valid_image():
    img_bytes = create_synthetic_image_bytes()
    resp = client.post(
        "/api/v1/analyses",
        files={"file": ("test_avatar.jpg", img_bytes, "image/jpeg")}
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["media_type"] == "image"
    assert data["original_filename"] == "test_avatar.jpg"
    assert data["status"] in ["queued", "processing", "completed"]

    # Poll analysis detail
    analysis_id = data["id"]
    detail_resp = client.get(f"/api/v1/analyses/{analysis_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["id"] == analysis_id

def test_upload_invalid_file_extension():
    resp = client.post(
        "/api/v1/analyses",
        files={"file": ("bad_script.exe", b"MZbinarycontent", "application/octet-stream")}
    )
    assert resp.status_code == 400
    assert "Unsupported file extension" in resp.json()["detail"]

def test_get_nonexistent_analysis_returns_404():
    resp = client.get("/api/v1/analyses/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404

def test_list_analyses_pagination():
    resp = client.get("/api/v1/analyses?page=1&page_size=5")
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)
