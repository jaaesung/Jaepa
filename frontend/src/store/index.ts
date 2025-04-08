import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import newsReducer from './slices/newsSlice';
import stockReducer from './slices/stockSlice';
import uiReducer from './slices/uiSlice';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import { RootState } from '../types';

const store = configureStore({
  reducer: {
    auth: authReducer,
    news: newsReducer,
    stocks: stockReducer,
    ui: uiReducer,
  },
  // 필요한 경우 여기에 미들웨어 추가
});

// Redux 타입 설정
export type AppDispatch = typeof store.dispatch;

// 타입이 지정된 훅 내보내기
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

export default store;