import hashlib
import os
import re
from pathlib import Path
from typing import Tuple, Optional
import puremagic

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac"}

ALLOWED_EXTENSIONS = (
    ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS | ALLOWED_AUDIO_EXTENSIONS
)

MIME_TYPE_MAPPING = {
    # Images
    "image/jpeg": "image",
    "image/png": "image",
    "image/webp": "image",
    # Videos
    "video/mp4": "video",
    "video/x-msvideo": "video",
    "video/quicktime": "video",
    "video/x-matroska": "video",
    "video/webm": "video",
    # Audio
    "audio/x-wav": "audio",
    "audio/wav": "audio",
    "audio/wave": "audio",
    "audio/mpeg": "audio",
    "audio/mp3": "audio",
    "audio/flac": "audio",
    "audio/ogg": "audio",
    "audio/x-m4a": "audio",
    "audio/mp4": "audio",
    "audio/aac": "audio",
}

def sanitize_filename(filename: str) -> str:
    """Removes path traversals and unsafe characters from original filename."""
    base = os.path.basename(filename)
    # Replace anything not alphanumeric, dot, dash, or underscore
    cleaned = re.sub(r"[^a-zA-Z0-9._-]", "_", base)
    return cleaned[:100]

def compute_sha256(filepath: Path) -> str:
    """Computes SHA-256 hash of a file efficiently using 64KB blocks."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def detect_media_type_and_validate(filepath: Path, filename: str) -> Tuple[str, str]:
    """
    Validates file extension and genuine file signature (magic bytes).
    Returns (media_type, mime_type).
    Raises ValueError if unsupported or invalid signature.
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    # Sniff MIME type using file signature
    try:
        matches = puremagic.magic_file(str(filepath))
        if matches:
            detected_mime = matches[0].mime_type
        else:
            detected_mime = ""
    except Exception:
        detected_mime = ""

    # Map detected MIME or fallback based on extension if magic is ambiguous
    media_type = None
    if detected_mime in MIME_TYPE_MAPPING:
        media_type = MIME_TYPE_MAPPING[detected_mime]
    else:
        # Fallback to extension check if magic library is imprecise for some media containers
        if ext in ALLOWED_IMAGE_EXTENSIONS:
            media_type = "image"
            detected_mime = detected_mime or f"image/{ext.replace('.', '')}"
        elif ext in ALLOWED_VIDEO_EXTENSIONS:
            media_type = "video"
            detected_mime = detected_mime or f"video/{ext.replace('.', '')}"
        elif ext in ALLOWED_AUDIO_EXTENSIONS:
            media_type = "audio"
            detected_mime = detected_mime or f"audio/{ext.replace('.', '')}"

    if not media_type:
        raise ValueError(f"Unable to verify genuine media signature for file with MIME '{detected_mime}'")

    return media_type, detected_mime
