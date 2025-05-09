/**
 * 뉴스 관련 타입 정의
 */

// 뉴스 기사 타입
export interface NewsArticle {
  id: string;
  title: string;
  content: string;
  summary?: string;
  source: string;
  author?: string;
  url: string;
  publishedAt: string;
  publishedDate?: string; // 레거시 코드와의 호환성을 위해 추가
  updatedAt?: string;
  imageUrl?: string;
  category?: string;
  keywords?: string[];
  sentiment?: SentimentInfo;
}

// 감성 정보 타입
export interface SentimentInfo {
  label: 'positive' | 'negative' | 'neutral';
  score: number;
  positive: number;
  negative: number;
  neutral: number;
  scores?: {
    // 레거시 코드와의 호환성을 위해 추가
    positive: number;
    negative: number;
    neutral: number;
  };
}

// 뉴스 상태 타입
export interface NewsState {
  articles: NewsArticle[];
  selectedArticle: NewsArticle | null;
  totalArticles: number;
  currentPage: number;
  pageSize: number;
  categories: string[];
  sources: string[];
  isLoading: boolean;
  error: string | null;
}

// 페이지네이션 뉴스 응답 타입
export interface PaginatedNewsResponse {
  articles: NewsArticle[];
  items?: NewsArticle[]; // 레거시 코드와의 호환성을 위해 추가
  total: number;
  page: number;
  pageSize: number;
}

// 뉴스 가져오기 필터 타입
export interface NewsFilters {
  startDate?: string;
  endDate?: string;
  source?: string;
  sentiment?: string;
  keyword?: string;
  category?: string;
}

// 뉴스 가져오기 매개변수 타입
export interface FetchNewsParams {
  page?: number;
  pageSize?: number;
  limit?: number; // 레거시 코드와의 호환성을 위해 추가
  filters?: NewsFilters; // 필터 그룹화
  startDate?: string; // 직접 사용을 위해 유지
  endDate?: string; // 직접 사용을 위해 유지
  source?: string; // 직접 사용을 위해 유지
  sentiment?: string; // 직접 사용을 위해 유지
  keyword?: string; // 직접 사용을 위해 유지
  category?: string; // 직접 사용을 위해 유지
}

// 뉴스 검색 매개변수 타입
export interface SearchNewsParams extends FetchNewsParams {
  query: string;
}

// 인기 키워드 타입
export interface PopularKeyword {
  keyword: string;
  count: number;
  sentiment?: SentimentInfo;
}

// 감성 트렌드 타입
export interface SentimentTrend {
  date: string;
  positive: number;
  neutral: number;
  negative: number;
  total: number;
}

// 뉴스 인사이트 타입
export interface NewsInsight {
  id: string;
  title: string;
  description: string;
  score: number;
  sources: string[];
  createdAt: string;
}
