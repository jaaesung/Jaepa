import api from './api';

/**
 * 주식 데이터 가져오기
 * @param {string} symbol - 주식 심볼
 * @param {string} period - 기간 (1d, 1w, 1m, 3m, 6m, 1y, 5y)
 * @returns {Promise<Object>} 주식 데이터
 */
const getStockData = async (symbol, period = '1y') => {
  const response = await api.get(`/stocks/data/${symbol}`, {
    params: { period },
  });
  return response.data;
};

/**
 * 주식 분석 데이터 가져오기
 * @param {string} symbol - 주식 심볼
 * @returns {Promise<Object>} 주식 분석 데이터
 */
const getStockAnalysis = async (symbol) => {
  const response = await api.get(`/stocks/analysis/${symbol}`);
  return response.data;
};

/**
 * 주식-감성 상관관계 데이터 가져오기
 * @param {string} symbol - 주식 심볼
 * @param {string} sentimentType - 감성 타입 (all, positive, negative, neutral)
 * @returns {Promise<Object>} 상관관계 데이터
 */
const getCorrelationData = async (symbol, sentimentType = 'all') => {
  const response = await api.get(`/stocks/correlation/${symbol}`, {
    params: { sentiment_type: sentimentType },
  });
  return response.data;
};

/**
 * 기술적 지표 데이터 가져오기
 * @param {string} symbol - 주식 심볼
 * @param {Array} indicators - 가져올 지표 목록 (예: ['sma', 'rsi', 'macd'])
 * @returns {Promise<Object>} 기술적 지표 데이터
 */
const getTechnicalIndicators = async (symbol, indicators = []) => {
  const response = await api.get(`/stocks/indicators/${symbol}`, {
    params: { indicators: indicators.join(',') },
  });
  return response.data;
};

/**
 * 주식 비교 데이터 가져오기
 * @param {Array} symbols - 비교할 주식 심볼 목록
 * @param {string} period - 기간 (1d, 1w, 1m, 3m, 6m, 1y, 5y)
 * @returns {Promise<Object>} 주식 비교 데이터
 */
const compareStocks = async (symbols, period = '1y') => {
  const response = await api.get('/stocks/compare', {
    params: {
      symbols: symbols.join(','),
      period,
    },
  });
  return response.data;
};

/**
 * 업종별 주식 목록 가져오기
 * @param {string} sector - 업종 이름
 * @returns {Promise<Object>} 업종별 주식 목록
 */
const getSectorStocks = async (sector) => {
  const response = await api.get(`/stocks/sector/${sector}`);
  return response.data;
};

/**
 * 주식 검색
 * @param {string} query - 검색어
 * @returns {Promise<Object>} 검색 결과
 */
const searchStocks = async (query) => {
  const response = await api.get('/stocks/search', {
    params: { query },
  });
  return response.data;
};

const stockService = {
  getStockData,
  getStockAnalysis,
  getCorrelationData,
  getTechnicalIndicators,
  compareStocks,
  getSectorStocks,
  searchStocks,
};

export default stockService;