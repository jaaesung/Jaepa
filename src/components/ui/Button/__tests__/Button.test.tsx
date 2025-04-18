/**
 * 버튼 컴포넌트 테스트
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Button, { ButtonProps } from '../Button';

describe('Button Component', () => {
  const defaultProps: ButtonProps = {
    children: 'Test Button',
    onClick: jest.fn(),
  };

  const renderButton = (props: Partial<ButtonProps> = {}) => {
    return render(<Button {...defaultProps} {...props} />);
  };

  it('should render correctly with default props', () => {
    renderButton();
    const button = screen.getByRole('button', { name: /test button/i });
    
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('button');
    expect(button).toHaveClass('button--primary');
    expect(button).toHaveClass('button--medium');
    expect(button).not.toHaveClass('button--disabled');
    expect(button).not.toHaveAttribute('disabled');
  });

  it('should render with different variants', () => {
    const { rerender } = renderButton({ variant: 'primary' });
    expect(screen.getByRole('button')).toHaveClass('button--primary');
    
    rerender(<Button {...defaultProps} variant="secondary" />);
    expect(screen.getByRole('button')).toHaveClass('button--secondary');
    
    rerender(<Button {...defaultProps} variant="outline" />);
    expect(screen.getByRole('button')).toHaveClass('button--outline');
    
    rerender(<Button {...defaultProps} variant="text" />);
    expect(screen.getByRole('button')).toHaveClass('button--text');
    
    rerender(<Button {...defaultProps} variant="danger" />);
    expect(screen.getByRole('button')).toHaveClass('button--danger');
  });

  it('should render with different sizes', () => {
    const { rerender } = renderButton({ size: 'small' });
    expect(screen.getByRole('button')).toHaveClass('button--small');
    
    rerender(<Button {...defaultProps} size="medium" />);
    expect(screen.getByRole('button')).toHaveClass('button--medium');
    
    rerender(<Button {...defaultProps} size="large" />);
    expect(screen.getByRole('button')).toHaveClass('button--large');
  });

  it('should apply fullWidth class when fullWidth prop is true', () => {
    renderButton({ fullWidth: true });
    expect(screen.getByRole('button')).toHaveClass('button--full-width');
  });

  it('should be disabled when disabled prop is true', () => {
    renderButton({ disabled: true });
    const button = screen.getByRole('button');
    
    expect(button).toHaveClass('button--disabled');
    expect(button).toBeDisabled();
  });

  it('should call onClick handler when clicked', () => {
    renderButton();
    fireEvent.click(screen.getByRole('button'));
    
    expect(defaultProps.onClick).toHaveBeenCalledTimes(1);
  });

  it('should not call onClick handler when disabled', () => {
    renderButton({ disabled: true });
    fireEvent.click(screen.getByRole('button'));
    
    expect(defaultProps.onClick).not.toHaveBeenCalled();
  });

  it('should render with custom className', () => {
    renderButton({ className: 'custom-class' });
    expect(screen.getByRole('button')).toHaveClass('custom-class');
  });

  it('should render with custom type', () => {
    renderButton({ type: 'submit' });
    expect(screen.getByRole('button')).toHaveAttribute('type', 'submit');
  });

  it('should render with startIcon', () => {
    renderButton({ startIcon: <span data-testid="start-icon">Start</span> });
    expect(screen.getByTestId('start-icon')).toBeInTheDocument();
  });

  it('should render with endIcon', () => {
    renderButton({ endIcon: <span data-testid="end-icon">End</span> });
    expect(screen.getByTestId('end-icon')).toBeInTheDocument();
  });

  it('should render with loading state', () => {
    renderButton({ loading: true });
    
    expect(screen.getByRole('button')).toHaveClass('button--loading');
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
