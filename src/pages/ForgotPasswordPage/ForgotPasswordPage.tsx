/**
 * 비밀번호 찾기 페이지 컴포넌트
 * 
 * 비밀번호 재설정 이메일을 요청하는 페이지를 제공합니다.
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { AuthLayout } from '../../components/layout';
import { Card, Button, Input } from '../../components/ui';
import { useAuth } from '../../features/auth';
import { validationUtils } from '../../core/utils';
import './ForgotPasswordPage.css';

/**
 * 비밀번호 찾기 페이지 컴포넌트
 */
const ForgotPasswordPage: React.FC = () => {
  const { forgotPassword, isLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // 이메일 변경 핸들러
  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    setError('');
  };

  // 폼 제출 핸들러
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 유효성 검사
    if (!email) {
      setError('이메일을 입력해주세요.');
      return;
    }
    
    if (!validationUtils.isValidEmail(email)) {
      setError('유효한 이메일 주소를 입력해주세요.');
      return;
    }
    
    try {
      const result = await forgotPassword(email);
      
      if (result) {
        setSuccess(true);
      } else {
        setError('비밀번호 재설정 이메일 전송에 실패했습니다. 다시 시도해주세요.');
      }
    } catch (error) {
      setError('서버 오류가 발생했습니다. 나중에 다시 시도해주세요.');
    }
  };

  return (
    <AuthLayout>
      <div className="forgot-password-page">
        <Card className="forgot-password-card">
          <h1 className="forgot-password-title">비밀번호 찾기</h1>
          
          {success ? (
            <div className="forgot-password-success">
              <p className="forgot-password-success-message">
                비밀번호 재설정 링크가 이메일로 전송되었습니다.
              </p>
              <p className="forgot-password-success-info">
                이메일을 확인하고 링크를 클릭하여 비밀번호를 재설정하세요.
              </p>
              <div className="forgot-password-actions">
                <Link to="/login" className="forgot-password-link">
                  로그인 페이지로 돌아가기
                </Link>
              </div>
            </div>
          ) : (
            <>
              <p className="forgot-password-description">
                가입한 이메일 주소를 입력하시면 비밀번호 재설정 링크를 보내드립니다.
              </p>
              
              <form className="forgot-password-form" onSubmit={handleSubmit}>
                {error && <div className="forgot-password-error">{error}</div>}
                
                <div className="forgot-password-field">
                  <Input
                    type="email"
                    label="이메일"
                    value={email}
                    onChange={handleEmailChange}
                    placeholder="이메일 주소 입력"
                    fullWidth
                    required
                  />
                </div>
                
                <div className="forgot-password-actions">
                  <Button
                    type="submit"
                    fullWidth
                    isLoading={isLoading}
                    disabled={isLoading}
                  >
                    비밀번호 재설정 링크 받기
                  </Button>
                </div>
                
                <div className="forgot-password-links">
                  <Link to="/login" className="forgot-password-link">
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

export default ForgotPasswordPage;
