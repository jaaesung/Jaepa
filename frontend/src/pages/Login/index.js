import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { login, clearError } from '../../store/slices/authSlice';
import './Login.css';

/**
 * 로그인 페이지 컴포넌트
 */
const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [formErrors, setFormErrors] = useState({});
  
  const dispatch = useDispatch();
  const navigate = useNavigate();
  
  const { isAuthenticated, isLoading, error } = useSelector((state) => state.auth);

  useEffect(() => {
    // 이미 인증된 사용자는 대시보드로 리디렉션
    if (isAuthenticated) {
      navigate('/');
    }
    
    // 컴포넌트 언마운트 시 에러 초기화
    return () => {
      dispatch(clearError());
    };
  }, [isAuthenticated, navigate, dispatch]);

  const validateForm = () => {
    const errors = {};
    
    if (!email.trim()) {
      errors.email = '이메일을 입력해주세요';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = '유효한 이메일 주소를 입력해주세요';
    }
    
    if (!password) {
      errors.password = '비밀번호를 입력해주세요';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      dispatch(login({ email, password }));
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1 className="login-title">JaePa</h1>
          <p className="login-subtitle">금융 데이터 분석 플랫폼</p>
        </div>
        
        <form className="login-form" onSubmit={handleSubmit}>
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-group">
            <label htmlFor="email">이메일</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="example@email.com"
              className={formErrors.email ? 'error' : ''}
            />
            {formErrors.email && <div className="field-error">{formErrors.email}</div>}
          </div>
          
          <div className="form-group">
            <label htmlFor="password">비밀번호</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="비밀번호 입력"
              className={formErrors.password ? 'error' : ''}
            />
            {formErrors.password && <div className="field-error">{formErrors.password}</div>}
          </div>
          
          <div className="form-group remember-forgot">
            <div className="remember-me">
              <input
                type="checkbox"
                id="remember"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              />
              <label htmlFor="remember">로그인 상태 유지</label>
            </div>
            
            <Link to="/forgot-password" className="forgot-password">
              비밀번호를 잊으셨나요?
            </Link>
          </div>
          
          <button
            type="submit"
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? '로그인 중...' : '로그인'}
          </button>
        </form>
        
        <div className="signup-link">
          계정이 없으신가요? <Link to="/register">회원가입</Link>
        </div>
      </div>
    </div>
  );
};

export default Login;