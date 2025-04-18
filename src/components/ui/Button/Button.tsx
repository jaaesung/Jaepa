/**
 * 버튼 컴포넌트
 *
 * 다양한 스타일과 크기의 버튼을 제공합니다.
 */

import React, { ButtonHTMLAttributes } from 'react';
import './Button.css';

export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'text' | 'danger';
export type ButtonSize = 'small' | 'medium' | 'large';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  fullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

/**
 * 버튼 컴포넌트
 */
const Button: React.FC<ButtonProps> = React.memo(({
  children,
  variant = 'primary',
  size = 'medium',
  isLoading = false,
  fullWidth = false,
  leftIcon,
  rightIcon,
  className = '',
  disabled,
  ...rest
}) => {
  // 클래스 이름 계산을 위한 변수들
  const baseClass = 'jaepa-button';
  const variantClass = `${baseClass}--${variant}`;
  const sizeClass = `${baseClass}--${size}`;
  const fullWidthClass = fullWidth ? `${baseClass}--full-width` : '';
  const loadingClass = isLoading ? `${baseClass}--loading` : '';

  // useMemo를 사용하여 클래스 이름 계산 최적화
  const combinedClassName = React.useMemo(() => {
    return [
      baseClass,
      variantClass,
      sizeClass,
      fullWidthClass,
      loadingClass,
      className
    ].filter(Boolean).join(' ');
  }, [baseClass, variantClass, sizeClass, fullWidthClass, loadingClass, className]);

  // 버튼 렌더링
  return (
    <button
      className={combinedClassName}
      disabled={disabled || isLoading}
      {...rest}
    >
      {isLoading && <span className="button-spinner" data-testid="loading-spinner"></span>}
      {!isLoading && leftIcon && <span className="button-icon button-icon--left">{leftIcon}</span>}
      <span className="button-text">{children}</span>
      {!isLoading && rightIcon && <span className="button-icon button-icon--right">{rightIcon}</span>}
    </button>
  );
});

export default Button;
