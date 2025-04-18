/**
 * 보호된 라우트 컴포넌트
 * 
 * 인증이 필요한 라우트를 보호하는 컴포넌트를 제공합니다.
 */

import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../features/auth';
import { routeConstants } from '../../core/constants';
import { LoadingSpinner } from '../ui';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

/**
 * 보호된 라우트 컴포넌트
 * 
 * 인증되지 않은 사용자가 접근하면 로그인 페이지로 리디렉션합니다.
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, checkAuthStatus } = useAuth();
  const [isVerifying, setIsVerifying] = useState(true);
  const [isValid, setIsValid] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const verifyAuth = async () => {
      try {
        setIsVerifying(true);
        const isValid = await checkAuthStatus();
        setIsValid(isValid);
      } catch (error) {
        setIsValid(false);
      } finally {
        setIsVerifying(false);
      }
    };

    if (isAuthenticated) {
      verifyAuth();
    } else {
      setIsVerifying(false);
    }
  }, [isAuthenticated, checkAuthStatus]);

  if (isVerifying) {
    return (
      <div className="protected-route-loading">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (!isAuthenticated || !isValid) {
    // 현재 위치를 state로 전달하여 로그인 후 원래 페이지로 리디렉션할 수 있도록 함
    return (
      <Navigate
        to={routeConstants.ROUTES.LOGIN}
        state={{ from: location }}
        replace
      />
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;
