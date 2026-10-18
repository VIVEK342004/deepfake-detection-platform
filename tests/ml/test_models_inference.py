import pytest
import torch
import numpy as np
from pathlib import Path
from ml.models.visual_detector import VisualDeepfakeClassifier, VisualDetectorService
from ml.models.audio_detector import AudioDeepfakeClassifier, AudioDetectorService

def test_visual_model_tensor_shape_and_finite_values():
    model = VisualDeepfakeClassifier(num_classes=2)
    model.eval()
    dummy_input = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        logits = model(dummy_input)
        probs = torch.softmax(logits, dim=1)

    assert logits.shape == (2, 2)
    assert probs.shape == (2, 2)
    assert torch.all(torch.isfinite(probs))
    # Probabilities should sum to 1.0 along class dimension
    sums = torch.sum(probs, dim=1).numpy()
    np.testing.assert_allclose(sums, [1.0, 1.0], atol=1e-5)

def test_audio_model_tensor_shape_and_finite_values():
    model = AudioDeepfakeClassifier(num_classes=2)
    model.eval()
    dummy_input = torch.randn(2, 1, 128, 94)
    with torch.no_grad():
        logits = model(dummy_input)
        probs = torch.softmax(logits, dim=1)

    assert logits.shape == (2, 2)
    assert probs.shape == (2, 2)
    assert torch.all(torch.isfinite(probs))
    sums = torch.sum(probs, dim=1).numpy()
    np.testing.assert_allclose(sums, [1.0, 1.0], atol=1e-5)

def test_visual_detector_service_loading():
    service = VisualDetectorService()
    assert service.status in ["model_ready", "model_unavailable"]
    if service.status == "model_ready":
        # Run test prediction on synthetic image
        sample_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        res = service.predict_image(sample_img)
        assert res["status"] == "completed"
        assert "confidence_score" in res
        assert 0.0 <= res["confidence_score"] <= 1.0
        assert "prob_real" in res["raw_scores"]
        assert "prob_synthetic" in res["raw_scores"]

def test_model_unavailable_behavior_when_path_wrong():
    service = VisualDetectorService(checkpoints_dir="./nonexistent_dir")
    assert service.status == "model_unavailable"
    sample_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    res = service.predict_image(sample_img)
    assert res["status"] == "model_unavailable"
    assert res["is_synthetic"] is None
