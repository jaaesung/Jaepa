/**
 * 푸터 컴포넌트
 */

import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

/**
 * 애플리케이션 푸터 컴포넌트
 */
const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-section">
          <h3 className="footer-title">JaePa</h3>
          <p className="footer-description">
            금융 뉴스 크롤링과 감성 분석을 통한<br />
            투자 의사결정 도구
          </p>
        </div>

        <div className="footer-section">
          <h3 className="footer-title">링크</h3>
          <ul className="footer-links">
            <li>
              <Link to="/">홈</Link>
            </li>
            <li>
              <Link to="/about">소개</Link>
            </li>
            <li>
              <Link to="/terms">이용약관</Link>
            </li>
            <li>
              <Link to="/privacy">개인정보처리방침</Link>
            </li>
          </ul>
        </div>

        <div className="footer-section">
          <h3 className="footer-title">문의</h3>
          <address className="footer-contact">
            <p>이메일: <a href="mailto:info@jaepa.com">info@jaepa.com</a></p>
            <p>GitHub: <a href="https://github.com/jaaesung/jaepa" target="_blank" rel="noopener noreferrer">github.com/jaaesung/jaepa</a></p>
          </address>
        </div>
      </div>

      <div className="footer-bottom">
        <p className="footer-copyright">
          &copy; {currentYear} JaePa. All rights reserved.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
