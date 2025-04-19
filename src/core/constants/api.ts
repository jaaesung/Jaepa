/**
 * API 관련 상수 모듈
 *
 * API 관련 상수를 정의합니다.
 */

// API 기본 URL
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

// API 타임아웃은 config에서 가져옵니다.

// API 엔드포인트
export const API_ENDPOINTS = {
  // 인증 관련 엔드포인트
  AUTH: {
    LOGIN: 'login',
    REGISTER: 'register',
    LOGOUT: 'logout',
    REFRESH_TOKEN: 'refresh-token',
    VERIFY_TOKEN: 'verify-token',
    CHANGE_PASSWORD: 'change-password',
    FORGOT_PASSWORD: 'forgot-password',
    RESET_PASSWORD: 'reset-password',
    UPDATE_PROFILE: 'update-profile',
  },

  // 뉴스 관련 엔드포인트
  NEWS: {
    LIST: 'list',
    DETAIL: 'detail',
    SEARCH: 'search',
    CATEGORIES: 'categories',
    SOURCES: 'sources',
  },

  // 감성 분석 관련 엔드포인트
  SENTIMENT: {
    ANALYZE: 'analyze',
    TREND: 'trend',
    STATS: 'stats',
    MODELS: 'models',
  },

  // 주식 관련 엔드포인트
  STOCK: {
    LIST: 'list',
    DETAIL: 'detail',
    SEARCH: 'search',
    HISTORY: 'history',
    INDICATORS: 'indicators',
    POPULAR: 'popular',
  },
};

// API 서비스 이름
export const API_SERVICES = {
  AUTH: 'auth',
  NEWS: 'news',
  SENTIMENT: 'sentiment',
  STOCK: 'stock',
  STOCKS: 'stocks', // 주식 서비스 (레거시 코드와의 호환성을 위해 추가)
  ANALYSIS: 'analysis', // 분석 서비스 (레거시 코드와의 호환성을 위해 추가)
  USER: 'user',
};

// API 응답 상태 코드
export const API_STATUS_CODES = {
  SUCCESS: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  VALIDATION_ERROR: 422,
  SERVER_ERROR: 500,
};

// API 헤더
export const API_HEADERS = {
  CONTENT_TYPE: 'Content-Type',
  AUTHORIZATION: 'Authorization',
  ACCEPT: 'Accept',
};

// API 콘텐츠 타입
export const API_CONTENT_TYPES = {
  JSON: 'application/json',
  FORM_DATA: 'multipart/form-data',
  URL_ENCODED: 'application/x-www-form-urlencoded',
};
