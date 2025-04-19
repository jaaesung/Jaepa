/**
 * 대시보드 관련 타입 정의
 */

import { NewsArticle } from '../../news/types';
import { StockInfo, StockData } from '../../stock/types';
import { SentimentStats, SentimentTrend } from '../../sentiment-analysis/types';

// 위젯 위치 및 크기 타입
export interface WidgetPosition {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
  minW?: number;
  minH?: number;
  maxW?: number;
  maxH?: number;
  isResizable?: boolean;
  isDraggable?: boolean;
}

// 위젯 타입
export interface Widget {
  id: string;
  type: WidgetType;
  title: string;
  position: WidgetPosition;
  settings: Record<string, any>;
}

// 위젯 타입 열거형
export type WidgetType = 
  | 'stock-price'
  | 'stock-chart'
  | 'news-list'
  | 'sentiment-overview'
  | 'sentiment-trend'
  | 'watchlist'
  | 'popular-stocks'
  | 'calendar'
  | 'performance';

// 알림 타입
export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  createdAt: string;
}

// 대시보드 데이터 타입
export interface DashboardData {
  recentNews: NewsArticle[];
  popularStocks: StockInfo[];
  watchlistStocks: StockInfo[];
  stockData: Record<string, StockData[]>;
  sentimentStats: SentimentStats;
  sentimentTrends: SentimentTrend[];
  notifications: Notification[];
}

// 대시보드 설정 타입
export interface DashboardSettings {
  layout: Widget[];
  autoRefresh: boolean;
  refreshInterval: number;
  defaultStockSymbol: string;
  theme: 'light' | 'dark' | 'system';
}

// 대시보드 상태 타입
export interface DashboardState {
  data: DashboardData | null;
  settings: DashboardSettings;
  isLoading: boolean;
  error: string | null;
}
