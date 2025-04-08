// 전역 타입 선언

// 사용자 관련 타입
export interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  createdAt: string;
  updatedAt: string;
}

// 인증 상태 관련 타입
export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
}

// 뉴스 기사 관련 타입
export interface NewsArticle {
  id: string;
  title: string;
  content: string;
  source: string;
  url: string;
  publishedDate: string;
  sentiment?: {
    positive: number;
    neutral: number;
    negative: number;
  };
  keywords: string[];
}

// 뉴스 상태 관련 타입
export interface NewsState {
  articles: NewsArticle[];
  isLoading: boolean;
  error: string | null;
}

// 주식 데이터 관련 타입
export interface StockData {
  id: string;
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  date: string;
  historical?: {
    date: string;
    price: number;
  }[];
}

// 주식 상태 관련 타입
export interface StockState {
  stocks: StockData[];
  selectedStock: StockData | null;
  isLoading: boolean;
  error: string | null;
}

// UI 상태 관련 타입
export interface UiState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  notifications: Notification[];
}

// 알림 관련 타입
export interface Notification {
  id: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  createdAt: string;
}

// 전체 스토어 상태 타입
export interface RootState {
  auth: AuthState;
  news: NewsState;
  stocks: StockState;
  ui: UiState;
}
