import axios from 'axios';

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request and response logging
API.interceptors.request.use((request) => {
  console.log('Request:', request);
  return request;
});

API.interceptors.response.use(
  (response) => {
    console.log('Response:', response);
    return response.data; // Return plain string directly
  },
  (error) => {
    console.error('Error Response:', error.response || error.message);
    return Promise.reject(error);
  }
);

export const searchPapers = (query) => API.post('/search', { query });
export const getSummary = (paperId) => API.get(`/summarize/${paperId}`);
export const getAudio = (summaryId) => API.get(`/audio/${summaryId}`);
export const getHealth = () => API.get('/health');