/**
 * 404 페이지 컴포넌트
 * 
 * 페이지를 찾을 수 없을 때 표시되는 페이지를 제공합니다.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { Header, Footer } from '../../components/layout';
import { Button } from '../../components/ui';
import './NotFoundPage.css';

/**
 * 404 페이지 컴포넌트
 */
const NotFoundPage: React.FC = () => {
  return (
    <div className="not-found-page">
      <Header />
      
      <main className="not-found-content">
        <div className="not-found-container">
          <div className="not-found-image">
            <span className="not-found-code">404</span>
          </div>
          
          <h1 className="not-found-title">페이지를 찾을 수 없습니다</h1>
          <p className="not-found-description">
            요청하신 페이지가 존재하지 않거나 이동되었을 수 있습니다.
            URL을 확인하시거나 아래 버튼을 클릭하여 홈페이지로 이동하세요.
          </p>
          
          <div className="not-found-actions">
            <Link to="/">
              <Button variant="primary" size="large">홈페이지로 이동</Button>
            </Link>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default NotFoundPage;
