/**
 * 입력 컴포넌트 테스트
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Input, { InputProps } from '../Input';

describe('Input Component', () => {
  const defaultProps: InputProps = {
    id: 'test-input',
    name: 'test',
    value: '',
    onChange: jest.fn(),
  };

  const renderInput = (props: Partial<InputProps> = {}) => {
    return render(<Input {...defaultProps} {...props} />);
  };

  it('should render correctly with default props', () => {
    renderInput();
    const input = screen.getByRole('textbox');
    
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('id', 'test-input');
    expect(input).toHaveAttribute('name', 'test');
    expect(input).toHaveValue('');
    expect(input).not.toBeDisabled();
    expect(input).not.toHaveAttribute('required');
  });

  it('should render with label when provided', () => {
    renderInput({ label: 'Test Label' });
    
    expect(screen.getByText('Test Label')).toBeInTheDocument();
    expect(screen.getByLabelText('Test Label')).toBeInTheDocument();
  });

  it('should show required indicator when required prop is true', () => {
    renderInput({ label: 'Test Label', required: true });
    
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('should render with placeholder', () => {
    renderInput({ placeholder: 'Test Placeholder' });
    
    expect(screen.getByPlaceholderText('Test Placeholder')).toBeInTheDocument();
  });

  it('should be disabled when disabled prop is true', () => {
    renderInput({ disabled: true });
    
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('should render with error message when error prop is provided', () => {
    renderInput({ error: 'Test Error Message' });
    
    expect(screen.getByText('Test Error Message')).toBeInTheDocument();
    expect(screen.getByRole('textbox').parentElement).toHaveClass('input--error');
  });

  it('should render with helper text when helperText prop is provided', () => {
    renderInput({ helperText: 'Test Helper Text' });
    
    expect(screen.getByText('Test Helper Text')).toBeInTheDocument();
  });

  it('should apply fullWidth class when fullWidth prop is true', () => {
    renderInput({ fullWidth: true });
    
    expect(screen.getByRole('textbox').parentElement).toHaveClass('input--full-width');
  });

  it('should call onChange handler when input value changes', () => {
    renderInput();
    const input = screen.getByRole('textbox');
    
    fireEvent.change(input, { target: { value: 'test value' } });
    
    expect(defaultProps.onChange).toHaveBeenCalledTimes(1);
    expect(defaultProps.onChange).toHaveBeenCalledWith(expect.any(Object));
  });

  it('should render with different types', () => {
    const { rerender } = renderInput({ type: 'text' });
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'text');
    
    rerender(<Input {...defaultProps} type="password" />);
    expect(screen.getByLabelText(/password/i)).toHaveAttribute('type', 'password');
    
    rerender(<Input {...defaultProps} type="email" />);
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'email');
    
    rerender(<Input {...defaultProps} type="number" />);
    expect(screen.getByRole('spinbutton')).toHaveAttribute('type', 'number');
  });

  it('should render with startIcon', () => {
    renderInput({ startIcon: <span data-testid="start-icon">Start</span> });
    
    expect(screen.getByTestId('start-icon')).toBeInTheDocument();
    expect(screen.getByRole('textbox').parentElement).toHaveClass('input--with-start-icon');
  });

  it('should render with endIcon', () => {
    renderInput({ endIcon: <span data-testid="end-icon">End</span> });
    
    expect(screen.getByTestId('end-icon')).toBeInTheDocument();
    expect(screen.getByRole('textbox').parentElement).toHaveClass('input--with-end-icon');
  });

  it('should call onFocus handler when input is focused', () => {
    const onFocus = jest.fn();
    renderInput({ onFocus });
    
    fireEvent.focus(screen.getByRole('textbox'));
    
    expect(onFocus).toHaveBeenCalledTimes(1);
  });

  it('should call onBlur handler when input loses focus', () => {
    const onBlur = jest.fn();
    renderInput({ onBlur });
    
    fireEvent.blur(screen.getByRole('textbox'));
    
    expect(onBlur).toHaveBeenCalledTimes(1);
  });
});
