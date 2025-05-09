/**
 * 사이드바 컴포넌트
 */

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { routeConstants } from '../../../core/constants';
import './Sidebar.css';

/**
 * 앱 사이드바 컴포넌트
 */
const Sidebar: React.FC = () => {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  const toggleSidebar = () => {
    setCollapsed(!collapsed);
  };

  // 현재 경로 활성화 확인
  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <button className="sidebar-toggle" onClick={toggleSidebar}>
          {collapsed ? '>' : '<'}
        </button>
      </div>

      <nav className="sidebar-nav">
        <ul className="sidebar-nav-list">
          <li className={`sidebar-nav-item ${isActive(routeConstants.DASHBOARD) ? 'active' : ''}`}>
            <Link to={routeConstants.DASHBOARD}>
              <span className="sidebar-icon">📊</span>
              {!collapsed && <span className="sidebar-text">대시보드</span>}
            </Link>
          </li>
          <li className={`sidebar-nav-item ${isActive(routeConstants.NEWS_ANALYSIS) ? 'active' : ''}`}>
            <Link to={routeConstants.NEWS_ANALYSIS}>
              <span className="sidebar-icon">📰</span>
              {!collapsed && <span className="sidebar-text">뉴스 분석</span>}
            </Link>
          </li>
          <li className={`sidebar-nav-item ${isActive(routeConstants.STOCK_ANALYSIS) ? 'active' : ''}`}>
            <Link to={routeConstants.STOCK_ANALYSIS}>
              <span className="sidebar-icon">📈</span>
              {!collapsed && <span className="sidebar-text">주식 분석</span>}
            </Link>
          </li>
          <li className={`sidebar-nav-item ${isActive(routeConstants.SENTIMENT_ANALYSIS) ? 'active' : ''}`}>
            <Link to={routeConstants.SENTIMENT_ANALYSIS}>
              <span className="sidebar-icon">🔍</span>
              {!collapsed && <span className="sidebar-text">감성 분석</span>}
            </Link>
          </li>
        </ul>
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-nav-item">
          <Link to={routeConstants.SETTINGS}>
            <span className="sidebar-icon">⚙️</span>
            {!collapsed && <span className="sidebar-text">설정</span>}
          </Link>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
