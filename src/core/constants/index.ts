/**
 * 애플리케이션 상수 모듈
 * 
 * 애플리케이션 전체에서 사용되는 상수를 정의합니다.
 */

// API 관련 상수
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
export const API_TIMEOUT = 30000; // 30초

// 인증 관련 상수
export const TOKEN_STORAGE_KEY = 'token';
export const REFRESH_TOKEN_STORAGE_KEY = 'refreshToken';
export const TOKEN_EXPIRY_MARGIN = 5 * 60 * 1000; // 5분 (밀리초)

// 페이지네이션 관련 상수
export const DEFAULT_PAGE_SIZE = 10;
export const DEFAULT_PAGE = 1;

// 날짜 형식 관련 상수
export const DATE_FORMAT = 'YYYY-MM-DD';
export const DATETIME_FORMAT = 'YYYY-MM-DD HH:mm:ss';

// 테마 관련 상수
export const THEME_STORAGE_KEY = 'theme';
export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark',
} as const;

// 로컬 스토리지 키
export const STORAGE_KEYS = {
  USER_PREFERENCES: 'userPreferences',
  RECENT_SEARCHES: 'recentSearches',
  SAVED_STOCKS: 'savedStocks',
} as const;

// 에러 메시지
export const ERROR_MESSAGES = {
  NETWORK_ERROR: '네트워크 연결에 문제가 있습니다. 인터넷 연결을 확인해주세요.',
  SERVER_ERROR: '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
  UNAUTHORIZED: '인증이 필요합니다. 다시 로그인해주세요.',
  FORBIDDEN: '접근 권한이 없습니다.',
  NOT_FOUND: '요청한 리소스를 찾을 수 없습니다.',
  VALIDATION_ERROR: '입력 데이터가 유효하지 않습니다.',
} as const;
