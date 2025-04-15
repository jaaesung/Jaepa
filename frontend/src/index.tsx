import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import './index.css';
import App from './App';
import store from './store';
import reportWebVitals from './reportWebVitals';

// 인증 체크 비활성화
// import { checkAuthStatus } from './store/slices/authSlice';
// store.dispatch(checkAuthStatus());

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

root.render(
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </Provider>
  </React.StrictMode>
);

// 성능 측정을 위한 웹 바이탈스
reportWebVitals();
