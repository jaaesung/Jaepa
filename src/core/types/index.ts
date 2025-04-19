/**
 * 애플리케이션 공통 타입 모듈
 *
 * 애플리케이션 전체에서 사용되는 공통 타입을 정의합니다.
 */

// Redux 액션 관련 타입
export type AsyncThunkConfig = {
  state?: unknown;
  dispatch?: unknown;
  extra?: unknown;
  rejectValue: string;
  serializedErrorType?: unknown;
  pendingMeta?: unknown;
  fulfilledMeta?: unknown;
  rejectedMeta?: unknown;
};

// 기간 타입
export type PeriodType = '1d' | '1w' | '1m' | '3m' | '6m' | '1y';

// 알림 관련 타입
export interface Notification {
  id: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  createdAt: string;
}

// 페이지네이션 관련 타입
export interface PaginationParams {
  page: number;
  limit: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}

// API 응답 관련 타입
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

// 전체 스토어 상태 타입
export interface RootState {
  auth: any; // 인증 관련 상태
  news: any; // 뉴스 관련 상태
  stocks: any; // 주식 관련 상태
  sentimentAnalysis: any; // 감성 분석 관련 상태
  dashboard: any; // 대시보드 관련 상태
  ui: any; // UI 관련 상태
}
