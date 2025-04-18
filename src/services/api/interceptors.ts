/**
 * API 인터셉터 모듈
 * 
 * API 요청 및 응답을 가로채서 처리하는 인터셉터를 제공합니다.
 */

import { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { tokenService } from '../auth';
import { errorHandler } from './error-handler';

/**
 * Axios 인스턴스에 인터셉터 설정
 * 
 * @param instance Axios 인스턴스
 */
export const setupInterceptors = (instance: AxiosInstance): void => {
  // 요청 인터셉터
  instance.interceptors.request.use(
    (config: AxiosRequestConfig) => requestInterceptor(config),
    (error: AxiosError) => Promise.reject(error)
  );

  // 응답 인터셉터
  instance.interceptors.response.use(
    (response: AxiosResponse) => responseInterceptor(response),
    (error: AxiosError) => responseErrorInterceptor(error, instance)
  );
};

/**
 * 요청 인터셉터
 * 
 * @param config Axios 요청 설정
 * @returns 수정된 요청 설정
 */
const requestInterceptor = (config: AxiosRequestConfig): AxiosRequestConfig => {
  // 인증 토큰이 있으면 헤더에 추가
  const token = tokenService.getAccessToken();
  
  if (token && config.headers) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  
  return config;
};

/**
 * 응답 인터셉터
 * 
 * @param response Axios 응답
 * @returns 응답 데이터
 */
const responseInterceptor = (response: AxiosResponse): AxiosResponse => {
  // 응답 데이터 처리 (필요한 경우)
  return response;
};

/**
 * 응답 에러 인터셉터
 * 
 * @param error Axios 에러
 * @param instance Axios 인스턴스
 * @returns 처리된 응답 또는 에러
 */
const responseErrorInterceptor = async (
  error: AxiosError,
  instance: AxiosInstance
): Promise<AxiosResponse | any> => {
  const originalRequest = error.config;
  
  // 401 에러 (인증 실패) 처리
  if (error.response?.status === 401 && originalRequest) {
    // 토큰 갱신 시도
    try {
      const refreshed = await tokenService.refreshToken();
      
      if (refreshed && originalRequest.headers) {
        // 새 토큰으로 헤더 업데이트
        originalRequest.headers['Authorization'] = `Bearer ${tokenService.getAccessToken()}`;
        
        // 원래 요청 재시도
        return instance(originalRequest);
      }
    } catch (refreshError) {
      // 토큰 갱신 실패 시 로그아웃 처리
      tokenService.clearTokens();
      window.location.href = '/login';
      return Promise.reject(refreshError);
    }
  }
  
  // 기타 에러 처리
  return errorHandler.handleApiError(error);
};

export default setupInterceptors;
