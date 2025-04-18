/**
 * 사이드바 컴포넌트
 * 
 * 애플리케이션의 사이드바 네비게이션을 제공합니다.
 */

import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../../features/auth';
import './Sidebar.css';

interface SidebarProps {
  isOpen: boolean;
}

/**
 * 사이드바 컴포넌트
 */
const Sidebar: React.FC<SidebarProps> = ({ isOpen }) => {
  const { user } = useAuth();
  
  return (
    <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-header">
        <div className="sidebar-user">
          <div className="sidebar-avatar">
            {user?.name?.charAt(0) || 'U'}
          </div>
          <div className="sidebar-user-info">
            <h3 className="sidebar-user-name">{user?.name || 'User'}</h3>
            <p className="sidebar-user-email">{user?.email || 'user@example.com'}</p>
          </div>
        </div>
      </div>
      
      <nav className="sidebar-nav">
        <ul className="sidebar-nav-list">
          <li className="sidebar-nav-item">
            <NavLink
              to="/dashboard"
              className={({ isActive }) => `sidebar-nav-link ${isActive ? 'active' : ''}`}
            >
              <span className="sidebar-nav-icon">📊</span>
              <span className="sidebar-nav-text">대시보드</span>
            </NavLink>
          </li>
          
          <li className="sidebar-nav-item">
            <NavLink
              to="/news-analysis"
              className={({ isActive }) => `sidebar-nav-link ${isActive ? 'active' : ''}`}
            >
              <span className="sidebar-nav-icon">📰</span>
              <span className="sidebar-nav-text">뉴스 분석</span>
            </NavLink>
          </li>
          
          <li className="sidebar-nav-item">
            <NavLink
              to="/stock-analysis"
              className={({ isActive }) => `sidebar-nav-link ${isActive ? 'active' : ''}`}
            >
              <span className="sidebar-nav-icon">📈</span>
              <span className="sidebar-nav-text">주식 분석</span>
            </NavLink>
          </li>
          
          <li className="sidebar-nav-item">
            <NavLink
              to="/sentiment-analysis"
              className={({ isActive }) => `sidebar-nav-link ${isActive ? 'active' : ''}`}
            >
              <span className="sidebar-nav-icon">🔍</span>
              <span className="sidebar-nav-text">감성 분석</span>
            </NavLink>
          </li>
        </ul>
      </nav>
      
      <div className="sidebar-footer">
        <ul className="sidebar-nav-list">
          <li className="sidebar-nav-item">
            <NavLink
              to="/settings"
              className={({ isActive }) => `sidebar-nav-link ${isActive ? 'active' : ''}`}
            >
              <span className="sidebar-nav-icon">⚙️</span>
              <span className="sidebar-nav-text">설정</span>
            </NavLink>
          </li>
          
          <li className="sidebar-nav-item">
            <NavLink
              to="/help"
              className={({ isActive }) => `sidebar-nav-link ${isActive ? 'active' : ''}`}
            >
              <span className="sidebar-nav-icon">❓</span>
              <span className="sidebar-nav-text">도움말</span>
            </NavLink>
          </li>
        </ul>
      </div>
    </aside>
  );
};

export default Sidebar;
