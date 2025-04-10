import api from './api';
import { User } from '../types';

interface LoginResponse {
  token: string;
  refreshToken?: string;
  user: User;
}

interface RegisterResponse {
  token: string;
  refreshToken?: string;
  user: User;
}

interface AuthStatusResponse {
  isAuthenticated: boolean;
  user: User | null;
}

interface ProfileUpdateData {
  username?: string;
  email?: string;
  role?: string;
  [key: string]: any;
}

interface PasswordChangeResponse {
  success: boolean;
  message: string;
}

interface PasswordResetRequestResponse {
  success: boolean;
  message: string;
}

interface PasswordResetResponse {
  success: boolean;
  message: string;
}

/**
 * 사용자 로그인
 * @param email - 사용자 이메일
 * @param password - 사용자 비밀번호
 * @returns 로그인 응답 데이터
 */
const login = async (email: string, password: string): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>('/auth/login', { email, password });
  if (response.data.token) {
    localStorage.setItem('token', response.data.token);
    if (response.data.refreshToken) {
      localStorage.setItem('refreshToken', response.data.refreshToken);
    }
  }
  return response.data;
};

/**
 * 사용자 회원가입
 * @param username - 사용자 이름
 * @param email - 사용자 이메일
 * @param password - 사용자 비밀번호
 * @returns 회원가입 응답 데이터
 */
const register = async (username: string, email: string, password: string): Promise<RegisterResponse> => {
  const response = await api.post<RegisterResponse>('/auth/register', { username, email, password });
  if (response.data.token) {
    localStorage.setItem('token', response.data.token);
    if (response.data.refreshToken) {
      localStorage.setItem('refreshToken', response.data.refreshToken);
    }
  }
  return response.data;
};

/**
 * 사용자 로그아웃
 */
const logout = (): void => {
  localStorage.removeItem('token');
  localStorage.removeItem('refreshToken');
};

/**
 * 인증 상태 확인
 * @returns 인증 상태 데이터
 */
const checkAuthStatus = async (): Promise<AuthStatusResponse> => {
  const token = localStorage.getItem('token');
  if (!token) {
    return { isAuthenticated: false, user: null };
  }
  
  try {
    const response = await api.get<User>('/auth/user');
    return { isAuthenticated: true, user: response.data };
  } catch (error) {
    return { isAuthenticated: false, user: null };
  }
};

/**
 * 사용자 프로필 업데이트
 * @param userData - 업데이트할 사용자 데이터
 * @returns 업데이트된 사용자 데이터
 */
const updateProfile = async (userData: ProfileUpdateData): Promise<User> => {
  const response = await api.put<User>('/auth/profile', userData);
  return response.data;
};

/**
 * 비밀번호 변경
 * @param currentPassword - 현재 비밀번호
 * @param newPassword - 새 비밀번호
 * @returns 비밀번호 변경 응답 데이터
 */
const changePassword = async (currentPassword: string, newPassword: string): Promise<PasswordChangeResponse> => {
  const response = await api.post<PasswordChangeResponse>('/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
  });
  return response.data;
};

/**
 * 비밀번호 재설정 요청
 * @param email - 사용자 이메일
 * @returns 비밀번호 재설정 요청 응답 데이터
 */
const requestPasswordReset = async (email: string): Promise<PasswordResetRequestResponse> => {
  const response = await api.post<PasswordResetRequestResponse>('/auth/reset-password-request', { email });
  return response.data;
};

/**
 * 비밀번호 재설정
 * @param token - 비밀번호 재설정 토큰
 * @param newPassword - 새 비밀번호
 * @returns 비밀번호 재설정 응답 데이터
 */
const resetPassword = async (token: string, newPassword: string): Promise<PasswordResetResponse> => {
  const response = await api.post<PasswordResetResponse>('/auth/reset-password', {
    token,
    new_password: newPassword,
  });
  return response.data;
};

const authService = {
  login,
  register,
  logout,
  checkAuthStatus,
  updateProfile,
  changePassword,
  requestPasswordReset,
  resetPassword,
};

export default authService;