/**
 * 뉴스 상태 관리 모듈
 *
 * 뉴스 관련 상태 관리를 위한 Redux 슬라이스를 제공합니다.
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import newsService from '../services/newsService';
import { NewsArticle, NewsState, PaginatedNewsResponse, FetchNewsParams } from '../types';

interface FetchNewsKeywordsParams {
  limit?: number;
  startDate?: string;
  endDate?: string;
}

interface KeywordData {
  text: string;
  value: number;
  sentiment: number;
}

interface FetchNewsSentimentTrendParams {
  startDate?: string;
  endDate?: string;
  interval?: 'day' | 'week' | 'month';
}

interface SentimentTrendData {
  date: string;
  positive: number;
  neutral: number;
  negative: number;
}

// 뉴스 데이터 가져오기
export const fetchNews = createAsyncThunk<
  PaginatedNewsResponse,
  FetchNewsParams,
  { rejectValue: string }
>('news/fetchNews', async ({ page = 1, limit = 10, filters = {} }, { rejectWithValue }) => {
  try {
    const params = {
      page,
      limit,
      ...filters,
    };

    const response = await newsService.getAll(params);
    return response;
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch news');
  }
});

// 특정 뉴스 항목 가져오기
export const fetchNewsItem = createAsyncThunk<NewsArticle, string, { rejectValue: string }>(
  'news/fetchNewsItem',
  async (newsId, { rejectWithValue }) => {
    try {
      const response = await newsService.getById(newsId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch news item');
    }
  }
);

// 뉴스 검색하기
export const fetchNewsSearch = createAsyncThunk<
  PaginatedNewsResponse,
  { query: string } & Omit<FetchNewsParams, 'filters'>,
  { rejectValue: string }
>('news/fetchNewsSearch', async ({ query, ...params }, { rejectWithValue }) => {
  try {
    const response = await newsService.search(query, params);
    return response;
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to search news');
  }
});

// 뉴스 카테고리 목록 가져오기
export const fetchNewsCategories = createAsyncThunk<string[], void, { rejectValue: string }>(
  'news/fetchCategories',
  async (_, { rejectWithValue }) => {
    try {
      const response = await newsService.getCategories();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch news categories');
    }
  }
);

// 뉴스 소스 목록 가져오기
export const fetchNewsSources = createAsyncThunk<string[], void, { rejectValue: string }>(
  'news/fetchSources',
  async (_, { rejectWithValue }) => {
    try {
      const response = await newsService.getSources();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch news sources');
    }
  }
);

// 인기 키워드 가져오기
export const fetchNewsKeywords = createAsyncThunk<
  KeywordData[],
  FetchNewsKeywordsParams,
  { rejectValue: string }
>('news/fetchKeywords', async (params, { rejectWithValue }) => {
  try {
    const response = await newsService.getPopularKeywords(params);
    return response;
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch keywords');
  }
});

// 뉴스 감성 트렌드 가져오기
export const fetchNewsSentimentTrend = createAsyncThunk<
  SentimentTrendData[],
  FetchNewsSentimentTrendParams,
  { rejectValue: string }
>('news/fetchSentimentTrend', async (params, { rejectWithValue }) => {
  try {
    const response = await newsService.getSentimentTrend(params);
    return response;
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch sentiment trend');
  }
});

interface ExtendedNewsState extends NewsState {
  selectedArticle: NewsArticle | null;
  totalItems: number;
  currentPage: number;
  totalArticles: number;
  pageSize: number;
  categories: string[];
  sources: string[];
  keywords: KeywordData[];
  sentimentTrend: SentimentTrendData[];
  categoriesLoading: boolean;
  categoriesError: string | null;
  sourcesLoading: boolean;
  sourcesError: string | null;
  keywordsLoading: boolean;
  keywordsError: string | null;
  trendLoading: boolean;
  trendError: string | null;
}

const initialState: ExtendedNewsState = {
  articles: [],
  selectedArticle: null,
  totalItems: 0,
  currentPage: 1,
  totalArticles: 0,
  pageSize: 10,
  isLoading: false,
  error: null,
  categories: [],
  sources: [],
  keywords: [],
  sentimentTrend: [],
  categoriesLoading: false,
  categoriesError: null,
  sourcesLoading: false,
  sourcesError: null,
  keywordsLoading: false,
  keywordsError: null,
  trendLoading: false,
  trendError: null,
};

const newsSlice = createSlice({
  name: 'news',
  initialState,
  reducers: {
    clearNewsError: state => {
      state.error = null;
    },
    setSelectedArticle: (state, action: PayloadAction<NewsArticle | null>) => {
      state.selectedArticle = action.payload;
    },
    clearSelectedArticle: state => {
      state.selectedArticle = null;
    },
  },
  extraReducers: builder => {
    builder
      // Fetch news reducers
      .addCase(fetchNews.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchNews.fulfilled, (state, action: PayloadAction<PaginatedNewsResponse>) => {
        state.isLoading = false;
        state.articles = action.payload.items || action.payload.articles || [];
        state.totalItems = action.payload.total || action.payload.totalItems || 0;
        state.currentPage = action.payload.page || 1;
      })
      .addCase(fetchNews.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload ?? 'An unknown error occurred';
      })

      // Fetch news item reducers
      .addCase(fetchNewsItem.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchNewsItem.fulfilled, (state, action: PayloadAction<NewsArticle>) => {
        state.isLoading = false;
        state.selectedArticle = action.payload;
      })
      .addCase(fetchNewsItem.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload ?? 'An unknown error occurred';
      })

      // Fetch keywords reducers
      .addCase(fetchNewsKeywords.pending, state => {
        state.keywordsLoading = true;
        state.keywordsError = null;
      })
      .addCase(fetchNewsKeywords.fulfilled, (state, action: PayloadAction<KeywordData[]>) => {
        state.keywordsLoading = false;
        state.keywords = action.payload;
      })
      .addCase(fetchNewsKeywords.rejected, (state, action) => {
        state.keywordsLoading = false;
        state.keywordsError = action.payload ?? 'An unknown error occurred';
      })

      // Fetch sentiment trend reducers
      .addCase(fetchNewsSentimentTrend.pending, state => {
        state.trendLoading = true;
        state.trendError = null;
      })
      .addCase(
        fetchNewsSentimentTrend.fulfilled,
        (state, action: PayloadAction<SentimentTrendData[]>) => {
          state.trendLoading = false;
          state.sentimentTrend = action.payload;
        }
      )
      .addCase(fetchNewsSentimentTrend.rejected, (state, action) => {
        state.trendLoading = false;
        state.trendError = action.payload ?? 'An unknown error occurred';
      })

      // Fetch news search reducers
      .addCase(fetchNewsSearch.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchNewsSearch.fulfilled, (state, action: PayloadAction<PaginatedNewsResponse>) => {
        state.isLoading = false;
        state.articles = action.payload.items || action.payload.articles || [];
        state.totalItems = action.payload.total || action.payload.totalItems || 0;
        state.currentPage = action.payload.page || 1;
      })
      .addCase(fetchNewsSearch.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload ?? 'An unknown error occurred';
      })

      // Fetch news categories reducers
      .addCase(fetchNewsCategories.pending, state => {
        state.categoriesLoading = true;
        state.categoriesError = null;
      })
      .addCase(fetchNewsCategories.fulfilled, (state, action: PayloadAction<string[]>) => {
        state.categoriesLoading = false;
        state.categories = action.payload;
      })
      .addCase(fetchNewsCategories.rejected, (state, action) => {
        state.categoriesLoading = false;
        state.categoriesError = action.payload ?? 'An unknown error occurred';
      })

      // Fetch news sources reducers
      .addCase(fetchNewsSources.pending, state => {
        state.sourcesLoading = true;
        state.sourcesError = null;
      })
      .addCase(fetchNewsSources.fulfilled, (state, action: PayloadAction<string[]>) => {
        state.sourcesLoading = false;
        state.sources = action.payload;
      })
      .addCase(fetchNewsSources.rejected, (state, action) => {
        state.sourcesLoading = false;
        state.sourcesError = action.payload ?? 'An unknown error occurred';
      });
  },
});

export const { clearNewsError, setSelectedArticle, clearSelectedArticle } = newsSlice.actions;
export default newsSlice.reducer;
