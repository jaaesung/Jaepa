/**
 * 인증 레이아웃 컴포넌트
 */

import React from 'react';
import './AuthLayout.css';

export interface AuthLayoutProps {
  children: React.ReactNode;
}

/**
 * 인증 레이아웃
 * 
 * 로그인/회원가입 등 인증 관련 페이지에 사용하는 레이아웃
 */
const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <div className="auth-layout">
      <div className="auth-layout-header">
        <div className="auth-layout-logo">
          <h1>JaePa</h1>
          <p>금융 뉴스 감성 분석 도구</p>
        </div>
      </div>
      <div className="auth-layout-content">
        {children}
      </div>
      <div className="auth-layout-footer">
        <p>&copy; 2025 JaePa. All rights reserved.</p>
      </div>
    </div>
  );
};

export default AuthLayout;
