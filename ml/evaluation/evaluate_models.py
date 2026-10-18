import time
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix
)
import torch

from ml.models.visual_detector import VisualDeepfakeClassifier
from ml.models.audio_detector import AudioDeepfakeClassifier

def compute_metrics(y_true: List[int], y_prob: List[float], threshold: float = 0.5) -> Dict[str, Any]:
    """Computes comprehensive binary classification forensic metrics."""
    y_pred = [1 if p >= threshold else 0 for p in y_prob]
    
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    precision = float(precision_score(y_true, y_pred, zero_division=0))
    recall = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = 0.5

    try:
        pr_auc = float(average_precision_score(y_true, y_prob))
    except Exception:
        pr_auc = 0.5

    return {
        "samples_evaluated": len(y_true),
        "decision_threshold": threshold,
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp)
        },
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4)
    }

def benchmark_model_latency(model: torch.nn.Module, input_tensor: torch.Tensor, runs: int = 20) -> Dict[str, Any]:
    """Measures inference latency and throughput on current hardware."""
    model.eval()
    times = []
    # Warmup
    for _ in range(3):
        with torch.no_grad():
            _ = model(input_tensor)

    for _ in range(runs):
        t0 = time.perf_counter()
        with torch.no_grad():
            _ = model(input_tensor)
        times.append(time.perf_counter() - t0)

    avg_ms = float(np.mean(times) * 1000)
    std_ms = float(np.std(times) * 1000)
    fps = float(1.0 / np.mean(times))

    return {
        "runs": runs,
        "mean_latency_ms": round(avg_ms, 2),
        "std_latency_ms": round(std_ms, 2),
        "throughput_fps": round(fps, 1)
    }

def run_evaluation_suite():
    print("=======================================================")
    print("   DEEPFAKE DETECTION PLATFORM - MODEL EVALUATION      ")
    print("=======================================================")

    # 1. Visual Model Evaluation
    visual_model = VisualDeepfakeClassifier(num_classes=2)
    vis_input = torch.randn(1, 3, 224, 224)
    vis_bench = benchmark_model_latency(visual_model, vis_input)
    print(f"\n[Visual Model Benchmark]")
    print(f"Latency: {vis_bench['mean_latency_ms']} ms ± {vis_bench['std_latency_ms']} ms")
    print(f"Throughput: {vis_bench['throughput_fps']} items/sec")

    # 2. Audio Model Evaluation
    audio_model = AudioDeepfakeClassifier(num_classes=2)
    aud_input = torch.randn(1, 1, 128, 94)
    aud_bench = benchmark_model_latency(audio_model, aud_input)
    print(f"\n[Audio Model Benchmark]")
    print(f"Latency: {aud_bench['mean_latency_ms']} ms ± {aud_bench['std_latency_ms']} ms")
    print(f"Throughput: {aud_bench['throughput_fps']} items/sec")

    print("\n[Protocol & Responsible AI Guidelines]")
    print("- Predictions must be treated as probabilistic indicators, not forensic proof.")
    print("- Calibrated thresholds are essential to prevent biased false positives on cross-demographic faces.")
    print("- Ensure face resolution >= 64x64px and audio duration >= 0.5s for meaningful inference.")
    print("=======================================================\n")

if __name__ == "__main__":
    run_evaluation_suite()
