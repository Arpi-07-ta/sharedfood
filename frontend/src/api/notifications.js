import apiClient from './client';

const notificationsApi = {
  list: (params = {}) => apiClient.get('/notifications/', { params }),
  unreadCount: () => apiClient.get('/notifications/unread-count/'),
  markRead: (id) => apiClient.post(`/notifications/${id}/read/`),
  markAllRead: () => apiClient.post('/notifications/read-all/'),
};

export default notificationsApi;
