import io
import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import app
import backend.app.db.models  # Ensure all models are registered


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create an isolated test database and authenticated client."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            email = f"test-{uuid.uuid4().hex}@example.com"
            password = "TestPassword!123"

            register_response = test_client.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": password,
                },
            )
            assert register_response.status_code == 201, (
                f"Registration failed: {register_response.text}"
            )

            login_response = test_client.post(
                "/api/v1/auth/login",
                json={
                    "email": email,
                    "password": password,
                },
            )
            assert login_response.status_code == 200, (
                f"Login failed: {login_response.text}"
            )

            token = login_response.json()["access_token"]
            test_client.headers.update(
                {"Authorization": f"Bearer {token}"}
            )

            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


def create_synthetic_image_bytes() -> bytes:
    """Generate a valid JPEG byte stream for test uploads."""
    img = Image.new("RGB", (128, 128), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_health_endpoint(client: TestClient):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "database_connected" in data
    assert "storage_accessible" in data


def test_models_health_endpoint(client: TestClient):
    resp = client.get("/api/v1/health/models")
    assert resp.status_code == 200

    data = resp.json()
    assert "models" in data
    assert len(data["models"]) >= 2

    for model in data["models"]:
        assert "status" in model
        assert "architecture" in model
        assert "limitations" in model


def test_upload_valid_image(client: TestClient):
    img_bytes = create_synthetic_image_bytes()

    resp = client.post(
        "/api/v1/analyses",
        files={
            "file": (
                "test_avatar.jpg",
                img_bytes,
                "image/jpeg",
            )
        },
    )

    assert resp.status_code == 201, resp.text

    data = resp.json()
    assert "id" in data
    assert data["media_type"] == "image"
    assert data["original_filename"] == "test_avatar.jpg"
    assert data["status"] in ["queued", "processing", "completed"]

    analysis_id = data["id"]

    detail_resp = client.get(
        f"/api/v1/analyses/{analysis_id}"
    )
    assert detail_resp.status_code == 200, detail_resp.text

    detail = detail_resp.json()
    assert detail["id"] == analysis_id


def test_upload_invalid_file_extension(client: TestClient):
    resp = client.post(
        "/api/v1/analyses",
        files={
            "file": (
                "bad_script.exe",
                b"MZbinarycontent",
                "application/octet-stream",
            )
        },
    )

    assert resp.status_code == 400, resp.text
    assert "Unsupported file extension" in resp.json()["detail"]


def test_get_nonexistent_analysis_returns_404(client: TestClient):
    resp = client.get(
        "/api/v1/analyses/00000000-0000-0000-0000-000000000000"
    )

    assert resp.status_code == 404


def test_list_analyses_pagination(client: TestClient):
    resp = client.get(
        "/api/v1/analyses?page=1&page_size=5"
    )

    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)