import apiClient from './client';

const ngoOperationsApi = {
  analytics: () => apiClient.get('/analytics/ngo/summary/'),
  feedback: () => apiClient.get('/feedback/ngo/'),
  submitFeedback: (payload) => apiClient.post('/feedback/ngo/', payload),
};

export default ngoOperationsApi;
