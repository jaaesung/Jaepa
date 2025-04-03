import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import newsService from '../../services/newsService';

export const fetchNews = createAsyncThunk(
  'news/fetchNews',
  async ({ page = 1, limit = 10, filters = {} }, { rejectWithValue }) => {
    try {
      return await newsService.getNews(page, limit, filters);
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch news');
    }
  }
);

export const fetchSentimentAnalysis = createAsyncThunk(
  'news/fetchSentimentAnalysis',
  async ({ newsId }, { rejectWithValue }) => {
    try {
      return await newsService.getSentimentAnalysis(newsId);
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch sentiment analysis');
    }
  }
);

const initialState = {
  items: [],
  totalItems: 0,
  currentPage: 1,
  isLoading: false,
  error: null,
  sentimentAnalysis: null,
  sentimentIsLoading: false,
  sentimentError: null,
};

const newsSlice = createSlice({
  name: 'news',
  initialState,
  reducers: {
    clearNewsError: (state) => {
      state.error = null;
    },
    clearSentimentError: (state) => {
      state.sentimentError = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch news reducers
      .addCase(fetchNews.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchNews.fulfilled, (state, action) => {
        state.isLoading = false;
        state.items = action.payload.items;
        state.totalItems = action.payload.totalItems;
        state.currentPage = action.payload.currentPage;
      })
      .addCase(fetchNews.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      
      // Fetch sentiment analysis reducers
      .addCase(fetchSentimentAnalysis.pending, (state) => {
        state.sentimentIsLoading = true;
        state.sentimentError = null;
      })
      .addCase(fetchSentimentAnalysis.fulfilled, (state, action) => {
        state.sentimentIsLoading = false;
        state.sentimentAnalysis = action.payload;
      })
      .addCase(fetchSentimentAnalysis.rejected, (state, action) => {
        state.sentimentIsLoading = false;
        state.sentimentError = action.payload;
      });
  },
});

export const { clearNewsError, clearSentimentError } = newsSlice.actions;
export default newsSlice.reducer;