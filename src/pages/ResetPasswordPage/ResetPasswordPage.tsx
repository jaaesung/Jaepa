/**
 * 비밀번호 재설정 페이지 컴포넌트
 * 
 * 비밀번호를 재설정하는 페이지를 제공합니다.
 */

import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { AuthLayout } from '../../components/layout';
import { Card, Button, Input } from '../../components/ui';
import { useAuth } from '../../features/auth';
import { validationUtils } from '../../core/utils';
import './ResetPasswordPage.css';

/**
 * 비밀번호 재설정 페이지 컴포넌트
 */
const ResetPasswordPage: React.FC = () => {
  const { resetPassword, isLoading } = useAuth();
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isTokenValid, setIsTokenValid] = useState(true);

  // 토큰 유효성 검사
  useEffect(() => {
    if (!token) {
      setIsTokenValid(false);
      setError('유효하지 않은 비밀번호 재설정 링크입니다.');
    }
  }, [token]);

  // 비밀번호 변경 핸들러
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    setError('');
  };

  // 비밀번호 확인 변경 핸들러
  const handleConfirmPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setConfirmPassword(e.target.value);
    setError('');
  };

  // 폼 제출 핸들러
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 유효성 검사
    if (!password) {
      setError('새 비밀번호를 입력해주세요.');
      return;
    }
    
    if (!confirmPassword) {
      setError('비밀번호 확인을 입력해주세요.');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('비밀번호가 일치하지 않습니다.');
      return;
    }
    
    if (!validationUtils.isValidPassword(password)) {
      setError('비밀번호는 최소 8자 이상이며, 문자, 숫자, 특수문자를 포함해야 합니다.');
      return;
    }
    
    try {
      if (token) {
        const result = await resetPassword(token, password);
        
        if (result) {
          setSuccess(true);
          // 3초 후 로그인 페이지로 리디렉션
          setTimeout(() => {
            navigate('/login');
          }, 3000);
        } else {
          setError('비밀번호 재설정에 실패했습니다. 다시 시도해주세요.');
        }
      } else {
        setError('유효하지 않은 비밀번호 재설정 링크입니다.');
      }
    } catch (error) {
      setError('서버 오류가 발생했습니다. 나중에 다시 시도해주세요.');
    }
  };

  return (
    <AuthLayout>
      <div className="reset-password-page">
        <Card className="reset-password-card">
          <h1 className="reset-password-title">비밀번호 재설정</h1>
          
          {!isTokenValid ? (
            <div className="reset-password-error-container">
              <p className="reset-password-error-message">
                유효하지 않은 비밀번호 재설정 링크입니다.
              </p>
              <p className="reset-password-error-info">
                비밀번호 재설정 링크가 만료되었거나 유효하지 않습니다.
                새로운 비밀번호 재설정 링크를 요청해주세요.
              </p>
              <div className="reset-password-actions">
                <Link to="/forgot-password" className="reset-password-link">
                  비밀번호 찾기로 돌아가기
                </Link>
              </div>
            </div>
          ) : success ? (
            <div className="reset-password-success">
              <p className="reset-password-success-message">
                비밀번호가 성공적으로 재설정되었습니다.
              </p>
              <p className="reset-password-success-info">
                잠시 후 로그인 페이지로 이동합니다.
              </p>
              <div className="reset-password-actions">
                <Link to="/login" className="reset-password-link">
                  로그인 페이지로 이동
                </Link>
              </div>
            </div>
          ) : (
            <>
              <p className="reset-password-description">
                새로운 비밀번호를 입력해주세요.
              </p>
              
              <form className="reset-password-form" onSubmit={handleSubmit}>
                {error && <div className="reset-password-error">{error}</div>}
                
                <div className="reset-password-field">
                  <Input
                    type="password"
                    label="새 비밀번호"
                    value={password}
                    onChange={handlePasswordChange}
                    placeholder="새 비밀번호 입력"
                    fullWidth
                    required
                  />
                </div>
                
                <div className="reset-password-field">
                  <Input
                    type="password"
                    label="비밀번호 확인"
                    value={confirmPassword}
                    onChange={handleConfirmPasswordChange}
                    placeholder="비밀번호 확인 입력"
                    fullWidth
                    required
                  />
                </div>
                
                <div className="reset-password-actions">
                  <Button
                    type="submit"
                    fullWidth
                    isLoading={isLoading}
                    disabled={isLoading}
                  >
                    비밀번호 재설정
                  </Button>
                </div>
                
                <div className="reset-password-links">
                  <Link to="/login" className="reset-password-link">
                    로그인 페이지로 돌아가기
                  </Link>
                </div>
              </form>
            </>
          )}
        </Card>
      </div>
    </AuthLayout>
  );
};

export default ResetPasswordPage;
