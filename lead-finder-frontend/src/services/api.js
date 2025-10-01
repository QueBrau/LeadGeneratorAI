import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000'; // Replace with your backend URL

export const fetchLeads = async () => {
  const response = await axios.get(`${API_BASE_URL}/leads`);
  return response.data;
};

export const searchLeads = async (query) => {
  const response = await axios.get(`${API_BASE_URL}/search`, { params: { query } });
  return response.data;
};