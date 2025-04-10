import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { UiState, Notification } from '../../types';

const initialState: UiState = {
  sidebarOpen: true,
  theme: 'light',
  notifications: [],
};

type ThemeType = 'light' | 'dark';

interface NotificationPayload {
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read?: boolean;
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    toggleTheme: (state) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
    },
    setTheme: (state, action: PayloadAction<ThemeType>) => {
      state.theme = action.payload;
    },
    addNotification: (state, action: PayloadAction<NotificationPayload>) => {
      const newNotification: Notification = {
        id: Date.now().toString(),
        read: false,
        createdAt: new Date().toISOString(),
        ...action.payload,
      };
      state.notifications.push(newNotification);
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        (notification) => notification.id !== action.payload
      );
    },
    clearAllNotifications: (state) => {
      state.notifications = [];
    },
  },
});

export const {
  toggleSidebar,
  setSidebarOpen,
  toggleTheme,
  setTheme,
  addNotification,
  removeNotification,
  clearAllNotifications,
} = uiSlice.actions;

export default uiSlice.reducer;