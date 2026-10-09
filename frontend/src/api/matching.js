import apiClient from './client';

const matchingApi = {
  profile: () => apiClient.get('/matching/profile/'),
  updateProfile: (payload) => apiClient.patch('/matching/profile/', payload),
  myMatches: (params = {}) => apiClient.get('/matching/my/', { params }),
  forDonation: (donationId, params = {}) => apiClient.get(`/matching/donations/${donationId}/matches/`, { params }),
  generate: (donationId, params = {}) => apiClient.post(`/matching/donations/${donationId}/generate/`, null, { params }),
  accept: (recommendationId) => apiClient.post(`/matching/matches/${recommendationId}/accept/`),
  decline: (recommendationId) => apiClient.post(`/matching/matches/${recommendationId}/decline/`),
};

export default matchingApi;
