import apiClient from './client';

const trackingApi = {
  volunteerProfile: () => apiClient.get('/auth/volunteer/profile/'),
  updateVolunteerProfile: (payload) => apiClient.patch('/auth/volunteer/profile/', payload),
  assignments: () => apiClient.get('/tracking/volunteer/assignments/'),
  available: () => apiClient.get('/tracking/volunteer/available/'),
  accept: (pickupId) => apiClient.post(`/tracking/volunteer/pickups/${pickupId}/accept/`),
  detail: (pickupId) => apiClient.get(`/tracking/pickups/${pickupId}/`),
  proof: (pickupId) => apiClient.get(`/tracking/pickups/${pickupId}/proof/`, { responseType: 'blob' }),
  updateStatus: (pickupId, payload) => apiClient.patch(`/tracking/pickups/${pickupId}/status/`, payload, {
    headers: payload instanceof FormData ? { 'Content-Type': 'multipart/form-data' } : undefined,
  }),
  ngoPickups: () => apiClient.get('/tracking/ngo/pickups/'),
  schedule: (donationId, payload) => apiClient.post(`/tracking/donations/${donationId}/schedule-pickup/`, payload),
  confirmReceived: (pickupId) => apiClient.post(`/tracking/pickups/${pickupId}/confirm-received/`),
};

export default trackingApi;
