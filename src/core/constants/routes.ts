/**
 * 라우트 관련 상수 모듈
 * 
 * 애플리케이션의 라우트 경로를 정의합니다.
 */

// 기본 라우트
export const ROUTES = {
  // 공개 라우트
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
  
  // 인증 필요 라우트
  DASHBOARD: '/dashboard',
  NEWS_ANALYSIS: '/news-analysis',
  STOCK_ANALYSIS: '/stock-analysis',
  SENTIMENT_ANALYSIS: '/sentiment-analysis',
  SETTINGS: '/settings',
  PROFILE: '/profile',
  
  // 기타 라우트
  NOT_FOUND: '/404',
};

// 라우트 그룹
export const ROUTE_GROUPS = {
  PUBLIC: [
    ROUTES.HOME,
    ROUTES.LOGIN,
    ROUTES.REGISTER,
    ROUTES.FORGOT_PASSWORD,
    ROUTES.RESET_PASSWORD,
    ROUTES.NOT_FOUND,
  ],
  PRIVATE: [
    ROUTES.DASHBOARD,
    ROUTES.NEWS_ANALYSIS,
    ROUTES.STOCK_ANALYSIS,
    ROUTES.SENTIMENT_ANALYSIS,
    ROUTES.SETTINGS,
    ROUTES.PROFILE,
  ],
};

// 리디렉션 라우트
export const REDIRECT_ROUTES = {
  AFTER_LOGIN: ROUTES.DASHBOARD,
  AFTER_LOGOUT: ROUTES.HOME,
  AFTER_REGISTER: ROUTES.DASHBOARD,
  UNAUTHORIZED: ROUTES.LOGIN,
};

// 네비게이션 항목
export const NAVIGATION_ITEMS = [
  {
    label: '대시보드',
    path: ROUTES.DASHBOARD,
    icon: 'dashboard',
    requiresAuth: true,
  },
  {
    label: '뉴스 분석',
    path: ROUTES.NEWS_ANALYSIS,
    icon: 'news',
    requiresAuth: true,
  },
  {
    label: '주식 분석',
    path: ROUTES.STOCK_ANALYSIS,
    icon: 'stock',
    requiresAuth: true,
  },
  {
    label: '감성 분석',
    path: ROUTES.SENTIMENT_ANALYSIS,
    icon: 'sentiment',
    requiresAuth: true,
  },
  {
    label: '설정',
    path: ROUTES.SETTINGS,
    icon: 'settings',
    requiresAuth: true,
  },
];
