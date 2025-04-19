/**
 * 메인 레이아웃 컴포넌트
 */

import React from 'react';
import Header from '../Header/Header';
import Sidebar from '../Sidebar/Sidebar';
import Footer from '../Footer/Footer';
import './MainLayout.css';

export interface MainLayoutProps {
  children: React.ReactNode;
}

/**
 * 메인 레이아웃
 * 
 * 헤더, 사이드바, 푸터를 포함한 메인 레이아웃
 */
const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="main-layout">
      <Header />
      <div className="main-layout-content">
        <Sidebar />
        <main className="main-layout-main">
          {children}
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default MainLayout;
