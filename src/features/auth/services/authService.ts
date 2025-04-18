/**
 * 인증 서비스 모듈
 * 
 * 사용자 인증 관련 API 서비스를 제공합니다.
 */

import api from '../../../services/api';
import logger from '../../../core/utils/logger';
import { User } from '../types';

// 인증 관련 API 서비스
const authService = {
  // 로그인
  login: async (email: string, password: string): Promise<{ token: string; user: User }> => {
    try {
      logger.log('로그인 요청 데이터:', { email, password });

      // 로그인 요청 - 일반 JSON 형식으로 변경
      const loginData = {
        email: email,
        password: password,
      };

      // 로그인 요청 시도
      const response = await api.post('/auth/login', loginData);
      logger.log('로그인 응답:', response.data);

      // 토큰 저장
      const token = response.data.token || response.data.access_token;
      if (token) {
        localStorage.setItem('token', token);

        // 리프레시 토큰이 있는 경우 저장
        if (response.data.refresh_token || response.data.refreshToken) {
          const refreshToken = response.data.refresh_token || response.data.refreshToken;
          localStorage.setItem('refreshToken', refreshToken);
        }
      } else {
        logger.error('토큰이 응답에 없습니다:', response.data);
        throw new Error('서버에서 토큰을 받지 못했습니다.');
      }

      // 사용자 정보가 응답에 포함되어 있는지 확인
      let user: User;
      if (response.data.user) {
        user = response.data.user;
      } else {
        // 사용자 정보가 없는 경우 추가 요청
        try {
          const userResponse = await api.get('/auth/me', {
            headers: { Authorization: `Bearer ${token}` },
          });
          logger.log('사용자 정보 응답:', userResponse.data);
          user = userResponse.data.data || userResponse.data;
        } catch (userError) {
          logger.error('사용자 정보 가져오기 오류:', userError);
          // 기본 사용자 정보 생성
          user = {
            id: 'unknown',
            username: email.split('@')[0],
            name: email.split('@')[0],
            email: email,
            role: 'user',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          };
        }
      }

      return {
        token,
        user,
      };
    } catch (error) {
      const errorResponse = error as {
        response?: { data?: { detail?: string; message?: string } };
        message?: string;
      };
      logger.error('로그인 오류:', error);
      const errorData = error as { response?: { data?: any } };
      logger.error('오류 응답:', errorData.response?.data);

      // 오류 메시지 추출 개선
      const errorMessage =
        errorResponse.response?.data?.detail ||
        errorResponse.response?.data?.message ||
        errorResponse.message ||
        '로그인 중 오류가 발생했습니다.';

      throw new Error(errorMessage);
    }
  },

  // 회원가입
  register: async (userData: {
    username: string;
    email: string;
    password: string;
  }): Promise<{ token: string; user: User }> => {
    try {
      logger.log('회원가입 요청 데이터:', userData);

      // 회원가입 요청 데이터 준비
      const registerData = {
        username: userData.username,
        email: userData.email,
        password: userData.password,
        // name 필드가 필요한 경우 추가
        name: userData.username,
      };

      logger.log('회원가입 요청 데이터 (수정됨):', registerData);

      // 회원가입 요청
      const registerResponse = await api.post('/auth/register', registerData);
      logger.log('회원가입 응답:', registerResponse.data);

      // 토큰이 응답에 포함되어 있는 경우
      if (registerResponse.data.token || registerResponse.data.access_token) {
        const token = registerResponse.data.token || registerResponse.data.access_token;
        localStorage.setItem('token', token);

        // 리프레시 토큰이 있는 경우 저장
        if (registerResponse.data.refresh_token || registerResponse.data.refreshToken) {
          const refreshToken =
            registerResponse.data.refresh_token || registerResponse.data.refreshToken;
          localStorage.setItem('refreshToken', refreshToken);
        }

        // 사용자 정보 추출
        let user: User;
        if (registerResponse.data.user) {
          user = registerResponse.data.user;
        } else {
          // 사용자 정보가 없는 경우 기본 정보 생성
          user = {
            id: 'new-user',
            username: userData.username,
            name: userData.username,
            email: userData.email,
            role: 'user',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          };
        }

        return {
          token,
          user,
        };
      }

      // 토큰이 없는 경우 로그인 시도
      return authService.login(userData.email, userData.password);
    } catch (error) {
      const errorResponse = error as {
        response?: { data?: { detail?: string; message?: string } };
        message?: string;
      };
      logger.error('회원가입 오류:', error);
      const errorData = error as { response?: { data?: any } };
      logger.error('오류 응답:', errorData.response?.data);

      // 오류 메시지 추출 개선
      const errorMessage =
        errorResponse.response?.data?.detail ||
        errorResponse.response?.data?.message ||
        errorResponse.message ||
        '회원가입 중 오류가 발생했습니다.';

      throw new Error(errorMessage);
    }
  },

  // 사용자 정보 가져오기
  getUser: async (): Promise<User> => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('인증 토큰이 없습니다.');
      }

      const response = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    } catch (error) {
      const errorResponse = error as {
        response?: { data?: { detail?: string } };
        message?: string;
      };
      logger.error('사용자 정보 가져오기 오류:', error);
      throw new Error(
        errorResponse.response?.data?.detail ||
          errorResponse.message ||
          '사용자 정보를 가져오는 중 오류가 발생했습니다.'
      );
    }
  },

  // 로그아웃
  logout: (): void => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  },

  // 비밀번호 변경
  changePassword: async (
    currentPassword: string,
    newPassword: string
  ): Promise<{ success: boolean }> => {
    try {
      const response = await api.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      return { success: true };
    } catch (error) {
      const errorResponse = error as {
        response?: { data?: { detail?: string } };
        message?: string;
      };
      logger.error('비밀번호 변경 오류:', error);
      throw new Error(
        errorResponse.response?.data?.detail ||
          errorResponse.message ||
          '비밀번호 변경 중 오류가 발생했습니다.'
      );
    }
  },

  // 프로필 업데이트
  updateProfile: async (userData: Partial<User>): Promise<User> => {
    try {
      const response = await api.put('/auth/profile', userData);
      return response.data;
    } catch (error) {
      const errorResponse = error as {
        response?: { data?: { detail?: string } };
        message?: string;
      };
      logger.error('프로필 업데이트 오류:', error);
      throw new Error(
        errorResponse.response?.data?.detail ||
          errorResponse.message ||
          '프로필 업데이트 중 오류가 발생했습니다.'
      );
    }
  },
};

export default authService;
