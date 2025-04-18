/**
 * 회원가입 폼 컴포넌트
 *
 * 사용자 회원가입을 위한 폼 컴포넌트를 제공합니다.
 */

import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { Button, Input, Checkbox } from "../../../../components/ui";
import { validationUtils } from "../../../../core/utils";
import "./RegisterForm.css";

interface RegisterFormProps {
  onSuccess?: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess }) => {
  const [username, setUsername] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [errors, setErrors] = useState<{
    username?: string;
    name?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
    agreeTerms?: string;
  }>({});

  const { register, isLoading, error } = useAuth();

  // 사용자명 유효성 검사
  const validateUsername = (username: string): boolean => {
    const isValid = username.length >= 3;

    if (!isValid) {
      setErrors((prev) => ({
        ...prev,
        username: "사용자명은 최소 3자 이상이어야 합니다.",
      }));
    } else {
      setErrors((prev) => ({ ...prev, username: undefined }));
    }

    return isValid;
  };

  // 이름 유효성 검사
  const validateName = (name: string): boolean => {
    const isValid = name.length >= 2;

    if (!isValid) {
      setErrors((prev) => ({
        ...prev,
        name: "이름은 최소 2자 이상이어야 합니다.",
      }));
    } else {
      setErrors((prev) => ({ ...prev, name: undefined }));
    }

    return isValid;
  };

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
    const isValid = validationUtils.isValidPassword(password);

    if (!isValid) {
      setErrors((prev) => ({
        ...prev,
        password:
          "비밀번호는 최소 8자 이상이며, 문자, 숫자, 특수문자를 포함해야 합니다.",
      }));
    } else {
      setErrors((prev) => ({ ...prev, password: undefined }));
    }

    return isValid;
  };

  // 비밀번호 확인 유효성 검사
  const validateConfirmPassword = (confirmPassword: string): boolean => {
    const isValid = confirmPassword === password;

    if (!isValid) {
      setErrors((prev) => ({
        ...prev,
        confirmPassword: "비밀번호가 일치하지 않습니다.",
      }));
    } else {
      setErrors((prev) => ({ ...prev, confirmPassword: undefined }));
    }

    return isValid;
  };

  // 약관 동의 유효성 검사
  const validateAgreeTerms = (): boolean => {
    const isValid = agreeTerms;

    if (!isValid) {
      setErrors((prev) => ({
        ...prev,
        agreeTerms: "서비스 이용약관에 동의해주세요.",
      }));
    } else {
      setErrors((prev) => ({ ...prev, agreeTerms: undefined }));
    }

    return isValid;
  };

  // 폼 제출 핸들러
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // 유효성 검사
    const isUsernameValid = validateUsername(username);
    const isNameValid = validateName(name);
    const isEmailValid = validateEmail(email);
    const isPasswordValid = validatePassword(password);
    const isConfirmPasswordValid = validateConfirmPassword(confirmPassword);
    const isAgreeTermsValid = validateAgreeTerms();

    if (
      !isUsernameValid ||
      !isNameValid ||
      !isEmailValid ||
      !isPasswordValid ||
      !isConfirmPasswordValid ||
      !isAgreeTermsValid
    ) {
      return;
    }

    // 회원가입 시도
    const success = await register({
      username,
      name,
      email,
      password,
    });

    if (success && onSuccess) {
      onSuccess();
    }
  };

  return (
    <div className="register-form-container">
      <form className="register-form" onSubmit={handleSubmit}>
        <h2 className="register-title">회원가입</h2>

        {error && <div className="register-error">{error}</div>}

        <div className="form-group">
          <Input
            type="text"
            label="사용자명"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onBlur={() => validateUsername(username)}
            error={errors.username}
            fullWidth
            required
          />
        </div>

        <div className="form-group">
          <Input
            type="text"
            label="이름"
            value={name}
            onChange={(e) => setName(e.target.value)}
            onBlur={() => validateName(name)}
            error={errors.name}
            fullWidth
            required
          />
        </div>

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

        <div className="form-group">
          <Input
            type="password"
            label="비밀번호 확인"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            onBlur={() => validateConfirmPassword(confirmPassword)}
            error={errors.confirmPassword}
            fullWidth
            required
          />
        </div>

        <div className="form-agree">
          <Checkbox
            id="agree-terms"
            label="서비스 이용약관에 동의합니다."
            checked={agreeTerms}
            onChange={(e) => setAgreeTerms(e.target.checked)}
            error={errors.agreeTerms}
          />
        </div>

        <div className="form-actions">
          <Button
            type="submit"
            variant="primary"
            isLoading={isLoading}
            fullWidth
          >
            회원가입
          </Button>
        </div>

        <div className="form-links">
          <Link to="/login" className="login-link">
            이미 계정이 있으신가요? 로그인
          </Link>
        </div>
      </form>
    </div>
  );
};

export default RegisterForm;
