/**
 * 인증 서비스 모듈
 * 
 * 사용자 인증 관련 API 서비스를 제공합니다.
 */

import apiClient from '../../../services/api/client';
import tokenService from './token-service';
import { localStorageService } from '../../../services/storage';
import { storageConstants } from '../../../core/constants';
import { API_SERVICES, API_ENDPOINTS } from '../../../core/constants/api';
import { User, LoginRequest, RegisterRequest, UpdateProfileRequest } from '../types';

/**
 * 인증 서비스 클래스
 */
class AuthService {
  /**
   * 로그인
   * 
   * @param credentials 로그인 정보
   * @returns 로그인 결과
   */
  async login(credentials: LoginRequest): Promise<{ user: User; accessToken: string; refreshToken: string }> {
    const response = await apiClient.post<{ user: User; accessToken: string; refreshToken: string }>(
      API_SERVICES.AUTH,
      API_ENDPOINTS.AUTH.LOGIN,
      credentials
    );
    
    // 토큰 저장
    tokenService.setTokens(response.accessToken, response.refreshToken);
    
    // 사용자 정보 저장
    localStorageService.set(storageConstants.LOCAL_STORAGE_KEYS.USER, response.user);
    
    return response;
  }

  /**
   * 회원가입
   * 
   * @param userData 회원가입 정보
   * @returns 회원가입 결과
   */
  async register(userData: RegisterRequest): Promise<{ user: User; accessToken: string; refreshToken: string }> {
    const response = await apiClient.post<{ user: User; accessToken: string; refreshToken: string }>(
      API_SERVICES.AUTH,
      API_ENDPOINTS.AUTH.REGISTER,
      userData
    );
    
    // 토큰 저장
    tokenService.setTokens(response.accessToken, response.refreshToken);
    
    // 사용자 정보 저장
    localStorageService.set(storageConstants.LOCAL_STORAGE_KEYS.USER, response.user);
    
    return response;
  }

  /**
   * 로그아웃
   * 
   * @returns 로그아웃 성공 여부
   */
  async logout(): Promise<boolean> {
    try {
      const refreshToken = tokenService.getRefreshToken();
      
      if (refreshToken) {
        await apiClient.post(
          API_SERVICES.AUTH,
          API_ENDPOINTS.AUTH.LOGOUT,
          { refreshToken }
        );
      }
      
      // 토큰 및 사용자 정보 삭제
      tokenService.clearTokens();
      localStorageService.remove(storageConstants.LOCAL_STORAGE_KEYS.USER);
      
      return true;
    } catch (error) {
      console.error('로그아웃 오류:', error);
      
      // 오류가 발생해도 로컬 데이터는 삭제
      tokenService.clearTokens();
      localStorageService.remove(storageConstants.LOCAL_STORAGE_KEYS.USER);
      
      return false;
    }
  }

  /**
   * 현재 사용자 정보 조회
   * 
   * @returns 사용자 정보
   */
  getCurrentUser(): User | null {
    return localStorageService.get<User>(storageConstants.LOCAL_STORAGE_KEYS.USER);
  }

  /**
   * 사용자 정보 업데이트
   * 
   * @param userData 업데이트할 사용자 정보
   * @returns 업데이트된 사용자 정보
   */
  async updateProfile(userData: UpdateProfileRequest): Promise<User> {
    const response = await apiClient.put<User>(
      API_SERVICES.AUTH,
      API_ENDPOINTS.AUTH.UPDATE_PROFILE,
      userData
    );
    
    // 업데이트된 사용자 정보 저장
    localStorageService.set(storageConstants.LOCAL_STORAGE_KEYS.USER, response);
    
    return response;
  }

  /**
   * 비밀번호 변경
   * 
   * @param currentPassword 현재 비밀번호
   * @param newPassword 새 비밀번호
   * @returns 변경 성공 여부
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<boolean> {
    try {
      await apiClient.post(
        API_SERVICES.AUTH,
        API_ENDPOINTS.AUTH.CHANGE_PASSWORD,
        { currentPassword, newPassword }
      );
      
      return true;
    } catch (error) {
      console.error('비밀번호 변경 오류:', error);
      return false;
    }
  }

  /**
   * 비밀번호 재설정 요청
   * 
   * @param email 이메일
   * @returns 요청 성공 여부
   */
  async forgotPassword(email: string): Promise<boolean> {
    try {
      await apiClient.post(
        API_SERVICES.AUTH,
        API_ENDPOINTS.AUTH.FORGOT_PASSWORD,
        { email }
      );
      
      return true;
    } catch (error) {
      console.error('비밀번호 재설정 요청 오류:', error);
      return false;
    }
  }

  /**
   * 비밀번호 재설정
   * 
   * @param token 재설정 토큰
   * @param newPassword 새 비밀번호
   * @returns 재설정 성공 여부
   */
  async resetPassword(token: string, newPassword: string): Promise<boolean> {
    try {
      await apiClient.post(
        API_SERVICES.AUTH,
        API_ENDPOINTS.AUTH.RESET_PASSWORD,
        { token, newPassword }
      );
      
      return true;
    } catch (error) {
      console.error('비밀번호 재설정 오류:', error);
      return false;
    }
  }

  /**
   * 인증 상태 확인
   * 
   * @returns 인증 상태
   */
  isAuthenticated(): boolean {
    return tokenService.hasTokens() && !!this.getCurrentUser();
  }

  /**
   * 인증 상태 검증
   * 
   * @returns 인증 상태
   */
  async verifyAuth(): Promise<boolean> {
    if (!this.isAuthenticated()) {
      return false;
    }
    
    return tokenService.verifyToken();
  }
}

export const authService = new AuthService();
export default authService;
