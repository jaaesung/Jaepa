/**
 * 로딩 스피너 컴포넌트
 * 
 * 로딩 상태를 표시하는 스피너 컴포넌트를 제공합니다.
 */

import React from 'react';
import './LoadingSpinner.css';

export type LoadingSpinnerSize = 'small' | 'medium' | 'large';
export type LoadingSpinnerColor = 'primary' | 'secondary' | 'white';

interface LoadingSpinnerProps {
  /**
   * 스피너 크기
   */
  size?: LoadingSpinnerSize;
  
  /**
   * 스피너 색상
   */
  color?: LoadingSpinnerColor;
  
  /**
   * 추가 클래스명
   */
  className?: string;
  
  /**
   * 로딩 텍스트
   */
  text?: string;
}

/**
 * 로딩 스피너 컴포넌트
 */
const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  color = 'primary',
  className = '',
  text,
}) => {
  const spinnerClasses = [
    'loading-spinner',
    `loading-spinner--${size}`,
    `loading-spinner--${color}`,
    className,
  ].join(' ');

  return (
    <div className="loading-spinner-container">
      <div className={spinnerClasses}>
        <div className="loading-spinner-circle"></div>
      </div>
      {text && <p className="loading-spinner-text">{text}</p>}
    </div>
  );
};

export default LoadingSpinner;
