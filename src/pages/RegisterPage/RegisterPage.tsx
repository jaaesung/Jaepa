/**
 * 회원가입 페이지 컴포넌트
 * 
 * 사용자 회원가입을 위한 페이지를 제공합니다.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { Header, Footer } from '../../components/layout';
import { RegisterForm } from '../../features/auth';
import './RegisterPage.css';

/**
 * 회원가입 페이지 컴포넌트
 */
const RegisterPage: React.FC = () => {
  return (
    <div className="register-page">
      <Header />
      
      <main className="register-content">
        <div className="register-container">
          <div className="register-card">
            <div className="register-header">
              <h1 className="register-title">회원가입</h1>
              <p className="register-subtitle">JaePa 계정을 만들고 다양한 기능을 이용하세요</p>
            </div>
            
            <RegisterForm />
            
            <div className="register-footer">
              <p className="register-footer-text">
                이미 계정이 있으신가요? <Link to="/login" className="register-footer-link">로그인</Link>
              </p>
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default RegisterPage;
