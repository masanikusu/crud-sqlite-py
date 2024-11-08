import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const taskApi = {
    getAll: () => api.get('/tasks'),
    getById: (id) => api.get(`/task/${id}`),
    create: (data) => api.post('/tasks', data),
    update: (id, data) => api.put(`/tasks/${id}`, data),
    delete: (id) => api.delete(`/tasks/${id}`),
    complete: (id) => api.put(`tasks/${id}/complete`),
};

export const categoryApi = {
    getAll: () => api.get('/categories'),
    create: (data) => api.post('/categories', data),
    update: (id, data) => api.put(`/categories/${id}`, data),
    delete: (id) => api.delete(`/categories/${id}`),
};

export const authApi = {
    login: (username, password) =>
        api.post('/auth/login', { username, password }),
    register: (username, email, password) =>
        api.post('/auth/register', { username, email, password }),
    logout: () => api.post('/auth/logout'),
    getUser: () => api.get('/auth/user'),
};
