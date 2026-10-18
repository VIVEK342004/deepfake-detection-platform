import React from 'react';
import {
  ShieldAlert,
  Cpu,
  Layers,
  Eye,
  Mic,
  Film,
  Lock,
  AlertTriangle,
  FileCheck
} from 'lucide-react';

export const Methodology: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-10">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Methodology & Responsible AI Framework
        </h1>
        <p className="mt-1 text-sm text-cyber-muted">
          Transparent scientific foundations, model architectures, dataset protocols, and forensic limitations.
        </p>
      </div>

      {/* Forensic Notice Banner */}
      <div className="p-5 rounded-2xl bg-cyber-card border border-cyber-accent/40 text-slate-200 flex items-start space-x-4 shadow-lg shadow-cyber-accent/5">
        <ShieldAlert className="w-6 h-6 text-cyber-accent shrink-0 mt-0.5" />
        <div className="space-y-1 text-xs sm:text-sm">
          <span className="font-bold text-white block">Forensic Non-Absolute Disclaimer</span>
          <p className="text-cyber-muted leading-relaxed">
            Neural deepfake detectors produce probabilistic likelihoods, not infallible mathematical proofs. Real-world media may contain natural artifacts from aggressive social media recompression (H.264/H.265 bit-rate starvation), camera sensor noise, or low-light exposure. VeritasAI outputs must always be evaluated alongside cryptographic provenance (C2PA) and human expert analysis.
          </p>
        </div>
      </div>

      {/* 3 Pipeline Architectural Pillars */}
      <div className="space-y-6">
        <h2 className="text-lg font-bold text-white flex items-center space-x-2">
          <Layers className="w-5 h-5 text-cyber-blue" />
          <span>Multimodal Detection Architecture</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 space-y-3">
            <div className="p-2.5 rounded-lg w-fit bg-sky-950 text-sky-400 border border-sky-800">
              <Eye className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white text-sm">Visual Artifact Analysis</h3>
            <p className="text-xs text-cyber-muted leading-relaxed">
              Automated facial landmark extraction isolates the primary facial boundary. A 4-stage convolutional backbone analyzes high-frequency gradient discontinuities, boundary blending seam artifacts, and generative GAN/Diffusion texture anomalies.
            </p>
          </div>

          <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 space-y-3">
            <div className="p-2.5 rounded-lg w-fit bg-purple-950 text-purple-400 border border-purple-800">
              <Film className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white text-sm">Temporal Video Aggregation</h3>
            <p className="text-xs text-cyber-muted leading-relaxed">
              Videos are evaluated without loading the entire stream into memory. Uniform frame decimation samples representative frames. Predictions are synthesized via 60% top-percentile anomaly pooling + 40% sequence mean to reliably catch burst manipulations.
            </p>
          </div>

          <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 space-y-3">
            <div className="p-2.5 rounded-lg w-fit bg-emerald-950 text-emerald-400 border border-emerald-800">
              <Mic className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white text-sm">Acoustic Spoof Detection</h3>
            <p className="text-xs text-cyber-muted leading-relaxed">
              Audio tracks are resampled to 16,000 Hz mono and segmented into 3.0s windows. 128-bin Log-Mel spectrograms evaluate vocoder phase jitter, synthetic spectral flatness, and harmonic distortion characteristic of modern text-to-speech generators.
            </p>
          </div>
        </div>
      </div>

      {/* Known Limitations & Domain Shifts */}
      <div className="bg-cyber-card border border-cyber-border rounded-2xl p-6 space-y-4">
        <h2 className="text-base font-bold text-white flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <span>Known Limitations & Failure Modes</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-cyber-muted">
          <div className="p-4 rounded-xl bg-cyber-surface/60 border border-cyber-border space-y-2">
            <span className="font-semibold text-slate-200 block">Severe Lossy Compression</span>
            <p>
              Re-encoding video multiple times (e.g. WhatsApp, TikTok) removes high-frequency spatial harmonics, which may lead to false negatives or lower confidence ratings.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-cyber-surface/60 border border-cyber-border space-y-2">
            <span className="font-semibold text-slate-200 block">Extreme Facial Pose & Occlusion</span>
            <p>
              Yaw/pitch angles exceeding 45 degrees or facial masks reduce face detector recall, prompting fallback to whole-frame evaluation.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-cyber-surface/60 border border-cyber-border space-y-2">
            <span className="font-semibold text-slate-200 block">Acoustic Reverb & Background Music</span>
            <p>
              High acoustic background noise or heavy musical instrumentation interferes with Log-Mel voice analysis. Vocal isolation is recommended for multi-speaker recordings.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-cyber-surface/60 border border-cyber-border space-y-2">
            <span className="font-semibold text-slate-200 block">Generative Model Domain Shift</span>
            <p>
              New generative synthesis methods (e.g. Sora, novel flow-matching audio vocoders) can produce subtle artifacts that differ from historical benchmark datasets.
            </p>
          </div>
        </div>
      </div>

      {/* Security & Data Retention Policy */}
      <div className="bg-cyber-card border border-cyber-border rounded-2xl p-6 space-y-4">
        <h2 className="text-base font-bold text-white flex items-center space-x-2">
          <Lock className="w-5 h-5 text-cyber-accent" />
          <span>Privacy & Cryptographic Data Retention</span>
        </h2>
        <div className="space-y-3 text-xs text-cyber-muted leading-relaxed">
          <p>
            VeritasAI enforces enterprise-grade data isolation. Uploaded media is assigned an immutable UUID, validated against strict MIME and magic byte signatures, and stored in isolated non-executable directories.
          </p>
          <ul className="list-disc list-inside space-y-1">
            <li>Media files are automatically pruned after the retention expiry period (default 7 days).</li>
            <li>SHA-256 cryptographic hashes are preserved for digital evidence audit trails.</li>
            <li>No customer media is ever transmitted to unauthenticated third-party APIs or utilized for model training without consent.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
