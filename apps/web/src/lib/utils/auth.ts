import axios from 'axios';
import { browser } from '$app/environment';
import { authStore } from '$lib/stores/auth';
import { goto } from '$app/navigation';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  };
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  if (browser) {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Clear auth state on unauthorized
      authStore.clear();
      if (browser) {
        const currentPath = window.location.pathname;
        if (currentPath !== '/auth/login' && currentPath !== '/auth/register') {
          await goto('/auth/login');
        }
      }
    }
    return Promise.reject(error);
  }
);

export async function signIn(email: string, password: string): Promise<LoginResponse> {
  const params = new URLSearchParams();
  params.append('username', email);
  params.append('password', password);

  try {
    const { data } = await api.post<LoginResponse>('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    if (browser) {
      localStorage.setItem('token', data.access_token);
    }
    return data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Login error response:', error.response?.data);
    }
    throw error;
  }
}

export async function signUp(email: string, password: string, firstName: string, lastName: string): Promise<void> {
  try {
    await api.post('/auth/register', {
      email,
      password,
      first_name: firstName,
      last_name: lastName,
    });
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Registration error response:', error.response?.data);
    }
    throw error;
  }
}

export async function signOut(): Promise<void> {
  authStore.clear();
  if (browser) {
    await goto('/auth/login');
  }
}

export async function getCurrentUser(): Promise<User | null> {
  if (!getStoredToken()) return null;
  
  try {
    const { data } = await api.get<User>('/auth/me');
    return data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 401) {
        // Clear token if it's invalid or expired
        authStore.clear();
      }
      console.error('Get current user error:', error.response?.data);
    }
    return null;
  }
}

export function getStoredToken(): string | null {
  return browser ? localStorage.getItem('token') : null;
} 