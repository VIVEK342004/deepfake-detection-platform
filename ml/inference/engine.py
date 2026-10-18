import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import cv2
import numpy as np
import torch

from ml.models.visual_detector import VisualDetectorService
from ml.models.audio_detector import AudioDetectorService
from ml.inference.video_processor import VideoProcessor
from ml.models.multimodal_sync import MultimodalSyncAnalyzer
from backend.app.core.config import settings
from backend.app.core.logging import logger

class InferenceEngine:
    """
    Unified manager orchestrating multimodal inference pipelines,
    model readiness tracking, and calibrated forensic reporting.
    """
    def __init__(self):
        checkpoints_dir = settings.ML_CHECKPOINTS_DIR
        device_pref = settings.ML_DEVICE

        self.visual_detector = VisualDetectorService(
            checkpoints_dir=checkpoints_dir,
            device_pref=device_pref
        )
        self.audio_detector = AudioDetectorService(
            checkpoints_dir=checkpoints_dir,
            device_pref=device_pref
        )
        self.video_processor = VideoProcessor(
            visual_detector=self.visual_detector,
            audio_detector=self.audio_detector
        )
        self.multimodal_sync = MultimodalSyncAnalyzer()

    def get_models_status(self) -> List[Dict[str, Any]]:
        """Returns readiness, architecture, and limitation details for all pipelines."""
        return [
            {
                "name": "Visual Deepfake Classifier",
                "modality": "visual",
                "architecture": "CNN-4Block (Spatial Artifact Pooling)",
                "status": self.visual_detector.status,
                "is_ready": self.visual_detector.status == "model_ready",
                "device": str(self.visual_detector.device),
                "checkpoint_found": self.visual_detector.checkpoint_path.exists(),
                "checkpoint_path": str(self.visual_detector.checkpoint_path),
                "parameters_count": self.visual_detector.parameters_count,
                "description": "Analyzes face crops and spatial textures for warping artifacts, blending edges, and GAN synthesis signatures.",
                "limitations": [
                    "Requires visible facial features for optimal accuracy",
                    "High-compression artifacts may cause false positives",
                    "Domain shift may affect detection of novel generative models"
                ]
            },
            {
                "name": "Audio Synthetic Speech Classifier",
                "modality": "audio",
                "architecture": "Log-Mel Spectrogram 2D-CNN",
                "status": self.audio_detector.status,
                "is_ready": self.audio_detector.status == "model_ready",
                "device": str(self.audio_detector.device),
                "checkpoint_found": self.audio_detector.checkpoint_path.exists(),
                "checkpoint_path": str(self.audio_detector.checkpoint_path),
                "parameters_count": self.audio_detector.parameters_count,
                "description": "Analyzes Log-Mel spectrograms for phase anomalies, vocoder artifacts, and speech-synthesis patterns.",
                "limitations": [
                    "Minimum 0.5s audio length required",
                    "Extreme background noise can degrade spectral flatness readings",
                    "Does not detect voice disguise without neural synthesis"
                ]
            },
            {
                "name": "Multimodal Sync & Kinematics Analyzer",
                "modality": "multimodal_sync",
                "architecture": "Kinematic-Acoustic Cross-Correlation",
                "status": "model_ready",
                "is_ready": True,
                "device": "cpu",
                "checkpoint_found": True,
                "checkpoint_path": None,
                "parameters_count": 0,
                "description": "Correlates mouth motion energy with speech acoustic envelope to detect dubbed or desynchronized speech.",
                "limitations": [
                    "Requires simultaneous active video and speech audio tracks",
                    "Camera angles occluding the mouth reduce reliability"
                ]
            }
        ]

    def analyze_image(self, file_path: Path) -> Dict[str, Any]:
        """Runs image analysis."""
        image_bgr = cv2.imread(str(file_path))
        if image_bgr is None:
            raise ValueError(f"Could not read image file at {file_path}")
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        visual_res = self.visual_detector.predict_image(image_rgb)

        return {
            "media_type": "image",
            "visual": visual_res,
            "audio": None,
            "multimodal_sync": None
        }

    def analyze_video(self, file_path: Path) -> Dict[str, Any]:
        """Runs video analysis including frame sampling and audio track."""
        visual_res, audio_res = self.video_processor.process_video(
            video_path=file_path,
            max_samples=settings.MAX_VIDEO_FRAMES_SAMPLE
        )

        sync_res = None
        # If video had audio, run sync analyzer
        extracted_wav = self.video_processor.extract_audio_track(file_path)
        if extracted_wav:
            try:
                sync_res = self.multimodal_sync.analyze_sync(file_path, extracted_wav)
            finally:
                extracted_wav.unlink(missing_ok=True)

        return {
            "media_type": "video",
            "visual": visual_res,
            "audio": audio_res,
            "multimodal_sync": sync_res
        }

    def analyze_audio(self, file_path: Path) -> Dict[str, Any]:
        """Runs audio synthetic speech analysis."""
        audio_res = self.audio_detector.predict_audio(file_path)

        return {
            "media_type": "audio",
            "visual": None,
            "audio": audio_res,
            "multimodal_sync": None
        }

    def synthesize_verdict(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes overall verdict, risk level, and findings
        without illegitimately averaging uncalibrated probabilities.
        """
        visual = results.get("visual")
        audio = results.get("audio")
        sync = results.get("multimodal_sync")

        # Check for unavailable or failed states
        all_completed = []
        is_synthetic_flags = []
        confidences = []
        findings = []

        if visual:
            if visual.get("status") == "model_unavailable":
                return {
                    "overall_prediction": "unprocessed",
                    "overall_confidence": 0.0,
                    "risk_level": "unknown",
                    "status": "model_unavailable",
                    "summary_findings": {
                        "primary_modality": "visual",
                        "status_note": "Visual deepfake detection model is not yet loaded.",
                        "details": visual.get("error")
                    }
                }
            if visual.get("status") == "completed":
                all_completed.append("visual")
                syn = visual.get("is_synthetic")
                if syn is not None:
                    is_synthetic_flags.append(syn)
                    confidences.append(visual.get("confidence_score", 0.0))
                    if syn:
                        findings.append(f"Visual anomalies identified with {visual.get('confidence_score', 0.0)*100:.1f}% confidence.")
                    else:
                        findings.append("No visual manipulation artifacts detected in sampled regions.")

        if audio:
            if audio.get("status") == "model_unavailable":
                return {
                    "overall_prediction": "unprocessed",
                    "overall_confidence": 0.0,
                    "risk_level": "unknown",
                    "status": "model_unavailable",
                    "summary_findings": {
                        "primary_modality": "audio",
                        "status_note": "Audio synthetic speech model is not yet loaded.",
                        "details": audio.get("error")
                    }
                }
            if audio.get("status") == "completed":
                all_completed.append("audio")
                syn = audio.get("is_synthetic")
                if syn is not None:
                    is_synthetic_flags.append(syn)
                    confidences.append(audio.get("confidence_score", 0.0))
                    if syn:
                        findings.append(f"Acoustic synthesis indicators detected with {audio.get('confidence_score', 0.0)*100:.1f}% confidence.")
                    else:
                        findings.append("Acoustic spectral distribution consistent with natural human speech.")

        if sync and sync.get("status") == "completed":
            syn = sync.get("is_synthetic")
            if syn:
                findings.append("Audio-visual lip desynchronization detected.")

        if not all_completed:
            return {
                "overall_prediction": "inconclusive",
                "overall_confidence": 0.0,
                "risk_level": "unknown",
                "status": "failed",
                "summary_findings": {"note": "No modality completed successfully."}
            }

        # Any verified synthetic flag raises risk
        any_synthetic = any(is_synthetic_flags)
        highest_confidence = max(confidences) if confidences else 0.0

        if any_synthetic:
            overall_prediction = "likely_synthetic"
            if highest_confidence >= 0.85:
                risk_level = "critical"
            elif highest_confidence >= 0.70:
                risk_level = "high"
            else:
                risk_level = "medium"
        else:
            overall_prediction = "likely_authentic"
            risk_level = "low"

        return {
            "overall_prediction": overall_prediction,
            "overall_confidence": round(highest_confidence, 4),
            "risk_level": risk_level,
            "status": "completed",
            "summary_findings": {
                "findings": findings,
                "active_modalities": all_completed,
                "recommendation": "Review individual modality breakdown and model cards for decision context."
            }
        }

engine = InferenceEngine()
