/**
 * 헤더 컴포넌트
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../features/auth';
import { routeConstants } from '../../../core/constants';
import './Header.css';

/**
 * 애플리케이션 헤더
 */
const Header: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  // 로그아웃 처리
  const handleLogout = async () => {
    await logout();
    navigate(routeConstants.LOGIN);
  };

  // 메뉴 토글
  const toggleMenu = () => {
    setMenuOpen(prev => !prev);
  };

  return (
    <header className="app-header">
      <div className="header-container">
        <div className="header-logo">
          <Link to={routeConstants.HOME}>
            <h1>JaePa</h1>
          </Link>
        </div>

        <div className="header-nav">
          <nav className="header-navigation">
            <Link to={routeConstants.DASHBOARD}>대시보드</Link>
            <Link to={routeConstants.NEWS_ANALYSIS}>뉴스 분석</Link>
            <Link to={routeConstants.STOCK_ANALYSIS}>주식 분석</Link>
            <Link to={routeConstants.SENTIMENT_ANALYSIS}>감성 분석</Link>
          </nav>
        </div>

        <div className="header-actions">
          {isAuthenticated ? (
            <div className="header-user-menu">
              <button className="user-menu-button" onClick={toggleMenu}>
                <span className="user-name">{user?.username || '사용자'}</span>
              </button>
              
              {menuOpen && (
                <div className="user-menu-dropdown">
                  <Link to={routeConstants.PROFILE} className="dropdown-item">
                    프로필
                  </Link>
                  <Link to={routeConstants.SETTINGS} className="dropdown-item">
                    설정
                  </Link>
                  <button onClick={handleLogout} className="dropdown-item logout-button">
                    로그아웃
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="header-auth-buttons">
              <Link to={routeConstants.LOGIN} className="login-button">
                로그인
              </Link>
              <Link to={routeConstants.REGISTER} className="register-button">
                회원가입
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
