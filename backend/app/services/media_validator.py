import os
from pathlib import Path
from typing import Dict, Any, Tuple
import cv2
from PIL import Image
import soundfile as sf
from backend.app.core.config import settings
from backend.app.core.logging import logger

class MediaValidationError(ValueError):
    pass

class MediaValidator:
    @staticmethod
    def inspect_image(filepath: Path) -> Dict[str, Any]:
        """Validates and extracts metadata from an image."""
        try:
            with Image.open(filepath) as img:
                img.verify()  # Verify integrity
            # Reopen to get details after verify()
            with Image.open(filepath) as img:
                width, height = img.size
                format_name = img.format
                mode = img.mode

            if width < 32 or height < 32:
                raise MediaValidationError(f"Image dimensions ({width}x{height}) are too small for facial analysis.")
            if width > 8192 or height > 8192:
                raise MediaValidationError(f"Image dimensions ({width}x{height}) exceed maximum allowed dimension of 8192px.")

            return {
                "width": width,
                "height": height,
                "format": format_name,
                "mode": mode,
                "aspect_ratio": round(width / max(height, 1), 2)
            }
        except MediaValidationError:
            raise
        except Exception as e:
            raise MediaValidationError(f"Corrupted or invalid image file: {str(e)}")

    @staticmethod
    def inspect_video(filepath: Path) -> Dict[str, Any]:
        """Validates and extracts metadata from a video using OpenCV."""
        cap = cv2.VideoCapture(str(filepath))
        try:
            if not cap.isOpened():
                raise MediaValidationError("Could not decode video stream or unsupported video container.")

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

            if fps <= 0:
                fps = 25.0  # reasonable fallback if container metadata lacks fps

            duration_seconds = round(total_frames / max(fps, 1.0), 2)

            if duration_seconds > settings.MAX_VIDEO_DURATION_SECONDS:
                raise MediaValidationError(
                    f"Video duration ({duration_seconds:.1f}s) exceeds maximum allowed {settings.MAX_VIDEO_DURATION_SECONDS}s"
                )

            if total_frames < 3:
                raise MediaValidationError("Video contains insufficient frames for analysis (minimum 3 required).")

            return {
                "width": width,
                "height": height,
                "fps": round(fps, 2),
                "total_frames": total_frames,
                "duration_seconds": duration_seconds,
                "aspect_ratio": round(width / max(height, 1), 2)
            }
        finally:
            cap.release()

    @staticmethod
    def inspect_audio(filepath: Path) -> Dict[str, Any]:
        """Validates and extracts metadata from an audio file using SoundFile."""
        try:
            info = sf.info(str(filepath))
            duration_seconds = round(info.duration, 2)

            if duration_seconds > settings.MAX_AUDIO_DURATION_SECONDS:
                raise MediaValidationError(
                    f"Audio duration ({duration_seconds:.1f}s) exceeds maximum allowed {settings.MAX_AUDIO_DURATION_SECONDS}s"
                )

            if duration_seconds < 0.5:
                raise MediaValidationError("Audio recording is too short (minimum 0.5 seconds required).")

            return {
                "sample_rate": info.samplerate,
                "channels": info.channels,
                "duration_seconds": duration_seconds,
                "format": info.format,
                "subtype": info.subtype
            }
        except MediaValidationError:
            raise
        except Exception as e:
            raise MediaValidationError(f"Could not parse audio file or unsupported audio encoding: {str(e)}")

media_validator = MediaValidator()
