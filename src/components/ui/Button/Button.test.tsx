/**
 * Button 컴포넌트 테스트
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Button from './Button';

describe('Button 컴포넌트', () => {
  // 기본 렌더링 테스트
  test('기본 버튼이 올바르게 렌더링되어야 함', () => {
    render(<Button>테스트 버튼</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('jaepa-button');
    expect(button).toHaveClass('jaepa-button--primary');
    expect(button).toHaveClass('jaepa-button--medium');
  });

  // 변형 테스트
  test('secondary 변형이 올바르게 적용되어야 함', () => {
    render(<Button variant="secondary">Secondary 버튼</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('jaepa-button--secondary');
  });

  test('outline 변형이 올바르게 적용되어야 함', () => {
    render(<Button variant="outline">Outline 버튼</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('jaepa-button--outline');
  });

  test('text 변형이 올바르게 적용되어야 함', () => {
    render(<Button variant="text">Text 버튼</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('jaepa-button--text');
  });

  // 크기 테스트
  test('small 크기가 올바르게 적용되어야 함', () => {
    render(<Button size="small">Small 버튼</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('jaepa-button--small');
  });

  test('large 크기가 올바르게 적용되어야 함', () => {
    render(<Button size="large">Large 버튼</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('jaepa-button--large');
  });

  // 전체 너비 테스트
  test('fullWidth 속성이 올바르게 적용되어야 함', () => {
    render(<Button fullWidth>전체 너비 버튼</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('jaepa-button--full-width');
  });

  // 비활성화 테스트
  test('disabled 속성이 올바르게 적용되어야 함', () => {
    render(<Button disabled>비활성화 버튼</Button>);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  // 로딩 테스트
  test('isLoading 속성이 올바르게 적용되어야 함', () => {
    render(<Button isLoading>로딩 버튼</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('jaepa-button--loading');
    expect(button).toBeDisabled();
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  // 클릭 이벤트 테스트
  test('onClick 이벤트가 올바르게 호출되어야 함', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>클릭 버튼</Button>);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  // 비활성화 상태에서 클릭 이벤트 테스트
  test('disabled 상태에서는 onClick 이벤트가 호출되지 않아야 함', () => {
    const handleClick = jest.fn();
    render(
      <Button onClick={handleClick} disabled>
        비활성화 클릭 버튼
      </Button>
    );
    const button = screen.getByRole('button');
    fireEvent.click(button);
    expect(handleClick).not.toHaveBeenCalled();
  });

  // 로딩 상태에서 클릭 이벤트 테스트
  test('isLoading 상태에서는 onClick 이벤트가 호출되지 않아야 함', () => {
    const handleClick = jest.fn();
    render(
      <Button onClick={handleClick} isLoading>
        로딩 클릭 버튼
      </Button>
    );
    const button = screen.getByRole('button');
    fireEvent.click(button);
    expect(handleClick).not.toHaveBeenCalled();
  });

  // 아이콘 테스트
  test('leftIcon이 올바르게 렌더링되어야 함', () => {
    render(<Button leftIcon={<span data-testid="left-icon" />}>아이콘 버튼</Button>);
    expect(screen.getByTestId('left-icon')).toBeInTheDocument();
    expect(screen.getByTestId('left-icon').parentElement).toHaveClass('button-icon--left');
  });

  test('rightIcon이 올바르게 렌더링되어야 함', () => {
    render(<Button rightIcon={<span data-testid="right-icon" />}>아이콘 버튼</Button>);
    expect(screen.getByTestId('right-icon')).toBeInTheDocument();
    expect(screen.getByTestId('right-icon').parentElement).toHaveClass('button-icon--right');
  });

  // 로딩 상태에서 아이콘 테스트
  test('isLoading 상태에서는 아이콘이 렌더링되지 않아야 함', () => {
    render(
      <Button
        isLoading
        leftIcon={<span data-testid="left-icon" />}
        rightIcon={<span data-testid="right-icon" />}
      >
        로딩 아이콘 버튼
      </Button>
    );
    expect(screen.queryByTestId('left-icon')).not.toBeInTheDocument();
    expect(screen.queryByTestId('right-icon')).not.toBeInTheDocument();
  });

  // 커스텀 클래스 테스트
  test('className 속성이 올바르게 적용되어야 함', () => {
    render(<Button className="custom-class">커스텀 클래스 버튼</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('custom-class');
  });
});
