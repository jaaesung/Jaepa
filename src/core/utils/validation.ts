/**
 * 유효성 검사 유틸리티 모듈
 * 
 * 다양한 데이터 유효성 검사 유틸리티 함수를 제공합니다.
 */

/**
 * 이메일 주소 유효성 검사
 * 
 * @param email 검사할 이메일 주소
 * @returns 유효성 여부
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
};

/**
 * 비밀번호 유효성 검사
 * 최소 8자, 최소 하나의 문자, 하나의 숫자, 하나의 특수문자 포함
 * 
 * @param password 검사할 비밀번호
 * @returns 유효성 여부
 */
export const isValidPassword = (password: string): boolean => {
  const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
  return passwordRegex.test(password);
};

/**
 * 전화번호 유효성 검사
 * 
 * @param phoneNumber 검사할 전화번호
 * @returns 유효성 여부
 */
export const isValidPhoneNumber = (phoneNumber: string): boolean => {
  // 한국 전화번호 형식 (01X-XXXX-XXXX 또는 01X-XXX-XXXX)
  const phoneRegex = /^01([0|1|6|7|8|9])-?([0-9]{3,4})-?([0-9]{4})$/;
  return phoneRegex.test(phoneNumber);
};

/**
 * URL 유효성 검사
 * 
 * @param url 검사할 URL
 * @returns 유효성 여부
 */
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch (error) {
    return false;
  }
};

/**
 * 날짜 유효성 검사
 * 
 * @param date 검사할 날짜 문자열
 * @returns 유효성 여부
 */
export const isValidDate = (date: string): boolean => {
  const d = new Date(date);
  return !isNaN(d.getTime());
};

/**
 * 숫자 유효성 검사
 * 
 * @param value 검사할 값
 * @returns 유효성 여부
 */
export const isValidNumber = (value: any): boolean => {
  return !isNaN(parseFloat(value)) && isFinite(value);
};

/**
 * 정수 유효성 검사
 * 
 * @param value 검사할 값
 * @returns 유효성 여부
 */
export const isValidInteger = (value: any): boolean => {
  return Number.isInteger(Number(value));
};

/**
 * 양의 숫자 유효성 검사
 * 
 * @param value 검사할 값
 * @returns 유효성 여부
 */
export const isPositiveNumber = (value: any): boolean => {
  return isValidNumber(value) && parseFloat(value) > 0;
};

/**
 * 양의 정수 유효성 검사
 * 
 * @param value 검사할 값
 * @returns 유효성 여부
 */
export const isPositiveInteger = (value: any): boolean => {
  return isValidInteger(value) && Number(value) > 0;
};

/**
 * 비어있지 않은 문자열 검사
 * 
 * @param value 검사할 값
 * @returns 유효성 여부
 */
export const isNotEmptyString = (value: any): boolean => {
  return typeof value === 'string' && value.trim().length > 0;
};

/**
 * 객체 필드 필수 값 검사
 * 
 * @param obj 검사할 객체
 * @param fields 필수 필드 배열
 * @returns 유효성 여부
 */
export const hasRequiredFields = (obj: any, fields: string[]): boolean => {
  if (!obj || typeof obj !== 'object') return false;
  
  return fields.every(field => {
    const value = obj[field];
    
    if (value === undefined || value === null) return false;
    
    if (typeof value === 'string') return value.trim().length > 0;
    
    return true;
  });
};

/**
 * 배열 유효성 검사
 * 
 * @param value 검사할 값
 * @returns 유효성 여부
 */
export const isValidArray = (value: any): boolean => {
  return Array.isArray(value);
};

/**
 * 비어있지 않은 배열 검사
 * 
 * @param value 검사할 값
 * @returns 유효성 여부
 */
export const isNotEmptyArray = (value: any): boolean => {
  return isValidArray(value) && value.length > 0;
};

/**
 * 객체 유효성 검사
 * 
 * @param value 검사할 값
 * @returns 유효성 여부
 */
export const isValidObject = (value: any): boolean => {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
};

/**
 * 비어있지 않은 객체 검사
 * 
 * @param value 검사할 값
 * @returns 유효성 여부
 */
export const isNotEmptyObject = (value: any): boolean => {
  return isValidObject(value) && Object.keys(value).length > 0;
};

/**
 * 주민등록번호 유효성 검사
 * 
 * @param value 검사할 주민등록번호
 * @returns 유효성 여부
 */
export const isValidResidentNumber = (value: string): boolean => {
  // 하이픈 제거
  const ssn = value.replace(/-/g, '');
  
  // 길이 검사
  if (ssn.length !== 13) return false;
  
  // 숫자만 포함되어 있는지 검사
  if (!/^\d+$/.test(ssn)) return false;
  
  // 검증 로직
  const weights = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5];
  let sum = 0;
  
  for (let i = 0; i < 12; i++) {
    sum += parseInt(ssn.charAt(i)) * weights[i];
  }
  
  const checkDigit = (11 - (sum % 11)) % 10;
  
  return parseInt(ssn.charAt(12)) === checkDigit;
};

/**
 * 사업자등록번호 유효성 검사
 * 
 * @param value 검사할 사업자등록번호
 * @returns 유효성 여부
 */
export const isValidBusinessNumber = (value: string): boolean => {
  // 하이픈 제거
  const bizNum = value.replace(/-/g, '');
  
  // 길이 검사
  if (bizNum.length !== 10) return false;
  
  // 숫자만 포함되어 있는지 검사
  if (!/^\d+$/.test(bizNum)) return false;
  
  // 검증 로직
  const weights = [1, 3, 7, 1, 3, 7, 1, 3, 5];
  let sum = 0;
  
  for (let i = 0; i < 9; i++) {
    sum += parseInt(bizNum.charAt(i)) * weights[i];
  }
  
  sum += parseInt(bizNum.charAt(8)) * 5 / 10;
  
  const checkDigit = (10 - (sum % 10)) % 10;
  
  return parseInt(bizNum.charAt(9)) === checkDigit;
};
