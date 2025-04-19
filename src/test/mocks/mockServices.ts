/**
 * 모의 서비스
 *
 * 테스트에 사용할 모의 서비스를 제공합니다.
 */

// 서비스 모듈 가져오기 (실제 구현은 모킹됨)
import authService from '@features/auth/services/authService';
import newsService from '@features/news/services/newsService';
import stockService from '@features/stock/services/stockService';
import sentimentService from '@features/sentiment-analysis/services/sentimentService';
import {
  mockAuthResponse,
  mockNewsArticles,
  mockStockInfo,
  mockStockPrices,
  mockSentimentResult,
  mockSentimentModels,
  mockSentimentTrend,
  mockCorrelationData,
  mockPopularStocks,
} from './mockData';

// 모의 인증 서비스
jest.mock('@features/auth/services/authService', () => ({
  login: jest.fn().mockResolvedValue(mockAuthResponse),
  register: jest.fn().mockResolvedValue(mockAuthResponse),
  logout: jest.fn().mockResolvedValue({ success: true }),
  verifyToken: jest.fn().mockResolvedValue(mockAuthResponse),
  refreshToken: jest.fn().mockResolvedValue({ accessToken: 'new-mock-access-token' }),
  changePassword: jest.fn().mockResolvedValue({ success: true }),
  requestPasswordReset: jest.fn().mockResolvedValue({ success: true }),
  resetPassword: jest.fn().mockResolvedValue({ success: true }),
}));

// 모의 뉴스 서비스
jest.mock('@features/news/services/newsService', () => ({
  getNews: jest.fn().mockResolvedValue({
    articles: mockNewsArticles,
    totalItems: mockNewsArticles.length,
    totalArticles: mockNewsArticles.length,
    currentPage: 1,
    pageSize: 10,
  }),
  getNewsById: jest.fn().mockImplementation((id: string) => {
    const article = mockNewsArticles.find(article => article.id === id);
    return Promise.resolve(article || null);
  }),
  getNewsByCategory: jest.fn().mockResolvedValue({
    articles: mockNewsArticles,
    totalItems: mockNewsArticles.length,
  }),
  getNewsBySource: jest.fn().mockResolvedValue({
    articles: mockNewsArticles,
    totalItems: mockNewsArticles.length,
  }),
  searchNews: jest.fn().mockResolvedValue({
    articles: mockNewsArticles,
    totalItems: mockNewsArticles.length,
  }),
  getNewsCategories: jest.fn().mockResolvedValue(['business', 'technology', 'finance']),
  getNewsSources: jest.fn().mockResolvedValue(['Test Source 1', 'Test Source 2']),
}));

// 모의 주식 서비스
jest.mock('@features/stock/services/stockService', () => ({
  getStockInfo: jest.fn().mockResolvedValue(mockStockInfo),
  getStockPrices: jest.fn().mockResolvedValue(mockStockPrices),
  searchStocks: jest.fn().mockResolvedValue([
    { symbol: 'AAPL', name: 'Apple Inc.', exchange: 'NASDAQ' },
    { symbol: 'MSFT', name: 'Microsoft Corporation', exchange: 'NASDAQ' },
  ]),
  getCorrelation: jest.fn().mockResolvedValue(mockCorrelationData),
  getPopularStocks: jest.fn().mockResolvedValue(mockPopularStocks),
  getStockNews: jest.fn().mockResolvedValue(mockNewsArticles),
  addToWatchlist: jest.fn().mockResolvedValue({ success: true }),
  removeFromWatchlist: jest.fn().mockResolvedValue({ success: true }),
  getWatchlist: jest.fn().mockResolvedValue([
    { symbol: 'AAPL', name: 'Apple Inc.' },
    { symbol: 'MSFT', name: 'Microsoft Corporation' },
  ]),
}));

// 모의 감성 분석 서비스
jest.mock('@features/sentiment-analysis/services/sentimentService', () => ({
  analyzeSentiment: jest.fn().mockResolvedValue(mockSentimentResult),
  getSentimentModels: jest.fn().mockResolvedValue(mockSentimentModels),
  getSentimentHistory: jest.fn().mockResolvedValue([mockSentimentResult]),
  getStockSentimentTrend: jest.fn().mockResolvedValue(mockSentimentTrend),
}));

// 모의 서비스 내보내기
export { authService, newsService, stockService, sentimentService };
