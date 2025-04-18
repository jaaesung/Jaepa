/**
 * 테스트 유틸리티 모듈
 * 
 * 테스트를 위한 유틸리티 함수를 제공합니다.
 */

import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import { ThemeProvider, ToastProvider } from '../core/contexts';
import rootReducer from '../store/rootReducer';

// 테스트용 스토어 생성
export const createTestStore = (preloadedState = {}) => {
  return configureStore({
    reducer: rootReducer,
    preloadedState,
  });
};

// 테스트용 렌더 옵션 인터페이스
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  preloadedState?: Record<string, any>;
  store?: ReturnType<typeof createTestStore>;
  route?: string;
}

// 테스트용 렌더 함수
export function renderWithProviders(
  ui: ReactElement,
  {
    preloadedState = {},
    store = createTestStore(preloadedState),
    route = '/',
    ...renderOptions
  }: CustomRenderOptions = {}
) {
  // 테스트용 라우터 설정
  window.history.pushState({}, 'Test page', route);

  // 테스트용 래퍼 컴포넌트
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <Provider store={store}>
        <ThemeProvider>
          <ToastProvider>
            <BrowserRouter>{children}</BrowserRouter>
          </ToastProvider>
        </ThemeProvider>
      </Provider>
    );
  }

  // 컴포넌트 렌더링
  return {
    store,
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
  };
}

// 테스트 데이터 생성 유틸리티
export const createTestData = {
  // 사용자 데이터 생성
  user: (overrides = {}) => ({
    id: 'test-user-id',
    email: 'test@example.com',
    name: 'Test User',
    ...overrides,
  }),

  // 뉴스 기사 데이터 생성
  newsArticle: (overrides = {}) => ({
    id: 'test-article-id',
    title: 'Test Article Title',
    content: 'Test article content',
    source: 'Test Source',
    url: 'https://example.com/article',
    publishedAt: '2023-01-01T00:00:00Z',
    sentiment: 'neutral',
    ...overrides,
  }),

  // 주식 데이터 생성
  stockData: (overrides = {}) => ({
    symbol: 'AAPL',
    name: 'Apple Inc.',
    price: 150.0,
    change: 1.5,
    changePercent: 1.0,
    volume: 1000000,
    ...overrides,
  }),

  // 감성 분석 결과 생성
  sentimentResult: (overrides = {}) => ({
    id: 'test-sentiment-id',
    text: 'Test sentiment text',
    sentiment: 'neutral',
    positive: 0.3,
    neutral: 0.5,
    negative: 0.2,
    ...overrides,
  }),
};

// 테스트 모의 함수
export const mockFunctions = {
  // 모의 이벤트 핸들러
  mockEventHandler: jest.fn(),

  // 모의 비동기 함수
  mockAsyncFunction: jest.fn().mockResolvedValue({}),

  // 모의 실패 함수
  mockRejectedFunction: jest.fn().mockRejectedValue(new Error('Test error')),
};
