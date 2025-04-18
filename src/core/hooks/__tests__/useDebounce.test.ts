/**
 * useDebounce 훅 테스트
 */

import { renderHook, act } from '@testing-library/react';
import { useDebounce } from '../useDebounce';

// 타이머 모의 설정
jest.useFakeTimers();

describe('useDebounce Hook', () => {
  it('should return the initial value immediately', () => {
    const initialValue = 'initial';
    const { result } = renderHook(() => useDebounce(initialValue, 500));
    
    expect(result.current).toBe(initialValue);
  });

  it('should not update the value before the delay has elapsed', () => {
    const initialValue = 'initial';
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: initialValue, delay: 500 } }
    );
    
    // 값 변경
    rerender({ value: 'updated', delay: 500 });
    
    // 딜레이 시간 이전에는 초기값 유지
    expect(result.current).toBe(initialValue);
    
    // 300ms 진행 (아직 500ms에 도달하지 않음)
    act(() => {
      jest.advanceTimersByTime(300);
    });
    
    // 여전히 초기값 유지
    expect(result.current).toBe(initialValue);
  });

  it('should update the value after the delay has elapsed', () => {
    const initialValue = 'initial';
    const updatedValue = 'updated';
    const delay = 500;
    
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: initialValue, delay } }
    );
    
    // 값 변경
    rerender({ value: updatedValue, delay });
    
    // 딜레이 시간 이후에 값 업데이트
    act(() => {
      jest.advanceTimersByTime(delay);
    });
    
    // 업데이트된 값으로 변경
    expect(result.current).toBe(updatedValue);
  });

  it('should reset the timer when the value changes before the delay has elapsed', () => {
    const initialValue = 'initial';
    const firstUpdate = 'first update';
    const secondUpdate = 'second update';
    const delay = 500;
    
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: initialValue, delay } }
    );
    
    // 첫 번째 값 변경
    rerender({ value: firstUpdate, delay });
    
    // 300ms 진행 (아직 500ms에 도달하지 않음)
    act(() => {
      jest.advanceTimersByTime(300);
    });
    
    // 두 번째 값 변경 (타이머 리셋)
    rerender({ value: secondUpdate, delay });
    
    // 추가 300ms 진행 (첫 번째 타이머는 600ms가 되었지만, 두 번째 타이머는 300ms)
    act(() => {
      jest.advanceTimersByTime(300);
    });
    
    // 두 번째 타이머가 아직 완료되지 않았으므로 초기값 유지
    expect(result.current).toBe(initialValue);
    
    // 추가 200ms 진행 (두 번째 타이머가 500ms에 도달)
    act(() => {
      jest.advanceTimersByTime(200);
    });
    
    // 두 번째 업데이트된 값으로 변경
    expect(result.current).toBe(secondUpdate);
  });

  it('should handle delay changes', () => {
    const initialValue = 'initial';
    const updatedValue = 'updated';
    const initialDelay = 500;
    const updatedDelay = 1000;
    
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: initialValue, delay: initialDelay } }
    );
    
    // 값 변경 및 딜레이 변경
    rerender({ value: updatedValue, delay: updatedDelay });
    
    // 초기 딜레이 시간 이후에도 값 유지
    act(() => {
      jest.advanceTimersByTime(initialDelay);
    });
    
    // 아직 업데이트된 딜레이에 도달하지 않았으므로 초기값 유지
    expect(result.current).toBe(initialValue);
    
    // 업데이트된 딜레이 시간까지 진행
    act(() => {
      jest.advanceTimersByTime(updatedDelay - initialDelay);
    });
    
    // 업데이트된 값으로 변경
    expect(result.current).toBe(updatedValue);
  });

  it('should clean up the timer on unmount', () => {
    const clearTimeoutSpy = jest.spyOn(window, 'clearTimeout');
    
    const { unmount } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'test', delay: 500 } }
    );
    
    // 컴포넌트 언마운트
    unmount();
    
    // clearTimeout이 호출되었는지 확인
    expect(clearTimeoutSpy).toHaveBeenCalled();
    
    clearTimeoutSpy.mockRestore();
  });
});
