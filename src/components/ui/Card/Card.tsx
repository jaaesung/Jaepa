/**
 * 카드 컴포넌트
 *
 * 다양한 스타일과 기능의 카드를 제공합니다.
 */

import React, { HTMLAttributes } from 'react';
import './Card.css';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'elevated' | 'outlined' | 'filled';
  padding?: 'none' | 'small' | 'medium' | 'large';
  radius?: 'none' | 'small' | 'medium' | 'large';
  shadow?: 'none' | 'small' | 'medium' | 'large';
  bordered?: boolean;
  fullWidth?: boolean;
}

/**
 * 카드 컴포넌트
 */
const Card: React.FC<CardProps> = React.memo(({
  children,
  variant = 'elevated',
  padding = 'medium',
  radius = 'medium',
  shadow = 'medium',
  bordered = false,
  fullWidth = false,
  className = '',
  ...rest
}) => {
  // 클래스 이름 계산을 위한 변수들
  const baseClass = 'jaepa-card';
  const variantClass = `${baseClass}--${variant}`;
  const paddingClass = padding !== 'none' ? `${baseClass}--padding-${padding}` : '';
  const radiusClass = radius !== 'none' ? `${baseClass}--radius-${radius}` : '';
  const shadowClass = shadow !== 'none' ? `${baseClass}--shadow-${shadow}` : '';
  const borderedClass = bordered ? `${baseClass}--bordered` : '';
  const fullWidthClass = fullWidth ? `${baseClass}--full-width` : '';

  // useMemo를 사용하여 클래스 이름 계산 최적화
  const finalClassName = React.useMemo(() => {
    return [
      baseClass,
      variantClass,
      paddingClass,
      radiusClass,
      shadowClass,
      borderedClass,
      fullWidthClass,
      className
    ].filter(Boolean).join(' ');
  }, [baseClass, variantClass, paddingClass, radiusClass, shadowClass, borderedClass, fullWidthClass, className]);

  return (
    <div className={finalClassName} {...rest}>
      {children}
    </div>
  );
});

export default Card;
