import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiClient from '../../services/apiClient';
import { StockData, StockState, CorrelationData } from '../../types';

type PeriodType = '1d' | '1w' | '1m' | '3m' | '6m' | '1y' | '5y';

interface FetchStockDataParams {
  symbol: string;
  period?: PeriodType;
}

interface FetchMultipleStocksParams {
  symbols: string[];
  period?: PeriodType;
}

interface FetchCorrelationParams {
  symbol: string;
  startDate?: string;
  endDate?: string;
}

// 사용하지 않는 로컬 타입 정의 제거
// 전역 타입을 사용하도록 변경

// 주식 데이터 가져오기
export const fetchStockData = createAsyncThunk<
  StockData,
  FetchStockDataParams,
  { rejectValue: string }
>('stock/fetchStockData', async ({ symbol, period = '1m' }, { rejectWithValue }) => {
  try {
    return await apiClient.stocks.getBySymbol(symbol, period);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch stock data');
  }
});

// 여러 주식 데이터 가져오기
export const fetchMultipleStocks = createAsyncThunk<
  Record<string, StockData>,
  FetchMultipleStocksParams,
  { rejectValue: string }
>('stock/fetchMultipleStocks', async ({ symbols, period = '1m' }, { rejectWithValue }) => {
  try {
    return await apiClient.stocks.getMultiple(symbols, period);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch multiple stocks');
  }
});

// 주식-감성 상관관계 가져오기
export const fetchStockCorrelation = createAsyncThunk<
  CorrelationData[],
  FetchCorrelationParams,
  { rejectValue: string }
>('stock/fetchCorrelation', async ({ symbol, startDate, endDate }, { rejectWithValue }) => {
  try {
    const data = await apiClient.stocks.getCorrelation(symbol, { startDate, endDate });
    // volume 필드 추가
    return data.map(item => ({
      ...item,
      volume: 0, // volume 필드 기본값 설정
    }));
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to fetch correlation data');
  }
});

// 주식 검색
export const searchStocks = createAsyncThunk<
  Array<{ symbol: string; name: string }>,
  string,
  { rejectValue: string }
>('stock/searchStocks', async (query, { rejectWithValue }) => {
  try {
    return await apiClient.stocks.search(query);
  } catch (error: any) {
    return rejectWithValue(error.message || 'Failed to search stocks');
  }
});

interface ExtendedStockState extends StockState {
  stocksData: Record<string, StockData>;
  correlationData: CorrelationData[];
  searchResults: Array<{ symbol: string; name: string }>;
  correlationLoading: boolean;
  correlationError: string | null;
  searchLoading: boolean;
  searchError: string | null;
}

const initialState: ExtendedStockState = {
  stocks: [],
  selectedStock: null,
  stockData: null,
  stockAnalysis: null,
  sentimentAnalysis: null,
  stocksData: {},
  correlationData: [],
  searchResults: [],
  isLoading: false,
  error: null,
  analysisLoading: false,
  analysisError: null,
  correlationLoading: false,
  correlationError: null,
  sentimentLoading: false,
  sentimentError: null,
  searchLoading: false,
  searchError: null,
};

const stockSlice = createSlice({
  name: 'stocks',
  initialState,
  reducers: {
    clearStockError: state => {
      state.error = null;
    },
    setSelectedStock: (state, action: PayloadAction<StockData | null>) => {
      state.selectedStock = action.payload;
    },
    clearSelectedStock: state => {
      state.selectedStock = null;
    },
    clearSearchResults: state => {
      state.searchResults = [];
    },
  },
  extraReducers: builder => {
    builder
      // Fetch stock data reducers
      .addCase(fetchStockData.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchStockData.fulfilled, (state, action: PayloadAction<StockData>) => {
        state.isLoading = false;
        // 기존 배열에 새 데이터 추가 (중복 제거)
        const existingIndex = state.stocks.findIndex(
          stock => stock.symbol === action.payload.symbol
        );
        if (existingIndex >= 0) {
          state.stocks[existingIndex] = action.payload;
        } else {
          state.stocks.push(action.payload);
        }
        state.selectedStock = action.payload;
      })
      .addCase(fetchStockData.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload ?? 'An unknown error occurred';
      })

      // Fetch multiple stocks reducers
      .addCase(fetchMultipleStocks.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(
        fetchMultipleStocks.fulfilled,
        (state, action: PayloadAction<Record<string, StockData>>) => {
          state.isLoading = false;
          state.stocksData = { ...state.stocksData, ...action.payload };

          // 배열에도 추가
          Object.values(action.payload).forEach(stockData => {
            const existingIndex = state.stocks.findIndex(
              stock => stock.symbol === stockData.symbol
            );
            if (existingIndex >= 0) {
              state.stocks[existingIndex] = stockData;
            } else {
              state.stocks.push(stockData);
            }
          });
        }
      )
      .addCase(fetchMultipleStocks.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload ?? 'An unknown error occurred';
      })

      // Fetch correlation data reducers
      .addCase(fetchStockCorrelation.pending, state => {
        state.correlationLoading = true;
        state.correlationError = null;
      })
      .addCase(
        fetchStockCorrelation.fulfilled,
        (state, action: PayloadAction<CorrelationData[]>) => {
          state.correlationLoading = false;
          state.correlationData = action.payload;
        }
      )
      .addCase(fetchStockCorrelation.rejected, (state, action) => {
        state.correlationLoading = false;
        state.correlationError = action.payload || 'An unknown error occurred';
      })

      // Search stocks reducers
      .addCase(searchStocks.pending, state => {
        state.searchLoading = true;
        state.searchError = null;
      })
      .addCase(
        searchStocks.fulfilled,
        (state, action: PayloadAction<Array<{ symbol: string; name: string }>>) => {
          state.searchLoading = false;
          state.searchResults = action.payload;
        }
      )
      .addCase(searchStocks.rejected, (state, action) => {
        state.searchLoading = false;
        state.searchError = action.payload ?? 'An unknown error occurred';
      });
  },
});

export const { clearStockError, setSelectedStock, clearSelectedStock, clearSearchResults } =
  stockSlice.actions;
export default stockSlice.reducer;
