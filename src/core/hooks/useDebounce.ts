/**
 * 디바운스 훅 모듈
 * 
 * 값의 변경을 지연시키는 디바운스 기능을 제공합니다.
 */

import { useState, useEffect } from 'react';

/**
 * 디바운스 훅
 * 
 * @param value 디바운스할 값
 * @param delay 지연 시간 (밀리초)
 * @returns 지연된 값
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    // 지정된 지연 시간 후에 값 업데이트
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // 타이머 정리
    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}

export default useDebounce;
