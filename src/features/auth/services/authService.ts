/**
 * 인증 서비스 모듈
 * 
 * 인증 관련 API 호출 및 로직을 처리하는 서비스를 제공합니다.
 */

import api from '../../../services/api';
import { localStorageService } from '../../../services/storage';
import { storageConstants } from '../../../core/constants';
import { 
  User, 
  LoginRequest, 
  RegisterRequest, 
  UpdateProfileRequest,
  ChangePasswordRequest 
} from '../types';

const AUTH_API_PATH = '/auth';

// 인증 서비스
const authService = {
  /**
   * 로그인
   */
  login: async (email: string, password: string): Promise<{ user: User; accessToken: string }> => {
    const response = await api.post(`${AUTH_API_PATH}/login`, { email, password });
    
    // 토큰과 사용자 정보 저장
    if (response.accessToken) {
      localStorageService.setItem(storageConstants.TOKEN, response.accessToken);
      localStorageService.setItem(storageConstants.USER, response.user);
    }
    
    return response;
  },

  /**
   * 회원가입
   */
  register: async (data: RegisterRequest): Promise<{ user: User; accessToken: string }> => {
    const response = await api.post(`${AUTH_API_PATH}/register`, data);
    
    // 토큰과 사용자 정보 저장
    if (response.accessToken) {
      localStorageService.setItem(storageConstants.TOKEN, response.accessToken);
      localStorageService.setItem(storageConstants.USER, response.user);
    }
    
    return response;
  },

  /**
   * 로그아웃
   */
  logout: (): void => {
    // 토큰과 사용자 정보 삭제
    localStorageService.removeItem(storageConstants.TOKEN);
    localStorageService.removeItem(storageConstants.USER);
  },

  /**
   * 사용자 정보 가져오기
   */
  getUser: async (): Promise<User> => {
    // 캐시된 사용자 정보가 있으면 사용
    const cachedUser = localStorageService.getItem<User>(storageConstants.USER);
    if (cachedUser) {
      return cachedUser;
    }
    
    // 캐시된 정보가 없으면 API에서 가져오기
    const user = await api.get<User>(`${AUTH_API_PATH}/me`);
    localStorageService.setItem(storageConstants.USER, user);
    return user;
  },

  /**
   * 프로필 업데이트
   */
  updateProfile: async (data: UpdateProfileRequest): Promise<User> => {
    const updatedUser = await api.put<User>(`${AUTH_API_PATH}/profile`, data);
    
    // 캐시된 사용자 정보 업데이트
    localStorageService.setItem(storageConstants.USER, updatedUser);
    
    return updatedUser;
  },

  /**
   * 비밀번호 변경
   */
  changePassword: async (currentPassword: string, newPassword: string): Promise<{ success: boolean }> => {
    return api.put<{ success: boolean }>(`${AUTH_API_PATH}/password`, {
      currentPassword,
      newPassword,
    });
  },

  /**
   * 비밀번호 찾기 (비밀번호 재설정 이메일 전송)
   */
  forgotPassword: async (email: string): Promise<{ success: boolean; message: string }> => {
    return api.post<{ success: boolean; message: string }>(`${AUTH_API_PATH}/forgot-password`, { email });
  },

  /**
   * 비밀번호 재설정
   */
  resetPassword: async (token: string, password: string): Promise<{ success: boolean; message: string }> => {
    return api.post<{ success: boolean; message: string }>(`${AUTH_API_PATH}/reset-password`, {
      token,
      password,
    });
  },

  /**
   * 로그인 상태 확인
   */
  isLoggedIn: (): boolean => {
    return !!localStorageService.getItem(storageConstants.TOKEN);
  },
};

export default authService;
