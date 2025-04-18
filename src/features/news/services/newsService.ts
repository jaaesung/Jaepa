/**
 * 뉴스 서비스 모듈
 *
 * 뉴스 관련 API 서비스를 제공합니다.
 */

import apiClient from "../../../services/api";
import { API_SERVICES, API_ENDPOINTS } from "../../../core/constants/api";
import { NewsArticle, PaginatedNewsResponse, FetchNewsParams } from "../types";

// 뉴스 관련 API 서비스
const newsService = {
  // 뉴스 목록 가져오기
  getAll: async (
    params: FetchNewsParams = {}
  ): Promise<PaginatedNewsResponse> => {
    return apiClient.get<PaginatedNewsResponse>("news", "", params);
  },

  // 특정 뉴스 기사 가져오기
  getById: async (id: string): Promise<NewsArticle> => {
    return apiClient.get<NewsArticle>("news", id);
  },

  // 뉴스 감성 분석 결과 가져오기
  getSentiment: async (
    id: string
  ): Promise<{ positive: number; neutral: number; negative: number }> => {
    return apiClient.get<{
      positive: number;
      neutral: number;
      negative: number;
    }>("news", `${id}/sentiment`);
  },

  // 뉴스 감성 트렌드 가져오기
  getSentimentTrend: async (
    params: {
      startDate?: string;
      endDate?: string;
      interval?: "day" | "week" | "month";
    } = {}
  ): Promise<
    { date: string; positive: number; neutral: number; negative: number }[]
  > => {
    return apiClient.get<
      { date: string; positive: number; neutral: number; negative: number }[]
    >("news", "sentiment-trend", params);
  },

  // 인기 키워드 가져오기
  getPopularKeywords: async (
    params: { limit?: number; startDate?: string; endDate?: string } = {}
  ): Promise<{ text: string; value: number; sentiment: number }[]> => {
    return apiClient.get<{ text: string; value: number; sentiment: number }[]>(
      "news",
      "popular-keywords",
      params
    );
  },
};

export default newsService;
