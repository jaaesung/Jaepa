/**
 * 인증 보호 라우트 컴포넌트
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../features/auth';
import { routeConstants } from '../../core/constants';
import { LoadingSpinner } from '../ui';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

/**
 * 인증된 사용자만 접근할 수 있는 보호된 라우트
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  // 로딩 중이면 로딩 스피너 표시
  if (isLoading) {
    return (
      <div className="protected-route-loading">
        <LoadingSpinner />
      </div>
    );
  }

  // 인증되지 않았으면 로그인 페이지로 리다이렉트
  if (!isAuthenticated) {
    return <Navigate to={routeConstants.LOGIN} state={{ from: location }} replace />;
  }

  // 인증되었으면 자식 컴포넌트 렌더링
  return <>{children}</>;
};

export default ProtectedRoute;
