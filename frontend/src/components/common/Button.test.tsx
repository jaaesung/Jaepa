import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Button from './Button';

describe('Button Component', () => {
  test('renders button with text', () => {
    render(<Button text="Click me" />);
    const buttonElement = screen.getByTestId('button');
    expect(buttonElement).toBeInTheDocument();
    expect(buttonElement).toHaveTextContent('Click me');
  });

  test('calls onClick handler when clicked', () => {
    const handleClick = jest.fn();
    render(<Button text="Click me" onClick={handleClick} />);
    const buttonElement = screen.getByTestId('button');
    
    fireEvent.click(buttonElement);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('applies primary variant styles by default', () => {
    render(<Button text="Click me" />);
    const buttonElement = screen.getByTestId('button');
    expect(buttonElement).toHaveClass('bg-blue-600');
  });

  test('applies secondary variant styles when specified', () => {
    render(<Button text="Click me" variant="secondary" />);
    const buttonElement = screen.getByTestId('button');
    expect(buttonElement).toHaveClass('bg-gray-200');
  });

  test('applies danger variant styles when specified', () => {
    render(<Button text="Click me" variant="danger" />);
    const buttonElement = screen.getByTestId('button');
    expect(buttonElement).toHaveClass('bg-red-600');
  });

  test('applies disabled state when specified', () => {
    render(<Button text="Click me" disabled />);
    const buttonElement = screen.getByTestId('button');
    expect(buttonElement).toBeDisabled();
    expect(buttonElement).toHaveClass('opacity-50');
    expect(buttonElement).toHaveClass('cursor-not-allowed');
  });

  test('applies full width style when specified', () => {
    render(<Button text="Click me" fullWidth />);
    const buttonElement = screen.getByTestId('button');
    expect(buttonElement).toHaveClass('w-full');
  });
});
