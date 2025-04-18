/**
 * 테마 컨텍스트 모듈
 * 
 * 애플리케이션 테마 관리를 위한 React 컨텍스트를 제공합니다.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { THEME_STORAGE_KEY, THEMES } from '../constants';

type ThemeType = typeof THEMES.LIGHT | typeof THEMES.DARK;

interface ThemeContextType {
  theme: ThemeType;
  toggleTheme: () => void;
  setTheme: (theme: ThemeType) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setTheme] = useState<ThemeType>(() => {
    // 로컬 스토리지에서 테마 설정 가져오기
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    return (savedTheme as ThemeType) || THEMES.LIGHT;
  });

  useEffect(() => {
    // 테마 변경 시 로컬 스토리지에 저장
    localStorage.setItem(THEME_STORAGE_KEY, theme);
    
    // 문서 루트에 테마 클래스 적용
    document.documentElement.classList.remove(THEMES.LIGHT, THEMES.DARK);
    document.documentElement.classList.add(theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => 
      prevTheme === THEMES.LIGHT ? THEMES.DARK : THEMES.LIGHT
    );
  };

  const value = {
    theme,
    toggleTheme,
    setTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export default ThemeContext;
