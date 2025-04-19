/**
 * 뉴스 필터 컴포넌트
 *
 * 뉴스 기사 필터링을 위한 컴포넌트를 제공합니다.
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useDebounce } from '../../../../core/hooks';
import { Button, Card, Input, Dropdown } from '../../../../components/ui';
import { useNews } from '../../hooks';
import { FetchNewsParams } from '../../types';
import './NewsFilter.css';

interface NewsFilterProps {
  onFilter: (filters: FetchNewsParams['filters']) => void;
  initialFilters?: FetchNewsParams['filters'];
}

/**
 * 뉴스 필터 컴포넌트
 */
const NewsFilter: React.FC<NewsFilterProps> = ({ onFilter, initialFilters = {} }) => {
  const { getCategories, getSources, categories, sources } = useNews();

  const [startDate, setStartDate] = useState(initialFilters.startDate || '');
  const [endDate, setEndDate] = useState(initialFilters.endDate || '');
  const [source, setSource] = useState(initialFilters.source || '');
  const [category, setCategory] = useState(initialFilters.category || '');
  const [sentiment, setSentiment] = useState(initialFilters.sentiment || '');
  const [keyword, setKeyword] = useState(initialFilters.keyword || '');
  const [isExpanded, setIsExpanded] = useState(false);

  const debouncedKeyword = useDebounce(keyword, 500);

  // 카테고리 옵션 계산
  const categoryOptions = useMemo(() => {
    return categories.map((cat: string) => ({ value: cat, label: cat }));
  }, [categories]);

  // 출처 옵션 계산
  const sourceOptions = useMemo(() => {
    return sources.map((src: string) => ({ value: src, label: src }));
  }, [sources]);

  // 감성 옵션 계산
  const sentimentOptions = useMemo(() => {
    return [
      { value: '', label: '전체' },
      { value: 'positive', label: '긍정적' },
      { value: 'neutral', label: '중립적' },
      { value: 'negative', label: '부정적' },
    ];
  }, []);

  // 카테고리 및 소스 목록 가져오기
  useEffect(() => {
    getCategories();
    getSources();
  }, [getCategories, getSources]);

  // 초기 필터 설정
  useEffect(() => {
    if (initialFilters) {
      setStartDate(initialFilters.startDate || '');
      setEndDate(initialFilters.endDate || '');
      setSource(initialFilters.source || '');
      setCategory(initialFilters.category || '');
      setSentiment(initialFilters.sentiment || '');
      setKeyword(initialFilters.keyword || '');
    }
  }, [initialFilters]);

  // 필터 적용 핸들러
  const handleApplyFilter = useCallback(() => {
    const filters: FetchNewsParams['filters'] = {};

    if (startDate) filters.startDate = startDate;
    if (endDate) filters.endDate = endDate;
    if (source) filters.source = source;
    if (category) filters.category = category;
    if (sentiment) filters.sentiment = sentiment;
    if (keyword) filters.keyword = keyword;

    onFilter(filters);
  }, [startDate, endDate, source, category, sentiment, keyword, onFilter]);

  // 필터 초기화 핸들러
  const handleResetFilter = useCallback(() => {
    setStartDate('');
    setEndDate('');
    setSource('');
    setCategory('');
    setSentiment('');
    setKeyword('');
    onFilter({});
  }, [onFilter]);

  // 필터 토글 핸들러
  const toggleFilter = useCallback(() => {
    setIsExpanded(prev => !prev);
  }, []);

  // 키워드 변경 핸들러
  const handleKeywordChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setKeyword(e.target.value);
  }, []);

  // 시작일 변경 핸들러
  const handleStartDateChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setStartDate(e.target.value);
  }, []);

  // 종료일 변경 핸들러
  const handleEndDateChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setEndDate(e.target.value);
  }, []);

  // 카테고리 변경 핸들러
  const handleCategoryChange = useCallback((value: string) => {
    setCategory(value);
  }, []);

  // 출처 변경 핸들러
  const handleSourceChange = useCallback((value: string) => {
    setSource(value);
  }, []);

  // 감성 변경 핸들러
  const handleSentimentChange = useCallback((value: string) => {
    setSentiment(value);
  }, []);

  return (
    <Card className="news-filter">
      <div className="news-filter-header">
        <h3 className="news-filter-title">뉴스 필터</h3>
        <Button variant="text" onClick={toggleFilter}>
          {isExpanded ? '접기' : '펼치기'}
        </Button>
      </div>

      {isExpanded && (
        <div className="news-filter-content">
          <div className="news-filter-row">
            <div className="news-filter-field">
              <Input
                label="키워드"
                id="keyword"
                type="text"
                value={keyword}
                onChange={handleKeywordChange}
                placeholder="키워드 입력"
                fullWidth
              />
            </div>
          </div>

          <div className="news-filter-row">
            <div className="news-filter-field">
              <Input
                label="시작일"
                id="startDate"
                type="date"
                value={startDate}
                onChange={handleStartDateChange}
                fullWidth
              />
            </div>

            <div className="news-filter-field">
              <Input
                label="종료일"
                id="endDate"
                type="date"
                value={endDate}
                onChange={handleEndDateChange}
                fullWidth
              />
            </div>
          </div>

          <div className="news-filter-row">
            <div className="news-filter-field">
              <Dropdown
                label="카테고리"
                value={category}
                onChange={handleCategoryChange}
                options={categoryOptions}
                placeholder="카테고리 선택"
                fullWidth
              />
            </div>

            <div className="news-filter-field">
              <Dropdown
                label="출처"
                value={source}
                onChange={handleSourceChange}
                options={sourceOptions}
                placeholder="출처 선택"
                fullWidth
              />
            </div>
          </div>

          <div className="news-filter-row">
            <div className="news-filter-field">
              <Dropdown
                label="감성"
                value={sentiment}
                onChange={handleSentimentChange}
                options={sentimentOptions}
                placeholder="감성 선택"
                fullWidth
              />
            </div>
          </div>

          <div className="news-filter-actions">
            <Button variant="outline" onClick={handleResetFilter}>
              초기화
            </Button>
            <Button onClick={handleApplyFilter}>적용</Button>
          </div>
        </div>
      )}
    </Card>
  );
};

export default React.memo(NewsFilter);
