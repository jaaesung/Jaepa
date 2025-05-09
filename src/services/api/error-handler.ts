/**
 * API 오류 처리 유틸리티
 */

import { AxiosError } from 'axios';

interface ApiError {
  status: number;
  message: string;
  code?: string;
  details?: Record<string, any>;
}

/**
 * API 오류 처리 함수
 * 
 * @param error Axios 오류 객체
 * @returns 표준화된 API 오류 객체
 */
export const errorHandler = (error: AxiosError): ApiError => {
  let status = 500;
  let errorMessage = '서버 오류가 발생했습니다.';
  let errorCode;
  let errorDetails;

  if (error.response) {
    // 서버에서 응답을 받았지만 상태 코드가 2xx가 아닌 경우
    status = error.response.status;
    const data: any = error.response.data;

    // 응답 데이터 형식에 따른 오류 메시지 추출
    if (typeof data === 'string') {
      errorMessage = data;
    } else if (data && typeof data === 'object') {
      errorMessage = data.message || data.error || JSON.stringify(data);
      errorCode = data.code;
      errorDetails = data.details;
    }

    // 상태 코드별 에러 처리
    switch (status) {
      case 400:
        if (!errorMessage.includes('유효하지 않은')) {
          errorMessage = '잘못된 요청입니다. ' + errorMessage;
        }
        break;
      case 401:
        errorMessage = '인증이 필요합니다. 다시 로그인해주세요.';
        break;
      case 403:
        errorMessage = '접근 권한이 없습니다.';
        break;
      case 404:
        errorMessage = '요청한 리소스를 찾을 수 없습니다.';
        break;
      case 409:
        errorMessage = '데이터 충돌이 발생했습니다. ' + errorMessage;
        break;
      case 422:
        errorMessage = '입력 데이터가 유효하지 않습니다. ' + errorMessage;
        break;
      case 429:
        errorMessage = '너무 많은 요청을 보냈습니다. 잠시 후 다시 시도해주세요.';
        break;
      case 500:
      case 502:
      case 503:
      case 504:
        errorMessage = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
        break;
    }
  } else if (error.request) {
    // 요청은 보냈지만 응답을 받지 못한 경우
    status = 0;
    errorMessage = '서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.';
  } else {
    // 요청 설정 중에 오류가 발생한 경우
    errorMessage = '요청을 설정하는 중에 오류가 발생했습니다: ' + error.message;
  }

  return {
    status,
    message: errorMessage,
    code: errorCode,
    details: errorDetails
  };
};
