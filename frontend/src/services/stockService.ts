import api from './api';
import { StockData } from '../types';

type PeriodType = '1d' | '1w' | '1m' | '3m' | '6m' | '1y' | '5y';
type SentimentType = 'all' | 'positive' | 'negative' | 'neutral';
type IndicatorType = 'sma' | 'ema' | 'rsi' | 'macd' | 'bollinger' | 'obv';

interface StockDataResponse {
  data: StockData;
  historical: {
    date: string;
    price: number;
    volume: number;
    open: number;
    high: number;
    low: number;
    close: number;
  }[];
}

interface StockAnalysisResponse {
  symbol: string;
  analysis: {
    technical: {
      indicators: Record<string, any>;
      signals: Record<string, string>;
      summary: string;
    };
    fundamental: {
      pe_ratio: number;
      eps: number;
      market_cap: number;
      dividend_yield: number;
      revenue_growth: number;
      profit_margin: number;
    };
    sentiment: {
      news_sentiment: {
        positive: number;
        neutral: number;
        negative: number;
      };
      sentiment_trend: {
        date: string;
        sentiment: number;
      }[];
    };
  };
}

interface CorrelationResponse {
  symbol: string;
  sentiment_type: SentimentType;
  correlation_data: {
    date: string;
    price: number;
    sentiment: number;
  }[];
  correlation_coefficient: number;
  analysis: string;
}

interface TechnicalIndicatorResponse {
  symbol: string;
  indicators: Record<IndicatorType, {
    dates: string[];
    values: number[];
    signals?: { date: string; signal: 'buy' | 'sell' | 'hold' }[];
  }>;
}

interface CompareStocksResponse {
  period: PeriodType;
  stocks: {
    symbol: string;
    name: string;
    data: {
      date: string;
      price: number;
    }[];
    performance: {
      absolute: number;
      percentage: number;
    };
  }[];
}

interface SectorStocksResponse {
  sector: string;
  stocks: {
    symbol: string;
    name: string;
    price: number;
    change: number;
    change_percent: number;
    market_cap: number;
  }[];
}

interface SearchStocksResponse {
  query: string;
  results: {
    symbol: string;
    name: string;
    type: string;
    exchange: string;
  }[];
}

/**
 * 주식 데이터 가져오기
 * @param symbol - 주식 심볼
 * @param period - 기간 (1d, 1w, 1m, 3m, 6m, 1y, 5y)
 * @returns 주식 데이터
 */
const getStockData = async (symbol: string, period: PeriodType = '1y'): Promise<StockDataResponse> => {
  const response = await api.get<StockDataResponse>(`/stocks/data/${symbol}`, {
    params: { period },
  });
  return response.data;
};

/**
 * 주식 분석 데이터 가져오기
 * @param symbol - 주식 심볼
 * @returns 주식 분석 데이터
 */
const getStockAnalysis = async (symbol: string): Promise<StockAnalysisResponse> => {
  const response = await api.get<StockAnalysisResponse>(`/stocks/analysis/${symbol}`);
  return response.data;
};

/**
 * 주식-감성 상관관계 데이터 가져오기
 * @param symbol - 주식 심볼
 * @param sentimentType - 감성 타입 (all, positive, negative, neutral)
 * @returns 상관관계 데이터
 */
const getCorrelationData = async (symbol: string, sentimentType: SentimentType = 'all'): Promise<CorrelationResponse> => {
  const response = await api.get<CorrelationResponse>(`/stocks/correlation/${symbol}`, {
    params: { sentiment_type: sentimentType },
  });
  return response.data;
};

/**
 * 기술적 지표 데이터 가져오기
 * @param symbol - 주식 심볼
 * @param indicators - 가져올 지표 목록 (예: ['sma', 'rsi', 'macd'])
 * @returns 기술적 지표 데이터
 */
const getTechnicalIndicators = async (symbol: string, indicators: IndicatorType[] = []): Promise<TechnicalIndicatorResponse> => {
  const response = await api.get<TechnicalIndicatorResponse>(`/stocks/indicators/${symbol}`, {
    params: { indicators: indicators.join(',') },
  });
  return response.data;
};

/**
 * 주식 비교 데이터 가져오기
 * @param symbols - 비교할 주식 심볼 목록
 * @param period - 기간 (1d, 1w, 1m, 3m, 6m, 1y, 5y)
 * @returns 주식 비교 데이터
 */
const compareStocks = async (symbols: string[], period: PeriodType = '1y'): Promise<CompareStocksResponse> => {
  const response = await api.get<CompareStocksResponse>('/stocks/compare', {
    params: {
      symbols: symbols.join(','),
      period,
    },
  });
  return response.data;
};

/**
 * 업종별 주식 목록 가져오기
 * @param sector - 업종 이름
 * @returns 업종별 주식 목록
 */
const getSectorStocks = async (sector: string): Promise<SectorStocksResponse> => {
  const response = await api.get<SectorStocksResponse>(`/stocks/sector/${sector}`);
  return response.data;
};

/**
 * 주식 검색
 * @param query - 검색어
 * @returns 검색 결과
 */
const searchStocks = async (query: string): Promise<SearchStocksResponse> => {
  const response = await api.get<SearchStocksResponse>('/stocks/search', {
    params: { query },
  });
  return response.data;
};

const stockService = {
  getStockData,
  getStockAnalysis,
  getCorrelationData,
  getTechnicalIndicators,
  compareStocks,
  getSectorStocks,
  searchStocks,
};

export default stockService;