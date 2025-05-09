/**
 * 루트 리듀서 모듈
 *
 * 모든 리듀서를 통합하는 루트 리듀서를 제공합니다.
 */

import { combineReducers } from '@reduxjs/toolkit';
import { authReducer } from '../features/auth';
import { newsReducer } from '../features/news';
import { sentimentReducer } from '../features/sentiment-analysis';
import { stockReducer } from '../features/stock';

// 루트 리듀서 생성
const rootReducer = combineReducers({
  auth: authReducer,
  news: newsReducer,
  sentimentAnalysis: sentimentReducer,
  stock: stockReducer,
});

export type RootState = ReturnType<typeof rootReducer>;
export default rootReducer;
