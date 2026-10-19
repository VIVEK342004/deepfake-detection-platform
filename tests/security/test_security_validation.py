import uuid
import uuid
import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import app
import backend.app.db.models  # Register all SQLAlchemy models


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create an isolated database and authenticated test client."""
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
            email = f"security-{uuid.uuid4().hex}@example.com"
            password = "TestPassword!123"

            register_response = test_client.post(
                "/api/v1/auth/register",
                json={"email": email, "password": password},
            )
            assert register_response.status_code == 201, register_response.text

            login_response = test_client.post(
                "/api/v1/auth/login",
                json={"email": email, "password": password},
            )
            assert login_response.status_code == 200, login_response.text

            token = login_response.json()["access_token"]
            test_client.headers.update(
                {"Authorization": f"Bearer {token}"}
            )

            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


def test_path_traversal_in_upload_filename(client: TestClient):
    """Verify that traversal attempts in filenames are neutralized."""
    fake_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
        b"\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05"
        b"\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    malicious_filename = "../../../../../windows/system32/cmd.png"

    resp = client.post(
        "/api/v1/analyses",
        files={
            "file": (
                malicious_filename,
                fake_png,
                "image/png",
            )
        },
    )

    # If accepted, verify the returned filename is sanitized.
    if resp.status_code == 201:
        data = resp.json()
        assert ".." not in data["original_filename"]
        assert "/" not in data["original_filename"]
        assert "\\" not in data["original_filename"]
    else:
        # Rejecting malformed or invalid image content is also safe.
        assert resp.status_code in [400, 415, 422]


def test_spoofed_mime_type_rejection(client: TestClient):
    """Reject shell code disguised as a JPEG image."""
    shell_code = b"#!/bin/bash\nrm -rf / --no-preserve-root"

    resp = client.post(
        "/api/v1/analyses",
        files={
            "file": (
                "exploit.jpg",
                shell_code,
                "image/jpeg",
            )
        },
    )

    assert resp.status_code in [400, 415, 422], resp.text
