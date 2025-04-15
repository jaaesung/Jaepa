import React, { useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import './App.css';

// 페이지 컴포넌트 가져오기
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import NewsAnalysis from './pages/NewsAnalysis';
import Settings from './pages/Settings';
import StockAnalysis from './pages/StockAnalysis';
import Register from './pages/Register';
import Profile from './pages/Profile';
import NotFound from './pages/NotFound';
import MainPage from './pages/MainPage';

// 레이아웃 컴포넌트
import Layout from './components/Layout';

const App: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // 직접적인 방법: 기본 경로로 접속 시 메인 페이지로 강제 리디렉션
  useEffect(() => {
    console.log('현재 경로:', location.pathname);

    // 로그인 페이지나 회원가입 페이지, 메인페이지로 접속하는 경우를 제외
    if (
      location.pathname === '/login' ||
      location.pathname === '/register' ||
      location.pathname === '/mainpage'
    ) {
      // 해당 페이지는 그대로 남김
      return;
    }

    // 기본 경로나 다른 경로로 접속 시 메인페이지로 이동
    console.log('메인페이지로 리디렉션');
    navigate('/mainpage', { replace: true });
  }, [location.pathname, navigate]);
  return (
    <div className="app">
      <Routes>
        {/* 공개 경로 */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/mainpage" element={<MainPage />} />

        {/* 메인 레이아웃 (모든 사용자 접근 가능) */}
        <Route path="/dashboard" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="news-analysis" element={<NewsAnalysis />} />
          <Route path="stock-analysis" element={<StockAnalysis />} />
          <Route path="settings" element={<Settings />} />
          <Route path="profile" element={<Profile />} />
        </Route>

        {/* 기본 경로와 404 경로는 메인페이지로 리디렉션 */}
        <Route path="/" element={<Navigate to="/mainpage" replace />} />
        <Route path="*" element={<Navigate to="/mainpage" replace />} />
      </Routes>
    </div>
  );
};

export default App;
