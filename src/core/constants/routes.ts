/**
 * 라우트 상수 정의
 */

export const routeConstants = {
  // 공개 라우트
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password/:token',
  
  // 인증 필요 라우트
  DASHBOARD: '/dashboard',
  NEWS_ANALYSIS: '/news-analysis',
  STOCK_ANALYSIS: '/stock-analysis',
  SENTIMENT_ANALYSIS: '/sentiment-analysis',
  SETTINGS: '/settings',
  PROFILE: '/profile',
  
  // 기타
  NOT_FOUND: '*'
};
