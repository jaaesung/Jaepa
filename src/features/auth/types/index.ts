/**
 * 인증 관련 타입 정의
 */

// 사용자 정보 타입
export interface User {
  id: string;
  email: string;
  username: string;
  fullName?: string;
  avatar?: string;
  role: string;
  createdAt: string;
  updatedAt: string;
}

// 인증 상태 타입
export interface AuthState {
  user: User | null;
  accessToken?: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// 로그인 요청 타입
export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

// 회원가입 요청 타입
export interface RegisterRequest {
  email: string;
  password: string;
  username: string;
  fullName?: string;
}

// 비밀번호 변경 요청 타입
export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

// 프로필 업데이트 요청 타입
export interface UpdateProfileRequest {
  username?: string;
  fullName?: string;
  name?: string; // 레거시 코드와의 호환성을 위해 추가
  email?: string; // 레거시 코드와의 호환성을 위해 추가
  avatar?: string;
}

// 인증 응답 타입
export interface AuthResponse {
  user: User;
  accessToken?: string;
  isAuthenticated: boolean;
}

// 비밀번호 찾기 요청 타입
export interface ForgotPasswordRequest {
  email: string;
}

// 비밀번호 재설정 요청 타입
export interface ResetPasswordRequest {
  token: string;
  password: string;
  confirmPassword: string;
}
