/**
 * 개발 환경에서만 로그를 출력하는 로거 유틸리티
 */
const isDevelopment = process.env.NODE_ENV === 'development';

/**
 * 개발 환경에서만 로그를 출력하는 함수
 * @param message 로그 메시지
 * @param optionalParams 추가 매개변수
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const log = (message?: any, ...optionalParams: any[]): void => {
  if (isDevelopment) {
    console.log(message, ...optionalParams);
  }
};

/**
 * 개발 환경에서만 에러 로그를 출력하는 함수
 * @param message 에러 메시지
 * @param optionalParams 추가 매개변수
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const error = (message?: any, ...optionalParams: any[]): void => {
  if (isDevelopment) {
    console.error(message, ...optionalParams);
  }
};

/**
 * 개발 환경에서만 경고 로그를 출력하는 함수
 * @param message 경고 메시지
 * @param optionalParams 추가 매개변수
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const warn = (message?: any, ...optionalParams: any[]): void => {
  if (isDevelopment) {
    console.warn(message, ...optionalParams);
  }
};

/**
 * 개발 환경에서만 정보 로그를 출력하는 함수
 * @param message 정보 메시지
 * @param optionalParams 추가 매개변수
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const info = (message?: any, ...optionalParams: any[]): void => {
  if (isDevelopment) {
    console.info(message, ...optionalParams);
  }
};

const logger = {
  log,
  error,
  warn,
  info,
};

export default logger;
