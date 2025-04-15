import React from 'react';
import { Link } from 'react-router-dom';
import './MainPage.css';

/**
 * 메인 페이지 컴포넌트
 */
const MainPage: React.FC = () => {
  return (
    <div className="main-page">
      <div className="main-content">
        <h1 className="main-title">JaePa</h1>
        <h2 className="main-subtitle">금융 데이터 분석 플랫폼</h2>
        
        <p className="main-description">
          JaePa는 최신 금융 뉴스와 주식 데이터를 분석하여 투자 결정에 도움을 주는 플랫폼입니다.
          FinBERT 모델과 Polygon API를 활용하여 정확한 분석 결과를 제공합니다.
        </p>
        
        <div className="main-features">
          <div className="feature-card">
            <h3>뉴스 분석</h3>
            <p>금융 뉴스의 감성을 분석하여 시장 동향을 파악합니다.</p>
          </div>
          
          <div className="feature-card">
            <h3>주식 분석</h3>
            <p>주식 데이터를 분석하여 투자 기회를 발견합니다.</p>
          </div>
          
          <div className="feature-card">
            <h3>상관관계 분석</h3>
            <p>뉴스 감성과 주가 변동의 상관관계를 분석합니다.</p>
          </div>
        </div>
        
        <div className="main-actions">
          <Link to="/login" className="action-button login-button">로그인</Link>
          <Link to="/register" className="action-button register-button">회원가입</Link>
        </div>
      </div>
    </div>
  );
};

export default MainPage;
