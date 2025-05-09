/**
 * 뉴스 서비스 모듈
 *
 * 뉴스 관련 API 서비스를 제공합니다.
 */

import api from '../../../services/api';
import { API_SERVICES } from '../../../core/constants/api';
import { NewsArticle, PaginatedNewsResponse, FetchNewsParams } from '../types';

// 뉴스 관련 API 서비스
const newsService = {
  // 뉴스 목록 가져오기
  getAll: async (params: FetchNewsParams = {}): Promise<PaginatedNewsResponse> => {
    const url = api.buildUrl(API_SERVICES.NEWS, '');
    return api.get<PaginatedNewsResponse>(url, { params });
  },

  // 특정 뉴스 기사 가져오기
  getById: async (id: string): Promise<NewsArticle> => {
    const url = api.buildUrl(API_SERVICES.NEWS, id);
    return api.get<NewsArticle>(url);
  },

  // 뉴스 감성 분석 결과 가져오기
  getSentiment: async (
    id: string
  ): Promise<{ positive: number; neutral: number; negative: number }> => {
    const url = api.buildUrl(API_SERVICES.NEWS, `${id}/sentiment`);
    return api.get<{
      positive: number;
      neutral: number;
      negative: number;
    }>(url);
  },

  // 뉴스 감성 트렌드 가져오기
  getSentimentTrend: async (
    params: {
      startDate?: string;
      endDate?: string;
      interval?: 'day' | 'week' | 'month';
    } = {}
  ): Promise<{ date: string; positive: number; neutral: number; negative: number }[]> => {
    const url = api.buildUrl(API_SERVICES.NEWS, 'sentiment-trend');
    return api.get<{ date: string; positive: number; neutral: number; negative: number }[]>(url, {
      params,
    });
  },

  // 인기 키워드 가져오기
  getPopularKeywords: async (
    params: { limit?: number; startDate?: string; endDate?: string } = {}
  ): Promise<{ text: string; value: number; sentiment: number }[]> => {
    const url = api.buildUrl(API_SERVICES.NEWS, 'popular-keywords');
    return api.get<{ text: string; value: number; sentiment: number }[]>(url, { params });
  },

  // 뉴스 검색
  search: async (query: string, params: FetchNewsParams = {}): Promise<PaginatedNewsResponse> => {
    const searchParams = { ...params, query };
    const url = api.buildUrl(API_SERVICES.NEWS, 'search');
    return api.get<PaginatedNewsResponse>(url, { params: searchParams });
  },

  // 카테고리 목록 가져오기
  getCategories: async (): Promise<string[]> => {
    const url = api.buildUrl(API_SERVICES.NEWS, 'categories');
    return api.get<string[]>(url);
  },

  // 출처 목록 가져오기
  getSources: async (): Promise<string[]> => {
    const url = api.buildUrl(API_SERVICES.NEWS, 'sources');
    return api.get<string[]>(url);
  },
};

export default newsService;
