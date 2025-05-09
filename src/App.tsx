/**
 * 애플리케이션 진입점 컴포넌트
 *
 * 애플리케이션의 최상위 컴포넌트를 제공합니다.
 */

import React, { useEffect } from "react";
import { BrowserRouter as Router } from "react-router-dom";
import { Provider } from "react-redux";
import store from "@/store";
import { ThemeProvider, ToastProvider } from "@core/contexts";
import AppRoutes from "@/routes";
import { verifyAuth } from "./features/auth/store/authSlice";
import "./App.css";

const App: React.FC = () => {
  useEffect(() => {
    // 애플리케이션 시작 시 인증 상태 확인
    store.dispatch(verifyAuth());
  }, []);

  return (
    <Provider store={store}>
      <ThemeProvider>
        <ToastProvider position="top-right" maxToasts={5}>
          <Router>
            <div className="app">
              <AppRoutes />
            </div>
          </Router>
        </ToastProvider>
      </ThemeProvider>
    </Provider>
  );
};

export default App;
