/**
 * 토큰 서비스 모듈
 *
 * 인증 토큰 관리 기능을 제공합니다.
 */

import { localStorageService } from '../../../services/storage';
import { storageConstants } from '../../../core/constants';
import api from '../../../services/api';
import { API_SERVICES, API_ENDPOINTS } from '../../../core/constants/api';

/**
 * 토큰 서비스 클래스
 */
class TokenService {
  /**
   * 액세스 토큰 저장
   *
   * @param token 액세스 토큰
   */
  setAccessToken(token: string): void {
    localStorageService.setItem(storageConstants.LOCAL_STORAGE_KEYS.ACCESS_TOKEN, token);
  }

  /**
   * 리프레시 토큰 저장
   *
   * @param token 리프레시 토큰
   */
  setRefreshToken(token: string): void {
    localStorageService.setItem(storageConstants.LOCAL_STORAGE_KEYS.REFRESH_TOKEN, token);
  }

  /**
   * 액세스 토큰 조회
   *
   * @returns 액세스 토큰
   */
  getAccessToken(): string | null {
    return localStorageService.getItem<string>(storageConstants.LOCAL_STORAGE_KEYS.ACCESS_TOKEN);
  }

  /**
   * 리프레시 토큰 조회
   *
   * @returns 리프레시 토큰
   */
  getRefreshToken(): string | null {
    return localStorageService.getItem<string>(storageConstants.LOCAL_STORAGE_KEYS.REFRESH_TOKEN);
  }

  /**
   * 토큰 저장
   *
   * @param accessToken 액세스 토큰
   * @param refreshToken 리프레시 토큰
   */
  setTokens(accessToken: string, refreshToken: string): void {
    this.setAccessToken(accessToken);
    this.setRefreshToken(refreshToken);
  }

  /**
   * 토큰 삭제
   */
  clearTokens(): void {
    localStorageService.removeItem(storageConstants.LOCAL_STORAGE_KEYS.ACCESS_TOKEN);
    localStorageService.removeItem(storageConstants.LOCAL_STORAGE_KEYS.REFRESH_TOKEN);
  }

  /**
   * 토큰 존재 여부 확인
   *
   * @returns 토큰 존재 여부
   */
  hasTokens(): boolean {
    return !!this.getAccessToken() && !!this.getRefreshToken();
  }

  /**
   * 액세스 토큰 존재 여부 확인
   *
   * @returns 액세스 토큰 존재 여부
   */
  hasAccessToken(): boolean {
    return !!this.getAccessToken();
  }

  /**
   * 리프레시 토큰 존재 여부 확인
   *
   * @returns 리프레시 토큰 존재 여부
   */
  hasRefreshToken(): boolean {
    return !!this.getRefreshToken();
  }

  /**
   * 토큰 갱신
   *
   * @returns 갱신 성공 여부
   */
  async refreshToken(): Promise<boolean> {
    try {
      const refreshToken = this.getRefreshToken();

      if (!refreshToken) {
        return false;
      }

      const url = api.buildUrl(API_SERVICES.AUTH, API_ENDPOINTS.AUTH.REFRESH_TOKEN);
      const response = await api.post<{ accessToken: string; refreshToken: string }>(url, {
        refreshToken,
      });

      if (response && response.accessToken) {
        this.setTokens(response.accessToken, response.refreshToken || refreshToken);
        return true;
      }

      return false;
    } catch (error) {
      console.error('토큰 갱신 오류:', error);
      this.clearTokens();
      return false;
    }
  }

  /**
   * 토큰 유효성 검사
   *
   * @returns 유효성 여부
   */
  async verifyToken(): Promise<boolean> {
    try {
      const accessToken = this.getAccessToken();

      if (!accessToken) {
        return false;
      }

      const url = api.buildUrl(API_SERVICES.AUTH, API_ENDPOINTS.AUTH.VERIFY_TOKEN);
      await api.post(url, {
        token: accessToken,
      });

      return true;
    } catch (error) {
      console.error('토큰 검증 오류:', error);

      // 토큰이 유효하지 않으면 갱신 시도
      return this.refreshToken();
    }
  }
}

export const tokenService = new TokenService();
export default tokenService;
