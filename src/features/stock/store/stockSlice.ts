/**
 * 주식 상태 관리 모듈
 * 
 * 주식 관련 상태 관리를 위한 Redux 슬라이스를 제공합니다.
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import stockService from '../services/stockService';
import { StockData, StockInfo, CorrelationData, StockState, PeriodType } from '../types';
import { localStorageService } from '../../../services';

// 주식 데이터 가져오기
export const fetchStockData = createAsyncThunk<
  StockData,
  { symbol: string; period?: PeriodType; startDate?: string; endDate?: string },
  { rejectValue: string }
>('stock/fetchData', async ({ symbol, period, startDate, endDate }, { rejectWithValue }) => {
  try {
    return await stockService.getStockData(symbol, period, startDate, endDate);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch stock data');
  }
});

// 여러 주식 데이터 가져오기
export const fetchMultipleStocks = createAsyncThunk<
  Record<string, StockData>,
  { symbols: string[]; period?: PeriodType; startDate?: string; endDate?: string },
  { rejectValue: string }
>('stock/fetchMultiple', async ({ symbols, period, startDate, endDate }, { rejectWithValue }) => {
  try {
    return await stockService.getMultipleStocks(symbols, period, startDate, endDate);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch multiple stocks');
  }
});

// 주식 정보 가져오기
export const fetchStockInfo = createAsyncThunk<
  StockInfo,
  string,
  { rejectValue: string }
>('stock/fetchInfo', async (symbol, { rejectWithValue }) => {
  try {
    return await stockService.getStockInfo(symbol);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch stock info');
  }
});

// 여러 주식 정보 가져오기
export const fetchMultipleStockInfo = createAsyncThunk<
  Record<string, StockInfo>,
  string[],
  { rejectValue: string }
>('stock/fetchMultipleInfo', async (symbols, { rejectWithValue }) => {
  try {
    return await stockService.getMultipleStockInfo(symbols);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch multiple stock info');
  }
});

// 상관관계 데이터 가져오기
export const fetchCorrelation = createAsyncThunk<
  CorrelationData,
  { symbol: string; sentimentType?: string; period?: PeriodType },
  { rejectValue: string }
>('stock/fetchCorrelation', async ({ symbol, sentimentType, period }, { rejectWithValue }) => {
  try {
    return await stockService.getCorrelation(symbol, sentimentType, period);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch correlation data');
  }
});

// 주식 검색
export const searchStocks = createAsyncThunk<
  StockInfo[],
  string,
  { rejectValue: string }
>('stock/search', async (query, { rejectWithValue }) => {
  try {
    return await stockService.searchStocks(query);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to search stocks');
  }
});

// 인기 주식 가져오기
export const fetchPopularStocks = createAsyncThunk<
  StockInfo[],
  void,
  { rejectValue: string }
>('stock/fetchPopular', async (_, { rejectWithValue }) => {
  try {
    return await stockService.getPopularStocks();
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch popular stocks');
  }
});

interface ExtendedStockState extends StockState {
  popularStocks: StockInfo[];
  searchResults: StockInfo[];
  searchLoading: boolean;
  searchError: string | null;
  popularLoading: boolean;
  popularError: string | null;
}

// 초기 상태
const initialState: ExtendedStockState = {
  data: {},
  info: {},
  correlations: {},
  watchlist: localStorageService.get<string[]>('watchlist') || [],
  isLoading: false,
  error: null,
  popularStocks: [],
  searchResults: [],
  searchLoading: false,
  searchError: null,
  popularLoading: false,
  popularError: null,
};

// 주식 슬라이스
const stockSlice = createSlice({
  name: 'stock',
  initialState,
  reducers: {
    clearStockError: (state) => {
      state.error = null;
    },
    addToWatchlist: (state, action: PayloadAction<string>) => {
      if (!state.watchlist.includes(action.payload)) {
        state.watchlist.push(action.payload);
        localStorageService.set('watchlist', state.watchlist);
      }
    },
    removeFromWatchlist: (state, action: PayloadAction<string>) => {
      state.watchlist = state.watchlist.filter(symbol => symbol !== action.payload);
      localStorageService.set('watchlist', state.watchlist);
    },
    clearSearchResults: (state) => {
      state.searchResults = [];
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch stock data reducers
      .addCase(fetchStockData.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchStockData.fulfilled, (state, action: PayloadAction<StockData>) => {
        state.isLoading = false;
        state.data[action.payload.symbol] = action.payload;
      })
      .addCase(fetchStockData.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload ?? 'An unknown error occurred';
      })

      // Fetch multiple stocks reducers
      .addCase(fetchMultipleStocks.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchMultipleStocks.fulfilled, (state, action: PayloadAction<Record<string, StockData>>) => {
        state.isLoading = false;
        state.data = { ...state.data, ...action.payload };
      })
      .addCase(fetchMultipleStocks.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload ?? 'An unknown error occurred';
      })

      // Fetch stock info reducers
      .addCase(fetchStockInfo.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchStockInfo.fulfilled, (state, action: PayloadAction<StockInfo>) => {
        state.isLoading = false;
        state.info[action.payload.symbol] = action.payload;
      })
      .addCase(fetchStockInfo.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload ?? 'An unknown error occurred';
      })

      // Fetch multiple stock info reducers
      .addCase(fetchMultipleStockInfo.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchMultipleStockInfo.fulfilled, (state, action: PayloadAction<Record<string, StockInfo>>) => {
        state.isLoading = false;
        state.info = { ...state.info, ...action.payload };
      })
      .addCase(fetchMultipleStockInfo.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload ?? 'An unknown error occurred';
      })

      // Fetch correlation reducers
      .addCase(fetchCorrelation.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchCorrelation.fulfilled, (state, action: PayloadAction<CorrelationData>) => {
        state.isLoading = false;
        const key = `${action.payload.symbol}_${action.payload.sentimentType}_${action.payload.period}`;
        state.correlations[key] = action.payload;
      })
      .addCase(fetchCorrelation.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload ?? 'An unknown error occurred';
      })

      // Search stocks reducers
      .addCase(searchStocks.pending, (state) => {
        state.searchLoading = true;
        state.searchError = null;
      })
      .addCase(searchStocks.fulfilled, (state, action: PayloadAction<StockInfo[]>) => {
        state.searchLoading = false;
        state.searchResults = action.payload;
      })
      .addCase(searchStocks.rejected, (state, action) => {
        state.searchLoading = false;
        state.searchError = action.payload ?? 'An unknown error occurred';
      })

      // Fetch popular stocks reducers
      .addCase(fetchPopularStocks.pending, (state) => {
        state.popularLoading = true;
        state.popularError = null;
      })
      .addCase(fetchPopularStocks.fulfilled, (state, action: PayloadAction<StockInfo[]>) => {
        state.popularLoading = false;
        state.popularStocks = action.payload;
      })
      .addCase(fetchPopularStocks.rejected, (state, action) => {
        state.popularLoading = false;
        state.popularError = action.payload ?? 'An unknown error occurred';
      });
  },
});

export const { clearStockError, addToWatchlist, removeFromWatchlist, clearSearchResults } = stockSlice.actions;
export default stockSlice.reducer;
