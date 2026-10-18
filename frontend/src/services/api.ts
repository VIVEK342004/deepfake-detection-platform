import type {
  AnalysisDetail,
  AnalysisListResponse,
  HealthResponse,
  SystemStatusResponse
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000/api/v1';

export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed (${res.status})`);
  return res.json();
}

export async function getSystemStatus(): Promise<SystemStatusResponse> {
  const res = await fetch(`${API_BASE}/health/models`);
  if (!res.ok) throw new Error(`Model health check failed (${res.status})`);
  return res.json();
}

export async function uploadMedia(
  file: File,
  onProgress?: (percent: number) => void
): Promise<{ id: string; status: string; message: string }> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append('file', file);

    xhr.open('POST', `${API_BASE}/analyses`);

    if (xhr.upload && onProgress) {
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percent = Math.round((event.loaded / event.total) * 100);
          onProgress(percent);
        }
      };
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText));
        } catch (e) {
          reject(new Error('Invalid JSON response from server.'));
        }
      } else {
        try {
          const errData = JSON.parse(xhr.responseText);
          reject(new Error(errData.detail || `Upload failed with HTTP ${xhr.status}`));
        } catch {
          reject(new Error(`Upload failed with HTTP ${xhr.status}`));
        }
      }
    };

    xhr.onerror = () => {
      reject(new Error('Network error during upload. Ensure the backend server is reachable.'));
    };

    xhr.send(formData);
  });
}

export async function getAnalyses(params?: {
  page?: number;
  pageSize?: number;
  mediaType?: string;
  status?: string;
  riskLevel?: string;
  search?: string;
}): Promise<AnalysisListResponse> {
  const query = new URLSearchParams();
  if (params?.page) query.append('page', params.page.toString());
  if (params?.pageSize) query.append('page_size', params.pageSize.toString());
  if (params?.mediaType) query.append('media_type', params.mediaType);
  if (params?.status) query.append('status', params.status);
  if (params?.riskLevel) query.append('risk_level', params.riskLevel);
  if (params?.search) query.append('search', params.search);

  const res = await fetch(`${API_BASE}/analyses?${query.toString()}`);
  if (!res.ok) throw new Error(`Failed to fetch analyses (${res.status})`);
  return res.json();
}

export async function getAnalysisDetail(id: string): Promise<AnalysisDetail> {
  const res = await fetch(`${API_BASE}/analyses/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch analysis details (${res.status})`);
  return res.json();
}

export async function getAnalysisReport(id: string): Promise<any> {
  const res = await fetch(`${API_BASE}/analyses/${id}/report`);
  if (!res.ok) throw new Error(`Failed to fetch report (${res.status})`);
  return res.json();
}

export function getMediaUrl(id: string): string {
  return `${API_BASE}/analyses/${id}/media`;
}
