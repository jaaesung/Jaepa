// 전역 타입 선언

// Redux 액션 관련 타입
export type AsyncThunkConfig = {
  state?: unknown;
  dispatch?: unknown;
  extra?: unknown;
  rejectValue: string;
  serializedErrorType?: unknown;
  pendingMeta?: unknown;
  fulfilledMeta?: unknown;
  rejectedMeta?: unknown;
};

export type PeriodType = "1d" | "1w" | "1m" | "3m" | "6m" | "1y";

export interface FetchStockDataParams {
  symbol: string;
  period?: PeriodType;
}

export interface FetchMultipleStocksParams {
  symbols: string[];
  period?: PeriodType;
}

export interface FetchCorrelationParams {
  symbol: string;
  sentimentType?: string;
}

export interface FetchNewsParams {
  page?: number;
  limit?: number;
  filters?: {
    startDate?: string;
    endDate?: string;
    source?: string;
    sentiment?: string;
    keyword?: string;
  };
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  username: string;
  name: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  isAuthenticated: boolean;
  user: User;
  token?: string;
}

export interface PaginatedNewsResponse {
  items: NewsArticle[];
  total: number;
  page: number;
  limit: number;
}

// 상관관계 데이터 타입
export interface CorrelationData {
  date: string;
  price: number;
  sentiment: number;
  volume: number;
}

// 사용자 관련 타입
export interface User {
  id: string;
  username: string;
  name: string; // 이름 필드 추가
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
  // 백엔드와 호환을 위한 필드 정의
  id: string; // 백엔드에서는 _id로 사용될 수 있음
  title: string;
  content: string; // 백엔드에서는 description으로 사용될 수 있음
  source: string;
  url: string; // 백엔드에서는 article_url로 사용될 수 있음
  publishedDate: string; // 백엔드에서는 published_date 또는 published_utc로 사용될 수 있음
  crawledDate?: string; // 백엔드에서는 crawled_date로 사용될 수 있음
  sentiment?: {
    label?: string; // 백엔드에서 사용하는 감성 레이블
    score?: number; // 백엔드에서 사용하는 감성 점수
    scores?: {
      // 백엔드에서 사용하는 상세 점수
      positive: number;
      neutral: number;
      negative: number;
    };
    // 프론트엔드에서 사용하는 감성 필드
    positive?: number;
    neutral?: number;
    negative?: number;
  };
  keywords: string[];
}

// 뉴스 상태 관련 타입
export interface NewsState {
  articles: NewsArticle[];
  items: NewsArticle[];
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
  stockData: StockData | null;
  stockAnalysis: any | null;
  correlationData: CorrelationData[] | null;
  sentimentAnalysis: any | null;
  searchResults: { symbol: string; name: string }[];
  isLoading: boolean;
  analysisLoading: boolean;
  correlationLoading: boolean;
  sentimentLoading: boolean;
  searchLoading: boolean;
  error: string | null;
  analysisError: string | null;
  correlationError: string | null;
  sentimentError: string | null;
  searchError: string | null;
}

// UI 상태 관련 타입
export interface UiState {
  sidebarOpen: boolean;
  theme: "light" | "dark";
  notifications: Notification[];
}

// 알림 관련 타입
export interface Notification {
  id: string;
  message: string;
  type: "info" | "success" | "warning" | "error";
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
