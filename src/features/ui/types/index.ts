/**
 * UI 관련 타입 정의
 */

// 토스트 위치
export type ToastPosition = 
  | 'top-left'
  | 'top-center'
  | 'top-right'
  | 'bottom-left'
  | 'bottom-center'
  | 'bottom-right';

// 토스트 타입
export type ToastType = 'info' | 'success' | 'warning' | 'error';

// 토스트 메시지
export interface Toast {
  id: string;
  type: ToastType;
  title?: string;
  message: string;
  autoClose?: boolean;
  duration?: number;
}

// 모달 타입
export interface Modal {
  id: string;
  component: React.ComponentType<any>;
  props?: Record<string, any>;
}

// UI 테마
export type Theme = 'light' | 'dark' | 'system';

// UI 상태
export interface UiState {
  theme: Theme;
  toasts: Toast[];
  isSidebarOpen: boolean;
  modals: Modal[];
}
