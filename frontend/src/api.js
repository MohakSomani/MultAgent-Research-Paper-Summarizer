import axios from 'axios';

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchPapers = (query) => API.post('/search', { query });
export const getSummary = (paperId) => API.get(`/summarize/${paperId}`);
export const getAudio = (summaryId) => API.get(`/audio/${summaryId}`);