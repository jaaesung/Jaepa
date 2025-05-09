/**
 * 주식 관련 API 라우트
 */

const express = require('express');
const router = express.Router();
const stockController = require('../controllers/stock.controller');
const { validateToken } = require('../middleware/auth.middleware');

// 주식 검색
router.get('/search', stockController.searchStocks);

// 주식 상세 정보 가져오기
router.get('/:symbol', stockController.getStockDetails);

// 주식 실시간 데이터 가져오기
router.get('/:symbol/quote', stockController.getStockQuote);

// 주식 히스토리 데이터 가져오기
router.get('/:symbol/historical', stockController.getStockHistorical);

// 주식 관련 뉴스 가져오기
router.get('/:symbol/news', stockController.getStockNews);

// 주식 재무 정보 가져오기
router.get('/:symbol/financials', stockController.getStockFinancials);

// 주식 분석 정보 가져오기
router.get('/:symbol/analysis', stockController.getStockAnalysis);

// 주식 기술적 지표 가져오기
router.get('/:symbol/indicators', stockController.getTechnicalIndicators);

// 인기 주식 목록 가져오기
router.get('/popular', stockController.getPopularStocks);

// 섹터별 성과 가져오기
router.get('/sector-performance', stockController.getSectorPerformance);

// 시장 지수 가져오기
router.get('/market-indices', stockController.getMarketIndices);

// 관심 주식 목록 가져오기 (인증 필요)
router.get('/watchlist', validateToken, stockController.getWatchlist);

// 관심 주식 추가 (인증 필요)
router.post('/watchlist', validateToken, stockController.addToWatchlist);

// 관심 주식 삭제 (인증 필요)
router.delete('/watchlist/:symbol', validateToken, stockController.removeFromWatchlist);

module.exports = router;
