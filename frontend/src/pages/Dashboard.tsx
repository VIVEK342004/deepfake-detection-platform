import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldAlert,
  ShieldCheck,
  Film,
  Mic,
  Image as ImageIcon,
  ArrowRight,
  RefreshCw,
  Cpu,
  Layers,
  AlertTriangle
} from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';
import { getAnalyses, getSystemStatus } from '../services/api';
import type { AnalysisSummary, SystemStatusResponse } from '../types';

export const Dashboard: React.FC = () => {
  const [analyses, setAnalyses] = useState<AnalysisSummary[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [systemStatus, setSystemStatus] = useState<SystemStatusResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [listRes, sysRes] = await Promise.all([
        getAnalyses({ page: 1, pageSize: 6 }),
        getSystemStatus()
      ]);
      setAnalyses(listRes.items);
      setTotalCount(listRes.total);
      setSystemStatus(sysRes);
    } catch (err: any) {
      setError(err.message || 'Failed to communicate with Deepfake Platform backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const syntheticCount = analyses.filter(a => a.overall_prediction === 'likely_synthetic').length;
  const authenticCount = analyses.filter(a => a.overall_prediction === 'likely_authentic').length;
  const modelsReadyCount = systemStatus?.models.filter(m => m.is_ready).length || 0;
  const totalModelsCount = systemStatus?.models.length || 0;

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white flex items-center space-x-2">
            <span>Threat Intelligence & Deepfake Radar</span>
          </h1>
          <p className="mt-1 text-sm text-cyber-muted">
            Continuous multimodal monitoring across synthetic imagery, temporal video tampering, and cloned audio.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2.5 rounded-lg bg-cyber-card border border-cyber-border text-slate-300 hover:text-white hover:border-cyber-accent/50 transition-all"
            title="Refresh statistics"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <Link
            to="/new"
            className="flex items-center space-x-2 px-4 py-2.5 rounded-lg bg-cyber-accent text-cyber-bg font-semibold text-sm hover:bg-cyber-accent/90 transition-all shadow-lg shadow-cyber-accent/10"
          >
            <span>Scan New Media</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800 text-red-300 text-sm flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold">Backend Connection Notice: </span>
            <span>{error} (Ensure FastAPI backend is running on 127.0.0.1:8000)</span>
          </div>
        </div>
      )}

      {/* KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Scans"
          value={totalCount}
          subtitle="Processed media records"
          icon={Layers}
          variant="default"
        />
        <MetricCard
          title="Flagged Synthetic"
          value={syntheticCount}
          subtitle="Confirmed or likely deepfakes"
          icon={ShieldAlert}
          variant="danger"
        />
        <MetricCard
          title="Verified Authentic"
          value={authenticCount}
          subtitle="Natural media signatures"
          icon={ShieldCheck}
          variant="success"
        />
        <MetricCard
          title="Models Active"
          value={`${modelsReadyCount}/${totalModelsCount}`}
          subtitle={systemStatus?.device ? `Engine Device: ${systemStatus.device.toUpperCase()}` : 'Neural backbones'}
          icon={Cpu}
          variant="accent"
        />
      </div>

      {/* Secondary Row: Modalities + Architecture Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Modality Capabilities Card */}
        <div className="bg-cyber-card/70 border border-cyber-border rounded-xl p-5 lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between border-b border-cyber-border/60 pb-3">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-200">
              Active Forensic Pipelines
            </h3>
            <span className="text-xs text-cyber-accent font-mono">Multimodal Isolated</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-cyber-surface/70 border border-cyber-border space-y-2">
              <div className="p-2 rounded-lg w-fit bg-sky-950 text-sky-400 border border-sky-800">
                <ImageIcon className="w-5 h-5" />
              </div>
              <h4 className="font-semibold text-white text-sm">Visual Classifier</h4>
              <p className="text-xs text-cyber-muted leading-relaxed">
                4-Block CNN with spatial artifact pooling. Analyzes face crops for warping, blending seams, and generative diffusion noise.
              </p>
              <div className="text-[11px] font-mono text-slate-400 pt-1">
                Formats: JPG, PNG, WEBP
              </div>
            </div>

            <div className="p-4 rounded-xl bg-cyber-surface/70 border border-cyber-border space-y-2">
              <div className="p-2 rounded-lg w-fit bg-purple-950 text-purple-400 border border-purple-800">
                <Film className="w-5 h-5" />
              </div>
              <h4 className="font-semibold text-white text-sm">Video Temporal</h4>
              <p className="text-xs text-cyber-muted leading-relaxed">
                Uniform frame decimation, facial landmark tracking, and top-percentile anomaly score pooling.
              </p>
              <div className="text-[11px] font-mono text-slate-400 pt-1">
                Formats: MP4, AVI, MOV, MKV
              </div>
            </div>

            <div className="p-4 rounded-xl bg-cyber-surface/70 border border-cyber-border space-y-2">
              <div className="p-2 rounded-lg w-fit bg-emerald-950 text-emerald-400 border border-emerald-800">
                <Mic className="w-5 h-5" />
              </div>
              <h4 className="font-semibold text-white text-sm">Acoustic Spoof</h4>
              <p className="text-xs text-cyber-muted leading-relaxed">
                Log-Mel Spectrogram 2D-CNN at 16kHz. Evaluates spectral flatness, vocoder phase anomalies, and TTS speech cloning.
              </p>
              <div className="text-[11px] font-mono text-slate-400 pt-1">
                Formats: WAV, MP3, FLAC, M4A
              </div>
            </div>
          </div>
        </div>

        {/* System Limits & Notice */}
        <div className="bg-cyber-card/70 border border-cyber-border rounded-xl p-5 flex flex-col justify-between space-y-4">
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-200 border-b border-cyber-border/60 pb-3">
              Operational Constraints
            </h3>
            <ul className="mt-3 space-y-2.5 text-xs text-slate-300">
              <li className="flex justify-between">
                <span className="text-cyber-muted">Max Upload Size:</span>
                <span className="font-mono text-white">
                  {systemStatus?.limits.max_upload_size_mb || 50} MB
                </span>
              </li>
              <li className="flex justify-between">
                <span className="text-cyber-muted">Max Video Duration:</span>
                <span className="font-mono text-white">
                  {systemStatus?.limits.max_video_duration_seconds || 120}s
                </span>
              </li>
              <li className="flex justify-between">
                <span className="text-cyber-muted">Max Audio Duration:</span>
                <span className="font-mono text-white">
                  {systemStatus?.limits.max_audio_duration_seconds || 300}s
                </span>
              </li>
              <li className="flex justify-between">
                <span className="text-cyber-muted">Sampled Video Frames:</span>
                <span className="font-mono text-white">
                  {systemStatus?.limits.max_sampled_frames || 32} frames
                </span>
              </li>
              <li className="flex justify-between">
                <span className="text-cyber-muted">Inference Device:</span>
                <span className="font-mono text-cyber-accent">
                  {systemStatus?.device?.toUpperCase() || 'CPU'}
                </span>
              </li>
            </ul>
          </div>

          <div className="p-3 rounded-lg bg-cyber-surface/90 border border-cyber-border text-[11px] text-cyber-muted">
            <span className="text-slate-300 font-semibold block mb-0.5">Probabilistic Notice:</span>
            Forensic classifications are probabilistic indicators derived from convolutional neural network inference.
          </div>
        </div>
      </div>

      {/* Recent Analyses Table */}
      <div className="bg-cyber-card/70 border border-cyber-border rounded-xl overflow-hidden">
        <div className="p-5 border-b border-cyber-border flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold text-white">Recent Analyses</h3>
            <p className="text-xs text-cyber-muted">Latest forensic scans submitted to the queue</p>
          </div>
          <Link
            to="/history"
            className="text-xs text-cyber-accent hover:underline flex items-center space-x-1"
          >
            <span>View All Records</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {analyses.length === 0 ? (
          <div className="p-12 text-center text-cyber-muted">
            <Layers className="w-10 h-10 mx-auto text-slate-600 mb-3" />
            <p className="text-sm">No analysis records logged yet.</p>
            <Link
              to="/new"
              className="inline-block mt-3 text-xs text-cyber-accent hover:underline font-medium"
            >
              Upload media to start first scan &rarr;
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-cyber-surface text-cyber-muted uppercase font-mono tracking-wider border-b border-cyber-border">
                <tr>
                  <th className="px-5 py-3">File / Subject</th>
                  <th className="px-5 py-3">Type</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Verdict</th>
                  <th className="px-5 py-3">Risk</th>
                  <th className="px-5 py-3">Confidence</th>
                  <th className="px-5 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cyber-border/40">
                {analyses.map((item) => (
                  <tr key={item.id} className="hover:bg-cyber-surface/40 transition-colors">
                    <td className="px-5 py-4 font-medium text-white max-w-xs truncate">
                      {item.original_filename}
                    </td>
                    <td className="px-5 py-4">
                      <span className="inline-flex items-center space-x-1 uppercase font-mono text-[10px] text-cyber-muted bg-cyber-surface px-2 py-0.5 rounded border border-cyber-border">
                        {item.media_type === 'image' && <ImageIcon className="w-3 h-3 text-sky-400" />}
                        {item.media_type === 'video' && <Film className="w-3 h-3 text-purple-400" />}
                        {item.media_type === 'audio' && <Mic className="w-3 h-3 text-emerald-400" />}
                        <span>{item.media_type}</span>
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge status={item.status} />
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge verdict={item.overall_prediction} />
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge risk={item.risk_level} />
                    </td>
                    <td className="px-5 py-4 font-mono">
                      {item.overall_confidence > 0
                        ? `${Math.round(item.overall_confidence * 100)}%`
                        : '—'}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <Link
                        to={`/analyses/${item.id}`}
                        className="text-cyber-accent hover:text-white font-medium text-xs transition-colors"
                      >
                        Inspect &rarr;
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
