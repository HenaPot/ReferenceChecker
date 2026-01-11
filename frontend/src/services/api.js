// File: frontend/src/services/api.js

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data),
  getProfile: () => api.get('/api/auth/me'),
};

// Reference endpoints
export const referenceAPI = {
  checkReference: (url) => api.post('/api/references/check', { url }),
  getHistory: (skip = 0, limit = 20) => 
    api.get(`/api/references/history?skip=${skip}&limit=${limit}`),
  getReference: (id) => api.get(`/api/references/${id}`),
  reanalyze: (id) => api.post(`/api/references/${id}/reanalyze`),
  deleteReference: (id) => api.delete(`/api/references/${id}`),
};

// Rating endpoints (if you implement them)
export const ratingAPI = {
  rateReference: (referenceId, rating, comment) => 
    api.post(`/api/ratings/${referenceId}`, { rating, comment }),
  getRatings: (referenceId) => api.get(`/api/ratings/${referenceId}`),
};

export default api;