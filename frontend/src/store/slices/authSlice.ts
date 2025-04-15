import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiClient from '../../services/apiClient';
import { AuthState, User } from '../../types';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterCredentials {
  username: string;
  email: string;
  password: string;
}

interface AuthResponse {
  user: User;
  token?: string;
  isAuthenticated: boolean;
}

export const login = createAsyncThunk<AuthResponse, LoginCredentials, { rejectValue: string }>(
  'auth/login',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const response = await apiClient.auth.login(email, password);
      const authResponse: AuthResponse = {
        user: response.user,
        token: response.token,
        isAuthenticated: true,
      };
      return authResponse;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      return rejectWithValue(errorMessage);
    }
  }
);

export const register = createAsyncThunk<
  AuthResponse,
  RegisterCredentials,
  { rejectValue: string }
>('auth/register', async ({ username, email, password }, { rejectWithValue }) => {
  try {
    const response = await apiClient.auth.register({
      username,
      email,
      password,
    });
    const authResponse: AuthResponse = {
      user: response.user,
      token: response.token,
      isAuthenticated: true,
    };
    return authResponse;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Registration failed';
    return rejectWithValue(errorMessage);
  }
});

export const logout = createAsyncThunk('auth/logout', async () => {
  localStorage.removeItem('token');
  localStorage.removeItem('refreshToken');
});

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
        const user = await apiClient.auth.getUser();
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

export const updateProfile = createAsyncThunk<User, Partial<User>, { rejectValue: string }>(
  'auth/updateProfile',
  async (userData, { rejectWithValue }) => {
    try {
      return await apiClient.auth.updateProfile(userData);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Profile update failed';
      return rejectWithValue(errorMessage);
    }
  }
);

export const changePassword = createAsyncThunk<
  { success: boolean },
  { currentPassword: string; newPassword: string },
  { rejectValue: string }
>('auth/changePassword', async ({ currentPassword, newPassword }, { rejectWithValue }) => {
  try {
    return await apiClient.auth.changePassword(currentPassword, newPassword);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Password change failed';
    return rejectWithValue(errorMessage);
  }
});

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false, // 초기 로딩 상태를 false로 설정
  error: null,
};

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
