export type MediaType = 'image' | 'video' | 'audio';

export type AnalysisStatus =
  | 'queued'
  | 'processing'
  | 'completed'
  | 'failed'
  | 'model_unavailable';

export type PredictionVerdict =
  | 'likely_synthetic'
  | 'likely_authentic'
  | 'inconclusive'
  | 'unprocessed';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical' | 'unknown';

export interface FrameAnalysisResult {
  frame_index: number;
  timestamp_seconds: number;
  face_detected: boolean;
  face_box?: [number, number, number, number] | null;
  confidence_fake: number;
  confidence_real: number;
  is_anomaly: boolean;
}

export interface ModalityResult {
  id: string;
  analysis_id: string;
  modality: 'visual' | 'audio' | 'multimodal_sync';
  model_name: string;
  model_version: string;
  status: string;
  is_synthetic?: boolean | null;
  confidence_score: number;
  raw_scores: Record<string, any>;
  artifacts: Record<string, any>;
  execution_time_seconds: number;
  limitations_notes?: string;
  created_at: string;
}

export interface AnalysisSummary {
  id: string;
  media_type: MediaType;
  original_filename: string;
  file_size_bytes: number;
  mime_type: string;
  status: AnalysisStatus;
  overall_prediction: PredictionVerdict;
  overall_confidence: number;
  risk_level: RiskLevel;
  created_at: string;
  completed_at?: string | null;
}

export interface AnalysisDetail extends AnalysisSummary {
  file_sha256: string;
  summary_findings: Record<string, any>;
  media_metadata: Record<string, any>;
  error_message?: string | null;
  retention_expires_at?: string | null;
  modality_results: ModalityResult[];
}

export interface AnalysisListResponse {
  total: number;
  page: number;
  page_size: number;
  items: AnalysisSummary[];
}

export interface ModelStatusItem {
  name: string;
  modality: string;
  architecture: string;
  status: 'model_ready' | 'model_loading' | 'model_unavailable' | 'inference_failed';
  is_ready: boolean;
  device: string;
  checkpoint_found: boolean;
  checkpoint_path?: string | null;
  parameters_count?: number | null;
  description: string;
  limitations: string[];
}

export interface SystemStatusResponse {
  status: string;
  timestamp: string;
  device: string;
  gpu_available: boolean;
  gpu_name?: string | null;
  models: ModelStatusItem[];
  limits: {
    max_upload_size_mb: number;
    max_video_duration_seconds: number;
    max_audio_duration_seconds: number;
    max_sampled_frames: number;
  };
}

export interface HealthResponse {
  status: string;
  app_name: string;
  environment: string;
  version: string;
  database_connected: boolean;
  storage_accessible: boolean;
}
