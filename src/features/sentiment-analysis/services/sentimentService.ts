/**
 * 감성 분석 서비스 모듈
 *
 * 감성 분석 관련 API 서비스를 제공합니다.
 */

import apiClient from "../../../services/api";
import { API_SERVICES, API_ENDPOINTS } from "../../../core/constants/api";
import {
  SentimentAnalysisParams,
  SentimentResult,
  SentimentModel,
  SentimentStats,
  SentimentTrend,
} from "../types";

// 감성 분석 관련 API 서비스
const sentimentService = {
  // 텍스트 감성 분석
  analyzeText: async (
    params: SentimentAnalysisParams
  ): Promise<SentimentResult> => {
    return apiClient.post<SentimentResult>("analysis", "sentiment", params);
  },

  // 뉴스 기사 감성 분석
  analyzeArticle: async (articleId: string): Promise<SentimentResult> => {
    return apiClient.get<SentimentResult>(
      "analysis",
      `sentiment/article/${articleId}`
    );
  },

  // 감성 분석 모델 목록 가져오기
  getModels: async (): Promise<SentimentModel[]> => {
    return apiClient.get<SentimentModel[]>("analysis", "sentiment/models");
  },

  // 감성 분석 통계 가져오기
  getStats: async (
    params: { startDate?: string; endDate?: string } = {}
  ): Promise<SentimentStats> => {
    return apiClient.get<SentimentStats>("analysis", "sentiment/stats", params);
  },

  // 감성 분석 트렌드 가져오기
  getTrend: async (
    params: {
      startDate?: string;
      endDate?: string;
      interval?: "day" | "week" | "month";
    } = {}
  ): Promise<SentimentTrend[]> => {
    return apiClient.get<SentimentTrend[]>(
      "analysis",
      "sentiment/trend",
      params
    );
  },

  // 키워드 감성 분석
  analyzeKeyword: async (
    keyword: string,
    params: {
      startDate?: string;
      endDate?: string;
    } = {}
  ): Promise<SentimentResult> => {
    return apiClient.get<SentimentResult>(
      "analysis",
      `sentiment/keyword/${keyword}`,
      params
    );
  },
};

export default sentimentService;
