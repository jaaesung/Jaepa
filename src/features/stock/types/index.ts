/**
 * 주식 관련 타입 모듈
 * 
 * 주식 관련 타입 정의를 제공합니다.
 */

// 기간 타입
export type PeriodType = '1d' | '5d' | '1mo' | '3mo' | '6mo' | '1y' | '2y' | '5y' | 'max';

// 주식 데이터 가져오기 매개변수
export interface FetchStockDataParams {
  symbol: string;
  period?: PeriodType;
  startDate?: string;
  endDate?: string;
}

// 여러 주식 데이터 가져오기 매개변수
export interface FetchMultipleStocksParams {
  symbols: string[];
  period?: PeriodType;
  startDate?: string;
  endDate?: string;
}

// 상관관계 가져오기 매개변수
export interface FetchCorrelationParams {
  symbol: string;
  sentimentType?: string;
  period?: PeriodType;
}

// 주식 데이터 포인트
export interface StockDataPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  adjClose?: number;
  timestamp?: number;
}

// 주식 데이터
export interface StockData {
  symbol: string;
  name?: string;
  currency?: string;
  exchange?: string;
  dataPoints: StockDataPoint[];
  indicators?: {
    sma?: { [key: string]: number[] };
    ema?: { [key: string]: number[] };
    rsi?: number[];
    macd?: {
      macd: number[];
      signal: number[];
      histogram: number[];
    };
    bbands?: {
      upper: number[];
      middle: number[];
      lower: number[];
    };
  };
}

// 주식 정보
export interface StockInfo {
  symbol: string;
  name: string;
  exchange: string;
  currency: string;
  price: number;
  change: number;
  changePercent: number;
  marketCap?: number;
  volume?: number;
  avgVolume?: number;
  high52Week?: number;
  low52Week?: number;
  open?: number;
  previousClose?: number;
  industry?: string;
  sector?: string;
  description?: string;
}

// 상관관계 데이터
export interface CorrelationData {
  symbol: string;
  sentimentType: string;
  period: string;
  correlation: number;
  dataPoints: {
    date: string;
    price: number;
    sentiment: number;
  }[];
}

// 주식 상태
export interface StockState {
  data: Record<string, StockData>;
  info: Record<string, StockInfo>;
  correlations: Record<string, CorrelationData>;
  watchlist: string[];
  isLoading: boolean;
  error: string | null;
}
