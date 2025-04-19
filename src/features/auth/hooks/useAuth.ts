/**
 * 인증 관련 커스텀 훅
 * 
 * 인증 관련 동작을 위한 커스텀 훅을 제공합니다.
 */

import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../../../core/hooks';
import {
  login,
  register,
  logout,
  updateProfile,
  changePassword,
  verifyAuth,
  forgotPassword,
  resetPassword,
} from '../store/authSlice';
import { LoginRequest, RegisterRequest, UpdateProfileRequest } from '../types';
import { routeConstants } from '../../../core/constants';

/**
 * 인증 관련 기능을 제공하는 커스텀 훅
 */
export const useAuth = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  
  // 인증 상태 가져오기
  const { 
    user, 
    accessToken, 
    isAuthenticated, 
    isLoading, 
    error 
  } = useAppSelector(state => state.auth);
  
  // 로그인 함수
  const handleLogin = useCallback(
    async (credentials: LoginRequest) => {
      try {
        const resultAction = await dispatch(login(credentials));
        if (login.fulfilled.match(resultAction)) {
          navigate(routeConstants.DASHBOARD);
          return true;
        }
        return false;
      } catch (error) {
        console.error('로그인 오류:', error);
        return false;
      }
    },
    [dispatch, navigate]
  );
  
  // 회원가입 함수
  const handleRegister = useCallback(
    async (credentials: RegisterRequest) => {
      try {
        const resultAction = await dispatch(register(credentials));
        if (register.fulfilled.match(resultAction)) {
          navigate(routeConstants.DASHBOARD);
          return true;
        }
        return false;
      } catch (error) {
        console.error('회원가입 오류:', error);
        return false;
      }
    },
    [dispatch, navigate]
  );
  
  // 로그아웃 함수
  const handleLogout = useCallback(async () => {
    await dispatch(logout());
    navigate(routeConstants.LOGIN);
  }, [dispatch, navigate]);
  
  // 인증 상태 확인 함수
  const checkAuth = useCallback(async () => {
    return await dispatch(verifyAuth());
  }, [dispatch]);
  
  // 프로필 업데이트 함수
  const handleUpdateProfile = useCallback(
    async (data: UpdateProfileRequest) => {
      try {
        const resultAction = await dispatch(updateProfile(data));
        return updateProfile.fulfilled.match(resultAction);
      } catch (error) {
        console.error('프로필 업데이트 오류:', error);
        return false;
      }
    },
    [dispatch]
  );
  
  // 비밀번호 변경 함수
  const handleChangePassword = useCallback(
    async (currentPassword: string, newPassword: string) => {
      try {
        const resultAction = await dispatch(
          changePassword({ currentPassword, newPassword })
        );
        return changePassword.fulfilled.match(resultAction);
      } catch (error) {
        console.error('비밀번호 변경 오류:', error);
        return false;
      }
    },
    [dispatch]
  );
  
  // 비밀번호 찾기 함수
  const handleForgotPassword = useCallback(
    async (email: string) => {
      try {
        const resultAction = await dispatch(forgotPassword({ email }));
        return forgotPassword.fulfilled.match(resultAction);
      } catch (error) {
        console.error('비밀번호 찾기 오류:', error);
        return false;
      }
    },
    [dispatch]
  );
  
  // 비밀번호 재설정 함수
  const handleResetPassword = useCallback(
    async (token: string, password: string) => {
      try {
        const resultAction = await dispatch(resetPassword({ token, password }));
        if (resetPassword.fulfilled.match(resultAction)) {
          navigate(routeConstants.LOGIN);
          return true;
        }
        return false;
      } catch (error) {
        console.error('비밀번호 재설정 오류:', error);
        return false;
      }
    },
    [dispatch, navigate]
  );
  
  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    accessToken,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    checkAuth,
    updateProfile: handleUpdateProfile,
    changePassword: handleChangePassword,
    forgotPassword: handleForgotPassword,
    resetPassword: handleResetPassword
  };
};
