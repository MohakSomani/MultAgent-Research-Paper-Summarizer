import axios from 'axios';

// Fix the API base URL to consistently use port 8000
const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request and response logging - but only essential information
API.interceptors.request.use((request) => {
  console.log(`API Request: ${request.method} ${request.url}`);
  if (request.data) {
    console.log('Request Data:', request.data);
  }
  return request;
});

API.interceptors.response.use(
  (response) => {
    console.log(`API Response from ${response.config.url}:`, 
      typeof response.data === 'string' 
        ? `${response.data.substring(0, 100)}${response.data.length > 100 ? '...' : ''}` 
        : response.data);
    return response.data;
  },
  (error) => {
    console.error('API Error:', error.response?.status || error.message);
    return Promise.reject(error);
  }
);

export const searchPapers = (query) => API.post('/search', { query });
export const getSummary = (paperId) => API.get(`/summarize/${paperId}`);
export const getAudio = (summaryId) => API.get(`/audio/${summaryId}`);
export const getHealth = () => API.get('/health');