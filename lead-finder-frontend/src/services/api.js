import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Health check
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Get configuration
export const getConfig = async () => {
  const response = await api.get('/config');
  return response.data;
};

// Start a new search
export const startSearch = async (searchData) => {
  const response = await api.post('/search', searchData);
  return response.data;
};

// Get search status
export const getSearchStatus = async (searchId) => {
  const response = await api.get(`/search/${searchId}/status`);
  return response.data;
};

// Get search results
export const getSearchResults = async (searchId, qualifiedOnly = false) => {
  const response = await api.get(`/search/${searchId}/results`, {
    params: { qualified_only: qualifiedOnly }
  });
  return response.data;
};

// Cancel search
export const cancelSearch = async (searchId) => {
  const response = await api.post(`/search/${searchId}/cancel`);
  return response.data;
};

// Get all leads from history
export const fetchLeads = async () => {
  const response = await api.get('/leads');
  return response.data;
};

// Get specific lead details
export const getLeadDetail = async (leadId) => {
  const response = await api.get(`/leads/${leadId}`);
  return response.data;
};

// Legacy function for backward compatibility
export const searchLeads = async (query) => {
  // Convert old query format to new format
  const searchData = {
    searchTerms: query,
    location: 'Durham, NC'
  };
  return await startSearch(searchData);
};