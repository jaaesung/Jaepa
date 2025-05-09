/**
 * 주식 서비스 모듈
 *
 * 주식 관련 API 서비스를 제공합니다.
 */

import api from '../../../services/api';
import { API_SERVICES } from '../../../core/constants/api';
import { StockData, StockInfo, CorrelationData, PeriodType } from '../types';

// 주식 관련 API 서비스
const stockService = {
  // 주식 데이터 가져오기
  getStockData: async (
    symbol: string,
    period: PeriodType = '1mo',
    startDate?: string,
    endDate?: string
  ): Promise<StockData> => {
    const params: Record<string, any> = { period };
    if (startDate) params.startDate = startDate;
    if (endDate) params.endDate = endDate;

    const url = api.buildUrl(API_SERVICES.STOCKS, `${symbol}`);
    return api.get<StockData>(url, { params });
  },

  // 여러 주식 데이터 가져오기
  getMultipleStocks: async (
    symbols: string[],
    period: PeriodType = '1mo',
    startDate?: string,
    endDate?: string
  ): Promise<Record<string, StockData>> => {
    const params: Record<string, any> = { symbols: symbols.join(','), period };
    if (startDate) params.startDate = startDate;
    if (endDate) params.endDate = endDate;

    const url = api.buildUrl(API_SERVICES.STOCKS, 'batch');
    return api.get<Record<string, StockData>>(url, { params });
  },

  // 주식 정보 가져오기
  getStockInfo: async (symbol: string): Promise<StockInfo> => {
    const url = api.buildUrl(API_SERVICES.STOCKS, `${symbol}/info`);
    return api.get<StockInfo>(url);
  },

  // 여러 주식 정보 가져오기
  getMultipleStockInfo: async (symbols: string[]): Promise<Record<string, StockInfo>> => {
    const params = { symbols: symbols.join(',') };
    const url = api.buildUrl(API_SERVICES.STOCKS, 'info/batch');
    return api.get<Record<string, StockInfo>>(url, { params });
  },

  // 상관관계 데이터 가져오기
  getCorrelation: async (
    symbol: string,
    sentimentType = 'all',
    period: PeriodType = '3mo'
  ): Promise<CorrelationData> => {
    const params = { sentimentType, period };
    const url = api.buildUrl(API_SERVICES.ANALYSIS, `correlation/${symbol}`);
    return api.get<CorrelationData>(url, { params });
  },

  // 주식 검색
  searchStocks: async (query: string): Promise<StockInfo[]> => {
    const params = { q: query };
    const url = api.buildUrl(API_SERVICES.STOCKS, 'search');
    return api.get<StockInfo[]>(url, { params });
  },

  // 인기 주식 가져오기
  getPopularStocks: async (): Promise<StockInfo[]> => {
    const url = api.buildUrl(API_SERVICES.STOCKS, 'popular');
    return api.get<StockInfo[]>(url);
  },

  // 주식 기술적 지표 가져오기
  getTechnicalIndicators: async (
    symbol: string,
    indicators: string[],
    period: PeriodType = '1mo'
  ): Promise<any> => {
    const params = { indicators: indicators.join(','), period };
    const url = api.buildUrl(API_SERVICES.STOCKS, `${symbol}/indicators`);
    return api.get<any>(url, { params });
  },

  // 주식 뉴스 가져오기
  getStockNews: async (symbol: string, limit = 10): Promise<any> => {
    const params = { limit };
    const url = api.buildUrl(API_SERVICES.STOCKS, `${symbol}/news`);
    return api.get<any>(url, { params });
  },

  // 재무 정보 가져오기
  getFinancials: async (symbol: string): Promise<any> => {
    const url = api.buildUrl(API_SERVICES.STOCKS, `${symbol}/financials`);
    return api.get<any>(url);
  },

  // 분석 정보 가져오기
  getAnalysis: async (symbol: string): Promise<any> => {
    const url = api.buildUrl(API_SERVICES.STOCKS, `${symbol}/analysis`);
    return api.get<any>(url);
  },

  // 섹터 성과 가져오기
  getSectorPerformance: async (): Promise<any> => {
    const url = api.buildUrl(API_SERVICES.STOCKS, 'sectors/performance');
    return api.get<any>(url);
  },
};

export default stockService;
