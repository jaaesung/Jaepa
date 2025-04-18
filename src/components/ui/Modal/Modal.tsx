/**
 * 모달 컴포넌트
 * 
 * 사용자에게 중요한 정보를 표시하거나 작업을 수행하도록 요청하는 모달 컴포넌트를 제공합니다.
 */

import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import './Modal.css';

export interface ModalProps {
  /**
   * 모달 제목
   */
  title?: string;
  
  /**
   * 모달 내용
   */
  children: React.ReactNode;
  
  /**
   * 모달 표시 여부
   */
  isOpen: boolean;
  
  /**
   * 모달 닫기 핸들러
   */
  onClose: () => void;
  
  /**
   * 모달 크기
   */
  size?: 'small' | 'medium' | 'large' | 'full';
  
  /**
   * 모달 바깥 영역 클릭 시 닫기 여부
   */
  closeOnOutsideClick?: boolean;
  
  /**
   * ESC 키 누를 시 닫기 여부
   */
  closeOnEsc?: boolean;
  
  /**
   * 추가 클래스명
   */
  className?: string;
  
  /**
   * 모달 푸터
   */
  footer?: React.ReactNode;
  
  /**
   * 모달 헤더 숨김 여부
   */
  hideHeader?: boolean;
}

/**
 * 모달 컴포넌트
 */
const Modal: React.FC<ModalProps> = ({
  title,
  children,
  isOpen,
  onClose,
  size = 'medium',
  closeOnOutsideClick = true,
  closeOnEsc = true,
  className = '',
  footer,
  hideHeader = false,
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  
  // ESC 키 이벤트 핸들러
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (closeOnEsc && event.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [closeOnEsc, isOpen, onClose]);
  
  // 모달 열릴 때 스크롤 방지
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);
  
  // 모달 바깥 영역 클릭 핸들러
  const handleOutsideClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (closeOnOutsideClick && modalRef.current && !modalRef.current.contains(event.target as Node)) {
      onClose();
    }
  };
  
  // 모달이 닫혀있으면 렌더링하지 않음
  if (!isOpen) {
    return null;
  }
  
  // 모달 클래스 생성
  const modalClasses = [
    'modal-content',
    `modal-${size}`,
    className,
  ].filter(Boolean).join(' ');
  
  // 모달 포털 생성
  return createPortal(
    <div className="modal-overlay" onClick={handleOutsideClick}>
      <div className={modalClasses} ref={modalRef}>
        {!hideHeader && (
          <div className="modal-header">
            {title && <h2 className="modal-title">{title}</h2>}
            <button
              type="button"
              className="modal-close"
              onClick={onClose}
              aria-label="닫기"
            >
              &times;
            </button>
          </div>
        )}
        
        <div className="modal-body">{children}</div>
        
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>,
    document.body
  );
};

export default Modal;
