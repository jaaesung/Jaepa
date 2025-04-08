import React, { useEffect, ReactNode } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import './App.css';

// 페이지 컴포넌트 가져오기
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import NewsAnalysis from './pages/NewsAnalysis';
import StockAnalysis from './pages/StockAnalysis';
import Profile from './pages/Profile';
import NotFound from './pages/NotFound';

// 레이아웃 컴포넌트
import Layout from './components/Layout';

// 인증 체크 액션
import { checkAuthStatus } from './store/slices/authSlice';

// 타입 가져오기
import { RootState } from './types';

interface ProtectedRouteProps {
  children: ReactNode;
}

const App: React.FC = () => {
  const dispatch = useDispatch();
  const { isAuthenticated, isLoading } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    dispatch(checkAuthStatus());
  }, [dispatch]);

  if (isLoading) {
    return <div className="app-loading">Loading...</div>;
  }

  // 인증된 사용자만 접근 가능한 라우트를 정의하는 컴포넌트
  const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }
    return <>{children}</>;
  };

  return (
    <div className="app">
      <Routes>
        {/* 공개 경로 */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* 보호된 경로 */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Dashboard />} />
          <Route path="news-analysis" element={<NewsAnalysis />} />
          <Route path="stock-analysis" element={<StockAnalysis />} />
          <Route path="profile" element={<Profile />} />
        </Route>
        
        {/* 404 경로 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  );
}

export default App;
