/**
 * 주식 훅 모듈
 *
 * 주식 관련 기능을 쉽게 사용할 수 있는 커스텀 훅을 제공합니다.
 */

import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '../../../core/hooks';
import {
  fetchStockData,
  fetchMultipleStocks,
  fetchStockInfo,
  fetchMultipleStockInfo,
  fetchCorrelation,
  searchStocks,
  fetchPopularStocks,
  fetchStockNews,
  fetchFinancials,
  fetchAnalysis,
  fetchSectorPerformance,
  fetchTechnicalIndicators,
  addToWatchlist,
  removeFromWatchlist,
  clearSearchResults,
} from '../store/stockSlice';
import { PeriodType } from '../types';

/**
 * 주식 관련 기능을 제공하는 커스텀 훅
 */
export const useStock = () => {
  const dispatch = useAppDispatch();
  const {
    data,
    info,
    correlations,
    watchlist,
    isLoading,
    error,
    popularStocks,
    searchResults,
    stockNews,
    financials,
    analysis,
    sectorPerformance,
    technicalIndicators,
    searchLoading,
    searchError,
    popularLoading,
    popularError,
    newsLoading,
    newsError,
    financialsLoading,
    financialsError,
    analysisLoading,
    analysisError,
    sectorLoading,
    sectorError,
    indicatorsLoading,
    indicatorsError,
  } = useAppSelector(state => state.stocks);

  // 주식 데이터 가져오기
  const getStockData = useCallback(
    async (symbol: string, period?: PeriodType, startDate?: string, endDate?: string) => {
      const resultAction = await dispatch(fetchStockData({ symbol, period, startDate, endDate }));
      return fetchStockData.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 여러 주식 데이터 가져오기
  const getMultipleStocks = useCallback(
    async (symbols: string[], period?: PeriodType, startDate?: string, endDate?: string) => {
      const resultAction = await dispatch(
        fetchMultipleStocks({ symbols, period, startDate, endDate })
      );
      return fetchMultipleStocks.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 주식 정보 가져오기
  const getStockInfo = useCallback(
    async (symbol: string) => {
      const resultAction = await dispatch(fetchStockInfo(symbol));
      return fetchStockInfo.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 여러 주식 정보 가져오기
  const getMultipleStockInfo = useCallback(
    async (symbols: string[]) => {
      const resultAction = await dispatch(fetchMultipleStockInfo(symbols));
      return fetchMultipleStockInfo.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 상관관계 데이터 가져오기
  const getCorrelation = useCallback(
    async (symbol: string, sentimentType?: string, period?: PeriodType) => {
      const resultAction = await dispatch(fetchCorrelation({ symbol, sentimentType, period }));
      return fetchCorrelation.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 주식 검색
  const searchStock = useCallback(
    async (query: string) => {
      const resultAction = await dispatch(searchStocks(query));
      return searchStocks.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 인기 주식 가져오기
  const getPopularStocks = useCallback(async () => {
    const resultAction = await dispatch(fetchPopularStocks());
    return fetchPopularStocks.fulfilled.match(resultAction);
  }, [dispatch]);

  // 관심 목록에 추가
  const addStockToWatchlist = useCallback(
    (symbol: string) => {
      dispatch(addToWatchlist(symbol));
    },
    [dispatch]
  );

  // 관심 목록에서 제거
  const removeStockFromWatchlist = useCallback(
    (symbol: string) => {
      dispatch(removeFromWatchlist(symbol));
    },
    [dispatch]
  );

  // 주식 관련 뉴스 가져오기
  const getStockNews = useCallback(
    async (symbol: string, limit?: number, startDate?: string, endDate?: string) => {
      const params: { symbol: string; limit?: number; startDate?: string; endDate?: string } = {
        symbol,
        limit,
      };
      if (startDate) params.startDate = startDate;
      if (endDate) params.endDate = endDate;
      const resultAction = await dispatch(fetchStockNews(params));
      return fetchStockNews.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 주식 재무 정보 가져오기
  const getFinancials = useCallback(
    async (symbol: string) => {
      const resultAction = await dispatch(fetchFinancials({ symbol }));
      return fetchFinancials.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 주식 분석 정보 가져오기
  const getAnalysis = useCallback(
    async (symbol: string) => {
      const resultAction = await dispatch(fetchAnalysis({ symbol }));
      return fetchAnalysis.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 주식 섹터별 성과 가져오기
  const getSectorPerformance = useCallback(async () => {
    const resultAction = await dispatch(fetchSectorPerformance());
    return fetchSectorPerformance.fulfilled.match(resultAction);
  }, [dispatch]);

  // 주식 기술적 지표 가져오기
  const getTechnicalIndicators = useCallback(
    async (symbol: string, indicators: string[], period?: PeriodType) => {
      const resultAction = await dispatch(fetchTechnicalIndicators({ symbol, indicators, period }));
      return fetchTechnicalIndicators.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 검색 결과 초기화
  const clearStockSearchResults = useCallback(() => {
    dispatch(clearSearchResults());
  }, [dispatch]);

  return {
    // 상태
    data,
    info,
    correlations,
    watchlist,
    isLoading,
    error,
    popularStocks,
    searchResults,
    stockNews,
    financials,
    analysis,
    sectorPerformance,
    technicalIndicators,
    searchLoading,
    searchError,
    popularLoading,
    popularError,
    newsLoading,
    newsError,
    financialsLoading,
    financialsError,
    analysisLoading,
    analysisError,
    sectorLoading,
    sectorError,
    indicatorsLoading,
    indicatorsError,

    // 액션
    getStockData,
    getMultipleStocks,
    getStockInfo,
    getMultipleStockInfo,
    getCorrelation,
    searchStock,
    getPopularStocks,
    getStockNews,
    getFinancials,
    getAnalysis,
    getSectorPerformance,
    getTechnicalIndicators,
    addStockToWatchlist,
    removeStockFromWatchlist,
    clearStockSearchResults,
  };
};

export default useStock;
