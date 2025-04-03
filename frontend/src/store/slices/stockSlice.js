import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import stockService from '../../services/stockService';

export const fetchStockData = createAsyncThunk(
  'stock/fetchStockData',
  async ({ symbol, period = '1y' }, { rejectWithValue }) => {
    try {
      return await stockService.getStockData(symbol, period);
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch stock data');
    }
  }
);

export const fetchStockAnalysis = createAsyncThunk(
  'stock/fetchStockAnalysis',
  async ({ symbol }, { rejectWithValue }) => {
    try {
      return await stockService.getStockAnalysis(symbol);
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch stock analysis');
    }
  }
);

export const fetchCorrelationData = createAsyncThunk(
  'stock/fetchCorrelationData',
  async ({ symbol, sentimentType = 'all' }, { rejectWithValue }) => {
    try {
      return await stockService.getCorrelationData(symbol, sentimentType);
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch correlation data');
    }
  }
);

const initialState = {
  stockData: null,
  stockAnalysis: null,
  correlationData: null,
  isLoading: false,
  analysisLoading: false,
  correlationLoading: false,
  error: null,
  analysisError: null,
  correlationError: null,
};

const stockSlice = createSlice({
  name: 'stock',
  initialState,
  reducers: {
    clearStockError: (state) => {
      state.error = null;
    },
    clearAnalysisError: (state) => {
      state.analysisError = null;
    },
    clearCorrelationError: (state) => {
      state.correlationError = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch stock data reducers
      .addCase(fetchStockData.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchStockData.fulfilled, (state, action) => {
        state.isLoading = false;
        state.stockData = action.payload;
      })
      .addCase(fetchStockData.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      
      // Fetch stock analysis reducers
      .addCase(fetchStockAnalysis.pending, (state) => {
        state.analysisLoading = true;
        state.analysisError = null;
      })
      .addCase(fetchStockAnalysis.fulfilled, (state, action) => {
        state.analysisLoading = false;
        state.stockAnalysis = action.payload;
      })
      .addCase(fetchStockAnalysis.rejected, (state, action) => {
        state.analysisLoading = false;
        state.analysisError = action.payload;
      })
      
      // Fetch correlation data reducers
      .addCase(fetchCorrelationData.pending, (state) => {
        state.correlationLoading = true;
        state.correlationError = null;
      })
      .addCase(fetchCorrelationData.fulfilled, (state, action) => {
        state.correlationLoading = false;
        state.correlationData = action.payload;
      })
      .addCase(fetchCorrelationData.rejected, (state, action) => {
        state.correlationLoading = false;
        state.correlationError = action.payload;
      });
  },
});

export const { clearStockError, clearAnalysisError, clearCorrelationError } = stockSlice.actions;
export default stockSlice.reducer;