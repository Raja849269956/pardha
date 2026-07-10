let API_URL = 'http://localhost:8000';

export async function initApiUrl() {
  if (window.electronAPI) {
    const env = await window.electronAPI.getEnv();
    API_URL = env.API_URL || API_URL;
  }
}

export function getApiUrl() {
  return API_URL;
}

export function getWsUrl() {
  if (window.electronAPI) {
    return window.electronAPI.getEnv().then((env) => env.WS_URL || 'ws://localhost:8000');
  }
  return Promise.resolve('ws://localhost:8000');
}

function getToken() {
  return localStorage.getItem('token');
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(method, path, body = null, extraHeaders = {}) {
  const options = {
    method,
    headers: {
      ...authHeaders(),
      ...extraHeaders,
    },
  };
  if (body !== null) {
    if (body instanceof URLSearchParams) {
      options.body = body;
    } else {
      options.headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(body);
    }
  }
  const response = await fetch(`${API_URL}${path}`, options);
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(data?.detail || `${response.status} error`);
    error.response = { data, status: response.status };
    throw error;
  }
  return data;
}

export async function login(email, password) {
  const params = new URLSearchParams();
  params.append('username', email);
  params.append('password', password);
  const data = await request('POST', '/api/v1/auth/login', params, {
    'Content-Type': 'application/x-www-form-urlencoded',
  });
  localStorage.setItem('token', data.access_token);
  return data;
}

export async function register(email, password) {
  return request('POST', '/api/v1/auth/register', { email, password });
}

export async function getMe() {
  return request('GET', '/api/v1/auth/me');
}

export async function getProfiles() {
  return request('GET', '/api/v1/profiles/');
}

export async function createProfile(profile) {
  return request('POST', '/api/v1/profiles/', profile);
}

export async function updateProfile(id, profile) {
  return request('PUT', `/api/v1/profiles/${id}`, profile);
}

export async function deleteProfile(id) {
  return request('DELETE', `/api/v1/profiles/${id}`);
}

export async function extractResume(id) {
  return request('POST', `/api/v1/profiles/${id}/extract-resume`);
}

export async function createSession(profileId, name) {
  return request('POST', '/api/v1/sessions/', { profile_id: profileId, name });
}

export async function endSession(sessionId) {
  return request('POST', `/api/v1/sessions/${sessionId}/end`);
}
