/**
 * useLocalStorage 훅 테스트
 */

import { renderHook, act } from '@testing-library/react';
import { useLocalStorage } from '../useLocalStorage';

describe('useLocalStorage Hook', () => {
  beforeEach(() => {
    // 각 테스트 전에 로컬 스토리지 초기화
    window.localStorage.clear();
    jest.clearAllMocks();
  });

  it('should return the initial value when no stored value exists', () => {
    const key = 'testKey';
    const initialValue = 'initialValue';
    
    const { result } = renderHook(() => useLocalStorage(key, initialValue));
    
    expect(result.current[0]).toBe(initialValue);
  });

  it('should return the stored value when it exists', () => {
    const key = 'testKey';
    const storedValue = 'storedValue';
    const initialValue = 'initialValue';
    
    // 로컬 스토리지에 값 저장
    window.localStorage.setItem(key, JSON.stringify(storedValue));
    
    const { result } = renderHook(() => useLocalStorage(key, initialValue));
    
    expect(result.current[0]).toBe(storedValue);
  });

  it('should update the stored value and state when setValue is called', () => {
    const key = 'testKey';
    const initialValue = 'initialValue';
    const newValue = 'newValue';
    
    const { result } = renderHook(() => useLocalStorage(key, initialValue));
    
    // 값 업데이트
    act(() => {
      result.current[1](newValue);
    });
    
    // 상태 업데이트 확인
    expect(result.current[0]).toBe(newValue);
    
    // 로컬 스토리지 업데이트 확인
    expect(JSON.parse(window.localStorage.getItem(key) as string)).toBe(newValue);
  });

  it('should handle function updates correctly', () => {
    const key = 'testKey';
    const initialValue = { count: 0 };
    
    const { result } = renderHook(() => useLocalStorage(key, initialValue));
    
    // 함수를 사용하여 값 업데이트
    act(() => {
      result.current[1](prev => ({ count: prev.count + 1 }));
    });
    
    // 상태 업데이트 확인
    expect(result.current[0]).toEqual({ count: 1 });
    
    // 로컬 스토리지 업데이트 확인
    expect(JSON.parse(window.localStorage.getItem(key) as string)).toEqual({ count: 1 });
  });

  it('should handle complex objects correctly', () => {
    const key = 'testObject';
    const initialValue = { 
      name: 'Test', 
      details: { 
        age: 30, 
        address: { 
          city: 'Seoul', 
          country: 'Korea' 
        } 
      },
      tags: ['tag1', 'tag2']
    };
    
    const { result } = renderHook(() => useLocalStorage(key, initialValue));
    
    // 초기값 확인
    expect(result.current[0]).toEqual(initialValue);
    
    // 복잡한 객체 업데이트
    const updatedValue = {
      ...initialValue,
      details: {
        ...initialValue.details,
        age: 31,
        address: {
          ...initialValue.details.address,
          city: 'Busan'
        }
      },
      tags: [...initialValue.tags, 'tag3']
    };
    
    act(() => {
      result.current[1](updatedValue);
    });
    
    // 상태 업데이트 확인
    expect(result.current[0]).toEqual(updatedValue);
    
    // 로컬 스토리지 업데이트 확인
    expect(JSON.parse(window.localStorage.getItem(key) as string)).toEqual(updatedValue);
  });

  it('should handle parsing errors by returning the initial value', () => {
    const key = 'invalidJson';
    const initialValue = 'initialValue';
    
    // 유효하지 않은 JSON 저장
    window.localStorage.setItem(key, '{invalid json}');
    
    // 콘솔 에러 모의
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    const { result } = renderHook(() => useLocalStorage(key, initialValue));
    
    // 초기값 반환 확인
    expect(result.current[0]).toBe(initialValue);
    
    // 에러 로깅 확인
    expect(consoleErrorSpy).toHaveBeenCalled();
    
    consoleErrorSpy.mockRestore();
  });

  it('should remove the item from localStorage when setValue is called with null', () => {
    const key = 'testKey';
    const initialValue = 'initialValue';
    
    const { result } = renderHook(() => useLocalStorage(key, initialValue));
    
    // null로 값 업데이트
    act(() => {
      result.current[1](null);
    });
    
    // 상태 업데이트 확인
    expect(result.current[0]).toBeNull();
    
    // 로컬 스토리지에서 항목 제거 확인
    expect(window.localStorage.getItem(key)).toBeNull();
  });
});
