/**
 * 감성 분석 상태 관리 모듈
 *
 * 감성 분석 관련 상태 관리를 위한 Redux 슬라이스를 제공합니다.
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import sentimentService from '../services/sentimentService';
import {
  SentimentResult,
  SentimentAnalysisParams,
  SentimentAnalysisState,
  SentimentModel,
  SentimentStats,
  SentimentTrend,
} from '../types';

// 텍스트 감성 분석
export const analyzeSentiment = createAsyncThunk<
  SentimentResult,
  SentimentAnalysisParams,
  { rejectValue: string }
>('sentiment/analyze', async (params, { rejectWithValue }) => {
  try {
    return await sentimentService.analyzeText(params);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to analyze sentiment');
  }
});

// 뉴스 기사 감성 분석
export const analyzeArticleSentiment = createAsyncThunk<
  SentimentResult,
  string,
  { rejectValue: string }
>('sentiment/analyzeArticle', async (articleId, { rejectWithValue }) => {
  try {
    return await sentimentService.analyzeArticle(articleId);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to analyze article sentiment');
  }
});

// 감성 분석 모델 목록 가져오기
export const fetchSentimentModels = createAsyncThunk<
  SentimentModel[],
  void,
  { rejectValue: string }
>('sentiment/fetchModels', async (_, { rejectWithValue }) => {
  try {
    return await sentimentService.getModels();
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch sentiment models');
  }
});

// 감성 분석 통계 가져오기
export const fetchSentimentStats = createAsyncThunk<
  SentimentStats,
  { startDate?: string; endDate?: string },
  { rejectValue: string }
>('sentiment/fetchStats', async (params, { rejectWithValue }) => {
  try {
    return await sentimentService.getStats(params);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch sentiment stats');
  }
});

// 감성 분석 트렌드 가져오기
export const fetchSentimentTrend = createAsyncThunk<
  SentimentTrend[],
  { startDate?: string; endDate?: string; interval?: 'day' | 'week' | 'month' },
  { rejectValue: string }
>('sentiment/fetchTrend', async (params, { rejectWithValue }) => {
  try {
    return await sentimentService.getTrend(params);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch sentiment trend');
  }
});

// 키워드 감성 분석
export const analyzeKeywordSentiment = createAsyncThunk<
  SentimentResult,
  { keyword: string; startDate?: string; endDate?: string },
  { rejectValue: string }
>('sentiment/analyzeKeyword', async ({ keyword, ...params }, { rejectWithValue }) => {
  try {
    return await sentimentService.analyzeKeyword(keyword, params);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to analyze keyword sentiment');
  }
});

// 주식 감성 트렌드 가져오기
export const fetchStockSentimentTrend = createAsyncThunk<
  any,
  { symbol: string; period?: string },
  { rejectValue: string }
>('sentiment/fetchStockSentimentTrend', async ({ symbol, period = '3mo' }, { rejectWithValue }) => {
  try {
    return await sentimentService.getStockSentimentTrend(symbol, period);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch stock sentiment trend');
  }
});

// 감성 분석 피드백 제출
export const submitSentimentFeedback = createAsyncThunk<
  any,
  {
    analysisId: string;
    feedback: { isCorrect: boolean; userSentiment?: string; comment?: string };
  },
  { rejectValue: string }
>('sentiment/submitSentimentFeedback', async ({ analysisId, feedback }, { rejectWithValue }) => {
  try {
    return await sentimentService.submitFeedback(analysisId, feedback);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to submit sentiment feedback');
  }
});

// 배치 감성 분석
export const analyzeBatchSentiment = createAsyncThunk<
  any,
  { texts: string[]; modelId?: string; model?: string },
  { rejectValue: string }
>('sentiment/analyzeBatchSentiment', async ({ texts, modelId, model }, { rejectWithValue }) => {
  try {
    return await sentimentService.analyzeBatchSentiment(texts);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to analyze batch sentiment');
  }
});

// 초기 상태
const initialState: SentimentAnalysisState = {
  results: {},
  isLoading: false,
  error: null,
  models: [],
  modelsLoading: false,
  modelsError: null,
  stats: null,
  statsLoading: false,
  statsError: null,
  trend: [],
  trendLoading: false,
  trendError: null,
  stockSentimentTrend: null,
  stockSentimentLoading: false,
  stockSentimentError: null,
  feedbackResult: null,
  feedbackLoading: false,
  feedbackError: null,
  batchResults: [],
  batchLoading: false,
  batchError: null,
};

const sentimentSlice = createSlice({
  name: 'sentiment',
  initialState,
  reducers: {
    clearSentimentError: state => {
      state.error = null;
    },
    clearSentimentResults: state => {
      state.results = {};
    },
  },
  extraReducers: builder => {
    builder
      // Analyze sentiment reducers
      .addCase(analyzeSentiment.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(analyzeSentiment.fulfilled, (state, action: PayloadAction<SentimentResult>) => {
        state.isLoading = false;
        // 결과를 텍스트 내용을 키로 저장
        state.results[action.payload.text] = action.payload;
      })
      .addCase(analyzeSentiment.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload ?? 'An unknown error occurred';
      })

      // Analyze article sentiment reducers
      .addCase(analyzeArticleSentiment.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(
        analyzeArticleSentiment.fulfilled,
        (state, action: PayloadAction<SentimentResult>) => {
          state.isLoading = false;
          // 결과를 저장
          if (action.payload && action.payload.id) {
            state.results[action.payload.id] = action.payload;
          }
        }
      )
      .addCase(analyzeArticleSentiment.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload ?? 'An unknown error occurred';
      })

      // Fetch sentiment models reducers
      .addCase(fetchSentimentModels.pending, state => {
        state.modelsLoading = true;
        state.modelsError = null;
      })
      .addCase(fetchSentimentModels.fulfilled, (state, action: PayloadAction<SentimentModel[]>) => {
        state.modelsLoading = false;
        state.models = action.payload;
      })
      .addCase(fetchSentimentModels.rejected, (state, action) => {
        state.modelsLoading = false;
        state.modelsError = action.payload ?? 'An unknown error occurred';
      })

      // Fetch sentiment stats reducers
      .addCase(fetchSentimentStats.pending, state => {
        state.statsLoading = true;
        state.statsError = null;
      })
      .addCase(fetchSentimentStats.fulfilled, (state, action: PayloadAction<SentimentStats>) => {
        state.statsLoading = false;
        state.stats = action.payload;
      })
      .addCase(fetchSentimentStats.rejected, (state, action) => {
        state.statsLoading = false;
        state.statsError = action.payload ?? 'An unknown error occurred';
      })

      // Fetch sentiment trend reducers
      .addCase(fetchSentimentTrend.pending, state => {
        state.trendLoading = true;
        state.trendError = null;
      })
      .addCase(fetchSentimentTrend.fulfilled, (state, action: PayloadAction<SentimentTrend[]>) => {
        state.trendLoading = false;
        state.trend = action.payload;
      })
      .addCase(fetchSentimentTrend.rejected, (state, action) => {
        state.trendLoading = false;
        state.trendError = action.payload ?? 'An unknown error occurred';
      })

      // Analyze keyword sentiment reducers
      .addCase(analyzeKeywordSentiment.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(
        analyzeKeywordSentiment.fulfilled,
        (state, action: PayloadAction<SentimentResult>) => {
          state.isLoading = false;
          // 결과를 저장
          if (action.payload && action.payload.id) {
            state.results[action.payload.id] = action.payload;
          }
        }
      )
      .addCase(analyzeKeywordSentiment.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload ?? 'An unknown error occurred';
      })

      // Fetch stock sentiment trend reducers
      .addCase(fetchStockSentimentTrend.pending, state => {
        state.stockSentimentLoading = true;
        state.stockSentimentError = null;
      })
      .addCase(fetchStockSentimentTrend.fulfilled, (state, action) => {
        state.stockSentimentLoading = false;
        state.stockSentimentTrend = action.payload;
      })
      .addCase(fetchStockSentimentTrend.rejected, (state, action) => {
        state.stockSentimentLoading = false;
        state.stockSentimentError = action.payload ?? 'An unknown error occurred';
      })

      // Submit sentiment feedback reducers
      .addCase(submitSentimentFeedback.pending, state => {
        state.feedbackLoading = true;
        state.feedbackError = null;
      })
      .addCase(submitSentimentFeedback.fulfilled, (state, action) => {
        state.feedbackLoading = false;
        state.feedbackResult = action.payload;
      })
      .addCase(submitSentimentFeedback.rejected, (state, action) => {
        state.feedbackLoading = false;
        state.feedbackError = action.payload ?? 'An unknown error occurred';
      })

      // Analyze batch sentiment reducers
      .addCase(analyzeBatchSentiment.pending, state => {
        state.batchLoading = true;
        state.batchError = null;
      })
      .addCase(analyzeBatchSentiment.fulfilled, (state, action) => {
        state.batchLoading = false;
        state.batchResults = action.payload;
      })
      .addCase(analyzeBatchSentiment.rejected, (state, action) => {
        state.batchLoading = false;
        state.batchError = action.payload ?? 'An unknown error occurred';
      });
  },
});

export const { clearSentimentError, clearSentimentResults } = sentimentSlice.actions;
export default sentimentSlice.reducer;
