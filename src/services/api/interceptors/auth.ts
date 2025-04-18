/**
 * 인증 인터셉터 모듈
 * 
 * API 요청에 인증 토큰을 추가하고 토큰 만료 시 갱신하는 인터셉터를 제공합니다.
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { API_BASE_URL } from '../../../core/constants';
import logger from '../../../core/utils/logger';

interface RefreshTokenResponse {
  token: string;
  refresh_token?: string;
}

/**
 * 인증 인터셉터 설정 함수
 * @param instance axios 인스턴스
 */
export const setupAuthInterceptors = (instance: AxiosInstance): void => {
  // 요청 인터셉터 - 토큰 추가
  instance.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      logger.error('인증 요청 인터셉터 오류:', error);
      return Promise.reject(error);
    }
  );

  // 응답 인터셉터 - 토큰 만료 처리
  instance.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as AxiosRequestConfig & {
        _retry?: boolean;
      };

      // 401 에러이고 재시도가 아직 안된 경우 (토큰 만료)
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          // 리프레시 토큰으로 새 토큰 발급 요청
          const refreshToken = localStorage.getItem('refreshToken');
          if (!refreshToken) {
            // 리프레시 토큰이 없으면 로그아웃 처리
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
            window.location.href = '/login';
            return Promise.reject(error);
          }

          const response = await axios.post<RefreshTokenResponse>(
            `${API_BASE_URL}/auth/refresh-token`,
            { refresh_token: refreshToken }
          );

          if (response.data.token) {
            localStorage.setItem('token', response.data.token);
            
            // 새 리프레시 토큰이 있으면 저장
            if (response.data.refresh_token) {
              localStorage.setItem('refreshToken', response.data.refresh_token);
            }
            
            // 새 토큰으로 원래 요청 재시도
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${response.data.token}`;
            }
            return instance(originalRequest);
          }
        } catch (refreshError) {
          // 리프레시 토큰으로 새 토큰 발급 실패 시 로그아웃 처리
          logger.error('토큰 갱신 오류:', refreshError);
          localStorage.removeItem('token');
          localStorage.removeItem('refreshToken');
          window.location.href = '/login';
        }
      }

      return Promise.reject(error);
    }
  );
};
