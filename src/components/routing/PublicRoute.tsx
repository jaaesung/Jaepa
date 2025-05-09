/**
 * 공개 라우트 컴포넌트
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../features/auth';
import { routeConstants } from '../../core/constants';

interface PublicRouteProps {
  children: React.ReactNode;
  restricted?: boolean;
}

/**
 * 공개 접근 가능한 라우트 (제한 옵션)
 * 
 * restricted가 true인 경우 인증된 사용자는 대시보드로 리다이렉트됩니다.
 * (로그인/회원가입 페이지 등에 사용)
 */
const PublicRoute: React.FC<PublicRouteProps> = ({ 
  children, 
  restricted = false 
}) => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  
  // state에서 redirectTo 값을 가져옴 (없으면 대시보드)
  const from = location.state?.from?.pathname || routeConstants.DASHBOARD;

  // 제한된 라우트이고 인증된 경우 이전 페이지 또는 대시보드로 리다이렉트
  if (restricted && isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  // 그 외의 경우 자식 컴포넌트 렌더링
  return <>{children}</>;
};

export default PublicRoute;
