/**
 * 모의 데이터
 *
 * 테스트에 사용할 모의 데이터를 제공합니다.
 */

import { NewsArticle } from '@features/news/types';
import { StockInfo, StockDataPoint } from '@features/stock/types';
import { SentimentResult, SentimentModel } from '@features/sentiment-analysis/types';
import { User } from '@features/auth/types';

// 모의 사용자 데이터
export const mockUser: User = {
  id: '1',
  email: 'test@example.com',
  username: 'testuser',
  fullName: '테스트 사용자',
  role: 'user',
  createdAt: '2023-01-01T00:00:00.000Z',
  updatedAt: '2023-01-01T00:00:00.000Z',
};

// 모의 인증 응답 데이터
export const mockAuthResponse = {
  user: mockUser,
  accessToken: 'mock-access-token',
  refreshToken: 'mock-refresh-token',
};

// 모의 뉴스 기사 데이터
export const mockNewsArticles: NewsArticle[] = [
  {
    id: '1',
    title: '테스트 뉴스 제목 1',
    content: '테스트 뉴스 내용 1',
    summary: '테스트 뉴스 요약 1',
    source: 'Test Source 1',
    url: 'https://example.com/news/1',
    imageUrl: 'https://example.com/images/1.jpg',
    publishedAt: '2023-07-01T00:00:00.000Z',
    category: 'business',
    sentiment: {
      label: 'positive',
      score: 0.85,
      positive: 0.85,
      negative: 0.05,
      neutral: 0.1,
    },
    relevance: 0.85,
  },
  {
    id: '2',
    title: '테스트 뉴스 제목 2',
    content: '테스트 뉴스 내용 2',
    summary: '테스트 뉴스 요약 2',
    source: 'Test Source 2',
    url: 'https://example.com/news/2',
    imageUrl: 'https://example.com/images/2.jpg',
    publishedAt: '2023-07-02T00:00:00.000Z',
    category: 'technology',
    sentiment: {
      label: 'negative',
      score: 0.75,
      positive: 0.15,
      negative: 0.75,
      neutral: 0.1,
    },
    relevance: 0.75,
  },
];

// 모의 주식 정보 데이터
export const mockStockInfo: StockInfo = {
  symbol: 'AAPL',
  name: 'Apple Inc.',
  exchange: 'NASDAQ',
  sector: 'Technology',
  industry: 'Consumer Electronics',
  currency: 'USD',
  volume: 60000000,
  marketCap: 2800000000000,
  peRatio: 28.5,
  lastUpdated: '2023-07-02T00:00:00.000Z',

  change: 2.5,
  changePercent: 1.25,
  price: 190.5,
};

// 모의 주식 가격 데이터
export const mockStockPrices: StockDataPoint[] = [
  {
    date: '2023-07-01',
    open: 185.0,
    high: 188.5,
    low: 184.2,
    close: 187.5,
    volume: 55000000,
  },
  {
    date: '2023-07-02',
    open: 187.5,
    high: 191.2,
    low: 186.8,
    close: 190.5,
    volume: 60000000,
  },
];

// 모의 감성 분석 결과 데이터
export const mockSentimentResult: SentimentResult = {
  id: '1',
  text: '테스트 텍스트',
  label: 'positive',
  score: 0.85,
  scores: {
    positive: 0.85,
    neutral: 0.1,
    negative: 0.05,
  },
  model: 'finbert',
  language: 'ko',
  timestamp: '2023-07-01T00:00:00.000Z',
};

// 모의 감성 분석 모델 데이터
export const mockSentimentModels: SentimentModel[] = [
  {
    id: 'finbert',
    name: 'FinBERT',
    description: '금융 도메인에 특화된 BERT 모델',
    isDefault: true,
    languages: ['en', 'ko'],
  },
  {
    id: 'gdelt',
    name: 'GDELT',
    description: 'GDELT 프로젝트의 감성 분석 모델',
    isDefault: false,
    languages: ['en'],
  },
];

// 모의 감성 트렌드 데이터
export const mockSentimentTrend = {
  symbol: 'AAPL',
  period: '3mo',
  data: [
    { date: '2023-05-01', positive: 0.65, neutral: 0.25, negative: 0.1 },
    { date: '2023-06-01', positive: 0.55, neutral: 0.3, negative: 0.15 },
    { date: '2023-07-01', positive: 0.7, neutral: 0.2, negative: 0.1 },
  ],
};

// 모의 상관관계 데이터
export const mockCorrelationData = {
  symbol: 'AAPL',
  sentimentType: 'positive',
  period: '3mo',
  correlation: 0.65,
  data: [
    { date: '2023-05-01', price: 170.5, sentiment: 0.65 },
    { date: '2023-06-01', price: 180.2, sentiment: 0.55 },
    { date: '2023-07-01', price: 190.5, sentiment: 0.7 },
  ],
};

// 모의 인기 주식 데이터
export const mockPopularStocks = [
  { symbol: 'AAPL', name: 'Apple Inc.', change: 2.5, changePercent: 1.25 },
  { symbol: 'MSFT', name: 'Microsoft Corporation', change: 1.8, changePercent: 0.75 },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', change: -0.5, changePercent: -0.25 },
  { symbol: 'AMZN', name: 'Amazon.com, Inc.', change: 3.2, changePercent: 1.5 },
  { symbol: 'TSLA', name: 'Tesla, Inc.', change: -2.1, changePercent: -1.2 },
];
