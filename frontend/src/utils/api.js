import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: API_BASE });

export const uploadAndAnalyze = async (formData) => {
  const res = await api.post('/logs/upload-and-analyze', formData);
  return res.data;
};

export const getAnalysis = async (id) => {
  const res = await api.get(`/analyses/${id}`);
  return res.data;
};

export const getHistory = async (skip = 0, limit = 20) => {
  const res = await api.get(`/logs/history?skip=${skip}&limit=${limit}`);
  return res.data;
};

export const submitFeedback = async (analysisId, isCorrect, comment = '') => {
  const res = await api.post('/feedback/', {
    analysis_id: analysisId,
    is_correct: isCorrect,
    comment,
  });
  return res.data;
};

export const getMetrics = async () => {
  const res = await api.get('/metrics/');
  return res.data;
};

export default api;
