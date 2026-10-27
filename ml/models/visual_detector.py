import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image

from ml.preprocessing.face_detector import face_detector

class VisualDeepfakeClassifier(nn.Module):
    """
    Convolutional Neural Network tailored for visual artifact and facial deepfake detection.
    Combines feature extraction layers with spatial artifact pooling.
    """
    def __init__(self, num_classes: int = 2, dropout_rate: float = 0.3):
        super().__init__()
        # 4 Conv blocks with batch norm and LeakyReLU for capturing high-frequency tampering
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.1, inplace=True),
            nn.MaxPool2d(2, 2),  # 112x112

            nn.Conv2d(32, 64, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.1, inplace=True),
            nn.MaxPool2d(2, 2),  # 56x56

            nn.Conv2d(64, 128, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.1, inplace=True),
            nn.MaxPool2d(2, 2),  # 28x28

            nn.Conv2d(128, 256, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.1, inplace=True),
            nn.AdaptiveAvgPool2d((1, 1))  # 1x1
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, 64),
            nn.LeakyReLU(0.1, inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(64, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        logits = self.classifier(x)
        return logits


class VisualDetectorService:
    """
    Manages model loading, device allocation, image preprocessing,
    and genuine inference for image manipulation detection.
    """
    def __init__(self, checkpoints_dir: str = "./ml/checkpoints", device_pref: str = "auto"):
        self.checkpoints_dir = Path(checkpoints_dir)
        self.checkpoint_path = self.checkpoints_dir / "visual_deepfake_detector.pth"
        
        # Determine compute device
        if device_pref == "cuda" and torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif device_pref == "auto" and torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

        self.model: Optional[VisualDeepfakeClassifier] = None
        self.status: str = "model_unavailable"  # model_ready, model_unavailable, inference_failed
        self.parameters_count: int = 0
        self.error_detail: Optional[str] = None

        # Standard normalization for 224x224 RGB inputs
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        self.load_model()

    def load_model(self) -> bool:
        """Loads model weights from checkpoint if available."""
        try:
            self.model = VisualDeepfakeClassifier(num_classes=2)
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
                    f"Train or export a checkpoint using ml/training/train_visual.py."
                )
                return False
        except Exception as e:
            self.status = "inference_failed"
            self.error_detail = f"Failed to load checkpoint: {str(e)}"
            return False

    def predict_image(self, image_np: np.ndarray) -> Dict[str, Any]:
        """
        Executes genuine inference on an input RGB image numpy array.
        Handles face detection, cropping, normalization, and model prediction.
        """
        start_time = time.time()

        if self.status != "model_ready" or self.model is None:
            return {
                "status": self.status,
                "error": self.error_detail or "Visual model is unavailable.",
                "is_synthetic": None,
                "confidence_score": 0.0,
                "raw_scores": {},
                "artifacts": {},
                "execution_time_seconds": round(time.time() - start_time, 4),
                "limitations_notes": "Inference halted: Checkpoint missing or model unavailable."
            }

        # Step 1: Detect primary face
        face_crop, face_box, total_faces = face_detector.crop_primary_face(image_np)
        face_detected = face_crop is not None

        # Preprocess input tensor (use face crop if present, else center crop full image)
        if face_detected:
            input_img = face_crop
            subject_type = "cropped_face"
        else:
            # Fallback to whole image if no face detected
            input_img = cv2.resize(image_np, (224, 224))
            subject_type = "whole_image_no_face"

        try:
            tensor = self.transform(input_img).unsqueeze(0).to(self.device)

            with torch.no_grad():
                logits = self.model(tensor)
                probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()

            prob_real = float(probs[0])
            prob_fake = float(probs[1])

            # Class 1 is Synthetic/Deepfake, Class 0 is Authentic/Real
            is_synthetic = prob_fake >= 0.5
            confidence = prob_fake if is_synthetic else prob_real

            execution_time = round(time.time() - start_time, 4)

            notes = []
            if not face_detected:
                notes.append("No human face detected. Analysis performed on full frame, which may reduce deepfake detection accuracy.")
            if total_faces > 1:
                notes.append(f"Multiple faces ({total_faces}) detected. Primary (largest) face was prioritized for analysis.")

            return {
                "status": "completed",
                "is_synthetic": is_synthetic,
                "confidence_score": round(confidence, 4),
                "raw_scores": {
                    "prob_real": round(prob_real, 4),
                    "prob_synthetic": round(prob_fake, 4),
                    "decision_threshold": 0.5
                },
                "artifacts": {
                    "face_detected": bool(face_detected),
                    "face_box": [int(x) for x in face_box] if face_box else None,
                    "total_faces": int(total_faces),
                    "subject_type": subject_type,
                    "device_used": str(self.device)
                },
                "execution_time_seconds": execution_time,
                "limitations_notes": " ".join(notes) if notes else "Facial region successfully extracted and analyzed."
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": f"Inference execution failed: {str(e)}",
                "is_synthetic": None,
                "confidence_score": 0.0,
                "raw_scores": {},
                "artifacts": {},
                "execution_time_seconds": round(time.time() - start_time, 4),
                "limitations_notes": f"Runtime error during tensor evaluation: {str(e)}"
            }
