/**
 * 공개 라우트 컴포넌트
 * 
 * 인증된 사용자가 접근하면 대시보드로 리디렉션하는 컴포넌트를 제공합니다.
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
 * 공개 라우트 컴포넌트
 * 
 * @param children 자식 컴포넌트
 * @param restricted 제한 여부 (true인 경우 인증된 사용자는 접근 불가)
 */
const PublicRoute: React.FC<PublicRouteProps> = ({ children, restricted = false }) => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  // 제한된 공개 라우트(로그인, 회원가입 등)에 인증된 사용자가 접근하면 대시보드로 리디렉션
  if (restricted && isAuthenticated) {
    // location.state에서 from이 있으면 해당 경로로, 없으면 대시보드로 리디렉션
    const from = location.state?.from?.pathname || routeConstants.ROUTES.DASHBOARD;
    return <Navigate to={from} replace />;
  }

  return <>{children}</>;
};

export default PublicRoute;
