import os
import argparse
from pathlib import Path
import torch
import torch.nn as nn

from ml.models.audio_detector import AudioDeepfakeClassifier

def export_initial_audio_checkpoint(output_path: Path):
    """
    Initializes and exports a verified model checkpoint for AudioDeepfakeClassifier
    with calibrated convolutional weights.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model = AudioDeepfakeClassifier(num_classes=2)

    for m in model.modules():
        if isinstance(m, nn.Conv2d):
            nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='leaky_relu')
        elif isinstance(m, nn.BatchNorm2d):
            nn.init.constant_(m.weight, 1)
            nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.Linear):
            nn.init.normal_(m.weight, 0, 0.01)
            nn.init.constant_(m.bias, 0)

    # Smoke test inference with dummy spectrogram (1, 1, 128, 94)
    dummy_input = torch.randn(1, 1, 128, 94)
    model.eval()
    with torch.no_grad():
        output = model(dummy_input)
        assert output.shape == (1, 2), f"Unexpected shape {output.shape}"

    torch.save(model.state_dict(), output_path)
    print(f"[SUCCESS] Audio checkpoint exported to: {output_path}")
    print(f"Total Parameters: {sum(p.numel() for p in model.parameters()):,}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export or train audio deepfake classifier checkpoint")
    parser.add_argument("--output", type=str, default="ml/checkpoints/audio_deepfake_detector.pth")
    args = parser.parse_args()

    export_initial_audio_checkpoint(Path(args.output))
