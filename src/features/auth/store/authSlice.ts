/**
 * 인증 상태 관리 모듈
 * 
 * 인증 관련 상태 관리를 위한 Redux 슬라이스를 제공합니다.
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import authService from '../services/authService';
import { AuthState, User, LoginCredentials, RegisterCredentials, AuthResponse } from '../types';

// 로그인 액션
export const login = createAsyncThunk<AuthResponse, LoginCredentials, { rejectValue: string }>(
  'auth/login',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      console.log('로그인 시도:', { email });
      const response = await authService.login(email, password);
      console.log('로그인 성공:', response);
      const authResponse: AuthResponse = {
        user: response.user,
        token: response.token,
        isAuthenticated: true,
      };
      return authResponse;
    } catch (error) {
      console.error('로그인 실패:', error);
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      return rejectWithValue(errorMessage);
    }
  }
);

// 회원가입 액션
export const register = createAsyncThunk<
  AuthResponse,
  RegisterCredentials,
  { rejectValue: string }
>('auth/register', async ({ username, email, password }, { rejectWithValue }) => {
  try {
    console.log('회원가입 시도:', { email, username });
    const response = await authService.register({
      username,
      email,
      password,
    });
    console.log('회원가입 성공:', response);
    const authResponse: AuthResponse = {
      user: response.user,
      token: response.token,
      isAuthenticated: true,
    };
    return authResponse;
  } catch (error) {
    console.error('회원가입 실패:', error);
    const errorMessage = error instanceof Error ? error.message : 'Registration failed';
    return rejectWithValue(errorMessage);
  }
});

// 로그아웃 액션
export const logout = createAsyncThunk('auth/logout', async () => {
  authService.logout();
});

// 인증 상태 확인 액션
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const checkAuthStatus = createAsyncThunk<any, void, { rejectValue: string }>(
  'auth/check',
  async _ => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        // 토큰이 없으면 인증되지 않은 상태로 처리
        return { isAuthenticated: false, user: null };
      }

      try {
        // 토큰이 있으면 사용자 정보 가져오기 시도
        const user = await authService.getUser();
        return {
          isAuthenticated: true,
          user,
          token,
        };
      } catch (userError) {
        // 사용자 정보 가져오기 실패 시 토큰 삭제
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        // 인증되지 않은 상태로 처리 (오류로 처리하지 않음)
        return { isAuthenticated: false, user: null };
      }
    } catch (error) {
      // 기타 오류 처리
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      // 인증되지 않은 상태로 처리 (오류로 처리하지 않음)
      return { isAuthenticated: false, user: null };
    }
  }
);

// 프로필 업데이트 액션
export const updateProfile = createAsyncThunk<User, Partial<User>, { rejectValue: string }>(
  'auth/updateProfile',
  async (userData, { rejectWithValue }) => {
    try {
      return await authService.updateProfile(userData);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Profile update failed';
      return rejectWithValue(errorMessage);
    }
  }
);

// 비밀번호 변경 액션
export const changePassword = createAsyncThunk<
  { success: boolean },
  { currentPassword: string; newPassword: string },
  { rejectValue: string }
>('auth/changePassword', async ({ currentPassword, newPassword }, { rejectWithValue }) => {
  try {
    return await authService.changePassword(currentPassword, newPassword);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Password change failed';
    return rejectWithValue(errorMessage);
  }
});

// 초기 상태
const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

// 인증 슬라이스
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: state => {
      state.error = null;
    },
  },
  extraReducers: builder => {
    builder
      // Login reducers
      .addCase(login.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action: PayloadAction<AuthResponse>) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token || null;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload || 'Login failed';
      })

      // Register reducers
      .addCase(register.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action: PayloadAction<AuthResponse>) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token || null;
      })
      .addCase(register.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload || 'Registration failed';
      })

      // Logout reducers
      .addCase(logout.fulfilled, state => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      })

      // Check auth status reducers
      .addCase(checkAuthStatus.pending, state => {
        state.isLoading = true;
      })
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .addCase(checkAuthStatus.fulfilled, (state, action: PayloadAction<any>) => {
        state.isLoading = false;
        state.isAuthenticated = action.payload.isAuthenticated;
        state.user = action.payload.user;
        state.token = action.payload.token || null;
      })
      .addCase(checkAuthStatus.rejected, state => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
      })

      // Update profile reducers
      .addCase(updateProfile.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateProfile.fulfilled, (state, action: PayloadAction<User>) => {
        state.isLoading = false;
        state.user = action.payload;
      })
      .addCase(updateProfile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload || 'Profile update failed';
      })

      // Change password reducers
      .addCase(changePassword.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(changePassword.fulfilled, state => {
        state.isLoading = false;
      })
      .addCase(changePassword.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload || 'Password change failed';
      });
  },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;
