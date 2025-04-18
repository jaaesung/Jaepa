/**
 * 체크박스 컴포넌트
 * 
 * 사용자가 선택할 수 있는 체크박스 컴포넌트를 제공합니다.
 */

import React from 'react';
import './Checkbox.css';

export interface CheckboxProps {
  /**
   * 체크박스 ID
   */
  id: string;
  
  /**
   * 체크박스 라벨
   */
  label: string;
  
  /**
   * 체크 상태
   */
  checked: boolean;
  
  /**
   * 상태 변경 핸들러
   */
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  
  /**
   * 비활성화 여부
   */
  disabled?: boolean;
  
  /**
   * 추가 클래스명
   */
  className?: string;
  
  /**
   * 에러 메시지
   */
  error?: string;
}

/**
 * 체크박스 컴포넌트
 */
const Checkbox: React.FC<CheckboxProps> = ({
  id,
  label,
  checked,
  onChange,
  disabled = false,
  className = '',
  error,
}) => {
  const checkboxClasses = [
    'checkbox',
    disabled ? 'checkbox--disabled' : '',
    error ? 'checkbox--error' : '',
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={checkboxClasses}>
      <label className="checkbox-label" htmlFor={id}>
        <input
          type="checkbox"
          id={id}
          className="checkbox-input"
          checked={checked}
          onChange={onChange}
          disabled={disabled}
        />
        <span className="checkbox-custom"></span>
        <span className="checkbox-text">{label}</span>
      </label>
      {error && <div className="checkbox-error">{error}</div>}
    </div>
  );
};

export default Checkbox;
