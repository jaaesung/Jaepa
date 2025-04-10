import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import stockService from "../../services/stockService";

export const fetchStockData = createAsyncThunk(
  "stock/fetchStockData",
  async ({ symbol, period = "1y" }, { rejectWithValue }) => {
    try {
      return await stockService.getStockData(symbol, period);
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch stock data"
      );
    }
  }
);

export const fetchStockAnalysis = createAsyncThunk(
  "stock/fetchStockAnalysis",
  async ({ symbol }, { rejectWithValue }) => {
    try {
      return await stockService.getStockAnalysis(symbol);
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch stock analysis"
      );
    }
  }
);

export const fetchCorrelationData = createAsyncThunk(
  "stock/fetchCorrelationData",
  async ({ symbol, sentimentType = "all" }, { rejectWithValue }) => {
    try {
      return await stockService.getCorrelationData(symbol, sentimentType);
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch correlation data"
      );
    }
  }
);

export const fetchSentimentAnalysis = createAsyncThunk(
  "stock/fetchSentimentAnalysis",
  async ({ symbol }, { rejectWithValue }) => {
    try {
      return await stockService.getSentimentAnalysis(symbol);
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch sentiment analysis"
      );
    }
  }
);

export const fetchMultipleStocks = createAsyncThunk(
  "stock/fetchMultipleStocks",
  async ({ symbols, period }, { rejectWithValue }) => {
    try {
      const results = {};
      for (const symbol of symbols) {
        results[symbol] = await stockService.getStockData(symbol, period);
      }
      return results;
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch multiple stocks"
      );
    }
  }
);

export const fetchStockCorrelation = createAsyncThunk(
  "stock/fetchStockCorrelation",
  async ({ symbol }, { rejectWithValue }) => {
    try {
      return await stockService.getStockCorrelation(symbol);
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to fetch stock correlation"
      );
    }
  }
);

export const searchStocks = createAsyncThunk(
  "stock/searchStocks",
  async (query, { rejectWithValue }) => {
    try {
      return await stockService.searchStocks(query);
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.message || "Failed to search stocks"
      );
    }
  }
);

const initialState = {
  stockData: null,
  stockAnalysis: null,
  correlationData: null,
  sentimentAnalysis: null,
  stocks: [],
  selectedStock: null,
  searchResults: [],
  isLoading: false,
  analysisLoading: false,
  correlationLoading: false,
  sentimentLoading: false,
  searchLoading: false,
  error: null,
  analysisError: null,
  correlationError: null,
  sentimentError: null,
  searchError: null,
};

const stockSlice = createSlice({
  name: "stock",
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
      })

      // Fetch sentiment analysis reducers
      .addCase(fetchSentimentAnalysis.pending, (state) => {
        state.sentimentLoading = true;
        state.sentimentError = null;
      })
      .addCase(fetchSentimentAnalysis.fulfilled, (state, action) => {
        state.sentimentLoading = false;
        state.sentimentAnalysis = action.payload;
      })
      .addCase(fetchSentimentAnalysis.rejected, (state, action) => {
        state.sentimentLoading = false;
        state.sentimentError = action.payload;
      })

      // Fetch multiple stocks reducers
      .addCase(fetchMultipleStocks.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchMultipleStocks.fulfilled, (state, action) => {
        state.isLoading = false;
        state.stocks = Object.values(action.payload);
      })
      .addCase(fetchMultipleStocks.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })

      // Fetch stock correlation reducers
      .addCase(fetchStockCorrelation.pending, (state) => {
        state.correlationLoading = true;
        state.correlationError = null;
      })
      .addCase(fetchStockCorrelation.fulfilled, (state, action) => {
        state.correlationLoading = false;
        state.correlationData = action.payload;
      })
      .addCase(fetchStockCorrelation.rejected, (state, action) => {
        state.correlationLoading = false;
        state.correlationError = action.payload;
      })

      // Search stocks reducers
      .addCase(searchStocks.pending, (state) => {
        state.searchLoading = true;
        state.searchError = null;
      })
      .addCase(searchStocks.fulfilled, (state, action) => {
        state.searchLoading = false;
        state.searchResults = action.payload;
      })
      .addCase(searchStocks.rejected, (state, action) => {
        state.searchLoading = false;
        state.searchError = action.payload;
      });
  },
});

export const { clearStockError, clearAnalysisError, clearCorrelationError } =
  stockSlice.actions;
export default stockSlice.reducer;
