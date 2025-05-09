/**
 * 홈페이지 컴포넌트
 * 
 * 애플리케이션의 메인 랜딩 페이지를 제공합니다.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { Header, Footer } from '../../components/layout';
import { Button } from '../../components/ui';
import './HomePage.css';

/**
 * 홈페이지 컴포넌트
 */
const HomePage: React.FC = () => {
  return (
    <div className="home-page">
      <Header />
      
      <main className="home-content">
        <section className="hero-section">
          <div className="hero-container">
            <div className="hero-content">
              <h1 className="hero-title">금융 뉴스 감성 분석으로 투자 인사이트 발견</h1>
              <p className="hero-description">
                JaePa는 최신 금융 뉴스를 수집하고 AI 기반 감성 분석을 통해 주식 시장 트렌드를 예측하는 플랫폼입니다.
                데이터 기반 투자 결정을 내리는 데 도움이 되는 인사이트를 발견하세요.
              </p>
              <div className="hero-buttons">
                <Link to="/dashboard">
                  <Button variant="primary" size="large">시작하기</Button>
                </Link>
                <Link to="/about">
                  <Button variant="outline" size="large">더 알아보기</Button>
                </Link>
              </div>
            </div>
            <div className="hero-image">
              <img src="/assets/images/hero-image.svg" alt="JaePa 플랫폼 미리보기" />
            </div>
          </div>
        </section>
        
        <section className="features-section">
          <div className="container">
            <h2 className="section-title">주요 기능</h2>
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">📰</div>
                <h3 className="feature-title">뉴스 수집</h3>
                <p className="feature-description">
                  다양한 금융 뉴스 소스에서 실시간으로 최신 뉴스를 수집하고 분석합니다.
                </p>
              </div>
              
              <div className="feature-card">
                <div className="feature-icon">🔍</div>
                <h3 className="feature-title">감성 분석</h3>
                <p className="feature-description">
                  FinBERT 모델을 활용한 금융 특화 감성 분석으로 뉴스의 긍정/부정 감성을 파악합니다.
                </p>
              </div>
              
              <div className="feature-card">
                <div className="feature-icon">📈</div>
                <h3 className="feature-title">주식 데이터</h3>
                <p className="feature-description">
                  실시간 주식 데이터와 기술적 지표를 제공하여 시장 동향을 파악할 수 있습니다.
                </p>
              </div>
              
              <div className="feature-card">
                <div className="feature-icon">📊</div>
                <h3 className="feature-title">데이터 시각화</h3>
                <p className="feature-description">
                  직관적인 차트와 그래프로 복잡한 금융 데이터를 쉽게 이해할 수 있습니다.
                </p>
              </div>
            </div>
          </div>
        </section>
        
        <section className="how-it-works-section">
          <div className="container">
            <h2 className="section-title">작동 방식</h2>
            <div className="steps">
              <div className="step">
                <div className="step-number">1</div>
                <h3 className="step-title">뉴스 수집</h3>
                <p className="step-description">
                  다양한 금융 뉴스 소스에서 최신 뉴스를 자동으로 수집합니다.
                </p>
              </div>
              
              <div className="step">
                <div className="step-number">2</div>
                <h3 className="step-title">감성 분석</h3>
                <p className="step-description">
                  FinBERT 모델을 사용하여 뉴스 기사의 감성을 분석합니다.
                </p>
              </div>
              
              <div className="step">
                <div className="step-number">3</div>
                <h3 className="step-title">데이터 통합</h3>
                <p className="step-description">
                  감성 분석 결과와 주식 데이터를 통합하여 상관관계를 파악합니다.
                </p>
              </div>
              
              <div className="step">
                <div className="step-number">4</div>
                <h3 className="step-title">인사이트 제공</h3>
                <p className="step-description">
                  데이터 기반 인사이트를 통해 투자 결정에 도움을 줍니다.
                </p>
              </div>
            </div>
          </div>
        </section>
        
        <section className="cta-section">
          <div className="container">
            <div className="cta-content">
              <h2 className="cta-title">지금 바로 시작하세요</h2>
              <p className="cta-description">
                JaePa와 함께 데이터 기반 투자 결정을 내리고 더 나은 투자 성과를 달성하세요.
              </p>
              <div className="cta-buttons">
                <Link to="/register">
                  <Button variant="primary" size="large">무료로 시작하기</Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
};

export default HomePage;
