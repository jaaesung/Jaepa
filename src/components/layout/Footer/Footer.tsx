/**
 * 푸터 컴포넌트
 * 
 * 애플리케이션의 하단 푸터를 제공합니다.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

/**
 * 푸터 컴포넌트
 */
const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-top">
          <div className="footer-section">
            <h3 className="footer-title">JaePa</h3>
            <p className="footer-description">
              금융 뉴스 감성 분석과 주식 데이터 분석을 통한 투자 인사이트 제공 플랫폼
            </p>
          </div>
          
          <div className="footer-section">
            <h3 className="footer-title">서비스</h3>
            <ul className="footer-links">
              <li><Link to="/news-analysis">뉴스 분석</Link></li>
              <li><Link to="/stock-analysis">주식 분석</Link></li>
              <li><Link to="/dashboard">대시보드</Link></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h3 className="footer-title">회사</h3>
            <ul className="footer-links">
              <li><Link to="/about">소개</Link></li>
              <li><Link to="/contact">문의하기</Link></li>
              <li><Link to="/careers">채용</Link></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h3 className="footer-title">법적 고지</h3>
            <ul className="footer-links">
              <li><Link to="/terms">이용약관</Link></li>
              <li><Link to="/privacy">개인정보처리방침</Link></li>
              <li><Link to="/disclaimer">면책조항</Link></li>
            </ul>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p className="copyright">
            &copy; {currentYear} JaePa. All rights reserved.
          </p>
          <div className="social-links">
            <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" aria-label="Twitter">
              <span className="social-icon">🐦</span>
            </a>
            <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
              <span className="social-icon">📘</span>
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
              <span className="social-icon">🔗</span>
            </a>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
              <span className="social-icon">🐙</span>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
