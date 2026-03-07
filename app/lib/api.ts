const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

// --- Token management ---

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('kilter_token');
}

export function setToken(token: string) {
  localStorage.setItem('kilter_token', token);
}

export function clearToken() {
  localStorage.removeItem('kilter_token');
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

// --- Error class ---

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

// --- Fetch wrapper ---

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Don't set Content-Type for FormData — browser sets it with boundary
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearToken();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    throw new ApiError(401, 'Sessione scaduta. Effettua di nuovo il login.');
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({ detail: 'Errore sconosciuto' }));
    throw new ApiError(response.status, data.detail || 'Errore del server');
  }

  return response.json();
}

// --- Types ---

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  full_name: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Video {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  original_file_path: string;
  fragment_file_path: string | null;
  form_feedback: string | null;
  grade_estimate: string | null;
  body_position: Record<string, unknown> | null;
  holds_analysis: unknown[] | null;
  key_weaknesses: string[] | null;
  notes: string | null;
  duration: number | null;
  file_size: number | null;
  created_at: string;
}

// --- Auth API ---

export async function login(data: LoginRequest): Promise<AuthResponse> {
  const res = await apiFetch<AuthResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  setToken(res.access_token);
  return res;
}

export async function register(data: RegisterRequest): Promise<User> {
  return apiFetch<User>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getMe(): Promise<User> {
  return apiFetch<User>('/api/auth/me');
}

// --- Video API ---

export async function uploadVideo(file: File, notes?: string): Promise<Video> {
  const formData = new FormData();
  formData.append('video', file);
  if (notes) formData.append('notes', notes);

  return apiFetch<Video>('/api/videos/upload', {
    method: 'POST',
    body: formData,
  });
}

export async function analyzeVideo(videoId: string): Promise<Video> {
  return apiFetch<Video>(`/api/videos/${videoId}/analyze`, {
    method: 'POST',
  });
}

export async function getVideo(videoId: string): Promise<Video> {
  return apiFetch<Video>(`/api/videos/${videoId}`);
}

export async function getVideos(page = 1, perPage = 20): Promise<Video[]> {
  return apiFetch<Video[]>(`/api/videos?page=${page}&per_page=${perPage}`);
}
