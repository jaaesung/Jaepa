/**
 * 토스트 컨텍스트 모듈
 * 
 * 애플리케이션의 토스트 알림 관리를 위한 컨텍스트를 제공합니다.
 */

import React, { createContext, useContext, useState, useCallback } from 'react';
import { ToastContainer, ToastProps, ToastPosition, ToastType } from '../../components/ui';
import { v4 as uuidv4 } from 'uuid';

interface ToastOptions {
  /**
   * 토스트 타입
   */
  type?: ToastType;
  
  /**
   * 토스트 제목
   */
  title?: string;
  
  /**
   * 토스트 지속 시간 (밀리초)
   */
  duration?: number;
}

interface ToastContextType {
  /**
   * 토스트 추가
   */
  addToast: (message: string, options?: ToastOptions) => string;
  
  /**
   * 토스트 제거
   */
  removeToast: (id: string) => void;
  
  /**
   * 모든 토스트 제거
   */
  removeAllToasts: () => void;
  
  /**
   * 정보 토스트 추가
   */
  info: (message: string, options?: Omit<ToastOptions, 'type'>) => string;
  
  /**
   * 성공 토스트 추가
   */
  success: (message: string, options?: Omit<ToastOptions, 'type'>) => string;
  
  /**
   * 경고 토스트 추가
   */
  warning: (message: string, options?: Omit<ToastOptions, 'type'>) => string;
  
  /**
   * 에러 토스트 추가
   */
  error: (message: string, options?: Omit<ToastOptions, 'type'>) => string;
}

// 토스트 컨텍스트 생성
const ToastContext = createContext<ToastContextType | undefined>(undefined);

interface ToastProviderProps {
  /**
   * 자식 컴포넌트
   */
  children: React.ReactNode;
  
  /**
   * 토스트 위치
   */
  position?: ToastPosition;
  
  /**
   * 기본 지속 시간 (밀리초)
   */
  defaultDuration?: number;
  
  /**
   * 최대 토스트 개수
   */
  maxToasts?: number;
}

/**
 * 토스트 프로바이더 컴포넌트
 */
export const ToastProvider: React.FC<ToastProviderProps> = ({
  children,
  position = 'top-right',
  defaultDuration = 5000,
  maxToasts = 5,
}) => {
  const [toasts, setToasts] = useState<Omit<ToastProps, 'onClose'>[]>([]);
  
  // 토스트 추가
  const addToast = useCallback(
    (message: string, options?: ToastOptions): string => {
      const id = uuidv4();
      
      setToasts(prevToasts => {
        // 최대 토스트 개수 제한
        const updatedToasts = [...prevToasts];
        
        if (updatedToasts.length >= maxToasts) {
          updatedToasts.shift();
        }
        
        return [
          ...updatedToasts,
          {
            id,
            message,
            type: options?.type || 'info',
            title: options?.title,
            duration: options?.duration || defaultDuration,
          },
        ];
      });
      
      return id;
    },
    [defaultDuration, maxToasts]
  );
  
  // 토스트 제거
  const removeToast = useCallback((id: string) => {
    setToasts(prevToasts => prevToasts.filter(toast => toast.id !== id));
  }, []);
  
  // 모든 토스트 제거
  const removeAllToasts = useCallback(() => {
    setToasts([]);
  }, []);
  
  // 정보 토스트 추가
  const info = useCallback(
    (message: string, options?: Omit<ToastOptions, 'type'>): string => {
      return addToast(message, { ...options, type: 'info' });
    },
    [addToast]
  );
  
  // 성공 토스트 추가
  const success = useCallback(
    (message: string, options?: Omit<ToastOptions, 'type'>): string => {
      return addToast(message, { ...options, type: 'success' });
    },
    [addToast]
  );
  
  // 경고 토스트 추가
  const warning = useCallback(
    (message: string, options?: Omit<ToastOptions, 'type'>): string => {
      return addToast(message, { ...options, type: 'warning' });
    },
    [addToast]
  );
  
  // 에러 토스트 추가
  const error = useCallback(
    (message: string, options?: Omit<ToastOptions, 'type'>): string => {
      return addToast(message, { ...options, type: 'error' });
    },
    [addToast]
  );
  
  const contextValue = {
    addToast,
    removeToast,
    removeAllToasts,
    info,
    success,
    warning,
    error,
  };
  
  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      <ToastContainer toasts={toasts} onClose={removeToast} position={position} />
    </ToastContext.Provider>
  );
};

/**
 * 토스트 컨텍스트 훅
 */
export const useToast = (): ToastContextType => {
  const context = useContext(ToastContext);
  
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  
  return context;
};

export default ToastContext;
