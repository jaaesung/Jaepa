import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { logout } from '../store/slices/authSlice';
import { toggleTheme } from '../store/slices/uiSlice';
import { RootState } from '../types';
import { useAppDispatch } from '../hooks';

interface HeaderProps {
  onToggleSidebar: () => void;
}

/**
 * 애플리케이션 헤더 컴포넌트
 * 메뉴 토글, 사용자 프로필, 검색, 알림 기능 포함
 */
const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state: RootState) => state.auth);
  const { theme } = useSelector((state: RootState) => state.ui);
  const [isProfileOpen, setIsProfileOpen] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const handleLogout = (): void => {
    dispatch(logout());
    navigate('/login');
  };

  const handleThemeToggle = (): void => {
    dispatch(toggleTheme());
  };

  const handleSearch = (e: React.FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const toggleProfileMenu = (): void => {
    setIsProfileOpen(!isProfileOpen);
  };

  return (
    <header className="app-header">
      <div className="header-left">
        <button
          className="sidebar-toggle-btn"
          onClick={onToggleSidebar}
          aria-label="Toggle Sidebar"
        >
          <span className="menu-icon">☰</span>
        </button>

        <div className="search-container">
          <form onSubmit={handleSearch}>
            <input
              type="text"
              placeholder="뉴스 또는 주식 검색..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="search-input"
            />
            <button type="submit" className="search-btn">
              🔍
            </button>
          </form>
        </div>
      </div>

      <div className="header-right">
        <button
          className="theme-toggle-btn"
          onClick={handleThemeToggle}
          aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
          {theme === 'light' ? '🌙' : '☀️'}
        </button>

        <div className="notification-icon">
          🔔
          <span className="notification-badge">3</span>
        </div>

        <div className="profile-dropdown">
          <button className="profile-btn" onClick={toggleProfileMenu} aria-expanded={isProfileOpen}>
            <div className="avatar">{user?.username?.charAt(0).toUpperCase() || 'U'}</div>
            <span className="username">{user?.username || 'User'}</span>
          </button>

          {isProfileOpen && (
            <div className="dropdown-menu">
              <button onClick={() => navigate('/profile')}>프로필 관리</button>
              <button onClick={() => navigate('/settings')}>설정</button>
              <button onClick={handleLogout}>로그아웃</button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
