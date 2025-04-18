/**
 * 인증 훅 모듈
 *
 * 인증 관련 기능을 쉽게 사용할 수 있는 커스텀 훅을 제공합니다.
 */

import { useCallback, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "../../../core/hooks";
import {
  login,
  register,
  logout,
  updateProfile,
  changePassword,
  verifyAuth,
  forgotPassword,
  resetPassword,
} from "../store/authSlice";
import { LoginRequest, RegisterRequest, UpdateProfileRequest } from "../types";
import { routeConstants } from "../../../core/constants";

/**
 * 인증 관련 기능을 제공하는 커스텀 훅
 */
export const useAuth = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, isLoading, error } = useAppSelector(
    (state) => state.auth
  );

  // 인증 상태 확인
  useEffect(() => {
    const checkAuth = async () => {
      if (isAuthenticated) {
        await dispatch(verifyAuth());
      }
    };

    checkAuth();
  }, [dispatch, isAuthenticated]);

  // 로그인 함수
  const handleLogin = useCallback(
    async (credentials: LoginRequest) => {
      try {
        const resultAction = await dispatch(login(credentials));
        if (login.fulfilled.match(resultAction)) {
          const redirectTo = location.state?.from?.pathname || routeConstants.ROUTES.DASHBOARD;
          navigate(redirectTo);
          return true;
        }
        return false;
      } catch (error) {
        return false;
      }
    },
    [dispatch, navigate, location.state]

  // 회원가입 함수
  const handleRegister = useCallback(
    async (credentials: RegisterRequest) => {
      try {
        const resultAction = await dispatch(register(credentials));
        if (register.fulfilled.match(resultAction)) {
          navigate(routeConstants.ROUTES.DASHBOARD);
          return true;
        }
        return false;
      } catch (error) {
        return false;
      }
    },
    [dispatch, navigate]
  );

  // 로그아웃 함수
  const handleLogout = useCallback(async () => {
    await dispatch(logout());
    navigate(routeConstants.ROUTES.LOGIN);
  }, [dispatch, navigate]);

  // 프로필 업데이트 함수
  const handleUpdateProfile = useCallback(
    async (userData: UpdateProfileRequest) => {
      try {
        const resultAction = await dispatch(updateProfile(userData));
        return updateProfile.fulfilled.match(resultAction);
      } catch (error) {
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
        return false;
      }
    },
    [dispatch]
  );

  // 비밀번호 재설정 함수
  const handleResetPassword = useCallback(
    async (token: string, newPassword: string) => {
      try {
        const resultAction = await dispatch(resetPassword({ token, newPassword }));
        if (resetPassword.fulfilled.match(resultAction)) {
          navigate(routeConstants.ROUTES.LOGIN);
          return true;
        }
        return false;
      } catch (error) {
        return false;
      }
    },
    [dispatch, navigate]
  );

  // 인증 상태 검증 함수
  const checkAuthStatus = useCallback(async () => {
    if (isAuthenticated) {
      return await dispatch(verifyAuth()).unwrap();
    }
    return false;
  }, [dispatch, isAuthenticated]);

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    updateProfile: handleUpdateProfile,
    changePassword: handleChangePassword,
    forgotPassword: handleForgotPassword,
    resetPassword: handleResetPassword,
    checkAuthStatus,
  };
};

export default useAuth;
