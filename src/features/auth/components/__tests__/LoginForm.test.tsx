/**
 * 로그인 폼 통합 테스트
 */

import React from 'react';
import { screen, waitFor, fireEvent } from '@testing-library/react';
import { renderWithProviders } from '../../../../test/test-utils';
import LoginForm from '../LoginForm/LoginForm';
import { loginUser } from '../../store/authSlice';

// Redux 액션 모의
jest.mock('../../store/authSlice', () => ({
  ...jest.requireActual('../../store/authSlice'),
  loginUser: jest.fn(),
}));

describe('LoginForm Integration Test', () => {
  const mockLoginUser = loginUser as jest.Mock;
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render login form correctly', () => {
    renderWithProviders(<LoginForm />);
    
    // 폼 요소 확인
    expect(screen.getByRole('heading', { name: /로그인/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/이메일/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/비밀번호/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /로그인/i })).toBeInTheDocument();
    expect(screen.getByText(/비밀번호를 잊으셨나요?/i)).toBeInTheDocument();
    expect(screen.getByText(/계정이 없으신가요?/i)).toBeInTheDocument();
    expect(screen.getByText(/회원가입/i)).toBeInTheDocument();
  });

  it('should show validation errors for empty fields', async () => {
    renderWithProviders(<LoginForm />);
    
    // 빈 폼 제출
    fireEvent.click(screen.getByRole('button', { name: /로그인/i }));
    
    // 유효성 검사 오류 확인
    await waitFor(() => {
      expect(screen.getByText(/이메일을 입력해주세요/i)).toBeInTheDocument();
      expect(screen.getByText(/비밀번호를 입력해주세요/i)).toBeInTheDocument();
    });
    
    // 로그인 액션이 호출되지 않았는지 확인
    expect(mockLoginUser).not.toHaveBeenCalled();
  });

  it('should show validation error for invalid email', async () => {
    renderWithProviders(<LoginForm />);
    
    // 유효하지 않은 이메일 입력
    fireEvent.change(screen.getByLabelText(/이메일/i), { target: { value: 'invalid-email' } });
    fireEvent.change(screen.getByLabelText(/비밀번호/i), { target: { value: 'password123' } });
    
    // 폼 제출
    fireEvent.click(screen.getByRole('button', { name: /로그인/i }));
    
    // 유효성 검사 오류 확인
    await waitFor(() => {
      expect(screen.getByText(/유효한 이메일 주소를 입력해주세요/i)).toBeInTheDocument();
    });
    
    // 로그인 액션이 호출되지 않았는지 확인
    expect(mockLoginUser).not.toHaveBeenCalled();
  });

  it('should call loginUser action with correct credentials on form submission', async () => {
    // 성공적인 로그인 응답 모의
    mockLoginUser.mockResolvedValueOnce({
      payload: { user: { id: '1', email: 'test@example.com' }, token: 'test-token' },
    });
    
    renderWithProviders(<LoginForm />);
    
    // 유효한 자격 증명 입력
    fireEvent.change(screen.getByLabelText(/이메일/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/비밀번호/i), { target: { value: 'password123' } });
    
    // 폼 제출
    fireEvent.click(screen.getByRole('button', { name: /로그인/i }));
    
    // 로그인 액션이 올바른 자격 증명으로 호출되었는지 확인
    await waitFor(() => {
      expect(mockLoginUser).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });

  it('should show loading state during login process', async () => {
    // 지연된 로그인 응답 모의
    mockLoginUser.mockImplementationOnce(
      () => new Promise(resolve => setTimeout(() => resolve({ payload: {} }), 100))
    );
    
    renderWithProviders(<LoginForm />);
    
    // 유효한 자격 증명 입력
    fireEvent.change(screen.getByLabelText(/이메일/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/비밀번호/i), { target: { value: 'password123' } });
    
    // 폼 제출
    fireEvent.click(screen.getByRole('button', { name: /로그인/i }));
    
    // 로딩 상태 확인
    expect(screen.getByRole('button', { name: /로그인/i })).toHaveAttribute('disabled');
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    
    // 로딩 완료 대기
    await waitFor(() => {
      expect(mockLoginUser).toHaveBeenCalled();
    });
  });

  it('should show error message when login fails', async () => {
    // 실패한 로그인 응답 모의
    mockLoginUser.mockRejectedValueOnce({ message: '이메일 또는 비밀번호가 올바르지 않습니다.' });
    
    renderWithProviders(<LoginForm />);
    
    // 유효한 자격 증명 입력
    fireEvent.change(screen.getByLabelText(/이메일/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/비밀번호/i), { target: { value: 'wrong-password' } });
    
    // 폼 제출
    fireEvent.click(screen.getByRole('button', { name: /로그인/i }));
    
    // 오류 메시지 확인
    await waitFor(() => {
      expect(screen.getByText(/이메일 또는 비밀번호가 올바르지 않습니다/i)).toBeInTheDocument();
    });
  });

  it('should navigate to forgot password page when link is clicked', () => {
    renderWithProviders(<LoginForm />);
    
    // 비밀번호 찾기 링크 클릭
    fireEvent.click(screen.getByText(/비밀번호를 잊으셨나요?/i));
    
    // 페이지 이동 확인 (실제 라우팅은 테스트하지 않음)
    expect(window.location.pathname).toBe('/auth/forgot-password');
  });

  it('should navigate to register page when link is clicked', () => {
    renderWithProviders(<LoginForm />);
    
    // 회원가입 링크 클릭
    fireEvent.click(screen.getByText(/회원가입/i));
    
    // 페이지 이동 확인 (실제 라우팅은 테스트하지 않음)
    expect(window.location.pathname).toBe('/auth/register');
  });
});
