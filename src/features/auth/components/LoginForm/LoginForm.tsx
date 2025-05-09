/**
 * 로그인 폼 컴포넌트
 *
 * 사용자 로그인을 위한 폼 컴포넌트를 제공합니다.
 */

import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { Button, Input, Checkbox } from "../../../../components/ui";
import { validationUtils } from "../../../../core/utils";
import "./LoginForm.css";

interface LoginFormProps {
  onSuccess?: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string }>(
    {}
  );
  const { login, isLoading, error } = useAuth();

  // 이메일 유효성 검사
  const validateEmail = (email: string): boolean => {
    const isValid = validationUtils.isValidEmail(email);

    if (!isValid) {
      setErrors((prev) => ({
        ...prev,
        email: "유효한 이메일 주소를 입력해주세요.",
      }));
    } else {
      setErrors((prev) => ({ ...prev, email: undefined }));
    }

    return isValid;
  };

  // 비밀번호 유효성 검사
  const validatePassword = (password: string): boolean => {
    const isValid = password.length >= 8;

    if (!isValid) {
      setErrors((prev) => ({
        ...prev,
        password: "비밀번호는 최소 8자 이상이어야 합니다.",
      }));
    } else {
      setErrors((prev) => ({ ...prev, password: undefined }));
    }

    return isValid;
  };

  // 폼 제출 핸들러
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // 유효성 검사
    const isEmailValid = validateEmail(email);
    const isPasswordValid = validatePassword(password);

    if (!isEmailValid || !isPasswordValid) {
      return;
    }

    // 로그인 시도
    const success = await login({ email, password, rememberMe });

    if (success && onSuccess) {
      onSuccess();
    }
  };

  // 로그인 상태 변경 핸들러
  const handleRememberMeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRememberMe(e.target.checked);
  };

  return (
    <div className="login-form-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2 className="login-title">로그인</h2>

        {error && <div className="login-error">{error}</div>}

        <div className="form-group">
          <Input
            type="email"
            label="이메일"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onBlur={() => validateEmail(email)}
            error={errors.email}
            fullWidth
            required
          />
        </div>

        <div className="form-group">
          <Input
            type="password"
            label="비밀번호"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onBlur={() => validatePassword(password)}
            error={errors.password}
            fullWidth
            required
          />
        </div>

        <div className="form-remember">
          <Checkbox
            id="remember-me"
            label="로그인 상태 유지"
            checked={rememberMe}
            onChange={handleRememberMeChange}
          />
        </div>

        <div className="form-actions">
          <Button
            type="submit"
            variant="primary"
            isLoading={isLoading}
            fullWidth
          >
            로그인
          </Button>
        </div>

        <div className="form-links">
          <Link to="/forgot-password" className="forgot-password-link">
            비밀번호를 잊으셨나요?
          </Link>
          <Link to="/register" className="register-link">
            계정이 없으신가요? 회원가입
          </Link>
        </div>
      </form>
    </div>
  );
};

export default LoginForm;
