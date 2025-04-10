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
        isAuthenticated: true
      };
      return authResponse;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Login failed');
    }
  }
);

export const register = createAsyncThunk<AuthResponse, RegisterCredentials, { rejectValue: string }>(
  'auth/register',
  async ({ username, email, password }, { rejectWithValue }) => {
    try {
      const response = await apiClient.auth.register({ username, email, password });
      const authResponse: AuthResponse = {
        user: response.user,
        token: response.token,
        isAuthenticated: true
      };
      return authResponse;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Registration failed');
    }
  }
);

export const logout = createAsyncThunk('auth/logout', async () => {
  localStorage.removeItem('token');
  localStorage.removeItem('refreshToken');
});

export const checkAuthStatus = createAsyncThunk<AuthResponse>(
  'auth/check',
  async (_, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        return { isAuthenticated: false, user: null } as AuthResponse;
      }
      
      const user = await apiClient.auth.getUser();
      return {
        isAuthenticated: true,
        user,
        token
      };
    } catch (error) {
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      return rejectWithValue('Authentication check failed');
    }
  }
);

export const updateProfile = createAsyncThunk<User, Partial<User>, { rejectValue: string }>(
  'auth/updateProfile',
  async (userData, { rejectWithValue }) => {
    try {
      return await apiClient.auth.updateProfile(userData);
    } catch (error: any) {
      return rejectWithValue(error.message || 'Profile update failed');
    }
  }
);

export const changePassword = createAsyncThunk<
  { success: boolean },
  { currentPassword: string; newPassword: string },
  { rejectValue: string }
>(
  'auth/changePassword',
  async ({ currentPassword, newPassword }, { rejectWithValue }) => {
    try {
      return await apiClient.auth.changePassword(currentPassword, newPassword);
    } catch (error: any) {
      return rejectWithValue(error.message || 'Password change failed');
    }
  }
);

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login reducers
      .addCase(login.pending, (state) => {
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
      .addCase(register.pending, (state) => {
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
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      })
      
      // Check auth status reducers
      .addCase(checkAuthStatus.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(checkAuthStatus.fulfilled, (state, action: PayloadAction<AuthResponse>) => {
        state.isLoading = false;
        state.isAuthenticated = action.payload.isAuthenticated;
        state.user = action.payload.user;
        state.token = action.payload.token || null;
      })
      .addCase(checkAuthStatus.rejected, (state) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
      })
      
      // Update profile reducers
      .addCase(updateProfile.pending, (state) => {
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
      .addCase(changePassword.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(changePassword.fulfilled, (state) => {
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