import React from 'react';

/**
 * 애플리케이션 푸터 컴포넌트
 */
const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-left">
          <p>
            &copy; {currentYear} JaePa (재파). All rights reserved.
          </p>
        </div>
        
        <div className="footer-right">
          <a href="/terms" className="footer-link">
            이용약관
          </a>
          <a href="/privacy" className="footer-link">
            개인정보처리방침
          </a>
          <a href="/contact" className="footer-link">
            문의하기
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;