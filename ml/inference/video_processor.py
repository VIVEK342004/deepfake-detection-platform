import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np

from ml.models.visual_detector import VisualDetectorService
from ml.models.audio_detector import AudioDetectorService
from backend.app.core.config import settings
from backend.app.core.logging import logger

class VideoProcessor:
    """
    Decodes video streams, samples representative frames without full-memory buffering,
    extracts audio tracks with FFmpeg when available, and aggregates frame predictions.
    """
    def __init__(self, visual_detector: VisualDetectorService, audio_detector: AudioDetectorService):
        self.visual_detector = visual_detector
        self.audio_detector = audio_detector

    def extract_audio_track(self, video_path: Path) -> Optional[Path]:
        """
        Uses bundled FFmpeg to extract audio track to a temporary 16kHz mono WAV file.
        Returns Path to extracted wav or None if video has no audio track.
        """
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            ffmpeg_exe = "ffmpeg"

        temp_wav = Path(tempfile.gettempdir()) / f"extracted_{video_path.stem}.wav"
        
        # FFmpeg command: -vn (no video), -ac 1 (mono), -ar 16000 (16kHz), -y (overwrite)
        cmd = [
            ffmpeg_exe,
            "-y",
            "-v", "error",
            "-i", str(video_path),
            "-vn",
            "-ac", "1",
            "-ar", "16000",
            str(temp_wav)
        ]

        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            if result.returncode == 0 and temp_wav.exists() and temp_wav.stat().st_size > 1000:
                return temp_wav
            else:
                temp_wav.unlink(missing_ok=True)
                return None
        except Exception as e:
            logger.warning(f"Audio extraction via FFmpeg skipped or failed: {e}")
            temp_wav.unlink(missing_ok=True)
            return None

    def process_video(
        self,
        video_path: Path,
        max_samples: int = 32
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Analyzes video frames and audio track.
        Returns: (visual_result, audio_result_or_none)
        """
        start_time = time.time()
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            return {
                "status": "failed",
                "error": "Could not open video file.",
                "is_synthetic": None,
                "confidence_score": 0.0,
                "raw_scores": {},
                "artifacts": {},
                "execution_time_seconds": round(time.time() - start_time, 4),
                "limitations_notes": "Video decoding failed."
            }, None

        try:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
            duration = round(total_frames / max(fps, 1.0), 2)

            if total_frames <= 0:
                raise ValueError("Video contains no readable frames.")

            # Calculate uniform sampling frame indices
            sample_count = min(max_samples, total_frames)
            frame_indices = np.linspace(0, total_frames - 1, sample_count, dtype=int)

            frame_results: List[Dict[str, Any]] = []
            fake_scores: List[float] = []
            faces_detected_count = 0

            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
                ret, frame_bgr = cap.read()
                if not ret or frame_bgr is None:
                    continue

                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                timestamp = round(float(idx) / max(fps, 1.0), 2)

                # Predict single frame
                pred = self.visual_detector.predict_image(frame_rgb)
                if pred["status"] != "completed":
                    # If model is unavailable, return early with model_unavailable status
                    return pred, None

                is_face = pred["artifacts"].get("face_detected", False)
                if is_face:
                    faces_detected_count += 1

                p_fake = pred["raw_scores"].get("prob_synthetic", 0.0)
                p_real = pred["raw_scores"].get("prob_real", 1.0)
                fake_scores.append(p_fake)

                frame_results.append({
                    "frame_index": int(idx),
                    "timestamp_seconds": timestamp,
                    "face_detected": is_face,
                    "face_box": pred["artifacts"].get("face_box"),
                    "confidence_fake": round(p_fake, 4),
                    "confidence_real": round(p_real, 4),
                    "is_anomaly": p_fake >= 0.70
                })

            # Video Aggregation Logic:
            # Deepfake videos often tamper specific segments or key frames.
            # We aggregate using: 60% top 20% highest fake frames + 40% mean across all sampled frames
            if fake_scores:
                sorted_scores = sorted(fake_scores, reverse=True)
                top_k = max(1, int(len(sorted_scores) * 0.2))
                top_mean = float(np.mean(sorted_scores[:top_k]))
                overall_mean = float(np.mean(fake_scores))
                aggregated_fake_score = float(0.6 * top_mean + 0.4 * overall_mean)
            else:
                aggregated_fake_score = 0.0

            is_synthetic = aggregated_fake_score >= 0.5
            confidence = aggregated_fake_score if is_synthetic else (1.0 - aggregated_fake_score)

            notes = []
            if faces_detected_count == 0:
                notes.append("No facial landmarks identified across sampled video frames. Whole-frame detection used.")
            elif faces_detected_count < (len(frame_results) / 2):
                notes.append(f"Faces were only detectable in {faces_detected_count}/{len(frame_results)} analyzed frames.")

            visual_result = {
                "status": "completed",
                "is_synthetic": is_synthetic,
                "confidence_score": round(confidence, 4),
                "raw_scores": {
                    "prob_real": round(1.0 - aggregated_fake_score, 4),
                    "prob_synthetic": round(aggregated_fake_score, 4),
                    "top_frames_fake_mean": round(top_mean, 4) if fake_scores else 0.0,
                    "all_frames_fake_mean": round(overall_mean, 4) if fake_scores else 0.0
                },
                "artifacts": {
                    "total_video_frames": total_frames,
                    "sampled_frames_count": len(frame_results),
                    "faces_detected_count": faces_detected_count,
                    "fps": round(fps, 2),
                    "duration_seconds": duration,
                    "frame_results": frame_results
                },
                "execution_time_seconds": round(time.time() - start_time, 4),
                "limitations_notes": " ".join(notes) if notes else "Uniform frame sampling and facial aggregation successfully completed."
            }

        finally:
            cap.release()

        # Step 2: Extract and evaluate audio track if present
        audio_result = None
        extracted_audio_path = self.extract_audio_track(video_path)
        if extracted_audio_path:
            try:
                audio_result = self.audio_detector.predict_audio(extracted_audio_path)
            finally:
                extracted_audio_path.unlink(missing_ok=True)

        return visual_result, audio_result
