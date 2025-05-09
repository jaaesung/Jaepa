/**
 * 포맷팅 유틸리티 모듈
 * 
 * 다양한 데이터 포맷팅 유틸리티 함수를 제공합니다.
 */

/**
 * 숫자를 통화 형식으로 포맷팅합니다.
 * 
 * @param value 포맷팅할 숫자
 * @param currency 통화 코드 (기본값: 'KRW')
 * @param locale 로케일 (기본값: 'ko-KR')
 * @returns 포맷팅된 통화 문자열
 */
export const formatCurrency = (
  value: number,
  currency: string = 'KRW',
  locale: string = 'ko-KR'
): string => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(value);
};

/**
 * 숫자를 천 단위 구분자가 있는 형식으로 포맷팅합니다.
 * 
 * @param value 포맷팅할 숫자
 * @param locale 로케일 (기본값: 'ko-KR')
 * @returns 포맷팅된 숫자 문자열
 */
export const formatNumber = (
  value: number,
  locale: string = 'ko-KR'
): string => {
  return new Intl.NumberFormat(locale).format(value);
};

/**
 * 숫자를 퍼센트 형식으로 포맷팅합니다.
 * 
 * @param value 포맷팅할 숫자 (0.01 = 1%)
 * @param fractionDigits 소수점 자릿수 (기본값: 2)
 * @param locale 로케일 (기본값: 'ko-KR')
 * @returns 포맷팅된 퍼센트 문자열
 */
export const formatPercent = (
  value: number,
  fractionDigits: number = 2,
  locale: string = 'ko-KR'
): string => {
  return new Intl.NumberFormat(locale, {
    style: 'percent',
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  }).format(value);
};

/**
 * 숫자를 소수점 자릿수를 지정하여 포맷팅합니다.
 * 
 * @param value 포맷팅할 숫자
 * @param fractionDigits 소수점 자릿수 (기본값: 2)
 * @param locale 로케일 (기본값: 'ko-KR')
 * @returns 포맷팅된 숫자 문자열
 */
export const formatDecimal = (
  value: number,
  fractionDigits: number = 2,
  locale: string = 'ko-KR'
): string => {
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  }).format(value);
};

/**
 * 큰 숫자를 약식으로 포맷팅합니다. (예: 1.2K, 3.5M, 2.7B)
 * 
 * @param value 포맷팅할 숫자
 * @param fractionDigits 소수점 자릿수 (기본값: 1)
 * @returns 포맷팅된 약식 숫자 문자열
 */
export const formatCompactNumber = (
  value: number,
  fractionDigits: number = 1
): string => {
  if (value < 1000) {
    return value.toString();
  }
  
  const tier = Math.floor(Math.log10(Math.abs(value)) / 3);
  const suffix = ['', 'K', 'M', 'B', 'T'][tier];
  const scale = Math.pow(10, tier * 3);
  
  const scaled = value / scale;
  
  return `${scaled.toFixed(fractionDigits)}${suffix}`;
};

/**
 * 파일 크기를 사람이 읽기 쉬운 형식으로 포맷팅합니다. (예: 1.5 KB, 3.2 MB)
 * 
 * @param bytes 바이트 단위의 파일 크기
 * @param fractionDigits 소수점 자릿수 (기본값: 2)
 * @returns 포맷팅된 파일 크기 문자열
 */
export const formatFileSize = (
  bytes: number,
  fractionDigits: number = 2
): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(fractionDigits))} ${sizes[i]}`;
};

/**
 * 전화번호를 포맷팅합니다.
 * 
 * @param phoneNumber 포맷팅할 전화번호
 * @param format 포맷 (기본값: 'XXX-XXXX-XXXX')
 * @returns 포맷팅된 전화번호 문자열
 */
export const formatPhoneNumber = (
  phoneNumber: string,
  format: string = 'XXX-XXXX-XXXX'
): string => {
  // 숫자만 추출
  const digits = phoneNumber.replace(/\D/g, '');
  
  if (!digits) return phoneNumber;
  
  let result = format;
  let digitIndex = 0;
  
  // X를 숫자로 대체
  for (let i = 0; i < result.length && digitIndex < digits.length; i++) {
    if (result[i] === 'X') {
      result = result.substring(0, i) + digits[digitIndex++] + result.substring(i + 1);
    }
  }
  
  // 남은 X 제거
  result = result.replace(/X+/g, '');
  
  return result;
};

/**
 * 문자열의 첫 글자를 대문자로 변환합니다.
 * 
 * @param str 변환할 문자열
 * @returns 첫 글자가 대문자인 문자열
 */
export const capitalizeFirstLetter = (str: string): string => {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1);
};

/**
 * 문자열을 주어진 길이로 자르고 말줄임표를 추가합니다.
 * 
 * @param str 자를 문자열
 * @param maxLength 최대 길이 (기본값: 50)
 * @param ellipsis 말줄임표 (기본값: '...')
 * @returns 잘린 문자열
 */
export const truncateString = (
  str: string,
  maxLength: number = 50,
  ellipsis: string = '...'
): string => {
  if (!str || str.length <= maxLength) return str;
  return str.slice(0, maxLength) + ellipsis;
};

/**
 * 문자열에서 HTML 태그를 제거합니다.
 * 
 * @param html HTML 문자열
 * @returns HTML 태그가 제거된 문자열
 */
export const stripHtmlTags = (html: string): string => {
  return html.replace(/<[^>]*>/g, '');
};

/**
 * 문자열을 슬러그 형식으로 변환합니다. (예: "Hello World" -> "hello-world")
 * 
 * @param str 변환할 문자열
 * @returns 슬러그 형식의 문자열
 */
export const slugify = (str: string): string => {
  return str
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // 특수문자 제거
    .replace(/\s+/g, '-') // 공백을 하이픈으로 변환
    .replace(/--+/g, '-') // 중복 하이픈 제거
    .trim();
};
