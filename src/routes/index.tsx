/**
 * 라우팅 모듈
 *
 * 애플리케이션의 라우팅 설정을 제공합니다.
 */

import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { ProtectedRoute, PublicRoute } from "@components/routing";
import { LoadingSpinner } from "@components/ui";
import routes from "./routeConfig";

/**
 * 애플리케이션 라우트 컴포넌트
 */
const AppRoutes: React.FC = () => {
  // 로딩 표시를 위한 컴포넌트
  const LoadingFallback = (
    <div className="app-loading">
      <LoadingSpinner size="large" text="페이지 로딩 중..." />
    </div>
  );

  return (
    <React.Suspense fallback={LoadingFallback}>
      <Routes>
        {/* 라우트 구성 */}
        {routes.map((route) => {
          // 보호된 라우트
          if (route.protected) {
            return (
              <Route
                key={route.path}
                path={route.path}
                element={
                  <ProtectedRoute>
                    <route.component />
                  </ProtectedRoute>
                }
              />
            );
          }

          // 제한된 공개 라우트 (로그인한 사용자는 접근 불가)
          if (route.restricted) {
            return (
              <Route
                key={route.path}
                path={route.path}
                element={
                  <PublicRoute restricted={true}>
                    <route.component />
                  </PublicRoute>
                }
              />
            );
          }

          // 일반 공개 라우트
          return (
            <Route
              key={route.path}
              path={route.path}
              element={<route.component />}
            />
          );
        })}

        {/* 404 페이지 리디렉션 */}
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Routes>
    </React.Suspense>
  );
};

export default AppRoutes;
