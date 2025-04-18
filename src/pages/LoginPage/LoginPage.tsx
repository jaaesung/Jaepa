/**
 * 로그인 페이지 컴포넌트
 * 
 * 사용자 로그인을 위한 페이지를 제공합니다.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { Header, Footer } from '../../components/layout';
import { LoginForm } from '../../features/auth';
import './LoginPage.css';

/**
 * 로그인 페이지 컴포넌트
 */
const LoginPage: React.FC = () => {
  return (
    <div className="login-page">
      <Header />
      
      <main className="login-content">
        <div className="login-container">
          <div className="login-card">
            <div className="login-header">
              <h1 className="login-title">로그인</h1>
              <p className="login-subtitle">JaePa 계정으로 로그인하세요</p>
            </div>
            
            <LoginForm />
            
            <div className="login-footer">
              <p className="login-footer-text">
                계정이 없으신가요? <Link to="/register" className="login-footer-link">회원가입</Link>
              </p>
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default LoginPage;
