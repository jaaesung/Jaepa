import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiClient from '../../services/apiClient';
import { NewsArticle, NewsState } from '../../types';

interface FetchNewsParams {
  page?: number;
  limit?: number;
  filters?: {
    keyword?: string;
    startDate?: string;
    endDate?: string;
    source?: string;
    sentiment?: string;
  };
}

interface PaginatedNewsResponse {
  items: NewsArticle[];
  total: number;
  page: number;
  limit: number;
}

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

    const response = await apiClient.news.getAll(params);
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
      const response = await apiClient.news.getById(newsId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch news item');
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
    const response = await apiClient.news.getPopularKeywords(params);
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
    const response = await apiClient.news.getSentimentTrend(params);
    return response;
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch sentiment trend');
  }
});

interface ExtendedNewsState extends NewsState {
  selectedArticle: NewsArticle | null;
  totalItems: number;
  currentPage: number;
  keywords: KeywordData[];
  sentimentTrend: SentimentTrendData[];
  keywordsLoading: boolean;
  keywordsError: string | null;
  trendLoading: boolean;
  trendError: string | null;
}

const initialState: ExtendedNewsState = {
  articles: [],
  items: [],
  selectedArticle: null,
  totalItems: 0,
  currentPage: 1,
  isLoading: false,
  error: null,
  keywords: [],
  sentimentTrend: [],
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
        state.articles = action.payload.items;
        state.totalItems = action.payload.total;
        state.currentPage = action.payload.page;
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
      });
  },
});

export const { clearNewsError, setSelectedArticle, clearSelectedArticle } = newsSlice.actions;
export default newsSlice.reducer;
