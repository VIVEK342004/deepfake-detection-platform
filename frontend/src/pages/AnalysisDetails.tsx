
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ShieldAlert,
  ShieldCheck,
  Clock,
  Download,
  AlertTriangle,
  RefreshCw,
  Eye,
  Mic,
  Film,
  FileText,
  Hash,
  Activity,
  Layers,
  ChevronLeft
} from 'lucide-react';
import {
  getAnalysisDetail,
  fetchMediaBlob,
  getAnalysisReport
} from '../services/api';
import type { AnalysisDetail } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { ConfidenceMeter } from '../components/ConfidenceMeter';
import { ForensicWaveformChart } from '../components/ForensicWaveformChart';

export const AnalysisDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const [analysis, setAnalysis] = useState<AnalysisDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [downloadingReport, setDownloadingReport] = useState<boolean>(false);
  const [mediaUrl, setMediaUrl] = useState<string | null>(null);
  const [mediaError, setMediaError] = useState<string | null>(null);

  const fetchDetail = async (silent = false) => {
    if (!id) return;
    if (!silent) setLoading(true);

    try {
      const data = await getAnalysisDetail(id);
      setAnalysis(data);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to retrieve analysis.');
    } finally {
      if (!silent) setLoading(false);
    }
  };

  useEffect(() => {
    void fetchDetail();
  }, [id]);

  // Load media through the authenticated API and clean up the object URL.
  useEffect(() => {
    if (!id) return;

    let active = true;
    let objectUrl: string | null = null;

    setMediaUrl(null);
    setMediaError(null);

    fetchMediaBlob(id)
      .then((blob) => {
        if (!active) return;

        objectUrl = URL.createObjectURL(blob);
        setMediaUrl(objectUrl);
      })
      .catch((err: unknown) => {
        if (!active) return;

        setMediaError(
          err instanceof Error ? err.message : 'Unable to load media preview.'
        );
      });

    return () => {
      active = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [id]);

  // Poll while an analysis is queued or processing.
  useEffect(() => {
    if (!analysis) return;

    if (analysis.status === 'queued' || analysis.status === 'processing') {
      const timer = setInterval(() => {
        void fetchDetail(true);
      }, 2000);

      return () => clearInterval(timer);
    }
  }, [analysis?.status, id]);

  const handleDownloadReport = async () => {
    if (!id) return;

    setDownloadingReport(true);

    try {
      const report = await getAnalysisReport(id);
      const dataStr =
        'data:application/json;charset=utf-8,' +
        encodeURIComponent(JSON.stringify(report, null, 2));

      const downloadAnchor = document.createElement('a');
      downloadAnchor.href = dataStr;
      downloadAnchor.download = `forensic_report_${id.slice(0, 8)}.json`;

      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    } catch (err: unknown) {
      alert(
        `Report export failed: ${
          err instanceof Error ? err.message : 'Unknown error'
        }`
      );
    } finally {
      setDownloadingReport(false);
    }
  };

  if (loading) {
    return (
      <div className="py-20 text-center space-y-4">
        <RefreshCw className="w-8 h-8 text-cyber-accent animate-spin mx-auto" />
        <p className="text-sm text-cyber-muted font-mono">
          Loading forensic casefile...
        </p>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="max-w-2xl mx-auto py-12 text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-red-400 mx-auto" />
        <h2 className="text-xl font-bold text-white">Record Retrieval Failed</h2>
        <p className="text-sm text-cyber-muted">
          {error || 'The requested analysis does not exist.'}
        </p>
        <Link
          to="/history"
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-cyber-card border border-cyber-border text-sm text-white hover:border-cyber-accent"
        >
          <ChevronLeft className="w-4 h-4" />
          <span>Back to Analysis History</span>
        </Link>
      </div>
    );
  }

  const visualResult = analysis.modality_results.find(
    (m) => m.modality === 'visual'
  );
  const audioResult = analysis.modality_results.find(
    (m) => m.modality === 'audio'
  );
  const syncResult = analysis.modality_results.find(
    (m) => m.modality === 'multimodal_sync'
  );

  const audioChunks = audioResult?.artifacts?.chunk_results || [];
  const audioChartData = audioChunks.map((chunk: any) => ({
    label: `${chunk.start_seconds}s`,
    syntheticProbability: chunk.confidence_fake,
    threshold: 0.5
  }));

  const videoFrames = visualResult?.artifacts?.frame_results || [];
  const videoChartData = videoFrames.map((frame: any) => ({
    label: `Frame ${frame.frame_index}`,
    syntheticProbability: frame.confidence_fake,
    threshold: 0.5
  }));

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-cyber-border pb-5">
        <div className="flex items-center space-x-3">
          <Link
            to="/history"
            className="p-2 rounded-lg bg-cyber-card border border-cyber-border text-cyber-muted hover:text-white"
          >
            <ChevronLeft className="w-5 h-5" />
          </Link>

          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight truncate max-w-sm sm:max-w-xl">
                {analysis.original_filename}
              </h1>
              <StatusBadge status={analysis.status} />
            </div>
            <p className="text-xs text-cyber-muted font-mono mt-1">
              CASE ID: {analysis.id} &bull; Uploaded{' '}
              {new Date(analysis.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => void fetchDetail(false)}
            className="p-2.5 rounded-lg bg-cyber-card border border-cyber-border text-slate-300 hover:text-white"
            title="Refresh record"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <button
            onClick={handleDownloadReport}
            disabled={downloadingReport}
            className="flex items-center space-x-2 px-4 py-2.5 rounded-lg bg-cyber-card border border-cyber-border text-sm font-medium text-slate-200 hover:text-white hover:border-cyber-accent/60 transition-all disabled:opacity-60"
          >
            <Download className="w-4 h-4 text-cyber-accent" />
            <span>
              {downloadingReport ? 'Exporting...' : 'Export Forensic Report'}
            </span>
          </button>
        </div>
      </div>

      {(analysis.status === 'queued' || analysis.status === 'processing') && (
        <div className="p-5 rounded-2xl bg-blue-950/30 border border-blue-800 text-blue-200 flex items-center space-x-4 animate-pulse">
          <RefreshCw className="w-6 h-6 animate-spin text-blue-400 shrink-0" />
          <div>
            <h4 className="font-semibold text-sm">
              Deepfake Inference In Progress
            </h4>
            <p className="text-xs text-blue-300/80 mt-0.5">
              The media is currently undergoing neural tensor evaluation.
              Status updates automatically.
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-cyber-card border border-cyber-border rounded-2xl overflow-hidden p-5">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300 mb-4 flex items-center justify-between">
              <span>Primary Media Stream</span>
              <span className="text-xs font-mono text-cyber-accent uppercase">
                {analysis.media_type}
              </span>
            </h3>

            <div className="rounded-xl overflow-hidden bg-cyber-surface/80 border border-cyber-border flex items-center justify-center p-4 min-h-[260px]">
              {!mediaUrl && (
                <p className="text-sm text-cyber-muted text-center">
                  {mediaError || 'Loading authenticated media preview...'}
                </p>
              )}

              {mediaUrl && analysis.media_type === 'image' && (
                <img
                  src={mediaUrl}
                  alt="Inspected media"
                  className="max-h-96 max-w-full rounded-lg object-contain shadow-lg"
                />
              )}

              {mediaUrl && analysis.media_type === 'video' && (
                <video
                  src={mediaUrl}
                  controls
                  className="max-h-96 max-w-full rounded-lg shadow-lg"
                />
              )}

              {mediaUrl && analysis.media_type === 'audio' && (
                <div className="w-full max-w-md p-6 text-center space-y-4">
                  <Mic className="w-12 h-12 mx-auto text-emerald-400" />
                  <audio
                    src={mediaUrl}
                    controls
                    className="w-full"
                  />
                </div>
              )}
            </div>

            <div className="mt-4 pt-4 border-t border-cyber-border grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div>
                <span className="text-cyber-muted block">File Size</span>
                <span className="font-mono text-white">
                  {(analysis.file_size_bytes / (1024 * 1024)).toFixed(2)} MB
                </span>
              </div>
              <div>
                <span className="text-cyber-muted block">MIME Type</span>
                <span className="font-mono text-white truncate block">
                  {analysis.mime_type}
                </span>
              </div>
              <div>
                <span className="text-cyber-muted block">Dimensions / Rate</span>
                <span className="font-mono text-white">
                  {analysis.media_metadata?.width
                    ? `${analysis.media_metadata.width}x${analysis.media_metadata.height}`
                    : analysis.media_metadata?.sample_rate
                    ? `${analysis.media_metadata.sample_rate} Hz`
                    : 'N/A'}
                </span>
              </div>
              <div>
                <span className="text-cyber-muted block">Duration / Frames</span>
                <span className="font-mono text-white">
                  {analysis.media_metadata?.duration_seconds
                    ? `${analysis.media_metadata.duration_seconds}s`
                    : 'Static Frame'}
                </span>
              </div>
            </div>
          </div>

          {analysis.media_type === 'video' && videoChartData.length > 0 && (
            <ForensicWaveformChart
              data={videoChartData}
              title="Frame-by-Frame Synthetic Anomaly Trajectory"
              xLabel="Sampled Video Frames"
            />
          )}

          {analysis.media_type === 'audio' && audioChartData.length > 0 && (
            <ForensicWaveformChart
              data={audioChartData}
              title="Acoustic Chunk Synthetic Probability"
              xLabel="Temporal Audio Windows (s)"
            />
          )}

          <div className="space-y-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
              Modality Forensics Breakdown
            </h3>

            {visualResult && (
              <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-cyber-border/60 pb-3">
                  <div className="flex items-center space-x-2">
                    <Eye className="w-5 h-5 text-sky-400" />
                    <div>
                      <h4 className="font-semibold text-white text-sm">
                        Visual Artifact Detection
                      </h4>
                      <p className="text-[11px] text-cyber-muted font-mono">
                        Model: {visualResult.model_name} (v{visualResult.model_version})
                      </p>
                    </div>
                  </div>
                  <StatusBadge status={visualResult.status as any} />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <ConfidenceMeter
                    confidence={visualResult.confidence_score}
                    isSynthetic={visualResult.is_synthetic}
                    label="Visual Confidence Score"
                  />
                  <div className="space-y-1.5 text-xs">
                    <div className="flex justify-between">
                      <span className="text-cyber-muted">Prob Synthetic:</span>
                      <span className="font-mono text-red-400">
                        {visualResult.raw_scores?.prob_synthetic !== undefined
                          ? `${(visualResult.raw_scores.prob_synthetic * 100).toFixed(1)}%`
                          : '—'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-cyber-muted">Prob Authentic:</span>
                      <span className="font-mono text-emerald-400">
                        {visualResult.raw_scores?.prob_real !== undefined
                          ? `${(visualResult.raw_scores.prob_real * 100).toFixed(1)}%`
                          : '—'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-cyber-muted">Face Detected:</span>
                      <span className="font-mono text-white">
                        {visualResult.artifacts?.face_detected
                          ? 'Yes (Isolated Crop)'
                          : 'No (Whole Frame)'}
                      </span>
                    </div>
                  </div>
                </div>

                {visualResult.limitations_notes && (
                  <p className="text-xs text-cyber-muted italic bg-cyber-surface/60 p-2.5 rounded-lg border border-cyber-border">
                    {visualResult.limitations_notes}
                  </p>
                )}
              </div>
            )}

            {audioResult && (
              <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-cyber-border/60 pb-3">
                  <div className="flex items-center space-x-2">
                    <Mic className="w-5 h-5 text-emerald-400" />
                    <div>
                      <h4 className="font-semibold text-white text-sm">
                        Synthetic Speech & Anti-Spoofing
                      </h4>
                      <p className="text-[11px] text-cyber-muted font-mono">
                        Model: {audioResult.model_name} (v{audioResult.model_version})
                      </p>
                    </div>
                  </div>
                  <StatusBadge status={audioResult.status as any} />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <ConfidenceMeter
                    confidence={audioResult.confidence_score}
                    isSynthetic={audioResult.is_synthetic}
                    label="Acoustic Confidence Score"
                  />
                  <div className="space-y-1.5 text-xs">
                    <div className="flex justify-between">
                      <span className="text-cyber-muted">Spectral Flatness:</span>
                      <span className="font-mono text-white">
                        {audioResult.artifacts?.acoustic_features?.spectral_flatness_mean ?? 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-cyber-muted">Spectral Centroid:</span>
                      <span className="font-mono text-white">
                        {audioResult.artifacts?.acoustic_features?.spectral_centroid_hz
                          ? `${audioResult.artifacts.acoustic_features.spectral_centroid_hz} Hz`
                          : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-cyber-muted">Analyzed Chunks:</span>
                      <span className="font-mono text-white">
                        {audioResult.artifacts?.chunks_analyzed ?? '1'}
                      </span>
                    </div>
                  </div>
                </div>

                {audioResult.limitations_notes && (
                  <p className="text-xs text-cyber-muted italic bg-cyber-surface/60 p-2.5 rounded-lg border border-cyber-border">
                    {audioResult.limitations_notes}
                  </p>
                )}
              </div>
            )}

            {syncResult && (
              <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-cyber-border/60 pb-3">
                  <div className="flex items-center space-x-2">
                    <Activity className="w-5 h-5 text-purple-400" />
                    <div>
                      <h4 className="font-semibold text-white text-sm">
                        Lip-Sync & Temporal Kinematics
                      </h4>
                      <p className="text-[11px] text-cyber-muted font-mono">
                        Cross-Correlation: Mouth Motion vs Acoustic RMS
                      </p>
                    </div>
                  </div>
                  <StatusBadge status={syncResult.status as any} />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="text-cyber-muted block mb-1">Pearson Correlation:</span>
                    <span className="font-mono text-lg text-white font-bold">
                      {syncResult.raw_scores?.pearson_correlation ?? 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-cyber-muted block mb-1">Synchronization Assessment:</span>
                    <span className="font-semibold text-white">
                      {syncResult.is_synthetic
                        ? 'Desynchronized Speech Detected'
                        : 'Kinematically Synchronous'}
                    </span>
                  </div>
                </div>

                {syncResult.limitations_notes && (
                  <p className="text-xs text-cyber-muted italic bg-cyber-surface/60 p-2.5 rounded-lg border border-cyber-border">
                    {syncResult.limitations_notes}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-cyber-card border border-cyber-border rounded-2xl p-6 space-y-5">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300 border-b border-cyber-border/60 pb-3">
              Synthesized Forensic Verdict
            </h3>

            <div>
              <StatusBadge verdict={analysis.overall_prediction} />
              <div className="mt-3">
                <StatusBadge risk={analysis.risk_level} />
              </div>
            </div>

            <div className="pt-2">
              <ConfidenceMeter
                confidence={analysis.overall_confidence}
                isSynthetic={analysis.overall_prediction === 'likely_synthetic'}
                label="Forensic Confidence Assessment"
              />
            </div>

            {analysis.summary_findings?.findings && (
              <div className="space-y-2 pt-2">
                <span className="text-xs font-medium text-slate-300 block">
                  Identified Indicators:
                </span>
                <ul className="space-y-1.5 text-xs text-cyber-muted">
                  {analysis.summary_findings.findings.map((finding: string, index: number) => (
                    <li key={index} className="flex items-start space-x-2">
                      <span className="text-cyber-accent mt-0.5">&bull;</span>
                      <span>{finding}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="pt-4 border-t border-cyber-border space-y-2.5 text-xs">
              <span className="text-slate-300 font-semibold uppercase tracking-wider block text-[10px]">
                Cryptographic Integrity
              </span>
              <div>
                <span className="text-cyber-muted block">SHA-256 Hash:</span>
                <span className="font-mono text-[11px] text-cyber-accent break-all">
                  {analysis.file_sha256}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-cyber-muted">Inference Latency:</span>
                <span className="font-mono text-white">
                  {analysis.completed_at && analysis.created_at
                    ? `${(
                        (new Date(analysis.completed_at).getTime() -
                          new Date(analysis.created_at).getTime()) /
                        1000
                      ).toFixed(2)}s total`
                    : 'Pending'}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-cyber-surface/60 border border-cyber-border rounded-2xl p-5 space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-amber-400 flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span>Forensic Disclaimers</span>
            </h4>
            <p className="text-xs text-cyber-muted leading-relaxed">
              Predictions produced by this system represent probabilistic
              indicators of generative manipulation. They must not be interpreted
              as absolute legal proof of authenticity. Human forensic review
              alongside verifiable cryptographic provenance (e.g. C2PA) is
              recommended for critical decisions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisDetails;
