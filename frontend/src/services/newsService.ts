import api from './api';
import { NewsArticle } from '../types';

interface NewsResponse {
  articles: NewsArticle[];
  total: number;
  page: number;
  limit: number;
}

interface SentimentAnalysis {
  positive: number;
  neutral: number;
  negative: number;
  confidence: number;
}

interface SentimentTrendItem {
  date: string;
  positive: number;
  neutral: number;
  negative: number;
}

interface SentimentTrendResponse {
  trend: SentimentTrendItem[];
  period: string;
}

interface KeywordItem {
  keyword: string;
  count: number;
  sentiment: number;
}

interface KeywordsResponse {
  keywords: KeywordItem[];
  period: string;
}

interface SourceSentiment {
  source: string;
  positive: number;
  neutral: number;
  negative: number;
  articles_count: number;
}

interface SourceSentimentResponse {
  sources: SourceSentiment[];
  period: string;
}

interface NewsFilters {
  keyword?: string;
  startDate?: string;
  endDate?: string;
  source?: string;
  sentiment?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  [key: string]: any;
}

/**
 * 뉴스 데이터 가져오기
 * @param page - 페이지 번호
 * @param limit - 페이지당 항목 수
 * @param filters - 필터링 옵션 (키워드, 날짜 범위 등)
 * @returns 뉴스 데이터
 */
const getNews = async (page = 1, limit = 10, filters: NewsFilters = {}): Promise<NewsResponse> => {
  const params = {
    page,
    limit,
    ...filters,
  };
  
  const response = await api.get<NewsResponse>('/news', { params });
  return response.data;
};

/**
 * 특정 뉴스 항목 가져오기
 * @param newsId - 뉴스 ID
 * @returns 뉴스 상세 데이터
 */
const getNewsItem = async (newsId: string): Promise<NewsArticle> => {
  const response = await api.get<NewsArticle>(`/news/${newsId}`);
  return response.data;
};

/**
 * 뉴스 감성 분석 결과 가져오기
 * @param newsId - 뉴스 ID
 * @returns 감성 분석 결과
 */
const getSentimentAnalysis = async (newsId: string): Promise<SentimentAnalysis> => {
  const response = await api.get<SentimentAnalysis>(`/news/${newsId}/sentiment`);
  return response.data;
};

/**
 * 뉴스 감성 트렌드 가져오기
 * @param params - 트렌드 필터링 옵션 (날짜 범위, 키워드 등)
 * @returns 감성 트렌드 데이터
 */
const getSentimentTrend = async (params: NewsFilters = {}): Promise<SentimentTrendResponse> => {
  const response = await api.get<SentimentTrendResponse>('/news/sentiment-trend', { params });
  return response.data;
};

/**
 * 인기 키워드 가져오기
 * @param params - 필터링 옵션 (날짜 범위, 상위 항목 수 등)
 * @returns 인기 키워드 데이터
 */
const getPopularKeywords = async (params: NewsFilters = {}): Promise<KeywordsResponse> => {
  const response = await api.get<KeywordsResponse>('/news/popular-keywords', { params });
  return response.data;
};

/**
 * 뉴스 소스별 감성 분포 가져오기
 * @param params - 필터링 옵션 (날짜 범위 등)
 * @returns 소스별 감성 분포 데이터
 */
const getSourceSentimentDistribution = async (params: NewsFilters = {}): Promise<SourceSentimentResponse> => {
  const response = await api.get<SourceSentimentResponse>('/news/source-sentiment', { params });
  return response.data;
};

/**
 * 특정 키워드에 대한 뉴스 검색
 * @param keyword - 검색 키워드
 * @param params - 추가 검색 옵션 (날짜 범위, 페이지 등)
 * @returns 검색 결과
 */
const searchNews = async (keyword: string, params: NewsFilters = {}): Promise<NewsResponse> => {
  const response = await api.get<NewsResponse>('/news/search', {
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