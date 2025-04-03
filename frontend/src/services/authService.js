import api from './api';

/**
 * 사용자 로그인
 * @param {string} email - 사용자 이메일
 * @param {string} password - 사용자 비밀번호
 * @returns {Promise<Object>} 로그인 응답 데이터
 */
const login = async (email, password) => {
  const response = await api.post('/auth/login', { email, password });
  if (response.data.token) {
    localStorage.setItem('token', response.data.token);
    if (response.data.refreshToken) {
      localStorage.setItem('refreshToken', response.data.refreshToken);
    }
  }
  return response.data;
};

/**
 * 사용자 회원가입
 * @param {string} name - 사용자 이름
 * @param {string} email - 사용자 이메일
 * @param {string} password - 사용자 비밀번호
 * @returns {Promise<Object>} 회원가입 응답 데이터
 */
const register = async (name, email, password) => {
  const response = await api.post('/auth/register', { name, email, password });
  if (response.data.token) {
    localStorage.setItem('token', response.data.token);
    if (response.data.refreshToken) {
      localStorage.setItem('refreshToken', response.data.refreshToken);
    }
  }
  return response.data;
};

/**
 * 사용자 로그아웃
 */
const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('refreshToken');
};

/**
 * 인증 상태 확인
 * @returns {Promise<Object>} 인증 상태 데이터
 */
const checkAuthStatus = async () => {
  const token = localStorage.getItem('token');
  if (!token) {
    return { isAuthenticated: false, user: null };
  }
  
  try {
    const response = await api.get('/auth/user');
    return { isAuthenticated: true, user: response.data };
  } catch (error) {
    return { isAuthenticated: false, user: null };
  }
};

/**
 * 사용자 프로필 업데이트
 * @param {Object} userData - 업데이트할 사용자 데이터
 * @returns {Promise<Object>} 업데이트된 사용자 데이터
 */
const updateProfile = async (userData) => {
  const response = await api.put('/auth/profile', userData);
  return response.data;
};

/**
 * 비밀번호 변경
 * @param {string} currentPassword - 현재 비밀번호
 * @param {string} newPassword - 새 비밀번호
 * @returns {Promise<Object>} 비밀번호 변경 응답 데이터
 */
const changePassword = async (currentPassword, newPassword) => {
  const response = await api.post('/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
  });
  return response.data;
};

/**
 * 비밀번호 재설정 요청
 * @param {string} email - 사용자 이메일
 * @returns {Promise<Object>} 비밀번호 재설정 요청 응답 데이터
 */
const requestPasswordReset = async (email) => {
  const response = await api.post('/auth/reset-password-request', { email });
  return response.data;
};

/**
 * 비밀번호 재설정
 * @param {string} token - 비밀번호 재설정 토큰
 * @param {string} newPassword - 새 비밀번호
 * @returns {Promise<Object>} 비밀번호 재설정 응답 데이터
 */
const resetPassword = async (token, newPassword) => {
  const response = await api.post('/auth/reset-password', {
    token,
    new_password: newPassword,
  });
  return response.data;
};

const authService = {
  login,
  register,
  logout,
  checkAuthStatus,
  updateProfile,
  changePassword,
  requestPasswordReset,
  resetPassword,
};

export default authService;