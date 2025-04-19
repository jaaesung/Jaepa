/**
 * 입력 필드 컴포넌트
 *
 * 다양한 스타일과 기능의 입력 필드를 제공합니다.
 */

import React, { InputHTMLAttributes, forwardRef } from 'react';
import './Input.css';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
  variant?: 'outlined' | 'filled' | 'standard';
  /**
   * 스크린 리더에서 읽을 아리아 레이블
   */
  ariaLabel?: string;
  /**
   * 스크린 리더에서 읽을 아리아 설명
   */
  ariaDescription?: string;
}

/**
 * 입력 필드 컴포넌트
 */
const Input = React.memo(
  forwardRef<HTMLInputElement, InputProps>(
    (
      {
        label,
        error,
        helperText,
        leftIcon,
        rightIcon,
        fullWidth = false,
        variant = 'outlined',
        className = '',
        id,
        ariaLabel,
        ariaDescription,
        ...rest
      },
      ref
    ) => {
      // 고유 ID 생성 - 컴포넌트가 리렌더링되어도 동일한 ID 유지
      const inputId = React.useMemo(() => {
        return id || `input-${Math.random().toString(36).substring(2, 9)}`;
      }, [id]);

      // 클래스 이름 계산을 위한 변수들
      const baseClass = 'jaepa-input';
      const containerClass = `${baseClass}-container`;
      const variantClass = `${baseClass}--${variant}`;
      const fullWidthClass = fullWidth ? `${baseClass}--full-width` : '';
      const errorClass = error ? `${baseClass}--error` : '';
      const hasIconClass = leftIcon || rightIcon ? `${baseClass}--has-icon` : '';

      // 컨테이너 클래스 이름 계산 최적화
      const combinedContainerClassName = React.useMemo(() => {
        return [containerClass, fullWidthClass, className].filter(Boolean).join(' ');
      }, [containerClass, fullWidthClass, className]);

      // 입력 필드 클래스 이름 계산 최적화
      const combinedInputClassName = React.useMemo(() => {
        return [baseClass, variantClass, errorClass, hasIconClass].filter(Boolean).join(' ');
      }, [baseClass, variantClass, errorClass, hasIconClass]);

      return (
        <div className={combinedContainerClassName}>
          {label && (
            <label htmlFor={inputId} className={`${baseClass}-label`}>
              {label}
            </label>
          )}

          <div className={`${baseClass}-wrapper`}>
            {leftIcon && (
              <div className={`${baseClass}-icon ${baseClass}-icon--left`}>{leftIcon}</div>
            )}

            <input
              id={inputId}
              ref={ref}
              className={combinedInputClassName}
              aria-invalid={!!error}
              aria-label={ariaLabel}
              aria-describedby={helperText || error ? `${inputId}-description` : undefined}
              {...rest}
            />

            {rightIcon && (
              <div className={`${baseClass}-icon ${baseClass}-icon--right`}>{rightIcon}</div>
            )}
          </div>

          {(error || helperText) && (
            <div
              id={`${inputId}-description`}
              className={`${baseClass}-text ${error ? `${baseClass}-error-text` : `${baseClass}-helper-text`}`}
              aria-live={error ? 'assertive' : 'polite'}
            >
              {error || helperText}
            </div>
          )}
        </div>
      );
    }
  )
);

Input.displayName = 'Input';

export default Input;
