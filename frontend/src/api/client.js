import axios from 'axios';

const TOKEN_STORAGE_KEYS = {
  access: 'foodshare_access_token',
  refresh: 'foodshare_refresh_token',
  user: 'foodshare_user',
};

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const tokenStorage = {
  getAccessToken: () => localStorage.getItem(TOKEN_STORAGE_KEYS.access),
  getRefreshToken: () => localStorage.getItem(TOKEN_STORAGE_KEYS.refresh),
  persistAuth: ({ access, refresh, user }) => {
    if (access) localStorage.setItem(TOKEN_STORAGE_KEYS.access, access);
    if (refresh) localStorage.setItem(TOKEN_STORAGE_KEYS.refresh, refresh);
    if (user) localStorage.setItem(TOKEN_STORAGE_KEYS.user, JSON.stringify(user));
  },
  clearAuth: () => {
    localStorage.removeItem(TOKEN_STORAGE_KEYS.access);
    localStorage.removeItem(TOKEN_STORAGE_KEYS.refresh);
    localStorage.removeItem(TOKEN_STORAGE_KEYS.user);
  },
};

export const authApi = {
  register: (payload) => apiClient.post('/auth/register/', payload),
  login: (payload) => apiClient.post('/auth/login/', payload),
  refresh: (refreshToken) => apiClient.post('/auth/refresh/', { refresh: refreshToken }),
  profile: () => apiClient.get('/auth/profile/'),
  updateProfile: (payload) => apiClient.patch('/auth/profile/', payload),
  ngoProfile: () => apiClient.get('/auth/ngo/profile/'),
  updateNGOProfile: (payload) => apiClient.patch('/auth/ngo/profile/', payload),
  ngoVerification: () => apiClient.get('/auth/ngo/verification/'),
  submitNGOVerification: (payload) => apiClient.post('/auth/ngo/verification/', payload, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  volunteerProfile: () => apiClient.get('/auth/volunteer/profile/'),
  updateVolunteerProfile: (payload) => apiClient.patch('/auth/volunteer/profile/', payload),
};

apiClient.interceptors.request.use((config) => {
  const accessToken = tokenStorage.getAccessToken();

  if (accessToken) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = tokenStorage.getRefreshToken();

      if (!refreshToken) {
        tokenStorage.clearAuth();
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }

      try {
        const refreshResponse = await axios.post(`${baseURL}/auth/refresh/`, { refresh: refreshToken });
        const nextAccessToken = refreshResponse.data.access;
        tokenStorage.persistAuth({ access: nextAccessToken, refresh: refreshToken });
        originalRequest.headers.Authorization = `Bearer ${nextAccessToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        tokenStorage.clearAuth();
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);

export default apiClient;
