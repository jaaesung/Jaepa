/**
 * 뉴스 관련 타입 모듈
 * 
 * 뉴스 관련 타입 정의를 제공합니다.
 */

// 뉴스 검색 매개변수
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

// 페이지네이션된 뉴스 응답
export interface PaginatedNewsResponse {
  items: NewsArticle[];
  total: number;
  page: number;
  limit: number;
}

// 뉴스 기사
export interface NewsArticle {
  id: string;
  title: string;
  content: string;
  source: string;
  url: string;
  publishedDate: string;
  crawledDate?: string;
  sentiment?: {
    label?: string;
    score?: number;
    scores?: {
      positive: number;
      neutral: number;
      negative: number;
    };
    positive?: number;
    neutral?: number;
    negative?: number;
  };
  keywords: string[];
}

// 뉴스 상태
export interface NewsState {
  articles: NewsArticle[];
  items: NewsArticle[];
  isLoading: boolean;
  error: string | null;
}
