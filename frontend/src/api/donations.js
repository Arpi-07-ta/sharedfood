import apiClient from './client';

const donationApi = {
  list: (params = {}) => apiClient.get('/donations/', { params }),
  myDonations: (params = {}) => apiClient.get('/donations/my/', { params }),
  acceptedDonations: (params = {}) => apiClient.get('/donations/accepted/', { params }),
  myRequests: (params = {}) => apiClient.get('/donations/requests/my/', { params }),
  requestDonation: (donationId, payload) => apiClient.post(`/donations/${donationId}/requests/`, payload),
  acceptRequest: (requestId) => apiClient.post(`/donations/requests/${requestId}/accept/`),
  rejectRequest: (requestId) => apiClient.post(`/donations/requests/${requestId}/reject/`),
  categories: () => apiClient.get('/donations/categories/'),
  getById: (id) => apiClient.get(`/donations/${id}/`),
  create: (payload) => apiClient.post('/donations/', payload, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  update: (id, payload) => apiClient.patch(`/donations/${id}/`, payload, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  cancel: (id) => apiClient.post(`/donations/${id}/cancel/`),
  history: (id) => apiClient.get(`/donations/${id}/status-history/`),
};

export default donationApi;
