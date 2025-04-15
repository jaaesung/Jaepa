import api from './api';
import { NewsArticle, StockData, User } from '../types';

// API 엔드포인트 타입
type Endpoint = 'news' | 'stocks' | 'auth' | 'analysis';

// API 응답 타입
interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

// 페이지네이션된 응답 타입
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}

// API 클라이언트 클래스
class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
  }

  // GET 요청
  async get<T>(
    endpoint: Endpoint,
    path: string = '',
    params: Record<string, any> = {}
  ): Promise<T> {
    try {
      const url = `/${endpoint}${path ? `/${path}` : ''}`;
      const response = await api.get<ApiResponse<T>>(url, { params });
      return response.data.data;
    } catch (error: any) {
      console.error('API GET 요청 오류:', error);
      throw new Error(
        error.response?.data?.message || error.message || '요청을 처리하는 중 오류가 발생했습니다.'
      );
    }
  }

  // POST 요청
  async post<T>(endpoint: Endpoint, path: string = '', data: Record<string, any> = {}): Promise<T> {
    try {
      const url = `/${endpoint}${path ? `/${path}` : ''}`;
      const response = await api.post<ApiResponse<T>>(url, data);
      return response.data.data;
    } catch (error: any) {
      console.error('API POST 요청 오류:', error);
      throw new Error(
        error.response?.data?.message || error.message || '요청을 처리하는 중 오류가 발생했습니다.'
      );
    }
  }

  // PUT 요청
  async put<T>(endpoint: Endpoint, path: string = '', data: Record<string, any> = {}): Promise<T> {
    try {
      const url = `/${endpoint}${path ? `/${path}` : ''}`;
      const response = await api.put<ApiResponse<T>>(url, data);
      return response.data.data;
    } catch (error: any) {
      console.error('API PUT 요청 오류:', error);
      throw new Error(
        error.response?.data?.message || error.message || '요청을 처리하는 중 오류가 발생했습니다.'
      );
    }
  }

  // DELETE 요청
  async delete<T>(endpoint: Endpoint, path: string = ''): Promise<T> {
    try {
      const url = `/${endpoint}${path ? `/${path}` : ''}`;
      const response = await api.delete<ApiResponse<T>>(url);
      return response.data.data;
    } catch (error: any) {
      console.error('API DELETE 요청 오류:', error);
      throw new Error(
        error.response?.data?.message || error.message || '요청을 처리하는 중 오류가 발생했습니다.'
      );
    }
  }

  // 뉴스 관련 API
  news = {
    // 뉴스 목록 가져오기
    getAll: async (
      params: {
        page?: number;
        limit?: number;
        keyword?: string;
        startDate?: string;
        endDate?: string;
        source?: string;
        sentiment?: string;
      } = {}
    ): Promise<PaginatedResponse<NewsArticle>> => {
      return this.get<PaginatedResponse<NewsArticle>>('news', '', params);
    },

    // 특정 뉴스 기사 가져오기
    getById: async (id: string): Promise<NewsArticle> => {
      return this.get<NewsArticle>('news', id);
    },

    // 뉴스 감성 분석 결과 가져오기
    getSentiment: async (
      id: string
    ): Promise<{ positive: number; neutral: number; negative: number }> => {
      return this.get<{ positive: number; neutral: number; negative: number }>(
        'news',
        `${id}/sentiment`
      );
    },

    // 뉴스 감성 트렌드 가져오기
    getSentimentTrend: async (
      params: { startDate?: string; endDate?: string; interval?: 'day' | 'week' | 'month' } = {}
    ): Promise<{ date: string; positive: number; neutral: number; negative: number }[]> => {
      return this.get<{ date: string; positive: number; neutral: number; negative: number }[]>(
        'news',
        'sentiment-trend',
        params
      );
    },

    // 인기 키워드 가져오기
    getPopularKeywords: async (
      params: { limit?: number; startDate?: string; endDate?: string } = {}
    ): Promise<{ text: string; value: number; sentiment: number }[]> => {
      return this.get<{ text: string; value: number; sentiment: number }[]>(
        'news',
        'popular-keywords',
        params
      );
    },
  };

  // 주식 관련 API
  stocks = {
    // 주식 데이터 가져오기
    getBySymbol: async (symbol: string, period: string = '1m'): Promise<StockData> => {
      return this.get<StockData>('stocks', `data/${symbol}`, { period });
    },

    // 여러 주식 데이터 가져오기
    getMultiple: async (
      symbols: string[],
      period: string = '1m'
    ): Promise<Record<string, StockData>> => {
      return this.get<Record<string, StockData>>('stocks', 'multiple', {
        symbols: symbols.join(','),
        period,
      });
    },

    // 주식-감성 상관관계 가져오기
    getCorrelation: async (
      symbol: string,
      params: { startDate?: string; endDate?: string } = {}
    ): Promise<{ date: string; price: number; sentiment: number }[]> => {
      return this.get<{ date: string; price: number; sentiment: number }[]>(
        'stocks',
        `correlation/${symbol}`,
        params
      );
    },

    // 주식 검색
    search: async (query: string): Promise<{ symbol: string; name: string }[]> => {
      return this.get<{ symbol: string; name: string }[]>('stocks', 'search', { query });
    },
  };

  // 인증 관련 API
  auth = {
    // 로그인
    login: async (username: string, password: string): Promise<{ token: string; user: User }> => {
      try {
        console.log('로그인 요청 데이터:', { username, password });

        // OAuth2 형식으로 로그인 요청
        const formData = new FormData();
        formData.append('username', username); // API는 username으로 받음
        formData.append('password', password);

        const response = await api.post('/api/auth/token', formData);
        console.log('로그인 응답:', response.data);

        // 토큰 저장
        const token = response.data.access_token;
        localStorage.setItem('token', token);

        // 사용자 정보 가져오기
        const userResponse = await api.get('/api/auth/me', {
          headers: { Authorization: `Bearer ${token}` },
        });
        console.log('사용자 정보 응답:', userResponse.data);

        return {
          token,
          user: userResponse.data,
        };
      } catch (error: any) {
        console.error('로그인 오류:', error);
        console.error('오류 응답:', error.response?.data);
        throw new Error(
          error.response?.data?.detail || error.message || '로그인 중 오류가 발생했습니다.'
        );
      }
    },

    // 회원가입
    register: async (userData: {
      username: string;
      email: string;
      password: string;
    }): Promise<{ token: string; user: User }> => {
      try {
        console.log('회원가입 요청 데이터:', userData);

        // 회원가입 요청 (username을 사용자 이름으로 사용)
        const registerData = {
          username: userData.username,
          email: userData.email,
          password: userData.password,
        };

        console.log('회원가입 요청 데이터 (수정됨):', registerData);

        // 회원가입 요청
        const registerResponse = await api.post('/api/auth/register', registerData);
        console.log('회원가입 응답:', registerResponse.data);

        // 회원가입 후 바로 로그인 (username을 사용자 이름으로 사용)
        return this.auth.login(userData.username, userData.password);
      } catch (error: any) {
        console.error('회원가입 오류:', error);
        console.error('오류 응답:', error.response?.data);
        throw new Error(
          error.response?.data?.detail || error.message || '회원가입 중 오류가 발생했습니다.'
        );
      }
    },

    // 사용자 정보 가져오기
    getUser: async (): Promise<User> => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('인증 토큰이 없습니다.');
        }

        const response = await api.get('/api/auth/me', {
          headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
      } catch (error: any) {
        console.error('사용자 정보 가져오기 오류:', error);
        throw new Error(
          error.response?.data?.detail ||
            error.message ||
            '사용자 정보를 가져오는 중 오류가 발생했습니다.'
        );
      }
    },

    // 비밀번호 변경
    changePassword: async (
      currentPassword: string,
      newPassword: string
    ): Promise<{ success: boolean }> => {
      // 아직 구현되지 않은 API
      return { success: true };
    },

    // 프로필 업데이트
    updateProfile: async (userData: Partial<User>): Promise<User> => {
      // 아직 구현되지 않은 API
      return userData as User;
    },
  };

  // 분석 관련 API
  analysis = {
    // 사용 통계 가져오기
    getStats: async (): Promise<{
      newsCount: number;
      stocksCount: number;
      positiveSentiment: number;
      negativeSentiment: number;
      neutralSentiment: number;
    }> => {
      return this.get<{
        newsCount: number;
        stocksCount: number;
        positiveSentiment: number;
        negativeSentiment: number;
        neutralSentiment: number;
      }>('analysis', 'stats');
    },
  };
}

// API 클라이언트 싱글톤 인스턴스 생성
const apiClient = new ApiClient();

export default apiClient;
