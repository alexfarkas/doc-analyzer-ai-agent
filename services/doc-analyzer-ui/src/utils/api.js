// src/utils/api.js

const API_BASE = '/api';

export async function apiFetch(endpoint, options = {}) {
  const defaultOptions = {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  if (options.body instanceof FormData) {
    delete defaultOptions.headers['Content-Type'];
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...defaultOptions,
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || `Ошибка сети: ${response.status}`);
  }

  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return response.json();
  }

  return response;
}

export async function apiStream(endpoint, options = {}) {
  const defaultOptions = {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  return fetch(`${API_BASE}${endpoint}`, {
    ...defaultOptions,
    ...options,
  });
}