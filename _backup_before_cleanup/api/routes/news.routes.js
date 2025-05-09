/**
 * 뉴스 관련 API 라우트
 */

const express = require('express');
const router = express.Router();
const newsController = require('../controllers/news.controller');
const { validateToken } = require('../middleware/auth.middleware');

// 뉴스 목록 가져오기
router.get('/', newsController.getNews);

// 뉴스 검색
router.get('/search', newsController.searchNews);

// 뉴스 카테고리 목록 가져오기
router.get('/categories', newsController.getCategories);

// 뉴스 소스 목록 가져오기
router.get('/sources', newsController.getSources);

// 특정 뉴스 상세 정보 가져오기
router.get('/:id', newsController.getNewsById);

// 특정 뉴스의 감성 분석 결과 가져오기
router.get('/:id/sentiment', newsController.getNewsSentiment);

// 인기 키워드 가져오기
router.get('/popular-keywords', newsController.getPopularKeywords);

// 감성 트렌드 가져오기
router.get('/sentiment-trend', newsController.getSentimentTrend);

// 뉴스 저장 (인증 필요)
router.post('/save', validateToken, newsController.saveNews);

// 저장된 뉴스 목록 가져오기 (인증 필요)
router.get('/saved', validateToken, newsController.getSavedNews);

// 저장된 뉴스 삭제 (인증 필요)
router.delete('/saved/:id', validateToken, newsController.deleteSavedNews);

module.exports = router;
