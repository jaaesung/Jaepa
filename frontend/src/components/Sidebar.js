import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';

/**
 * 애플리케이션 사이드바 컴포넌트
 * 메뉴 항목과 네비게이션 포함
 */
const Sidebar = ({ isOpen }) => {
  const location = useLocation();
  const [expandedMenus, setExpandedMenus] = useState({
    newsAnalysis: false,
    stockAnalysis: false,
  });

  const toggleMenu = (menu) => {
    setExpandedMenus({
      ...expandedMenus,
      [menu]: !expandedMenus[menu],
    });
  };

  const menuItems = [
    {
      id: 'dashboard',
      label: '대시보드',
      icon: '📊',
      path: '/',
      exact: true,
    },
    {
      id: 'newsAnalysis',
      label: '뉴스 분석',
      icon: '📰',
      path: '/news-analysis',
      submenu: [
        {
          id: 'newsList',
          label: '뉴스 목록',
          path: '/news-analysis/list',
        },
        {
          id: 'sentimentAnalysis',
          label: '감성 분석',
          path: '/news-analysis/sentiment',
        },
        {
          id: 'keywordAnalysis',
          label: '키워드 분석',
          path: '/news-analysis/keywords',
        },
      ],
    },
    {
      id: 'stockAnalysis',
      label: '주식 분석',
      icon: '📈',
      path: '/stock-analysis',
      submenu: [
        {
          id: 'stockList',
          label: '주식 목록',
          path: '/stock-analysis/list',
        },
        {
          id: 'priceAnalysis',
          label: '가격 분석',
          path: '/stock-analysis/price',
        },
        {
          id: 'correlationAnalysis',
          label: '상관관계 분석',
          path: '/stock-analysis/correlation',
        },
      ],
    },
    {
      id: 'reports',
      label: '리포트',
      icon: '📝',
      path: '/reports',
    },
    {
      id: 'settings',
      label: '설정',
      icon: '⚙️',
      path: '/settings',
    },
  ];

  return (
    <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="logo-container">
        <span className="logo">JaePa</span>
        <span className="logo-text">재파</span>
      </div>

      <nav className="sidebar-nav">
        <ul>
          {menuItems.map((item) => (
            <li key={item.id} className="nav-item">
              {item.submenu ? (
                <>
                  <button
                    className={`nav-link ${
                      location.pathname.startsWith(item.path) ? 'active' : ''
                    }`}
                    onClick={() => toggleMenu(item.id)}
                  >
                    <span className="menu-icon">{item.icon}</span>
                    <span className="menu-text">{item.label}</span>
                    <span className="submenu-indicator">
                      {expandedMenus[item.id] ? '▼' : '▶'}
                    </span>
                  </button>
                  {expandedMenus[item.id] && (
                    <ul className="submenu">
                      {item.submenu.map((subitem) => (
                        <li key={subitem.id}>
                          <NavLink
                            to={subitem.path}
                            className={({ isActive }) =>
                              `submenu-link ${isActive ? 'active' : ''}`
                            }
                          >
                            {subitem.label}
                          </NavLink>
                        </li>
                      ))}
                    </ul>
                  )}
                </>
              ) : (
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    `nav-link ${isActive ? 'active' : ''}`
                  }
                  end={item.exact}
                >
                  <span className="menu-icon">{item.icon}</span>
                  <span className="menu-text">{item.label}</span>
                </NavLink>
              )}
            </li>
          ))}
        </ul>
      </nav>

      <div className="sidebar-footer">
        <div className="version-info">v0.1.0</div>
      </div>
    </div>
  );
};

export default Sidebar;