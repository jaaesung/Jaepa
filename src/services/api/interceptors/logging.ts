/**
 * 로깅 인터셉터 모듈
 * 
 * API 요청 및 응답을 로깅하는 인터셉터를 제공합니다.
 */

import { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import logger from '../../../core/utils/logger';

/**
 * 로깅 인터셉터 설정 함수
 * @param instance axios 인스턴스
 */
export const setupLoggingInterceptors = (instance: AxiosInstance): void => {
  // 요청 인터셉터 - 로깅
  instance.interceptors.request.use(
    (config) => {
      // 민감한 정보 제외하고 로깅
      const { headers, method, url, params, data } = config;
      const sanitizedData = data ? sanitizeData(data) : undefined;
      
      logger.info('API 요청:', {
        method,
        url,
        params,
        data: sanitizedData,
        headers: {
          'Content-Type': headers?.['Content-Type'],
        },
      });
      
      return config;
    },
    (error) => {
      logger.error('API 요청 오류:', error);
      return Promise.reject(error);
    }
  );

  // 응답 인터셉터 - 로깅
  instance.interceptors.response.use(
    (response) => {
      // 응답 데이터 로깅
      const { status, statusText, config, data } = response;
      const sanitizedData = data ? sanitizeData(data) : undefined;
      
      logger.info('API 응답:', {
        status,
        statusText,
        url: config.url,
        method: config.method,
        data: sanitizedData,
      });
      
      return response;
    },
    (error: AxiosError) => {
      // 오류 응답 로깅
      logger.error('API 응답 오류:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        url: error.config?.url,
        method: error.config?.method,
        data: error.response?.data,
      });
      
      return Promise.reject(error);
    }
  );
};

/**
 * 민감한 정보를 제거하는 함수
 * @param data 원본 데이터
 * @returns 민감 정보가 제거된 데이터
 */
const sanitizeData = (data: any): any => {
  if (!data) return data;
  
  // 객체인 경우
  if (typeof data === 'object' && data !== null) {
    const sanitized = { ...data };
    
    // 민감 필드 마스킹
    const sensitiveFields = ['password', 'token', 'refreshToken', 'secret', 'apiKey'];
    sensitiveFields.forEach(field => {
      if (field in sanitized) {
        sanitized[field] = '******';
      }
    });
    
    return sanitized;
  }
  
  return data;
};
