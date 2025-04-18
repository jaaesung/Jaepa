/**
 * 인증 관련 타입 모듈
 *
 * 인증 관련 타입 정의를 제공합니다.
 */

// 로그인 요청
export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

// 회원가입 요청
export interface RegisterRequest {
  username: string;
  name: string;
  email: string;
  password: string;
}

// 프로필 업데이트 요청
export interface UpdateProfileRequest {
  name?: string;
  email?: string;
  username?: string;
}

// 인증 응답
export interface AuthResponse {
  isAuthenticated: boolean;
  user: User | null;
  accessToken: string;
  refreshToken: string;
}

// 사용자 정보
export interface User {
  id: string;
  username: string;
  name: string;
  email: string;
  role: string;
  createdAt: string;
  updatedAt: string;
}

// 인증 상태
export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

// 비밀번호 변경 요청
export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
}

// 비밀번호 찾기 요청
export interface ForgotPasswordRequest {
  email: string;
}

// 비밀번호 재설정 요청
export interface ResetPasswordRequest {
  token: string;
  newPassword: string;
}
