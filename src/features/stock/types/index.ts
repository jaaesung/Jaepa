/**
 * 주식 관련 타입 정의
 */

// 주식 기간 타입
export type PeriodType = '1d' | '5d' | '1w' | '1mo' | '3mo' | '6m' | '1y' | '5y' | 'max';

// 주식 데이터 포인트 타입
export interface StockDataPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  changePercent?: number;
  ema20?: number;
  ema50?: number;
  sma20?: number;
  sma50?: number;
  rsi?: number;
  macd?: number;
  macdSignal?: number;
  macdHistogram?: number;
  bollingerUpper?: number;
  bollingerLower?: number;
  bollingerMiddle?: number;
}

// 주식 데이터 타입
export interface StockData {
  symbol: string;
  name?: string;
  period?: PeriodType;
  interval?: string;
  currency?: string;
  dataPoints: StockDataPoint[];
  startDate?: string;
  endDate?: string;
}

// 주식 정보 타입
export interface StockInfo {
  symbol: string;
  name: string;
  currency: string;
  exchange: string;
  sector?: string;
  industry?: string;
  price?: number;
  change?: number;
  changePercent?: number;
  marketCap?: number;
  volume?: number;
  lastUpdated?: string;
  peRatio?: number;
}

// 기술적 지표 타입
export interface TechnicalIndicators {
  rsi: number;
  macd: number;
  macdSignal: number;
  ema20: number;
  ema50: number;
  bollingerPosition: number;
  atr: number;
  lastUpdated: string;
}

// 기본 재무 데이터 타입
export interface FinancialData {
  symbol: string;
  revenue: number;
  revenueGrowth: number;
  netIncome: number;
  eps: number;
  epsGrowth: number;
  pe: number;
  pbv: number;
  roe: number;
  debtToEquity: number;
  currentRatio: number;
  dividendYield: number;
  reportDate: string;
}

// 상관관계 데이터 타입
export interface CorrelationData {
  symbol1: string;
  symbol2: string;
  symbol?: string; // 레거시 코드와의 호환성을 위해 추가
  sentimentType?: string; // 레거시 코드와의 호환성을 위해 추가
  correlation: number;
  period: string;
  startDate: string;
  endDate: string;
}

// 분석가 평가 타입
export interface AnalystRating {
  buy: number;
  hold: number;
  sell: number;
  targetPrice: number;
  currentPrice: number;
  consensus: 'Buy' | 'Hold' | 'Sell';
  lastUpdated: string;
}

// 섹터 성과 타입
export interface SectorPerformance {
  sector: string;
  change1d: number;
  change1w: number;
  change1m: number;
  change3m: number;
  change1y: number;
}

// 주식 상태 타입
export interface StockState {
  currentStock: StockInfo | null;
  data: Record<string, StockData>;
  info: Record<string, StockInfo>;
  correlations: Record<string, CorrelationData>;
  searchResults: StockInfo[];
  popularStocks: StockInfo[];
  watchlist: string[];
  stockNews: any[];
  financials: any;
  analysis: any;
  sectorPerformance: SectorPerformance[];
  technicalIndicators: TechnicalIndicators | null;
  period: PeriodType;
  isLoading: boolean;
  error: string | null;
  searchLoading: boolean;
  searchError: string | null;
  popularLoading: boolean;
  popularError: string | null;
  newsLoading: boolean;
  newsError: string | null;
  financialsLoading: boolean;
  financialsError: string | null;
  analysisLoading: boolean;
  analysisError: string | null;
  sectorLoading: boolean;
  sectorError: string | null;
  indicatorsLoading: boolean;
  indicatorsError: string | null;
}
