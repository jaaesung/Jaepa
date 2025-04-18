/**
 * API 에러 핸들러 모듈
 * 
 * API 요청 중 발생하는 에러를 처리하는 기능을 제공합니다.
 */

import { AxiosError } from 'axios';

/**
 * API 에러 타입
 */
export interface ApiError extends Error {
  status?: number;
  data?: any;
  isApiError: boolean;
}

/**
 * API 에러 핸들러 클래스
 */
class ApiErrorHandler {
  /**
   * API 에러 처리
   * 
   * @param error Axios 에러
   * @returns 처리된 에러 또는 거부된 프로미스
   */
  handleApiError(error: AxiosError): Promise<never> {
    if (!error.response) {
      // 네트워크 에러
      return Promise.reject(this.createApiError('Network Error', 0));
    }

    const { status, data } = error.response;
    let errorMessage = 'Unknown Error';

    // 에러 메시지 추출
    if (typeof data === 'string') {
      errorMessage = data;
    } else if (data && typeof data === 'object') {
      errorMessage = data.message || data.error || JSON.stringify(data);
    }

    // 상태 코드별 에러 처리
    switch (status) {
      case 400:
        return Promise.reject(this.createApiError(`Bad Request: ${errorMessage}`, status, data));
      case 401:
        return Promise.reject(this.createApiError(`Unauthorized: ${errorMessage}`, status, data));
      case 403:
        return Promise.reject(this.createApiError(`Forbidden: ${errorMessage}`, status, data));
      case 404:
        return Promise.reject(this.createApiError(`Not Found: ${errorMessage}`, status, data));
      case 422:
        return Promise.reject(this.createApiError(`Validation Error: ${errorMessage}`, status, data));
      case 500:
        return Promise.reject(this.createApiError(`Server Error: ${errorMessage}`, status, data));
      default:
        return Promise.reject(this.createApiError(`Error ${status}: ${errorMessage}`, status, data));
    }
  }

  /**
   * API 에러 객체 생성
   * 
   * @param message 에러 메시지
   * @param status HTTP 상태 코드
   * @param data 에러 데이터
   * @returns API 에러 객체
   */
  createApiError(message: string, status?: number, data?: any): ApiError {
    const error = new Error(message) as ApiError;
    error.status = status;
    error.data = data;
    error.isApiError = true;
    return error;
  }

  /**
   * API 에러 여부 확인
   * 
   * @param error 확인할 에러
   * @returns API 에러 여부
   */
  isApiError(error: any): error is ApiError {
    return error && error.isApiError === true;
  }
}

export const errorHandler = new ApiErrorHandler();
export default errorHandler;
