import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Complaints API
export const complaintsAPI = {
  getAll: (params) => api.get('/api/complaints/', { params }),
  getById: (id) => api.get(`/api/complaints/${id}`),
  create: (data) => api.post('/api/complaints/', data),
  update: (id, data) => api.patch(`/api/complaints/${id}`, data),
  getMessages: (id) => api.get(`/api/complaints/${id}/messages`),
  addMessage: (id, data) => api.post(`/api/complaints/${id}/messages`, data),
  escalate: (id) => api.post(`/api/complaints/${id}/escalate`),
}

// AI API
export const aiAPI = {
  classify: (text) => api.post('/api/ai/classify', { text }),
  sentiment: (text) => api.post('/api/ai/sentiment', { text }),
  summarize: (data) => api.post('/api/ai/summarize', data),
  generateDraft: (data) => api.post('/api/ai/draft', data),
  findSimilar: (text) => api.post('/api/ai/find-similar', { text }),
}

// Analytics API
export const analyticsAPI = {
  getSummary: () => api.get('/api/analytics/summary'),
  getTrends: (days = 30) => api.get('/api/analytics/trends', { params: { days } }),
  getSLA: () => api.get('/api/analytics/sla'),
  getRootCause: () => api.get('/api/analytics/root-cause'),
}

// Voice API
export const voiceAPI = {
  transcribe: (formData) => api.post('/api/voice/transcribe', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
}

export default api
