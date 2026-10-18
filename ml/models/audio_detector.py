import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np
import librosa
import soundfile as sf
import torch
import torch.nn as nn

class AudioDeepfakeClassifier(nn.Module):
    """
    Convolutional Neural Network for Log-Mel Spectrogram synthetic speech detection.
    Analyzes high-frequency phase and spectral discontinuities characteristic of vocoders & TTS.
    """
    def __init__(self, num_classes: int = 2, dropout_rate: float = 0.3):
        super().__init__()
        self.conv = nn.Sequential(
            # Input: (B, 1, 128, T)
            nn.Conv2d(1, 32, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.1, inplace=True),
            nn.MaxPool2d((2, 2)),  # 64, T/2

            nn.Conv2d(32, 64, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.1, inplace=True),
            nn.MaxPool2d((2, 2)),  # 32, T/4

            nn.Conv2d(64, 128, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.1, inplace=True),
            nn.MaxPool2d((2, 2)),  # 16, T/8

            nn.Conv2d(128, 256, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.1, inplace=True),
            nn.AdaptiveAvgPool2d((1, 1))  # 1x1
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, 64),
            nn.LeakyReLU(0.1, inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(64, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.conv(x)
        logits = self.fc(feat)
        return logits


class AudioDetectorService:
    """
    Manages audio decoding, resampling to 16kHz, spectrogram generation,
    chunking, and model inference for synthetic speech detection.
    """
    TARGET_SR = 16000
    CHUNK_DURATION_SEC = 3.0  # 3 second windows
    N_MELS = 128
    N_FFT = 1024
    HOP_LENGTH = 512

    def __init__(self, checkpoints_dir: str = "./ml/checkpoints", device_pref: str = "auto"):
        self.checkpoints_dir = Path(checkpoints_dir)
        self.checkpoint_path = self.checkpoints_dir / "audio_deepfake_detector.pth"

        if device_pref == "cuda" and torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif device_pref == "auto" and torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

        self.model: Optional[AudioDeepfakeClassifier] = None
        self.status: str = "model_unavailable"
        self.parameters_count: int = 0
        self.error_detail: Optional[str] = None

        self.load_model()

    def load_model(self) -> bool:
        """Loads model weights from checkpoint if available."""
        try:
            self.model = AudioDeepfakeClassifier(num_classes=2)
            self.parameters_count = sum(p.numel() for p in self.model.parameters())

            if self.checkpoint_path.exists():
                state_dict = torch.load(self.checkpoint_path, map_location=self.device, weights_only=True)
                self.model.load_state_dict(state_dict)
                self.model.to(self.device)
                self.model.eval()
                self.status = "model_ready"
                self.error_detail = None
                return True
            else:
                self.status = "model_unavailable"
                self.error_detail = (
                    f"Checkpoint not found at '{self.checkpoint_path}'. "
                    f"Train or export a checkpoint using ml/training/train_audio.py."
                )
                return False
        except Exception as e:
            self.status = "inference_failed"
            self.error_detail = f"Failed to load audio checkpoint: {str(e)}"
            return False

    def _extract_log_mel_spectrogram(self, y: np.ndarray, sr: int) -> torch.Tensor:
        """Computes normalized Log-Mel Spectrogram tensor from raw waveform."""
        mel_spec = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_mels=self.N_MELS,
            n_fft=self.N_FFT,
            hop_length=self.HOP_LENGTH
        )
        log_mel = librosa.power_to_db(mel_spec, ref=np.max)
        # Normalize to [-1, 1]
        norm_mel = (log_mel + 40.0) / 40.0
        norm_mel = np.clip(norm_mel, -1.0, 1.0)
        # Convert to tensor shape (1, 1, n_mels, time_steps)
        tensor = torch.from_numpy(norm_mel).float().unsqueeze(0).unsqueeze(0)
        return tensor

    def predict_audio(self, audio_path: Path) -> Dict[str, Any]:
        """
        Loads audio, handles chunking, extracts acoustic features, and performs inference.
        """
        start_time = time.time()

        if self.status != "model_ready" or self.model is None:
            return {
                "status": self.status,
                "error": self.error_detail or "Audio model is unavailable.",
                "is_synthetic": None,
                "confidence_score": 0.0,
                "raw_scores": {},
                "artifacts": {},
                "execution_time_seconds": round(time.time() - start_time, 4),
                "limitations_notes": "Inference halted: Audio model checkpoint is missing."
            }

        try:
            # Step 1: Load and resample audio to 16kHz mono
            y, sr = librosa.load(str(audio_path), sr=self.TARGET_SR, mono=True)
            duration = float(librosa.get_duration(y=y, sr=sr))

            if duration < 0.5:
                return {
                    "status": "failed",
                    "error": "Audio length is less than minimum 0.5s requirement.",
                    "is_synthetic": None,
                    "confidence_score": 0.0,
                    "raw_scores": {},
                    "artifacts": {},
                    "execution_time_seconds": round(time.time() - start_time, 4),
                    "limitations_notes": "Audio sample is too short to evaluate reliably."
                }

            # Extract acoustic forensic indicators
            flatness = float(np.mean(librosa.feature.spectral_flatness(y=y)))
            centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
            rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))

            # Step 2: Chunk into segments of CHUNK_DURATION_SEC
            samples_per_chunk = int(self.CHUNK_DURATION_SEC * sr)
            chunks = []
            if len(y) <= samples_per_chunk:
                # Pad to minimum chunk size
                padded = np.pad(y, (0, samples_per_chunk - len(y)), mode='constant')
                chunks.append((0.0, duration, padded))
            else:
                for i in range(0, len(y), samples_per_chunk):
                    chunk_y = y[i:i + samples_per_chunk]
                    if len(chunk_y) < (sr * 0.5):  # ignore tiny tail
                        continue
                    if len(chunk_y) < samples_per_chunk:
                        chunk_y = np.pad(chunk_y, (0, samples_per_chunk - len(chunk_y)), mode='constant')
                    t_start = round(i / sr, 2)
                    t_end = round(min((i + samples_per_chunk) / sr, duration), 2)
                    chunks.append((t_start, t_end, chunk_y))

            chunk_results: List[Dict[str, Any]] = []
            fake_probs: List[float] = []

            for start_sec, end_sec, chunk_wave in chunks:
                tensor = self._extract_log_mel_spectrogram(chunk_wave, sr).to(self.device)
                with torch.no_grad():
                    logits = self.model(tensor)
                    probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()

                p_real = float(probs[0])
                p_fake = float(probs[1])
                fake_probs.append(p_fake)

                chunk_results.append({
                    "start_seconds": start_sec,
                    "end_seconds": end_sec,
                    "confidence_fake": round(p_fake, 4),
                    "confidence_real": round(p_real, 4)
                })

            # Aggregation: use trimmed mean / max-pool across chunks
            avg_fake_prob = float(np.mean(fake_probs)) if fake_probs else 0.0
            max_fake_prob = float(np.max(fake_probs)) if fake_probs else 0.0
            # Weighting: 70% mean + 30% max peak anomaly
            aggregated_fake_prob = float(0.7 * avg_fake_prob + 0.3 * max_fake_prob)

            is_synthetic = aggregated_fake_prob >= 0.5
            confidence = aggregated_fake_prob if is_synthetic else (1.0 - aggregated_fake_prob)

            execution_time = round(time.time() - start_time, 4)

            notes = []
            if duration > 60.0:
                notes.append("Long audio recording processed in sequential chunks.")
            if flatness > 0.05:
                notes.append("Elevated spectral flatness detected; synthetic vocoder artifacts may be present.")

            return {
                "status": "completed",
                "is_synthetic": is_synthetic,
                "confidence_score": round(confidence, 4),
                "raw_scores": {
                    "prob_real": round(1.0 - aggregated_fake_prob, 4),
                    "prob_synthetic": round(aggregated_fake_prob, 4),
                    "avg_chunk_fake_prob": round(avg_fake_prob, 4),
                    "max_chunk_fake_prob": round(max_fake_prob, 4)
                },
                "artifacts": {
                    "duration_seconds": round(duration, 2),
                    "chunks_analyzed": len(chunks),
                    "chunk_results": chunk_results[:20],  # cap list for schema size
                    "acoustic_features": {
                        "spectral_flatness_mean": round(flatness, 6),
                        "spectral_centroid_hz": round(centroid, 2),
                        "spectral_rolloff_hz": round(rolloff, 2)
                    },
                    "device_used": str(self.device)
                },
                "execution_time_seconds": execution_time,
                "limitations_notes": " ".join(notes) if notes else "Audio waveform normalized and spectral analysis completed."
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": f"Audio processing failed: {str(e)}",
                "is_synthetic": None,
                "confidence_score": 0.0,
                "raw_scores": {},
                "artifacts": {},
                "execution_time_seconds": round(time.time() - start_time, 4),
                "limitations_notes": f"Audio decoding or analysis error: {str(e)}"
            }
