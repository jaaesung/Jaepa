/**
 * 뉴스 관련 타입 정의
 */

// 뉴스 기사 타입
export interface NewsArticle {
  id: string;
  title: string;
  content: string;
  summary: string;
  source: string;
  url: string;
  imageUrl: string;
  publishedAt: string;
  publishedDate?: string; // 후방 호환성을 위해 추가
  category: string;
  sentiment: {
    label: 'positive' | 'neutral' | 'negative';
    score: number;
    positive: number;
    negative: number;
    neutral: number;
    scores?: {
      // 후방 호환성을 위해 추가
      positive: number;
      negative: number;
      neutral: number;
    };
  };
  relevance?: number;
  keywords?: string[]; // 키워드 추가
}

// 뉴스 상태 타입
export interface NewsState {
  articles: NewsArticle[];
  isLoading: boolean;
  error: string | null;
}

// 페이지네이션된 뉴스 응답 타입
export interface PaginatedNewsResponse {
  items: NewsArticle[];
  articles?: NewsArticle[]; // 후방 호환성을 위해 추가
  totalItems: number;
  total?: number; // 후방 호환성을 위해 추가
  page: number;
  limit: number;
}

// 뉴스 필터 타입
export interface NewsFilters {
  keyword?: string;
  startDate?: string;
  endDate?: string;
  category?: string;
  source?: string;
  sentiment?: string;
}

// 뉴스 가져오기 매개변수 타입
export interface FetchNewsParams {
  page?: number;
  limit?: number;
  pageSize?: number; // 후방 호환성을 위해 추가
  filters?: NewsFilters;
}
