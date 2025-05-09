/**
 * 감성 분석 관련 타입 정의
 */

// 감성 분석 결과 타입
export interface SentimentResult {
  id?: string; // 결과 ID
  text: string;
  label: 'positive' | 'negative' | 'neutral';
  score: number;
  scores: {
    positive: number;
    neutral: number;
    negative: number;
  };
  model: string;
  language: string;
  timestamp: string;
}

// 감성 분석 모델 타입
export interface SentimentModel {
  id: string;
  name: string;
  description: string;
  languages: string[];
  isDefault: boolean;
}

// 감성 분석 매개변수 타입
export interface SentimentAnalysisParams {
  text: string;
  modelId?: string;
  model?: string; // 레거시 코드와의 호환성을 위해 추가
  language?: string;
}

// 감성 분석 모델 성능 타입
export interface SentimentModelPerformance {
  modelId: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  testSetSize: number;
  testDate: string;
}

// 감성 분석 통계 타입
export interface SentimentStats {
  total: number;
  positive: number;
  neutral: number;
  negative: number;
  positivePercent: number;
  neutralPercent: number;
  negativePercent: number;
  timePeriod: string;
  startDate: string;
  endDate: string;
}

// 감성 트렌드 타입
export interface SentimentTrend {
  date: string;
  positive: number;
  neutral: number;
  negative: number;
  total: number;
}

// 감성 분석 피드백 타입
export interface SentimentFeedback {
  resultId: string;
  userId: string;
  originalLabel: 'positive' | 'negative' | 'neutral';
  correctedLabel: 'positive' | 'negative' | 'neutral';
  comment?: string;
  createdAt: string;
}

// 주식 감성 트렌드 타입
export interface StockSentimentTrend {
  symbol: string;
  period: string;
  data: {
    date: string;
    sentiment: number;
    volume: number;
    price: number;
  }[];
  correlation: number;
}

// 감성 분석 피드백 결과 타입
export interface SentimentFeedbackResult {
  id: string;
  analysisId: string;
  isCorrect: boolean;
  userSentiment?: string;
  comment?: string;
  createdAt: string;
  updatedAt: string;
}

// 감성 분석 상태 타입
export interface SentimentAnalysisState {
  results: Record<string, SentimentResult>;
  isLoading: boolean;
  error: string | null;

  // 모델 관련
  models: SentimentModel[];
  modelsLoading: boolean;
  modelsError: string | null;

  // 통계 관련
  stats: SentimentStats | null;
  statsLoading: boolean;
  statsError: string | null;

  // 트렌드 관련
  trend: SentimentTrend[];
  trendLoading: boolean;
  trendError: string | null;

  // 주식 감성 트렌드 관련
  stockSentimentTrend: StockSentimentTrend | null;
  stockSentimentLoading: boolean;
  stockSentimentError: string | null;

  // 피드백 관련
  feedbackResult: SentimentFeedbackResult | null;
  feedbackLoading: boolean;
  feedbackError: string | null;

  // 배치 분석 관련
  batchResults: SentimentResult[];
  batchLoading: boolean;
  batchError: string | null;
}
