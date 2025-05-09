/**
 * API 라우트 인덱스
 * 
 * 모든 API 라우트를 통합하고 내보냅니다.
 */

const express = require('express');
const router = express.Router();

// 라우트 모듈 가져오기
const authRoutes = require('./auth.routes');
const newsRoutes = require('./news.routes');
const stockRoutes = require('./stock.routes');
const analysisRoutes = require('./analysis.routes');

// 라우트 등록
router.use('/auth', authRoutes);
router.use('/news', newsRoutes);
router.use('/stocks', stockRoutes);
router.use('/analysis', analysisRoutes);

module.exports = router;
