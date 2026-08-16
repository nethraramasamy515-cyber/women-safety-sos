import axios from 'axios';

const API = axios.create({ baseURL: '/api' });

API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => API.post('/auth/register', data),
  login: (data) => API.post('/auth/login', data),
  getProfile: () => API.get('/auth/profile'),
  updateProfile: (data) => API.put('/auth/profile', data),
};

export const contactsAPI = {
  getAll: () => API.get('/contacts'),
  create: (data) => API.post('/contacts', data),
  add: (data) => API.post('/contacts', data),
  update: (id, data) => API.put(`/contacts/${id}`, data),
  delete: (id) => API.delete(`/contacts/${id}`),
};

export const sosAPI = {
  trigger: (data) => API.post('/sos/trigger', data),
  getHistory: () => API.get('/sos/history'),
  getActive: () => API.get('/sos/active'),
  resolve: (id, status) => API.put(`/sos/${id}/resolve`, status),
};

export const historyAPI = {
  getAll: () => API.get('/sos/history'),
};

export const policeAPI = {
  getAll: () => API.get('/police-stations'),
  nearest: (lat, lon) => API.get(`/police-stations?latitude=${lat}&longitude=${lon}`),
};

export const publicAPI = {
  getPoliceStations: (lat, lon) => API.get(`/police-stations${lat ? `?latitude=${lat}&longitude=${lon}` : ''}`),
  getHelplines: () => API.get('/helplines'),
};

export const adminAPI = {
  getStats: () => API.get('/admin/dashboard'),
  getDashboard: () => API.get('/admin/dashboard'),
  getAllUsers: () => API.get('/admin/users'),
  getAllAlerts: (status) => API.get(`/admin/alerts${status ? `?status=${status}` : ''}`),
  updateAlertStatus: (id, status) => API.put(`/admin/alerts/${id}`, { status }),
};

export default API;
