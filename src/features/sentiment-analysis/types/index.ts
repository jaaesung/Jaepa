/**
 * 감성 분석 관련 타입 모듈
 * 
 * 감성 분석 관련 타입 정의를 제공합니다.
 */

// 감성 분석 매개변수
export interface SentimentAnalysisParams {
  text: string;
  model?: string;
  language?: string;
}

// 감성 분석 결과
export interface SentimentResult {
  text: string;
  label: 'positive' | 'neutral' | 'negative';
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

// 감성 분석 상태
export interface SentimentAnalysisState {
  results: Record<string, SentimentResult>;
  isLoading: boolean;
  error: string | null;
}

// 감성 분석 모델
export interface SentimentModel {
  id: string;
  name: string;
  description: string;
  languages: string[];
  isDefault: boolean;
}

// 감성 분석 통계
export interface SentimentStats {
  positive: number;
  neutral: number;
  negative: number;
  total: number;
}

// 감성 분석 트렌드
export interface SentimentTrend {
  date: string;
  positive: number;
  neutral: number;
  negative: number;
}
