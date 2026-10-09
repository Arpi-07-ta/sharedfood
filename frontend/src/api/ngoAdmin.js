import apiClient from './client';

const ngoAdminApi = {
  verifications: (params = {}) => apiClient.get('/auth/admin/ngo-verifications/', { params }),
  reviewVerification: (verificationId, payload) => apiClient.post(`/auth/admin/ngo-verifications/${verificationId}/review/`, payload),
  verificationDocument: (verificationId) => apiClient.get(`/auth/admin/ngo-verifications/${verificationId}/document/`, { responseType: 'blob' }),
};

export default ngoAdminApi;
