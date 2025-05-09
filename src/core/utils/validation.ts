/**
 * 입력값 검증 유틸리티
 */

export const validationUtils = {
  /**
   * 이메일 검증
   */
  isValidEmail: (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  /**
   * 비밀번호 검증
   * - 최소 8자 이상
   * - 최소 1개의 숫자 포함
   * - 최소 1개의 특수 문자 포함
   */
  isValidPassword: (password: string): boolean => {
    if (password.length < 8) return false;
    
    const hasNumber = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    
    return hasNumber && hasSpecialChar;
  },

  /**
   * 비밀번호 강도 검사
   * @returns 0-4 사이의 숫자 (0: 매우 약함, 4: 매우 강함)
   */
  getPasswordStrength: (password: string): number => {
    let strength = 0;
    
    if (password.length >= 8) strength += 1;
    if (password.length >= 12) strength += 1;
    if (/\d/.test(password)) strength += 1;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength += 1;
    if (/[A-Z]/.test(password) && /[a-z]/.test(password)) strength += 1;
    
    return Math.min(4, strength);
  },

  /**
   * 필수 필드 검증
   */
  isRequired: (value: string): boolean => {
    return value.trim().length > 0;
  },

  /**
   * 두 값이 일치하는지 검증
   */
  isMatching: (value1: string, value2: string): boolean => {
    return value1 === value2;
  },

  /**
   * 최소 길이 검증
   */
  minLength: (value: string, min: number): boolean => {
    return value.length >= min;
  },

  /**
   * 최대 길이 검증
   */
  maxLength: (value: string, max: number): boolean => {
    return value.length <= max;
  }
};
