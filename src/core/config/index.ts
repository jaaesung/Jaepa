/**
 * 애플리케이션 설정 모듈
 * 
 * 환경 변수 및 설정 값을 관리합니다.
 */

// 환경 변수
export const ENV = process.env.NODE_ENV || 'development';
export const IS_DEV = ENV === 'development';
export const IS_PROD = ENV === 'production';
export const IS_TEST = ENV === 'test';

// API 설정
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
export const API_TIMEOUT = 30000; // 30초

// 앱 설정
export const APP_NAME = 'JaePa';
export const APP_VERSION = '0.1.0';

// 기본 설정 객체
export const config = {
  env: ENV,
  isDev: IS_DEV,
  isProd: IS_PROD,
  isTest: IS_TEST,
  api: {
    url: API_URL,
    timeout: API_TIMEOUT,
  },
  app: {
    name: APP_NAME,
    version: APP_VERSION,
  },
};

export default config;
