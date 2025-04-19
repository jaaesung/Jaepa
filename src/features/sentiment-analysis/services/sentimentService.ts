/**
 * 감성 분석 서비스 모듈
 *
 * 감성 분석 관련 API 서비스를 제공합니다.
 */

import api from '../../../services/api';
import { API_SERVICES, API_ENDPOINTS } from '../../../core/constants/api';
import {
  SentimentAnalysisParams,
  SentimentResult,
  SentimentModel,
  SentimentStats,
  SentimentTrend,
} from '../types';

// 감성 분석 관련 API 서비스
const sentimentService = {
  // 텍스트 감성 분석
  analyzeText: async (params: SentimentAnalysisParams): Promise<SentimentResult> => {
    const url = api.buildUrl(API_SERVICES.ANALYSIS, API_ENDPOINTS.SENTIMENT.ANALYZE);
    return api.post<SentimentResult>(url, params);
  },

  // 뉴스 기사 감성 분석
  analyzeArticle: async (articleId: string): Promise<SentimentResult> => {
    const url = api.buildUrl(API_SERVICES.ANALYSIS, `sentiment/article/${articleId}`);
    return api.get<SentimentResult>(url);
  },

  // 감성 분석 모델 목록 가져오기
  getModels: async (): Promise<SentimentModel[]> => {
    const url = api.buildUrl(API_SERVICES.ANALYSIS, 'sentiment/models');
    return api.get<SentimentModel[]>(url);
  },

  // 감성 분석 통계 가져오기
  getStats: async (
    params: { startDate?: string; endDate?: string } = {}
  ): Promise<SentimentStats> => {
    const url = api.buildUrl(API_SERVICES.ANALYSIS, 'sentiment/stats');
    return api.get<SentimentStats>(url, { params });
  },

  // 감성 분석 트렌드 가져오기
  getTrend: async (
    params: {
      startDate?: string;
      endDate?: string;
      interval?: 'day' | 'week' | 'month';
    } = {}
  ): Promise<SentimentTrend[]> => {
    const url = api.buildUrl(API_SERVICES.ANALYSIS, 'sentiment/trend');
    return api.get<SentimentTrend[]>(url, { params });
  },

  // 키워드 감성 분석
  analyzeKeyword: async (
    keyword: string,
    params: {
      startDate?: string;
      endDate?: string;
    } = {}
  ): Promise<SentimentResult> => {
    const url = api.buildUrl(API_SERVICES.ANALYSIS, `sentiment/keyword/${keyword}`);
    return api.get<SentimentResult>(url, { params });
  },

  // 주식 감성 트렌드 가져오기
  getStockSentimentTrend: async (symbol: string, period = '3mo'): Promise<any> => {
    const params = { period };
    const url = api.buildUrl(API_SERVICES.ANALYSIS, `sentiment/stock/${symbol}/trend`);
    return api.get<any>(url, { params });
  },

  // 감성 분석 피드백 제출
  submitFeedback: async (
    analysisId: string,
    feedback: { isCorrect: boolean; userSentiment?: string; comment?: string }
  ): Promise<any> => {
    const url = api.buildUrl(API_SERVICES.ANALYSIS, `sentiment/feedback/${analysisId}`);
    return api.post<any>(url, feedback);
  },

  // 배치 감성 분석
  analyzeBatchSentiment: async (texts: string[]): Promise<any> => {
    const url = api.buildUrl(API_SERVICES.ANALYSIS, 'sentiment/batch');
    return api.post<any>(url, { texts });
  },
};

export default sentimentService;
