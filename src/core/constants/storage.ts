/**
 * 스토리지 관련 상수 모듈
 *
 * 로컬 스토리지 및 세션 스토리지 관련 상수를 정의합니다.
 */

// 로컬 스토리지 키
export const LOCAL_STORAGE_KEYS = {
  ACCESS_TOKEN: 'jaepa_token',
  REFRESH_TOKEN: 'jaepa_refresh_token',
  USER: 'jaepa_user',
  THEME: 'jaepa_theme',
  LANGUAGE: 'jaepa_language',
  RECENT_SEARCHES: 'jaepa_recent_searches',
  WATCHLIST: 'jaepa_watchlist',
  USER_PREFERENCES: 'jaepa_preferences',
};

// 세션 스토리지 키
export const SESSION_STORAGE_KEYS = {
  REDIRECT_URL: 'jaepa_redirect_url',
  TEMP_DATA: 'jaepa_temp_data',
};

// 스토리지 상수 (레거시 코드와의 호환성을 위해 유지)
export const storageConstants = {
  // 인증 관련
  TOKEN: 'jaepa_token',
  REFRESH_TOKEN: 'jaepa_refresh_token',
  USER: 'jaepa_user',

  // 설정 관련
  THEME: 'jaepa_theme',
  LANGUAGE: 'jaepa_language',

  // 데이터 관련
  RECENT_SEARCHES: 'jaepa_recent_searches',
  WATCHLIST: 'jaepa_watchlist',
  USER_PREFERENCES: 'jaepa_preferences',

  // 로컬 스토리지 키 (새로운 코드에서 사용)
  LOCAL_STORAGE_KEYS,
  SESSION_STORAGE_KEYS,
};

export default storageConstants;
