/**
 * 스토어 모듈
 *
 * 애플리케이션 상태 관리를 위한 Redux 스토어를 제공합니다.
 */

import { configureStore } from "@reduxjs/toolkit";
import { authReducer } from "../features/auth";
import { newsReducer } from "../features/news";
import { sentimentReducer } from "../features/sentiment-analysis";
import { stockReducer } from "../features/stock";

// 루트 리듀서
const rootReducer = {
  auth: authReducer,
  news: newsReducer,
  sentimentAnalysis: sentimentReducer,
  stock: stockReducer,
  // 다른 리듀서들을 여기에 추가
};

// 스토어 생성
const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // 직렬화 불가능한 값에 대한 경고 무시 (필요한 경우)
        ignoredActions: [],
        ignoredActionPaths: [],
        ignoredPaths: [],
      },
    }),
  devTools: process.env.NODE_ENV !== "production",
});

// 스토어 타입 내보내기
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;
