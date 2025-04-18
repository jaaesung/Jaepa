/**
 * 메인 레이아웃 컴포넌트
 * 
 * 애플리케이션의 기본 레이아웃을 제공합니다.
 */

import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Header from '../Header';
import Footer from '../Footer';
import Sidebar from '../Sidebar';
import { useAppSelector } from '../../../core/hooks';
import './MainLayout.css';

interface MainLayoutProps {
  showSidebar?: boolean;
}

/**
 * 메인 레이아웃 컴포넌트
 */
const MainLayout: React.FC<MainLayoutProps> = ({ showSidebar = true }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { isAuthenticated } = useAppSelector(state => state.auth);
  
  // 화면 크기에 따라 사이드바 상태 조정
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setSidebarOpen(false);
      } else {
        setSidebarOpen(true);
      }
    };
    
    // 초기 설정
    handleResize();
    
    // 리사이즈 이벤트 리스너 등록
    window.addEventListener('resize', handleResize);
    
    // 클린업
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);
  
  // 사이드바 토글
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
  
  return (
    <div className="main-layout">
      <Header onToggleSidebar={showSidebar ? toggleSidebar : undefined} />
      
      <div className="main-content">
        {showSidebar && isAuthenticated && (
          <Sidebar isOpen={sidebarOpen} />
        )}
        
        <main className={`content ${showSidebar && isAuthenticated && sidebarOpen ? 'with-sidebar' : ''}`}>
          <Outlet />
        </main>
      </div>
      
      <Footer />
    </div>
  );
};

export default MainLayout;
