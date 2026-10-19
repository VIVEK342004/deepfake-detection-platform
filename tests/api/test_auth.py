
from collections.abc import Generator
from io import BytesIO

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
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


def test_register_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "auth-test@example.com",
            "password": "TestPassword!123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "auth-test@example.com"
    assert "id" in data
    assert "hashed_password" not in data


def test_duplicate_registration_returns_conflict(client: TestClient):
    payload = {
        "email": "duplicate-test@example.com",
        "password": "TestPassword!123",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


def test_login_returns_access_token(client: TestClient):
    payload = {
        "email": "login-test@example.com",
        "password": "TestPassword!123",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201

    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("access_token"), str)
    assert data.get("token_type") == "bearer"


def test_login_rejects_wrong_password(client: TestClient):
    payload = {
        "email": "wrong-password-test@example.com",
        "password": "TestPassword!123",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201

    response = client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": "WrongPassword!123"},
    )
    assert response.status_code == 401


def test_analysis_endpoints_require_authentication(client: TestClient):
    paths = [
        "/api/v1/analyses",
        "/api/v1/analyses/test-id",
        "/api/v1/analyses/test-id/report",
        "/api/v1/analyses/test-id/media",
    ]
    for path in paths:
        response = client.get(path)
        assert response.status_code == 401, (
            f"{path} returned {response.status_code}"
        )


def test_user_cannot_access_another_users_analysis(client: TestClient):
    # Register and login User A.
    user_a = {
        "email": "owner-a@example.com",
        "password": "TestPassword!123",
    }
    response = client.post("/api/v1/auth/register", json=user_a)
    assert response.status_code == 201, response.text

    login_a = client.post("/api/v1/auth/login", json=user_a)
    assert login_a.status_code == 200, login_a.text
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Generate a valid test image and create an analysis as User A.
    image_buffer = BytesIO()
    Image.new("RGB", (32, 32), color=(73, 109, 137)).save(
        image_buffer, format="JPEG"
    )

    upload = client.post(
        "/api/v1/analyses",
        headers=headers_a,
        files={
            "file": (
                "owner-private.jpg",
                image_buffer.getvalue(),
                "image/jpeg",
            )
        },
    )
    assert upload.status_code == 201, upload.text
    analysis_id = upload.json()["id"]

    # Register and login User B.
    user_b = {
        "email": "owner-b@example.com",
        "password": "TestPassword!123",
    }
    response = client.post("/api/v1/auth/register", json=user_b)
    assert response.status_code == 201, response.text

    login_b = client.post("/api/v1/auth/login", json=user_b)
    assert login_b.status_code == 200, login_b.text
    headers_b = {
        "Authorization": f"Bearer {login_b.json()['access_token']}"
    }

    # User B must not access User A's analysis, report, or media.
    for suffix in ("", "/report", "/media"):
        response = client.get(
            f"/api/v1/analyses/{analysis_id}{suffix}",
            headers=headers_b,
        )
        assert response.status_code == 404, (
            f"User B accessed endpoint {suffix!r}: "
            f"HTTP {response.status_code}"
        )

    # User B's list must not expose User A's analysis.
    response = client.get("/api/v1/analyses", headers=headers_b)
    assert response.status_code == 200, response.text
    assert all(
        item["id"] != analysis_id
        for item in response.json()["items"]
    )
