/**
 * API 클라이언트
 */

import axios, { AxiosInstance, AxiosResponse, AxiosRequestConfig } from 'axios';
import { setupInterceptors } from './interceptors';

// API 기본 URL
import { API_BASE_URL } from '../../core/constants/api';
import { API_TIMEOUT } from '../../core/config';

// Axios 인스턴스 생성
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// 인터셉터 설정
setupInterceptors(apiClient);

// API 요청 메서드들
const api = {
  /**
   * GET 요청
   */
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    return apiClient.get<T, AxiosResponse<T>>(url, config).then(response => response.data);
  },

  /**
   * POST 요청
   */
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    return apiClient.post<T, AxiosResponse<T>>(url, data, config).then(response => response.data);
  },

  /**
   * PUT 요청
   */
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    return apiClient.put<T, AxiosResponse<T>>(url, data, config).then(response => response.data);
  },

  /**
   * PATCH 요청
   */
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    return apiClient.patch<T, AxiosResponse<T>>(url, data, config).then(response => response.data);
  },

  /**
   * DELETE 요청
   */
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    return apiClient.delete<T, AxiosResponse<T>>(url, config).then(response => response.data);
  },

  /**
   * 서비스와 엔드포인트를 조합하여 URL 생성
   */
  buildUrl: (service: string, endpoint: string): string => {
    return `${service}/${endpoint}`;
  },
};

export default api;
export { apiClient };
