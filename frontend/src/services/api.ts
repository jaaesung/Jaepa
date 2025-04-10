import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
} from "axios";

// API 기본 URL 설정
const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8000/api";

interface RefreshTokenResponse {
  token: string;
  refresh_token?: string;
}

// axios 인스턴스 생성
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// 요청 인터셉터 - 토큰 추가
api.interceptors.request.use(
  (config: any): any => {
    const token = localStorage.getItem("token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError): Promise<AxiosError> => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 토큰 만료 처리
api.interceptors.response.use(
  (response: AxiosResponse): AxiosResponse => {
    return response;
  },
  async (error: AxiosError): Promise<any> => {
    const originalRequest = error.config as AxiosRequestConfig & {
      _retry?: boolean;
    };

    // 401 에러이고 재시도가 아직 안된 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // 리프레시 토큰으로 새 토큰 발급 요청
        const refreshToken = localStorage.getItem("refreshToken");
        if (!refreshToken) {
          // 리프레시 토큰이 없으면 로그아웃 처리
          localStorage.removeItem("token");
          localStorage.removeItem("refreshToken");
          window.location.href = "/login";
          return Promise.reject(error);
        }

        const response = await axios.post<RefreshTokenResponse>(
          `${API_BASE_URL}/auth/refresh-token`,
          { refresh_token: refreshToken }
        );

        if (response.data.token) {
          localStorage.setItem("token", response.data.token);
          // 새 토큰으로 원래 요청 재시도
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${response.data.token}`;
          }
          return api(originalRequest);
        }
      } catch (refreshError) {
        // 리프레시 토큰 갱신 실패 - 로그아웃 처리
        localStorage.removeItem("token");
        localStorage.removeItem("refreshToken");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

import { NewsArticle, StockData } from "../types";

// 데이터 모델 어댑터 함수

interface BackendNewsArticle {
  _id?: string;
  id?: string;
  title?: string;
  content?: string;
  description?: string;
  source?: string;
  url?: string;
  article_url?: string;
  publishedDate?: string;
  published_date?: string;
  published_utc?: string;
  crawledDate?: string;
  crawled_date?: string;
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
  keywords?: string[];
}

interface BackendStockData {
  _id?: string;
  id?: string;
  symbol?: string;
  name?: string;
  company_name?: string;
  price?: number;
  close?: number;
  change?: number;
  changePercent?: number;
  change_percent?: number;
  date?: string;
  timestamp?: string;
  historical?: Array<{ date: string; price: number }>;
  prices?: Array<{ date: string; price: number }>;
}

/**
 * 백엔드에서 받은 뉴스 데이터를 프론트엔드 형식에 맞게 변환
 * @param article 백엔드에서 받은 뉴스 기사 데이터
 * @returns 프론트엔드 형식에 맞게 변환된 뉴스 기사 데이터
 */
export const adaptNewsArticle = (
  article: BackendNewsArticle | null
): NewsArticle | null => {
  if (!article) return null;

  return {
    id: article._id || article.id || "",
    title: article.title || "",
    content: article.content || article.description || "",
    source: article.source || "",
    url: article.url || article.article_url || "",
    publishedDate:
      article.publishedDate ||
      article.published_date ||
      article.published_utc ||
      "",
    crawledDate: article.crawledDate || article.crawled_date || "",
    sentiment: article.sentiment
      ? {
          // 백엔드에서 오는 감성 데이터 형식을 프론트엔드 형식에 맞게 변환
          label: article.sentiment.label,
          score: article.sentiment.score,
          scores: article.sentiment.scores,
          // 프론트엔드에서 사용하는 형식으로도 변환
          positive:
            article.sentiment.scores?.positive ||
            article.sentiment.positive ||
            0,
          neutral:
            article.sentiment.scores?.neutral || article.sentiment.neutral || 0,
          negative:
            article.sentiment.scores?.negative ||
            article.sentiment.negative ||
            0,
        }
      : undefined,
    keywords: article.keywords || [],
  };
};

/**
 * 백엔드에서 받은 주식 데이터를 프론트엔드 형식에 맞게 변환
 * @param stockData 백엔드에서 받은 주식 데이터
 * @returns 프론트엔드 형식에 맞게 변환된 주식 데이터
 */
export const adaptStockData = (
  stockData: BackendStockData | null
): StockData | null => {
  if (!stockData) return null;

  return {
    id: stockData._id || stockData.id || "",
    symbol: stockData.symbol || "",
    name: stockData.name || stockData.company_name || "",
    price: stockData.price || stockData.close || 0,
    change: stockData.change || 0,
    changePercent: stockData.changePercent || stockData.change_percent || 0,
    date: stockData.date || stockData.timestamp || "",
    historical: stockData.historical || stockData.prices || [],
  };
};

export default api;
