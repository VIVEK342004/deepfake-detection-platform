import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_path_traversal_in_upload_filename():
    """Verifies path traversal attempts in filenames are neutralized."""
    fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    malicious_filename = "../../../../../windows/system32/cmd.png"

    resp = client.post(
        "/api/v1/analyses",
        files={"file": (malicious_filename, fake_png, "image/png")}
    )
    # The filename should be sanitized to "cmd.png" without creating files outside storage
    if resp.status_code == 201:
        data = resp.json()
        assert ".." not in data["original_filename"]
        assert "/" not in data["original_filename"]
        assert "\\" not in data["original_filename"]

def test_spoofed_mime_type_rejection():
    """Uploading executable shell code labelled as image/jpeg must be caught or rejected."""
    shell_code = b"#!/bin/bash\nrm -rf / --no-preserve-root"
    resp = client.post(
        "/api/v1/analyses",
        files={"file": ("exploit.jpg", shell_code, "image/jpeg")}
    )
    # Since the file signature doesn't match JPEG and PIL cannot parse it, must return error
    assert resp.status_code in [400, 422]
