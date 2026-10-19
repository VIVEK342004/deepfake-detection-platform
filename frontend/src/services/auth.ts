
const API_BASE =
  import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000/api/v1';

const TOKEN_KEY = 'deepfake_access_token';

export interface AuthResponse {
  access_token: string;
  token_type: 'bearer' | string;
}

export interface RegisterData {
  email: string;
  password: string;
}

function getErrorMessage(data: unknown, fallback: string): string {
  if (
    typeof data === 'object' &&
    data !== null &&
    'detail' in data
  ) {
    const detail = (data as { detail?: unknown }).detail;

    if (typeof detail === 'string') return detail;

    if (Array.isArray(detail)) {
      return detail
        .map((item) =>
          typeof item === 'object' && item !== null && 'msg' in item
            ? String((item as { msg: unknown }).msg)
            : String(item)
        )
        .join(', ');
    }
  }

  return fallback;
}

export async function registerUser(data: RegisterData): Promise<void> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData: unknown = await response.json().catch(() => null);
    throw new Error(
      getErrorMessage(errorData, `Registration failed (${response.status})`)
    );
  }
}

export async function loginUser(
  data: RegisterData
): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData: unknown = await response.json().catch(() => null);
    throw new Error(
      getErrorMessage(errorData, `Login failed (${response.status})`)
    );
  }

  const result = (await response.json()) as AuthResponse;

  if (
    typeof result.access_token !== 'string' ||
    !result.access_token ||
    result.token_type.toLowerCase() !== 'bearer'
  ) {
    throw new Error('The server returned an invalid authentication response.');
  }

  sessionStorage.setItem(TOKEN_KEY, result.access_token);
  return result;
}

export function getAccessToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function logoutUser(): void {
  sessionStorage.removeItem(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  return getAccessToken() !== null;
}
