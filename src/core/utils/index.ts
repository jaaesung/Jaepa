/**
 * 유틸리티 모듈
 * 
 * 애플리케이션 전체에서 사용되는 유틸리티 함수를 제공합니다.
 */

import logger from './logger';

// 날짜 포맷팅 함수
export const formatDate = (date: string | Date, format: string = 'YYYY-MM-DD'): string => {
  const d = new Date(date);
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');
  
  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
};

// 숫자 포맷팅 함수
export const formatNumber = (num: number, options: Intl.NumberFormatOptions = {}): string => {
  return new Intl.NumberFormat('ko-KR', options).format(num);
};

// 통화 포맷팅 함수
export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency,
  }).format(amount);
};

// 퍼센트 포맷팅 함수
export const formatPercent = (value: number, fractionDigits: number = 2): string => {
  return new Intl.NumberFormat('ko-KR', {
    style: 'percent',
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  }).format(value / 100);
};

// 문자열 자르기 함수
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

// 객체 깊은 복사 함수
export const deepClone = <T>(obj: T): T => {
  return JSON.parse(JSON.stringify(obj));
};

// 배열 셔플 함수
export const shuffleArray = <T>(array: T[]): T[] => {
  const newArray = [...array];
  for (let i = newArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
  }
  return newArray;
};

// 디바운스 함수
export const debounce = <F extends (...args: any[]) => any>(
  func: F,
  waitFor: number
): ((...args: Parameters<F>) => void) => {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  
  return (...args: Parameters<F>): void => {
    if (timeout !== null) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(() => func(...args), waitFor);
  };
};

// 쓰로틀 함수
export const throttle = <F extends (...args: any[]) => any>(
  func: F,
  waitFor: number
): ((...args: Parameters<F>) => void) => {
  let lastTime = 0;
  
  return (...args: Parameters<F>): void => {
    const now = Date.now();
    if (now - lastTime >= waitFor) {
      func(...args);
      lastTime = now;
    }
  };
};

export { logger };
