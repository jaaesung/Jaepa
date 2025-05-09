/**
 * API 인터셉터
 */

import { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { errorHandler } from './error-handler';
import { storageConstants } from '../../core/constants';
import { localStorageService } from '../storage';

/**
 * API 인터셉터 설정
 */
export const setupInterceptors = (instance: AxiosInstance) => {
  // 요청 인터셉터
  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      // 요청 헤더에 토큰 추가
      const token = localStorageService.getItem(storageConstants.TOKEN);
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error: AxiosError) => Promise.reject(error)
  );

  // 응답 인터셉터
  instance.interceptors.response.use(
    (response: AxiosResponse) => response,
    async (error: AxiosError) => {
      // 에러 처리
      const processedError = errorHandler(error);
      
      // 401 오류 처리 (인증 만료)
      if (processedError.status === 401) {
        // 리프레시 토큰으로 액세스 토큰 갱신 로직이 필요한 경우 여기에 구현
        
        // 토큰이 만료되었거나 갱신할 수 없는 경우 로그아웃 처리
        localStorageService.removeItem(storageConstants.TOKEN);
        localStorageService.removeItem(storageConstants.USER);
        
        // 인증 페이지로 리다이렉트
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
      
      return Promise.reject(processedError);
    }
  );
};
