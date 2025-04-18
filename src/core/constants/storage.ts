/**
 * 스토리지 관련 상수 모듈
 * 
 * 스토리지 키 및 관련 상수를 정의합니다.
 */

// 로컬 스토리지 키
export const LOCAL_STORAGE_KEYS = {
  // 인증 관련 키
  ACCESS_TOKEN: 'jaepa_access_token',
  REFRESH_TOKEN: 'jaepa_refresh_token',
  USER: 'jaepa_user',
  
  // 설정 관련 키
  THEME: 'jaepa_theme',
  LANGUAGE: 'jaepa_language',
  
  // 사용자 기본 설정 키
  WATCHLIST: 'jaepa_watchlist',
  DASHBOARD_LAYOUT: 'jaepa_dashboard_layout',
  NEWS_FILTERS: 'jaepa_news_filters',
  STOCK_FILTERS: 'jaepa_stock_filters',
};

// 세션 스토리지 키
export const SESSION_STORAGE_KEYS = {
  // 임시 데이터 키
  TEMP_FORM_DATA: 'jaepa_temp_form_data',
  SEARCH_HISTORY: 'jaepa_search_history',
  LAST_VISITED_PAGE: 'jaepa_last_visited_page',
};

// 쿠키 키
export const COOKIE_KEYS = {
  // 인증 관련 키
  AUTH_COOKIE: 'jaepa_auth',
  
  // 설정 관련 키
  PREFERENCES: 'jaepa_preferences',
};

// 스토리지 만료 시간 (밀리초)
export const STORAGE_EXPIRY = {
  ACCESS_TOKEN: 60 * 60 * 1000, // 1시간
  REFRESH_TOKEN: 7 * 24 * 60 * 60 * 1000, // 7일
  USER_DATA: 24 * 60 * 60 * 1000, // 1일
  SEARCH_HISTORY: 30 * 24 * 60 * 60 * 1000, // 30일
};
