/**
 * 주식 서비스 모듈
 *
 * 주식 관련 API 서비스를 제공합니다.
 */

import apiClient from "../../../services/api";
import { API_SERVICES, API_ENDPOINTS } from "../../../core/constants/api";
import { StockData, StockInfo, CorrelationData, PeriodType } from "../types";

// 주식 관련 API 서비스
const stockService = {
  // 주식 데이터 가져오기
  getStockData: async (
    symbol: string,
    period: PeriodType = "1mo",
    startDate?: string,
    endDate?: string
  ): Promise<StockData> => {
    const params: Record<string, any> = { period };
    if (startDate) params.startDate = startDate;
    if (endDate) params.endDate = endDate;

    return apiClient.get<StockData>("stocks", symbol, params);
  },

  // 여러 주식 데이터 가져오기
  getMultipleStocks: async (
    symbols: string[],
    period: PeriodType = "1mo",
    startDate?: string,
    endDate?: string
  ): Promise<Record<string, StockData>> => {
    const params: Record<string, any> = { symbols: symbols.join(","), period };
    if (startDate) params.startDate = startDate;
    if (endDate) params.endDate = endDate;

    return apiClient.get<Record<string, StockData>>("stocks", "batch", params);
  },

  // 주식 정보 가져오기
  getStockInfo: async (symbol: string): Promise<StockInfo> => {
    return apiClient.get<StockInfo>("stocks", `${symbol}/info`);
  },

  // 여러 주식 정보 가져오기
  getMultipleStockInfo: async (
    symbols: string[]
  ): Promise<Record<string, StockInfo>> => {
    const params = { symbols: symbols.join(",") };
    return apiClient.get<Record<string, StockInfo>>(
      "stocks",
      "info/batch",
      params
    );
  },

  // 상관관계 데이터 가져오기
  getCorrelation: async (
    symbol: string,
    sentimentType: string = "all",
    period: PeriodType = "3mo"
  ): Promise<CorrelationData> => {
    const params = { sentimentType, period };
    return apiClient.get<CorrelationData>(
      "analysis",
      `correlation/${symbol}`,
      params
    );
  },

  // 주식 검색
  searchStocks: async (query: string): Promise<StockInfo[]> => {
    const params = { q: query };
    return apiClient.get<StockInfo[]>("stocks", "search", params);
  },

  // 인기 주식 가져오기
  getPopularStocks: async (): Promise<StockInfo[]> => {
    return apiClient.get<StockInfo[]>("stocks", "popular");
  },

  // 주식 기술적 지표 가져오기
  getTechnicalIndicators: async (
    symbol: string,
    indicators: string[],
    period: PeriodType = "1mo"
  ): Promise<any> => {
    const params = { indicators: indicators.join(","), period };
    return apiClient.get<any>("stocks", `${symbol}/indicators`, params);
  },
};

export default stockService;
