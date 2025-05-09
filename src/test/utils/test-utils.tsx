/**
 * 테스트 유틸리티 함수
 * 
 * 테스트에 사용할 유틸리티 함수를 제공합니다.
 */

import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import { ThemeProvider, ToastProvider } from '@core/contexts';
import authReducer from '@features/auth/store/authSlice';
import newsReducer from '@features/news/store/newsSlice';
import stockReducer from '@features/stock/store/stockSlice';
import sentimentAnalysisReducer from '@features/sentiment-analysis/store/sentimentSlice';

// 테스트용 스토어 생성
export const createTestStore = (preloadedState = {}) => {
  return configureStore({
    reducer: {
      auth: authReducer,
      news: newsReducer,
      stocks: stockReducer,
      sentimentAnalysis: sentimentAnalysisReducer,
    },
    preloadedState,
  });
};

// 테스트용 래퍼 컴포넌트
interface AllTheProvidersProps {
  children: React.ReactNode;
  store?: ReturnType<typeof createTestStore>;
}

export const AllTheProviders = ({ children, store = createTestStore() }: AllTheProvidersProps) => {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <ThemeProvider>
          <ToastProvider>{children}</ToastProvider>
        </ThemeProvider>
      </BrowserRouter>
    </Provider>
  );
};

// 커스텀 렌더 함수
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  store?: ReturnType<typeof createTestStore>;
}

export const renderWithProviders = (
  ui: ReactElement,
  { store = createTestStore(), ...renderOptions }: CustomRenderOptions = {}
) => {
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <AllTheProviders store={store}>{children}</AllTheProviders>
  );

  return {
    store,
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
  };
};

// 모의 응답 생성 함수
export const createMockResponse = <T,>(data: T, status = 200, statusText = 'OK') => {
  return {
    data,
    status,
    statusText,
    headers: {},
    config: {},
  };
};

// 모의 오류 생성 함수
export const createMockError = (message: string, status = 400) => {
  const error = new Error(message);
  (error as any).response = {
    status,
    data: { message },
  };
  return error;
};

// 모의 로컬 스토리지 설정 함수
export const setupLocalStorage = (items: Record<string, string>) => {
  Object.entries(items).forEach(([key, value]) => {
    window.localStorage.setItem(key, value);
  });
};

// 모의 세션 스토리지 설정 함수
export const setupSessionStorage = (items: Record<string, string>) => {
  Object.entries(items).forEach(([key, value]) => {
    window.sessionStorage.setItem(key, value);
  });
};

// 모의 API 응답 생성 함수
export const mockApiResponse = <T,>(data: T) => {
  return Promise.resolve({
    data,
    status: 200,
    statusText: 'OK',
    headers: {},
    config: {},
  });
};

// 모의 API 오류 생성 함수
export const mockApiError = (message: string, status = 400) => {
  return Promise.reject({
    response: {
      data: { message },
      status,
    },
  });
};

// 모의 이벤트 생성 함수
export const createMockEvent = (value = '') => {
  return {
    target: { value },
    preventDefault: jest.fn(),
    stopPropagation: jest.fn(),
  };
};
