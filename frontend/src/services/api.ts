
import type {
  AnalysisDetail,
  AnalysisListResponse,
  HealthResponse,
  SystemStatusResponse
} from '../types';
import { getAccessToken } from './auth';

const API_BASE =
  import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000/api/v1';

function authHeaders(): HeadersInit {
  const token = getAccessToken();

  if (!token) {
    throw new Error('Please log in to continue.');
  }

  return { Authorization: `Bearer ${token}` };
}

async function readError(res: Response, fallback: string): Promise<Error> {
  const data: unknown = await res.json().catch(() => null);

  if (typeof data === 'object' && data !== null && 'detail' in data) {
    const detail = (data as { detail?: unknown }).detail;
    if (typeof detail === 'string') return new Error(detail);
  }

  if (res.status === 401) {
    return new Error('Your session may have expired. Please log in again.');
  }

  return new Error(`${fallback} (HTTP ${res.status})`);
}

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
    let token: string | null;

    try {
      token = getAccessToken();
      if (!token) throw new Error('Please log in to upload media.');
    } catch (error) {
      reject(error);
      return;
    }

    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append('file', file);

    xhr.open('POST', `${API_BASE}/analyses`);
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);

    if (xhr.upload && onProgress) {
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          onProgress(Math.round((event.loaded / event.total) * 100));
        }
      };
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText));
        } catch {
          reject(new Error('Invalid JSON response from server.'));
        }
      } else {
        try {
          const errData = JSON.parse(xhr.responseText);
          reject(
            new Error(
              errData.detail ||
                (xhr.status === 401
                  ? 'Your session may have expired. Please log in again.'
                  : `Upload failed with HTTP ${xhr.status}`)
            )
          );
        } catch {
          reject(new Error(`Upload failed with HTTP ${xhr.status}`));
        }
      }
    };

    xhr.onerror = () => {
      reject(
        new Error('Network error during upload. Ensure the backend server is reachable.')
      );
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

  const res = await fetch(`${API_BASE}/analyses?${query.toString()}`, {
    headers: authHeaders(),
  });

  if (!res.ok) throw await readError(res, 'Failed to fetch analyses');
  return res.json();
}

export async function getAnalysisDetail(id: string): Promise<AnalysisDetail> {
  const res = await fetch(`${API_BASE}/analyses/${encodeURIComponent(id)}`, {
    headers: authHeaders(),
  });

  if (!res.ok) throw await readError(res, 'Failed to fetch analysis details');
  return res.json();
}

export async function getAnalysisReport(id: string): Promise<unknown> {
  const res = await fetch(
    `${API_BASE}/analyses/${encodeURIComponent(id)}/report`,
    { headers: authHeaders() }
  );

  if (!res.ok) throw await readError(res, 'Failed to fetch report');
  return res.json();
}

export async function fetchMediaBlob(id: string): Promise<Blob> {
  const res = await fetch(
    `${API_BASE}/analyses/${encodeURIComponent(id)}/media`,
    { headers: authHeaders() }
  );

  if (!res.ok) throw await readError(res, 'Failed to fetch media');
  return res.blob();
}
