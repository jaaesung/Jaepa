/**
 * 감성 분석 훅 모듈
 *
 * 감성 분석 관련 기능을 쉽게 사용할 수 있는 커스텀 훅을 제공합니다.
 */

import { useCallback } from "react";
import { useAppDispatch, useAppSelector } from "../../../core/hooks";
import {
  analyzeSentiment,
  analyzeArticleSentiment,
  analyzeKeywordSentiment,
  fetchSentimentModels,
  fetchSentimentStats,
  fetchSentimentTrend,
  fetchStockSentimentTrend,
  submitSentimentFeedback,
  analyzeBatchSentiment,
  clearSentimentResults,
} from "../store/sentimentSlice";
import { SentimentAnalysisParams } from "../types";

/**
 * 감성 분석 관련 기능을 제공하는 커스텀 훅
 */
export const useSentiment = () => {
  const dispatch = useAppDispatch();
  const {
    results,
    isLoading,
    error,
    models,
    modelsLoading,
    modelsError,
    stats,
    statsLoading,
    statsError,
    trend,
    trendLoading,
    trendError,
    stockTrend,
    stockTrendLoading,
    stockTrendError,
    batchResults,
    batchLoading,
    batchError,
    feedbackSuccess,
    feedbackLoading,
    feedbackError,
  } = useAppSelector((state) => state.sentimentAnalysis);

  // 텍스트 감성 분석
  const analyzeText = useCallback(
    async (params: SentimentAnalysisParams) => {
      const resultAction = await dispatch(analyzeSentiment(params));
      return analyzeSentiment.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 뉴스 기사 감성 분석
  const analyzeArticle = useCallback(
    async (articleId: string) => {
      const resultAction = await dispatch(analyzeArticleSentiment(articleId));
      return analyzeArticleSentiment.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 키워드 감성 분석
  const analyzeKeyword = useCallback(
    async (
      keyword: string,
      params: { startDate?: string; endDate?: string } = {}
    ) => {
      const resultAction = await dispatch(
        analyzeKeywordSentiment({ keyword, ...params })
      );
      return analyzeKeywordSentiment.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 감성 분석 모델 목록 가져오기
  const getModels = useCallback(async () => {
    const resultAction = await dispatch(fetchSentimentModels());
    return fetchSentimentModels.fulfilled.match(resultAction);
  }, [dispatch]);

  // 감성 분석 통계 가져오기
  const getStats = useCallback(
    async (params: { startDate?: string; endDate?: string } = {}) => {
      const resultAction = await dispatch(fetchSentimentStats(params));
      return fetchSentimentStats.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 감성 분석 트렌드 가져오기
  const getTrend = useCallback(
    async (
      params: {
        startDate?: string;
        endDate?: string;
        interval?: "day" | "week" | "month";
      } = {}
    ) => {
      const resultAction = await dispatch(fetchSentimentTrend(params));
      return fetchSentimentTrend.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 주식 관련 감성 트렌드 가져오기
  const getStockSentimentTrend = useCallback(
    async (
      symbol: string,
      params: {
        startDate?: string;
        endDate?: string;
        interval?: "day" | "week" | "month";
      } = {}
    ) => {
      const resultAction = await dispatch(
        fetchStockSentimentTrend({ symbol, ...params })
      );
      return fetchStockSentimentTrend.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 감성 분석 결과 피드백 제출
  const submitFeedback = useCallback(
    async (
      analysisId: string,
      feedback: {
        correctSentiment: "positive" | "neutral" | "negative";
        comment?: string;
      }
    ) => {
      const resultAction = await dispatch(
        submitSentimentFeedback({ analysisId, feedback })
      );
      return submitSentimentFeedback.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 감성 분석 배치 처리
  const analyzeBatch = useCallback(
    async (texts: string[], model: string = "finbert") => {
      const resultAction = await dispatch(
        analyzeBatchSentiment({ texts, model })
      );
      return analyzeBatchSentiment.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 감성 분석 결과 초기화
  const clearResults = useCallback(() => {
    dispatch(clearSentimentResults());
  }, [dispatch]);

  return {
    // 상태
    results,
    isLoading,
    error,
    models,
    modelsLoading,
    modelsError,
    stats,
    statsLoading,
    statsError,
    trend,
    trendLoading,
    trendError,
    stockTrend,
    stockTrendLoading,
    stockTrendError,
    batchResults,
    batchLoading,
    batchError,
    feedbackSuccess,
    feedbackLoading,
    feedbackError,

    // 액션
    analyzeText,
    analyzeArticle,
    analyzeKeyword,
    getModels,
    getStats,
    getTrend,
    getStockSentimentTrend,
    submitFeedback,
    analyzeBatch,
    clearResults,
  };
};

export default useSentiment;
