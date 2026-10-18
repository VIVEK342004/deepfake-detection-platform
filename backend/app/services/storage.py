import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile
from backend.app.core.config import settings
from backend.app.core.security import sanitize_filename, compute_sha256

class StorageService:
    def __init__(self):
        self.uploads_dir = settings.uploads_dir
        self.thumbnails_dir = settings.thumbnails_dir
        self.processed_dir = settings.processed_dir

    def save_upload_file(self, upload_file: UploadFile) -> tuple[str, str, int, Path]:
        """
        Saves an uploaded file safely to disk using a unique UUID filename.
        Returns: (stored_filename, file_sha256, file_size_bytes, destination_path)
        """
        original_clean = sanitize_filename(upload_file.filename or "upload.bin")
        ext = Path(original_clean).suffix.lower()
        unique_name = f"{uuid.uuid4()}{ext}"
        dest_path = self.uploads_dir / unique_name

        file_size = 0
        with open(dest_path, "wb") as buffer:
            while chunk := upload_file.file.read(1024 * 1024):  # 1MB chunks
                file_size += len(chunk)
                if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
                    buffer.close()
                    dest_path.unlink(missing_ok=True)
                    raise ValueError(
                        f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_BYTES / (1024*1024):.1f} MB"
                    )
                buffer.write(chunk)

        sha256_hash = compute_sha256(dest_path)
        return unique_name, sha256_hash, file_size, dest_path

    def get_file_path(self, stored_filename: str) -> Path:
        """Retrieves absolute path for a stored file, preventing path traversal."""
        safe_name = os.path.basename(stored_filename)
        path = self.uploads_dir / safe_name
        if not path.is_file():
            raise FileNotFoundError(f"File '{stored_filename}' does not exist on storage.")
        return path

    def delete_file(self, stored_filename: str) -> bool:
        """Deletes file from storage."""
        try:
            path = self.get_file_path(stored_filename)
            path.unlink(missing_ok=True)
            return True
        except Exception:
            return False

storage_service = StorageService()
