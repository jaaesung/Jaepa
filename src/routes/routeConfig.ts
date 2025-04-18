/**
 * 라우트 설정 모듈
 *
 * 애플리케이션의 라우트 설정을 제공합니다.
 */

import React from 'react';

// 라우트 그룹 타입
export type RouteGroup = 'public' | 'auth' | 'dashboard' | 'analysis';

// 라우트 설정 인터페이스
export interface RouteConfig {
  path: string;
  component: React.LazyExoticComponent<React.ComponentType<any>>;
  exact?: boolean;
  restricted?: boolean;
  protected?: boolean;
  group: RouteGroup;
}

// 페이지 컴포넌트 지연 로딩
const HomePage = React.lazy(() => import('@/pages/HomePage'));
const LoginPage = React.lazy(() => import('@/pages/LoginPage'));
const RegisterPage = React.lazy(() => import('@/pages/RegisterPage'));
const ForgotPasswordPage = React.lazy(() => import('@/pages/ForgotPasswordPage'));
const ResetPasswordPage = React.lazy(() => import('@/pages/ResetPasswordPage'));
const DashboardPage = React.lazy(() => import('@/pages/DashboardPage'));
const NewsAnalysisPage = React.lazy(() => import('@/pages/NewsAnalysisPage'));
const StockAnalysisPage = React.lazy(() => import('@/pages/StockAnalysisPage'));
const SentimentAnalysisPage = React.lazy(() => import('@/pages/SentimentAnalysisPage'));
const SettingsPage = React.lazy(() => import('@/pages/SettingsPage'));
const NotFoundPage = React.lazy(() => import('@/pages/NotFoundPage'));

// 라우트 설정
const routes: RouteConfig[] = [
  // 공개 라우트
  {
    path: '/',
    component: HomePage,
    exact: true,
    group: 'public',
  },

  // 인증 라우트
  {
    path: '/login',
    component: LoginPage,
    restricted: true,
    group: 'auth',
  },
  {
    path: '/register',
    component: RegisterPage,
    restricted: true,
    group: 'auth',
  },
  {
    path: '/forgot-password',
    component: ForgotPasswordPage,
    restricted: true,
    group: 'auth',
  },
  {
    path: '/reset-password/:token',
    component: ResetPasswordPage,
    restricted: true,
    group: 'auth',
  },

  // 대시보드 라우트
  {
    path: '/dashboard',
    component: DashboardPage,
    protected: true,
    group: 'dashboard',
  },
  {
    path: '/settings',
    component: SettingsPage,
    protected: true,
    group: 'dashboard',
  },

  // 분석 라우트
  {
    path: '/news-analysis',
    component: NewsAnalysisPage,
    protected: true,
    group: 'analysis',
  },
  {
    path: '/stock-analysis',
    component: StockAnalysisPage,
    protected: true,
    group: 'analysis',
  },
  {
    path: '/stock-analysis/:symbol',
    component: StockAnalysisPage,
    protected: true,
    group: 'analysis',
  },
  {
    path: '/sentiment-analysis',
    component: SentimentAnalysisPage,
    protected: true,
    group: 'analysis',
  },

  // 404 페이지
  {
    path: '/404',
    component: NotFoundPage,
    group: 'public',
  },
];

export default routes;
