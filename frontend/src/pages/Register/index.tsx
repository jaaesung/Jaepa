import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { register } from '../../store/slices/authSlice';
import { RootState } from '../../types';
import { useAppDispatch } from '../../hooks';
import './Register.css';

const Register: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { isLoading, error, isAuthenticated } = useSelector((state: RootState) => state.auth);

  // 이미 인증된 사용자는 대시보드로 리디렉션
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const [formErrors, setFormErrors] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });

    // 입력 시 해당 필드의 오류 메시지 초기화
    setFormErrors({
      ...formErrors,
      [name]: '',
    });
  };

  const validateForm = () => {
    let isValid = true;
    const newErrors = { ...formErrors };

    // 이름 검증
    if (!formData.name.trim()) {
      newErrors.name = '이름을 입력해주세요.';
      isValid = false;
    }

    // 이메일 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email.trim()) {
      newErrors.email = '이메일을 입력해주세요.';
      isValid = false;
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = '유효한 이메일 주소를 입력해주세요.';
      isValid = false;
    }

    // 비밀번호 검증
    if (!formData.password) {
      newErrors.password = '비밀번호를 입력해주세요.';
      isValid = false;
    } else if (formData.password.length < 8) {
      newErrors.password = '비밀번호는 8자 이상이어야 합니다.';
      isValid = false;
    }

    // 비밀번호 확인 검증
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = '비밀번호 확인을 입력해주세요.';
      isValid = false;
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = '비밀번호가 일치하지 않습니다.';
      isValid = false;
    }

    setFormErrors(newErrors);
    return isValid;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validateForm()) {
      // 회원가입 요청 데이터 디버깅
      console.log('회원가입 요청 데이터:', {
        username: formData.name,
        email: formData.email,
        password: formData.password,
      });

      dispatch(
        register({
          username: formData.name,
          email: formData.email,
          password: formData.password,
        })
      );
    }
  };

  return (
    <div className="register-container">
      <div className="register-card">
        <div className="register-header">
          <h1>회원가입</h1>
          <p>계정을 생성하여 모든 기능을 이용해보세요.</p>
        </div>

        <form className="register-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">이름</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="이름을 입력하세요"
              className={formErrors.name ? 'error' : ''}
            />
            {formErrors.name && <div className="error-message">{formErrors.name}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="email">이메일</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="이메일을 입력하세요"
              className={formErrors.email ? 'error' : ''}
            />
            {formErrors.email && <div className="error-message">{formErrors.email}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="password">비밀번호</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="비밀번호를 입력하세요"
              className={formErrors.password ? 'error' : ''}
            />
            {formErrors.password && <div className="error-message">{formErrors.password}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">비밀번호 확인</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="비밀번호를 다시 입력하세요"
              className={formErrors.confirmPassword ? 'error' : ''}
            />
            {formErrors.confirmPassword && (
              <div className="error-message">{formErrors.confirmPassword}</div>
            )}
          </div>

          {error && <div className="form-error">{error}</div>}

          <button type="submit" className="register-button" disabled={isLoading}>
            {isLoading ? '처리 중...' : '회원가입'}
          </button>
        </form>

        <div className="register-footer">
          <p>
            이미 계정이 있으신가요? <Link to="/login">로그인</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
