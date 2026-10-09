import apiClient from './client';

const fraudApi = {
  listAlerts: (params = {}) => apiClient.get('/fraud-detection/alerts/', { params }),
  getAlert: (alertId) => apiClient.get(`/fraud-detection/alerts/${alertId}/`),
  reviewAlert: (alertId, payload) => apiClient.post(`/fraud-detection/alerts/${alertId}/review/`, payload),
};

export default fraudApi;
