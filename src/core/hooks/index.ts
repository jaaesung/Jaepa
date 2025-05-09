/**
 * 공통 훅 모듈
 * 
 * 애플리케이션 전체에서 사용되는 공통 React 훅을 제공합니다.
 */

import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import { useState, useEffect, useCallback, useRef } from 'react';
import type { RootState } from '../types';
import type { AppDispatch } from '../../store';

// Redux 훅
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// 로컬 스토리지 훅
export function useLocalStorage<T>(key: string, initialValue: T) {
  // 상태 초기화
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      // 로컬 스토리지에서 값 가져오기
      const item = window.localStorage.getItem(key);
      // 값이 있으면 파싱, 없으면 초기값 반환
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  // 값 설정 함수
  const setValue = (value: T | ((val: T) => T)) => {
    try {
      // 함수인 경우 함수 실행 결과를 사용
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      // 상태 업데이트
      setStoredValue(valueToStore);
      // 로컬 스토리지에 저장
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue] as const;
}

// 디바운스 훅
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// 이전 값 훅
export function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();
  
  useEffect(() => {
    ref.current = value;
  }, [value]);
  
  return ref.current;
}

// 윈도우 크기 훅
export function useWindowSize() {
  const [windowSize, setWindowSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return windowSize;
}

// 클릭 외부 감지 훅
export function useOutsideClick(ref: React.RefObject<HTMLElement>, callback: () => void) {
  const handleClick = useCallback(
    (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        callback();
      }
    },
    [ref, callback]
  );

  useEffect(() => {
    document.addEventListener('mousedown', handleClick);
    
    return () => {
      document.removeEventListener('mousedown', handleClick);
    };
  }, [handleClick]);
}
