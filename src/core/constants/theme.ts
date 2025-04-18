/**
 * 테마 관련 상수 모듈
 * 
 * 애플리케이션의 테마 관련 상수를 정의합니다.
 */

// 테마 타입
export type ThemeType = 'light' | 'dark';

// 테마 모드
export const THEME_MODES = {
  LIGHT: 'light' as ThemeType,
  DARK: 'dark' as ThemeType,
};

// 테마 색상
export const THEME_COLORS = {
  // 라이트 테마 색상
  LIGHT: {
    PRIMARY: '#1a73e8',
    PRIMARY_HOVER: '#1557b0',
    SECONDARY: '#f1f3f4',
    SECONDARY_HOVER: '#e8eaed',
    DANGER: '#ea4335',
    DANGER_HOVER: '#d93025',
    SUCCESS: '#34a853',
    SUCCESS_HOVER: '#2d9249',
    WARNING: '#fbbc04',
    WARNING_HOVER: '#f29900',
    TEXT: '#202124',
    TEXT_SECONDARY: '#5f6368',
    BORDER: '#dadce0',
    BACKGROUND: '#ffffff',
    BACKGROUND_LIGHT: '#f1f3f4',
    CARD_BACKGROUND: '#ffffff',
  },
  
  // 다크 테마 색상
  DARK: {
    PRIMARY: '#8ab4f8',
    PRIMARY_HOVER: '#aecbfa',
    SECONDARY: '#3c4043',
    SECONDARY_HOVER: '#4a4d51',
    DANGER: '#f28b82',
    DANGER_HOVER: '#ee675c',
    SUCCESS: '#81c995',
    SUCCESS_HOVER: '#5bb974',
    WARNING: '#fdd663',
    WARNING_HOVER: '#fcc934',
    TEXT: '#e8eaed',
    TEXT_SECONDARY: '#9aa0a6',
    BORDER: '#5f6368',
    BACKGROUND: '#202124',
    BACKGROUND_LIGHT: '#3c4043',
    CARD_BACKGROUND: '#2d2e31',
  },
};

// 테마 그림자
export const THEME_SHADOWS = {
  // 라이트 테마 그림자
  LIGHT: {
    SM: '0 1px 2px rgba(0, 0, 0, 0.1)',
    MD: '0 2px 4px rgba(0, 0, 0, 0.1)',
    LG: '0 4px 8px rgba(0, 0, 0, 0.1)',
    XL: '0 8px 16px rgba(0, 0, 0, 0.1)',
  },
  
  // 다크 테마 그림자
  DARK: {
    SM: '0 1px 2px rgba(0, 0, 0, 0.3)',
    MD: '0 2px 4px rgba(0, 0, 0, 0.3)',
    LG: '0 4px 8px rgba(0, 0, 0, 0.3)',
    XL: '0 8px 16px rgba(0, 0, 0, 0.3)',
  },
};

// 테마 폰트
export const THEME_FONTS = {
  FAMILY: {
    PRIMARY: "'Roboto', 'Noto Sans KR', sans-serif",
    MONOSPACE: "'Roboto Mono', monospace",
  },
  SIZE: {
    XS: '0.75rem',
    SM: '0.875rem',
    MD: '1rem',
    LG: '1.125rem',
    XL: '1.25rem',
    XXL: '1.5rem',
    XXXL: '2rem',
  },
  WEIGHT: {
    LIGHT: 300,
    REGULAR: 400,
    MEDIUM: 500,
    BOLD: 700,
  },
};

// 테마 간격
export const THEME_SPACING = {
  XS: '0.25rem',
  SM: '0.5rem',
  MD: '1rem',
  LG: '1.5rem',
  XL: '2rem',
  XXL: '3rem',
};

// 테마 반응형 브레이크포인트
export const THEME_BREAKPOINTS = {
  XS: '0px',
  SM: '576px',
  MD: '768px',
  LG: '992px',
  XL: '1200px',
  XXL: '1400px',
};

// 테마 전환 애니메이션
export const THEME_TRANSITIONS = {
  DURATION: {
    SHORT: '0.2s',
    MEDIUM: '0.3s',
    LONG: '0.5s',
  },
  EASING: {
    EASE: 'ease',
    EASE_IN: 'ease-in',
    EASE_OUT: 'ease-out',
    EASE_IN_OUT: 'ease-in-out',
    LINEAR: 'linear',
  },
};
