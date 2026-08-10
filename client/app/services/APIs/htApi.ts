/**htApi.ts - service for making requests to the Haztrak API*/
import axios, { AxiosResponse, InternalAxiosRequestConfig } from 'axios';

/** An Axios instance with session cookies and CSRF headers */
export const htApi = axios.create({
  baseURL: import.meta.env.VITE_HT_API_URL ?? '',
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFTOKEN',
  withCredentials: true,
});

htApi.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    config.headers = config.headers ?? {};
    return config;
  },
  (error) => Promise.reject(error)
);

export const returnOnSuccess = (response: AxiosResponse) => response;

htApi.interceptors.response.use(returnOnSuccess, (error) => {
  if (error.response?.status === 401) {
    const path = window.location.pathname;
    if (path !== '/login' && path !== '/register') {
      window.location.assign('/login');
    }
  }
  return Promise.reject(error);
});
