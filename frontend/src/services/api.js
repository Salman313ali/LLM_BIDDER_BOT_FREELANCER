import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Bot Management API
export const botAPI = {
  start: (bidLimit) => api.post('/bot/start', { bid_limit: bidLimit }),
  stop: () => api.post('/bot/stop'),
  getStatus: () => api.get('/bot/status'),
  getStatistics: () => api.get('/bot/statistics'),
};

// Projects API
export const projectsAPI = {
  getAll: (limit = 100) => api.get(`/projects?limit=${limit}`),
  getById: (projectId) => api.get(`/projects/${projectId}`),
};

// Bids API
export const bidsAPI = {
  getAll: (limit = 50) => api.get(`/bids?limit=${limit}`),
  getById: (bidId) => api.get(`/bids/${bidId}`),
};

// Configuration API
export const configAPI = {
  get: () => api.get('/config'),
  update: (config) => api.put('/config', config),
};

// Logs API
export const logsAPI = {
  getAll: (sessionId, limit = 100) => api.get(`/logs?session_id=${sessionId}&limit=${limit}`),
};

// Analytics API
export const analyticsAPI = {
  getOverview: () => api.get('/analytics/overview'),
  getPerformance: () => api.get('/analytics/performance'),
};

// Health check
export const healthAPI = {
  check: () => api.get('/health'),
};

export default api;


