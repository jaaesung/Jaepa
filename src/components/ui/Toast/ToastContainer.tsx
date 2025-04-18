/**
 * 토스트 컨테이너 컴포넌트
 * 
 * 토스트 알림을 표시하는 컨테이너 컴포넌트를 제공합니다.
 */

import React from 'react';
import { createPortal } from 'react-dom';
import Toast, { ToastProps } from './Toast';
import './ToastContainer.css';

export type ToastPosition = 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';

export interface ToastContainerProps {
  /**
   * 토스트 목록
   */
  toasts: Omit<ToastProps, 'onClose'>[];
  
  /**
   * 토스트 닫기 핸들러
   */
  onClose: (id: string) => void;
  
  /**
   * 토스트 위치
   */
  position?: ToastPosition;
  
  /**
   * 추가 클래스명
   */
  className?: string;
}

/**
 * 토스트 컨테이너 컴포넌트
 */
const ToastContainer: React.FC<ToastContainerProps> = ({
  toasts,
  onClose,
  position = 'top-right',
  className = '',
}) => {
  // 토스트 컨테이너 클래스 생성
  const containerClasses = [
    'toast-container',
    `toast-container--${position}`,
    className,
  ].filter(Boolean).join(' ');
  
  // 토스트가 없으면 렌더링하지 않음
  if (toasts.length === 0) {
    return null;
  }
  
  // 토스트 컨테이너 포털 생성
  return createPortal(
    <div className={containerClasses}>
      {toasts.map(toast => (
        <Toast
          key={toast.id}
          {...toast}
          onClose={onClose}
        />
      ))}
    </div>,
    document.body
  );
};

export default ToastContainer;
