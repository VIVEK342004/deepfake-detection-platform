import os
from typing import List, Tuple, Optional
import cv2
import numpy as np
from PIL import Image

class FaceDetector:
    """
    Detects faces in images or video frames using OpenCV Haar Cascades
    and returns cropped, normalized face patches.
    """
    def __init__(self, min_face_size: Tuple[int, int] = (64, 64)):
        self.min_face_size = min_face_size
        # Load OpenCV pre-packaged Haar cascade
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if not os.path.exists(cascade_path):
            raise FileNotFoundError(f"OpenCV Haar cascade not found at {cascade_path}")
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def detect_faces(self, image_np: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detects face bounding boxes in an image (RGB or BGR numpy array).
        Returns list of bounding boxes as (x, y, w, h).
        """
        if len(image_np.shape) == 3 and image_np.shape[2] == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        elif len(image_np.shape) == 2:
            gray = image_np
        else:
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGBA2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=self.min_face_size,
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        return [tuple(box) for box in faces]

    def crop_primary_face(
        self,
        image_np: np.ndarray,
        target_size: Tuple[int, int] = (224, 224),
        margin_ratio: float = 0.2
    ) -> Tuple[Optional[np.ndarray], Optional[Tuple[int, int, int, int]], int]:
        """
        Detects and crops the primary (largest area) face with a proportional margin.
        Returns: (cropped_face_rgb, bounding_box, total_faces_count)
        """
        faces = self.detect_faces(image_np)
        if not faces:
            return None, None, 0

        # Sort by area descending to find the primary face
        faces_sorted = sorted(faces, key=lambda b: b[2] * b[3], reverse=True)
        x, y, w, h = faces_sorted[0]

        img_h, img_w = image_np.shape[:2]
        margin_x = int(w * margin_ratio)
        margin_y = int(h * margin_ratio)

        x1 = max(0, x - margin_x)
        y1 = max(0, y - margin_y)
        x2 = min(img_w, x + w + margin_x)
        y2 = min(img_h, y + h + margin_y)

        face_crop = image_np[y1:y2, x1:x2]
        if face_crop.size == 0:
            return None, (x, y, w, h), len(faces)

        resized_face = cv2.resize(face_crop, target_size, interpolation=cv2.INTER_AREA)
        return resized_face, (x, y, w, h), len(faces)

face_detector = FaceDetector()
