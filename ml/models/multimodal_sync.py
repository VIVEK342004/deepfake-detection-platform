import time
from pathlib import Path
from typing import Dict, Any, Optional
import cv2
import numpy as np

class MultimodalSyncAnalyzer:
    """
    Evaluates audio-visual lip-synchronization and temporal consistency
    by correlating mouth motion energy with speech acoustic envelope.
    """
    def __init__(self):
        self.status = "model_ready"

    def analyze_sync(
        self,
        video_path: Path,
        audio_path: Optional[Path] = None,
        max_duration: float = 15.0
    ) -> Dict[str, Any]:
        start_time = time.time()

        if audio_path is None or not audio_path.exists():
            return {
                "status": "model_unavailable",
                "is_synthetic": None,
                "confidence_score": 0.0,
                "raw_scores": {},
                "artifacts": {},
                "execution_time_seconds": round(time.time() - start_time, 4),
                "limitations_notes": "Multimodal sync requires both active video and audio tracks."
            }

        try:
            import librosa
            # Load audio envelope
            y, sr = librosa.load(str(audio_path), sr=16000, mono=True, duration=max_duration)
            hop_len = 512
            audio_rms = librosa.feature.rms(y=y, hop_length=hop_len)[0]
            audio_times = librosa.times_like(audio_rms, sr=sr, hop_length=hop_len)

            # Sample video frames to calculate visual movement
            cap = cv2.VideoCapture(str(video_path))
            fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            max_frames = int(min(total_frames, max_duration * fps))

            prev_gray = None
            motion_energies = []
            frame_times = []

            for f_idx in range(0, max_frames, 2):  # step 2 frames
                cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
                ret, frame = cap.read()
                if not ret or frame is None:
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Lower half of frame (mouth region approximation if face detector not run)
                h, w = gray.shape
                mouth_region = gray[int(h * 0.5):, int(w * 0.25):int(w * 0.75)]

                if prev_gray is not None and prev_gray.shape == mouth_region.shape:
                    diff = cv2.absdiff(mouth_region, prev_gray)
                    motion_energies.append(float(np.mean(diff)))
                else:
                    motion_energies.append(0.0)

                prev_gray = mouth_region
                frame_times.append(f_idx / fps)

            cap.release()

            if len(motion_energies) < 5 or len(audio_rms) < 5:
                return {
                    "status": "inconclusive",
                    "is_synthetic": None,
                    "confidence_score": 0.5,
                    "raw_scores": {"sync_correlation": 0.0},
                    "artifacts": {},
                    "execution_time_seconds": round(time.time() - start_time, 4),
                    "limitations_notes": "Insufficient motion or audio samples for correlation calculation."
                }

            # Resample audio RMS to match video motion timestamps
            interp_audio_rms = np.interp(frame_times, audio_times, audio_rms)

            # Compute normalized cross-correlation
            norm_motion = motion_energies - np.mean(motion_energies)
            norm_audio = interp_audio_rms - np.mean(interp_audio_rms)

            std_prod = np.std(motion_energies) * np.std(interp_audio_rms)
            if std_prod > 1e-6:
                corr = float(np.mean(norm_motion * norm_audio) / std_prod)
            else:
                corr = 0.0

            # Desync indicates possible deepfake / dubbing if correlation is strongly anomalous (< 0.10)
            # Authentic speech typically exhibits positive correlation between mouth kinematics and acoustic amplitude
            sync_desynchronized = corr < 0.10
            confidence = round(abs(corr), 4)

            return {
                "status": "completed",
                "is_synthetic": sync_desynchronized,
                "confidence_score": confidence,
                "raw_scores": {
                    "pearson_correlation": round(corr, 4),
                    "desync_threshold": 0.10
                },
                "artifacts": {
                    "evaluated_duration_sec": round(float(frame_times[-1]), 2) if frame_times else 0.0,
                    "evaluated_frames": len(frame_times),
                    "mean_motion_energy": round(float(np.mean(motion_energies)), 4),
                    "mean_audio_rms": round(float(np.mean(interp_audio_rms)), 4)
                },
                "execution_time_seconds": round(time.time() - start_time, 4),
                "limitations_notes": "Sync metrics measure kinematic-acoustic correlation; external noise or wide angles may lower correlation."
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": f"Audio-video sync evaluation failed: {str(e)}",
                "is_synthetic": None,
                "confidence_score": 0.0,
                "raw_scores": {},
                "artifacts": {},
                "execution_time_seconds": round(time.time() - start_time, 4),
                "limitations_notes": f"Sync analysis error: {str(e)}"
            }

multimodal_sync_analyzer = MultimodalSyncAnalyzer()
