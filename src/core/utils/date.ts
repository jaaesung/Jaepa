/**
 * 날짜 유틸리티 모듈
 * 
 * 날짜 관련 유틸리티 함수를 제공합니다.
 */

/**
 * 날짜를 포맷팅합니다.
 * 
 * @param date 포맷팅할 날짜
 * @param format 날짜 포맷 (기본값: 'YYYY-MM-DD')
 * @returns 포맷팅된 날짜 문자열
 */
export const formatDate = (
  date: Date | string | number,
  format: string = 'YYYY-MM-DD'
): string => {
  const d = new Date(date);
  
  if (isNaN(d.getTime())) {
    return 'Invalid Date';
  }
  
  const year = d.getFullYear();
  const month = d.getMonth() + 1;
  const day = d.getDate();
  const hours = d.getHours();
  const minutes = d.getMinutes();
  const seconds = d.getSeconds();
  
  const pad = (num: number): string => (num < 10 ? `0${num}` : `${num}`);
  
  return format
    .replace('YYYY', year.toString())
    .replace('YY', year.toString().slice(-2))
    .replace('MM', pad(month))
    .replace('M', month.toString())
    .replace('DD', pad(day))
    .replace('D', day.toString())
    .replace('HH', pad(hours))
    .replace('H', hours.toString())
    .replace('hh', pad(hours % 12 || 12))
    .replace('h', (hours % 12 || 12).toString())
    .replace('mm', pad(minutes))
    .replace('m', minutes.toString())
    .replace('ss', pad(seconds))
    .replace('s', seconds.toString())
    .replace('A', hours >= 12 ? 'PM' : 'AM')
    .replace('a', hours >= 12 ? 'pm' : 'am');
};

/**
 * 상대적인 시간을 반환합니다. (예: '3시간 전', '2일 전')
 * 
 * @param date 기준 날짜
 * @param baseDate 비교 날짜 (기본값: 현재 시간)
 * @returns 상대적인 시간 문자열
 */
export const getRelativeTime = (
  date: Date | string | number,
  baseDate: Date | string | number = new Date()
): string => {
  const d1 = new Date(date);
  const d2 = new Date(baseDate);
  
  if (isNaN(d1.getTime()) || isNaN(d2.getTime())) {
    return 'Invalid Date';
  }
  
  const diffInSeconds = Math.floor((d2.getTime() - d1.getTime()) / 1000);
  
  if (diffInSeconds < 60) {
    return `${diffInSeconds}초 전`;
  }
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes}분 전`;
  }
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours}시간 전`;
  }
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 30) {
    return `${diffInDays}일 전`;
  }
  
  const diffInMonths = Math.floor(diffInDays / 30);
  if (diffInMonths < 12) {
    return `${diffInMonths}개월 전`;
  }
  
  const diffInYears = Math.floor(diffInMonths / 12);
  return `${diffInYears}년 전`;
};

/**
 * 날짜가 오늘인지 확인합니다.
 * 
 * @param date 확인할 날짜
 * @returns 오늘 여부
 */
export const isToday = (date: Date | string | number): boolean => {
  const d = new Date(date);
  const today = new Date();
  
  return (
    d.getDate() === today.getDate() &&
    d.getMonth() === today.getMonth() &&
    d.getFullYear() === today.getFullYear()
  );
};

/**
 * 날짜가 어제인지 확인합니다.
 * 
 * @param date 확인할 날짜
 * @returns 어제 여부
 */
export const isYesterday = (date: Date | string | number): boolean => {
  const d = new Date(date);
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  
  return (
    d.getDate() === yesterday.getDate() &&
    d.getMonth() === yesterday.getMonth() &&
    d.getFullYear() === yesterday.getFullYear()
  );
};

/**
 * 날짜가 이번 주인지 확인합니다.
 * 
 * @param date 확인할 날짜
 * @returns 이번 주 여부
 */
export const isThisWeek = (date: Date | string | number): boolean => {
  const d = new Date(date);
  const now = new Date();
  
  const startOfWeek = new Date(now);
  startOfWeek.setDate(now.getDate() - now.getDay());
  startOfWeek.setHours(0, 0, 0, 0);
  
  const endOfWeek = new Date(startOfWeek);
  endOfWeek.setDate(startOfWeek.getDate() + 7);
  
  return d >= startOfWeek && d < endOfWeek;
};

/**
 * 날짜가 이번 달인지 확인합니다.
 * 
 * @param date 확인할 날짜
 * @returns 이번 달 여부
 */
export const isThisMonth = (date: Date | string | number): boolean => {
  const d = new Date(date);
  const now = new Date();
  
  return (
    d.getMonth() === now.getMonth() &&
    d.getFullYear() === now.getFullYear()
  );
};

/**
 * 날짜가 이번 년도인지 확인합니다.
 * 
 * @param date 확인할 날짜
 * @returns 이번 년도 여부
 */
export const isThisYear = (date: Date | string | number): boolean => {
  const d = new Date(date);
  const now = new Date();
  
  return d.getFullYear() === now.getFullYear();
};

/**
 * 두 날짜 사이의 일수를 계산합니다.
 * 
 * @param startDate 시작 날짜
 * @param endDate 종료 날짜
 * @returns 일수
 */
export const getDaysBetween = (
  startDate: Date | string | number,
  endDate: Date | string | number
): number => {
  const d1 = new Date(startDate);
  const d2 = new Date(endDate);
  
  if (isNaN(d1.getTime()) || isNaN(d2.getTime())) {
    return 0;
  }
  
  // 시간, 분, 초, 밀리초를 0으로 설정하여 날짜만 비교
  d1.setHours(0, 0, 0, 0);
  d2.setHours(0, 0, 0, 0);
  
  const diffInTime = Math.abs(d2.getTime() - d1.getTime());
  return Math.floor(diffInTime / (1000 * 60 * 60 * 24));
};

/**
 * 날짜에 일수를 더합니다.
 * 
 * @param date 기준 날짜
 * @param days 더할 일수
 * @returns 계산된 날짜
 */
export const addDays = (
  date: Date | string | number,
  days: number
): Date => {
  const d = new Date(date);
  d.setDate(d.getDate() + days);
  return d;
};

/**
 * 날짜에 월수를 더합니다.
 * 
 * @param date 기준 날짜
 * @param months 더할 월수
 * @returns 계산된 날짜
 */
export const addMonths = (
  date: Date | string | number,
  months: number
): Date => {
  const d = new Date(date);
  d.setMonth(d.getMonth() + months);
  return d;
};

/**
 * 날짜에 년수를 더합니다.
 * 
 * @param date 기준 날짜
 * @param years 더할 년수
 * @returns 계산된 날짜
 */
export const addYears = (
  date: Date | string | number,
  years: number
): Date => {
  const d = new Date(date);
  d.setFullYear(d.getFullYear() + years);
  return d;
};
