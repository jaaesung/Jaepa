import React from 'react';
import { Outlet } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { toggleSidebar } from '../store/slices/uiSlice';
import Sidebar from './Sidebar';
import Header from './Header';
import Footer from './Footer';
import { RootState } from '../types';

/**
 * 메인 레이아웃 컴포넌트
 * 사이드바, 헤더, 메인 콘텐츠 영역, 푸터를 포함
 */
const Layout: React.FC = () => {
  const { sidebarOpen, theme } = useSelector((state: RootState) => state.ui);
  const dispatch = useDispatch();

  const handleToggleSidebar = (): void => {
    dispatch(toggleSidebar());
  };

  return (
    <div className={`app-layout ${theme}`}>
      <Sidebar isOpen={sidebarOpen} />
      
      <div className={`main-content ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        <Header onToggleSidebar={handleToggleSidebar} />
        
        <main className="content">
          <Outlet />
        </main>
        
        <Footer />
      </div>
    </div>
  );
};

export default Layout;