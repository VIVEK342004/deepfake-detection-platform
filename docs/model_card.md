# VeritasAI Model Cards & Specification

This document provides transparent documentation for all neural networks and heuristic forensic modules deployed within the VeritasAI platform, adhering to the Responsible AI guidelines.

---

## 1. Visual Deepfake Classifier

### Overview
- **Model Name**: VisualDeepfakeClassifier
- **Version**: 1.0.0
- **Modality**: Visual (Image & Video Frames)
- **Task**: Binary Classification (Authentic vs. Synthetic/Manipulated)
- **Architecture**: 4-Block Convolutional Neural Network with Spatial Artifact Pooling
- **Checkpoint Location**: `ml/checkpoints/visual_deepfake_detector.pth`
- **Parameter Count**: 405,474 parameters
- **License**: Apache-2.0 / Academic Research

### Input / Output Specifications
- **Input Tensor**: `(B, 3, 224, 224)` normalized RGB tensor (`mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]`).
- **Output Tensor**: `(B, 2)` unnormalized logits, passed through `Softmax` to generate `[P(Real), P(Synthetic)]`.
- **Decision Threshold**: 0.50 (Calibrated for equal error rate under balanced benchmarks).

### Preprocessing & Face Isolation
- Faces are automatically localized using OpenCV Haar cascade.
- Bounding boxes are expanded by 20% to capture boundary warping and blending artifact transitions around the jawline and forehead.
- If no face is detected, the full frame is resized and evaluated, with a limitation warning attached to the report.

### Measured Performance
- **Inference Latency**: 114.6 ms ± 82.4 ms (CPU) / ~18 ms (GPU CUDA)
- **Throughput**: ~8.7 frames / second (CPU)

### Limitations & Ethical Considerations
- **Demographic Parity**: Performance may vary across skin tones if lighting causes facial detector failures.
- **Compression Sensitivity**: High-frequency tampering signatures degrade rapidly under aggressive JPEG compression (quality < 50).
- **Domain Shift**: Generative diffusion models with high step counts may produce novel artifacts unseen during training.

---

## 2. Audio Synthetic Speech Classifier

### Overview
- **Model Name**: AudioDeepfakeClassifier
- **Version**: 1.0.0
- **Modality**: Acoustic Speech
- **Task**: Binary Classification (Natural Human Speech vs. Synthetic Vocoder / TTS)
- **Architecture**: 2D-Convolutional Neural Network over Log-Mel Spectrograms
- **Checkpoint Location**: `ml/checkpoints/audio_deepfake_detector.pth`
- **Parameter Count**: 404,898 parameters
- **License**: Apache-2.0 / Academic Research

### Input / Output Specifications
- **Input Sampling Rate**: 16,000 Hz Mono.
- **Feature Extraction**: 128 Mel frequency bins, N_FFT = 1024, Hop Length = 512. Normalized to `[-1.0, 1.0]`.
- **Input Tensor**: `(B, 1, 128, T)` where T is proportional to chunk duration (default 3.0s window).
- **Output Tensor**: `(B, 2)` Softmax probabilities.

### Measured Performance
- **Inference Latency**: 27.6 ms ± 9.1 ms (CPU)
- **Throughput**: ~36.2 chunks / second (CPU)

### Limitations & Ethical Considerations
- **Minimum Recording Length**: Audio samples under 0.5 seconds cannot provide sufficient spectral resolution.
- **Acoustic Environment**: Heavy background music, reverberation, or low-quality cellular codecs can distort spectral flatness readings.

---

## 3. Multimodal Lip-Sync & Kinematic Analyzer

### Overview
- **Model Name**: MultimodalSyncAnalyzer
- **Modality**: Audio-Visual Fusion
- **Task**: Temporal Kinematic Cross-Correlation
- **Architecture**: Cross-Correlation between Mouth Optical Motion Energy and Speech Acoustic RMS Energy Envelope

### Specifications
- **Sampling Window**: First 15.0 seconds of video.
- **Metric**: Pearson Cross-Correlation coefficient `r`.
- **Desync Threshold**: `r < 0.10` flags potential dubbing or generative mouth manipulation.

### Limitations
- Requires unobstructed view of speaker's mouth. Side profiles or rapid camera movements induce noise into optical flow estimations.
