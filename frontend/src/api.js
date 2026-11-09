import axios from 'axios';

export const API_URL = (process.env.REACT_APP_API_URL || 'http://localhost:8000').replace(/\/$/, '');
export const WS_URL = API_URL.replace(/^http/, 'ws');

const api = axios.create({ baseURL: `${API_URL}/api`, withCredentials: true });

function readCookie(name) {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

// Django checks a CSRF token on every request that changes something.
api.interceptors.request.use((config) => {
  if (!['get', 'head', 'options'].includes((config.method || 'get').toLowerCase())) {
    const token = readCookie('csrftoken');
    if (token) config.headers['X-CSRFToken'] = token;
  }
  return config;
});

/** Turns an error from the API into one readable sentence. */
export function errorMessage(error, fallback = 'Something went wrong. Please try again.') {
  const data = error?.response?.data;
  if (!data) return error?.response ? fallback : 'Cannot reach the server. Is it running?';
  if (typeof data.detail === 'string') return data.detail;
  const first = Object.values(data).flat()[0];
  return typeof first === 'string' ? first : fallback;
}

export const auth = {
  csrf: () => api.get('/auth/csrf/'),
  me: () => api.get('/auth/me/').then((r) => r.data),
  login: (username, password) => api.post('/auth/login/', { username, password }).then((r) => r.data),
  register: (form) => api.post('/auth/register/', form).then((r) => r.data),
  logout: () => api.post('/auth/logout/'),
};

export const chat = {
  contacts: () => api.get('/users/').then((r) => r.data),
  socketUrl: (username) => `${WS_URL}/ws/chat/${encodeURIComponent(username)}/`,
};

export const moderation = {
  check: (text) => api.post('/moderation/check/', { text }).then((r) => r.data),
  status: () => api.get('/moderation/status/').then((r) => r.data),
};

export const feedback = {
  send: (text) => api.post('/feedback/', { feedback: text }).then((r) => r.data),
};

/** Profile photos come back as paths on the API server. */
export function mediaUrl(path) {
  if (!path) return null;
  return path.startsWith('http') ? path : `${API_URL}${path}`;
}
