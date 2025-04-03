import api from './api';

/**
 * 뉴스 데이터 가져오기
 * @param {number} page - 페이지 번호
 * @param {number} limit - 페이지당 항목 수
 * @param {Object} filters - 필터링 옵션 (키워드, 날짜 범위 등)
 * @returns {Promise<Object>} 뉴스 데이터
 */
const getNews = async (page = 1, limit = 10, filters = {}) => {
  const params = {
    page,
    limit,
    ...filters,
  };
  
  const response = await api.get('/news', { params });
  return response.data;
};

/**
 * 특정 뉴스 항목 가져오기
 * @param {string} newsId - 뉴스 ID
 * @returns {Promise<Object>} 뉴스 상세 데이터
 */
const getNewsItem = async (newsId) => {
  const response = await api.get(`/news/${newsId}`);
  return response.data;
};

/**
 * 뉴스 감성 분석 결과 가져오기
 * @param {string} newsId - 뉴스 ID
 * @returns {Promise<Object>} 감성 분석 결과
 */
const getSentimentAnalysis = async (newsId) => {
  const response = await api.get(`/news/${newsId}/sentiment`);
  return response.data;
};

/**
 * 뉴스 감성 트렌드 가져오기
 * @param {Object} params - 트렌드 필터링 옵션 (날짜 범위, 키워드 등)
 * @returns {Promise<Object>} 감성 트렌드 데이터
 */
const getSentimentTrend = async (params = {}) => {
  const response = await api.get('/news/sentiment-trend', { params });
  return response.data;
};

/**
 * 인기 키워드 가져오기
 * @param {Object} params - 필터링 옵션 (날짜 범위, 상위 항목 수 등)
 * @returns {Promise<Object>} 인기 키워드 데이터
 */
const getPopularKeywords = async (params = {}) => {
  const response = await api.get('/news/popular-keywords', { params });
  return response.data;
};

/**
 * 뉴스 소스별 감성 분포 가져오기
 * @param {Object} params - 필터링 옵션 (날짜 범위 등)
 * @returns {Promise<Object>} 소스별 감성 분포 데이터
 */
const getSourceSentimentDistribution = async (params = {}) => {
  const response = await api.get('/news/source-sentiment', { params });
  return response.data;
};

/**
 * 특정 키워드에 대한 뉴스 검색
 * @param {string} keyword - 검색 키워드
 * @param {Object} params - 추가 검색 옵션 (날짜 범위, 페이지 등)
 * @returns {Promise<Object>} 검색 결과
 */
const searchNews = async (keyword, params = {}) => {
  const response = await api.get('/news/search', {
    params: {
      keyword,
      ...params,
    },
  });
  return response.data;
};

const newsService = {
  getNews,
  getNewsItem,
  getSentimentAnalysis,
  getSentimentTrend,
  getPopularKeywords,
  getSourceSentimentDistribution,
  searchNews,
};

export default newsService;