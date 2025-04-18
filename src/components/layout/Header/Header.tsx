/**
 * 헤더 컴포넌트
 * 
 * 애플리케이션의 상단 헤더를 제공합니다.
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../features/auth';
import { useTheme } from '../../../core/contexts';
import Button from '../../ui/Button';
import './Header.css';

interface HeaderProps {
  onToggleSidebar?: () => void;
}

/**
 * 헤더 컴포넌트
 */
const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // 로그아웃 핸들러
  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // 검색 핸들러
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  // 프로필 메뉴 토글
  const toggleProfileMenu = () => {
    setIsProfileOpen(!isProfileOpen);
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="header-left">
          {onToggleSidebar && (
            <button className="sidebar-toggle" onClick={onToggleSidebar} aria-label="Toggle Sidebar">
              <span className="sidebar-toggle-icon">☰</span>
            </button>
          )}
          
          <Link to="/" className="logo">
            <span className="logo-text">JaePa</span>
          </Link>
          
          <form className="search-form" onSubmit={handleSearch}>
            <input
              type="text"
              placeholder="뉴스 또는 주식 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            <button type="submit" className="search-button">
              <span className="search-icon">🔍</span>
            </button>
          </form>
        </div>
        
        <div className="header-right">
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
          
          {isAuthenticated ? (
            <>
              <div className="notifications">
                <button className="notifications-button" aria-label="Notifications">
                  <span className="notifications-icon">🔔</span>
                  <span className="notifications-badge">3</span>
                </button>
              </div>
              
              <div className="profile">
                <button
                  className="profile-button"
                  onClick={toggleProfileMenu}
                  aria-expanded={isProfileOpen}
                >
                  <div className="avatar">
                    {user?.name?.charAt(0) || 'U'}
                  </div>
                  <span className="profile-name">{user?.name || 'User'}</span>
                </button>
                
                {isProfileOpen && (
                  <div className="profile-menu">
                    <Link to="/profile" className="profile-menu-item">프로필</Link>
                    <Link to="/settings" className="profile-menu-item">설정</Link>
                    <button onClick={handleLogout} className="profile-menu-item logout">로그아웃</button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="auth-buttons">
              <Button
                variant="text"
                size="small"
                onClick={() => navigate('/login')}
              >
                로그인
              </Button>
              <Button
                variant="primary"
                size="small"
                onClick={() => navigate('/register')}
              >
                회원가입
              </Button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
