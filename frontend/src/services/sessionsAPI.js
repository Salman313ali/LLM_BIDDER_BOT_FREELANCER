import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Session Management API
export const sessionsAPI = {
  // Create a new session
  create: (sessionData) => api.post('/sessions', sessionData),
  
  // Get all sessions
  getAll: () => api.get('/sessions'),
  
  // Get specific session
  getById: (sessionId) => api.get(`/sessions/${sessionId}`),
  
  // Update session
  update: (sessionId, sessionData) => api.put(`/sessions/${sessionId}`, sessionData),
  
  // Delete session
  delete: (sessionId) => api.delete(`/sessions/${sessionId}`),
  
  // Start bot for session
  startBot: (sessionId) => api.post(`/sessions/${sessionId}/start`),
  
  // Stop bot for session
  stopBot: (sessionId) => api.post(`/sessions/${sessionId}/stop`),
  
  // Get bot status for session
  getBotStatus: (sessionId) => api.get(`/sessions/${sessionId}/status`),
  
  // Get all bot statuses
  getAllBotStatuses: () => api.get('/sessions/status'),
  
  // Get session statistics
  getStatistics: (sessionId) => api.get(`/sessions/${sessionId}/statistics`),
};

export default sessionsAPI;




