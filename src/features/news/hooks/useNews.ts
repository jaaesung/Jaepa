/**
 * 뉴스 훅 모듈
 *
 * 뉴스 관련 기능을 쉽게 사용할 수 있는 커스텀 훅을 제공합니다.
 */

import { useCallback } from "react";
import { useAppDispatch, useAppSelector } from "../../../core/hooks";
import {
  fetchNews,
  fetchNewsItem,
  fetchNewsSearch,
  fetchNewsCategories,
  fetchNewsSources,
  fetchNewsKeywords,
  fetchNewsSentimentTrend,
  setSelectedArticle,
  clearSelectedArticle,
} from "../store/newsSlice";
import { FetchNewsParams } from "../types";

/**
 * 뉴스 관련 기능을 제공하는 커스텀 훅
 */
export const useNews = () => {
  const dispatch = useAppDispatch();
  const {
    articles,
    selectedArticle,
    totalItems,
    currentPage,
    isLoading,
    error,
    categories,
    sources,
    keywords,
    sentimentTrend,
    categoriesLoading,
    categoriesError,
    sourcesLoading,
    sourcesError,
    keywordsLoading,
    keywordsError,
    trendLoading,
    trendError,
  } = useAppSelector((state) => state.news);

  // 뉴스 목록 가져오기
  const getNews = useCallback(
    async (params: FetchNewsParams = {}) => {
      const resultAction = await dispatch(fetchNews(params));
      return fetchNews.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 특정 뉴스 기사 가져오기
  const getNewsItem = useCallback(
    async (newsId: string) => {
      const resultAction = await dispatch(fetchNewsItem(newsId));
      return fetchNewsItem.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 뉴스 검색하기
  const searchNews = useCallback(
    async (query: string, params: Omit<FetchNewsParams, "filters"> = {}) => {
      const resultAction = await dispatch(
        fetchNewsSearch({ query, ...params })
      );
      return fetchNewsSearch.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 뉴스 카테고리 목록 가져오기
  const getCategories = useCallback(async () => {
    const resultAction = await dispatch(fetchNewsCategories());
    return fetchNewsCategories.fulfilled.match(resultAction);
  }, [dispatch]);

  // 뉴스 소스 목록 가져오기
  const getSources = useCallback(async () => {
    const resultAction = await dispatch(fetchNewsSources());
    return fetchNewsSources.fulfilled.match(resultAction);
  }, [dispatch]);

  // 인기 키워드 가져오기
  const getKeywords = useCallback(
    async (
      params: { limit?: number; startDate?: string; endDate?: string } = {}
    ) => {
      const resultAction = await dispatch(fetchNewsKeywords(params));
      return fetchNewsKeywords.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 감성 트렌드 가져오기
  const getSentimentTrend = useCallback(
    async (
      params: {
        startDate?: string;
        endDate?: string;
        interval?: "day" | "week" | "month";
      } = {}
    ) => {
      const resultAction = await dispatch(fetchNewsSentimentTrend(params));
      return fetchNewsSentimentTrend.fulfilled.match(resultAction);
    },
    [dispatch]
  );

  // 선택된 기사 설정
  const selectArticle = useCallback(
    (article) => {
      dispatch(setSelectedArticle(article));
    },
    [dispatch]
  );

  // 선택된 기사 초기화
  const clearArticle = useCallback(() => {
    dispatch(clearSelectedArticle());
  }, [dispatch]);

  return {
    // 상태
    articles,
    selectedArticle,
    totalItems,
    currentPage,
    isLoading,
    error,
    categories,
    sources,
    keywords,
    sentimentTrend,
    categoriesLoading,
    categoriesError,
    sourcesLoading,
    sourcesError,
    keywordsLoading,
    keywordsError,
    trendLoading,
    trendError,

    // 액션
    getNews,
    getNewsItem,
    searchNews,
    getCategories,
    getSources,
    getKeywords,
    getSentimentTrend,
    selectArticle,
    clearArticle,
  };
};

export default useNews;
