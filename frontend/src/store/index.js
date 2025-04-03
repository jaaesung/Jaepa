import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import newsReducer from './slices/newsSlice';
import stockReducer from './slices/stockSlice';
import uiReducer from './slices/uiSlice';

const store = configureStore({
  reducer: {
    auth: authReducer,
    news: newsReducer,
    stock: stockReducer,
    ui: uiReducer,
  },
  // 필요한 경우 여기에 미들웨어 추가
});

export default store;