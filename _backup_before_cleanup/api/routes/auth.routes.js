/**
 * 인증 관련 API 라우트
 */

const express = require('express');
const router = express.Router();
const authController = require('../controllers/auth.controller');
const { validateToken } = require('../middleware/auth.middleware');

// 회원가입
router.post('/register', authController.register);

// 로그인
router.post('/login', authController.login);

// 토큰 갱신
router.post('/refresh-token', authController.refreshToken);

// 비밀번호 재설정 요청
router.post('/forgot-password', authController.forgotPassword);

// 비밀번호 재설정
router.post('/reset-password', authController.resetPassword);

// 사용자 정보 가져오기 (인증 필요)
router.get('/me', validateToken, authController.getProfile);

// 사용자 정보 업데이트 (인증 필요)
router.put('/me', validateToken, authController.updateProfile);

module.exports = router;
