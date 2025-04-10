/**
 * 숫자를 통화 형식으로 포맷팅 (예: '1,234.56')
 * @param number - 포맷팅할 숫자
 * @param currency - 통화 기호 (예: '$', '₩')
 * @param decimals - 소수점 자릿수
 * @returns 포맷팅된 통화 문자열
 */
export const formatCurrency = (number: number | null | undefined, currency: string = '', decimals: number = 2): string => {
  if (number === null || number === undefined) return '';
  
  const formatted = Number(number).toLocaleString('ko-KR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  
  return currency ? `${currency}${formatted}` : formatted;
};

/**
 * 퍼센트 값 포맷팅 (예: '12.34%')
 * @param value - 포맷팅할 값 (0.1234 형식)
 * @param decimals - 소수점 자릿수
 * @returns 포맷팅된 퍼센트 문자열
 */
export const formatPercent = (value: number | null | undefined, decimals: number = 2): string => {
  if (value === null || value === undefined) return '';
  
  const percentValue = value * 100;
  return `${percentValue.toFixed(decimals)}%`;
};

/**
 * 큰 숫자 약식 표현 (예: '1.2M', '5.4K')
 * @param number - 포맷팅할 숫자
 * @param decimals - 소수점 자릿수
 * @returns 약식 표현 문자열
 */
export const formatCompact = (number: number | null | undefined, decimals: number = 1): string => {
  if (number === null || number === undefined) return '';
  
  const absNumber = Math.abs(number);
  const sign = number < 0 ? '-' : '';
  
  if (absNumber >= 1000000000) {
    return `${sign}${(absNumber / 1000000000).toFixed(decimals)}B`;
  } else if (absNumber >= 1000000) {
    return `${sign}${(absNumber / 1000000).toFixed(decimals)}M`;
  } else if (absNumber >= 1000) {
    return `${sign}${(absNumber / 1000).toFixed(decimals)}K`;
  } else {
    return `${sign}${absNumber.toFixed(decimals)}`;
  }
};

/**
 * 문자열 길이 제한 및 말줄임표 추가
 * @param text - 원본 문자열
 * @param maxLength - 최대 길이
 * @returns 제한된 문자열
 */
export const truncateText = (text: string | null | undefined, maxLength: number): string => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
};

/**
 * 감성 점수를 라벨로 변환
 * @param score - 감성 점수 (-1.0 ~ 1.0)
 * @returns 감성 라벨 (Negative, Neutral, Positive)
 */
export const sentimentToLabel = (score: number): string => {
  if (score < -0.3) return 'Negative';
  if (score > 0.3) return 'Positive';
  return 'Neutral';
};

/**
 * 감성 점수에 따른 색상 코드 반환
 * @param score - 감성 점수 (-1.0 ~ 1.0)
 * @returns 색상 코드
 */
export const sentimentToColor = (score: number): string => {
  if (score < -0.3) return '#ff4d4f'; // 빨간색 (부정)
  if (score > 0.3) return '#52c41a'; // 녹색 (긍정)
  return '#faad14'; // 노란색 (중립)
};

/**
 * 숫자에 단위 추가 (예: '1,234 USD', '5,678 KRW')
 * @param number - 포맷팅할 숫자
 * @param unit - 단위 문자열
 * @param decimals - 소수점 자릿수
 * @returns 단위가 추가된 문자열
 */
export const formatWithUnit = (number: number | null | undefined, unit: string, decimals: number = 0): string => {
  if (number === null || number === undefined) return '';
  
  const formatted = Number(number).toLocaleString('ko-KR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  
  return `${formatted} ${unit}`;
};