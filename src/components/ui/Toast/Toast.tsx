/**
 * 토스트 컴포넌트
 * 
 * 사용자에게 짧은 알림 메시지를 표시하는 토스트 컴포넌트를 제공합니다.
 */

import React, { useEffect } from 'react';
import './Toast.css';

export type ToastType = 'info' | 'success' | 'warning' | 'error';

export interface ToastProps {
  /**
   * 토스트 ID
   */
  id: string;
  
  /**
   * 토스트 타입
   */
  type: ToastType;
  
  /**
   * 토스트 메시지
   */
  message: string;
  
  /**
   * 토스트 제목
   */
  title?: string;
  
  /**
   * 토스트 지속 시간 (밀리초)
   */
  duration?: number;
  
  /**
   * 토스트 닫기 핸들러
   */
  onClose: (id: string) => void;
  
  /**
   * 추가 클래스명
   */
  className?: string;
}

/**
 * 토스트 컴포넌트
 */
const Toast: React.FC<ToastProps> = ({
  id,
  type = 'info',
  message,
  title,
  duration = 5000,
  onClose,
  className = '',
}) => {
  // 토스트 아이콘 선택
  const getIcon = () => {
    switch (type) {
      case 'success':
        return (
          <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM8 15L3 10L4.41 8.59L8 12.17L15.59 4.58L17 6L8 15Z"
              fill="currentColor"
            />
          </svg>
        );
      case 'warning':
        return (
          <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM11 15H9V13H11V15ZM11 11H9V5H11V11Z"
              fill="currentColor"
            />
          </svg>
        );
      case 'error':
        return (
          <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM11 15H9V13H11V15ZM11 11H9V5H11V11Z"
              fill="currentColor"
            />
          </svg>
        );
      default:
        return (
          <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM11 15H9V13H11V15ZM11 11H9V5H11V11Z"
              fill="currentColor"
            />
          </svg>
        );
    }
  };
  
  // 자동 닫기
  useEffect(() => {
    if (duration) {
      const timer = setTimeout(() => {
        onClose(id);
      }, duration);
      
      return () => {
        clearTimeout(timer);
      };
    }
  }, [id, duration, onClose]);
  
  // 토스트 클래스 생성
  const toastClasses = [
    'toast',
    `toast--${type}`,
    className,
  ].filter(Boolean).join(' ');
  
  return (
    <div className={toastClasses} role="alert">
      <div className="toast-icon">{getIcon()}</div>
      
      <div className="toast-content">
        {title && <div className="toast-title">{title}</div>}
        <div className="toast-message">{message}</div>
      </div>
      
      <button
        type="button"
        className="toast-close"
        onClick={() => onClose(id)}
        aria-label="닫기"
      >
        &times;
      </button>
    </div>
  );
};

export default Toast;
