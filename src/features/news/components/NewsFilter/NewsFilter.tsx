/**
 * 뉴스 필터 컴포넌트
 *
 * 뉴스 기사 필터링을 위한 컴포넌트를 제공합니다.
 */

import React, { useState, useEffect } from "react";
import { useDebounce } from "../../../../core/hooks";
import { Button, Card, Input, Dropdown } from "../../../../components/ui";
import { useNews } from "../../hooks";
import { FetchNewsParams } from "../../types";
import "./NewsFilter.css";

interface NewsFilterProps {
  onFilter: (filters: FetchNewsParams["filters"]) => void;
  initialFilters?: FetchNewsParams["filters"];
}

/**
 * 뉴스 필터 컴포넌트
 */
const NewsFilter: React.FC<NewsFilterProps> = ({
  onFilter,
  initialFilters = {},
}) => {
  const { getCategories, getSources, categories, sources } = useNews();

  const [startDate, setStartDate] = useState(initialFilters.startDate || "");
  const [endDate, setEndDate] = useState(initialFilters.endDate || "");
  const [source, setSource] = useState(initialFilters.source || "");
  const [category, setCategory] = useState(initialFilters.category || "");
  const [sentiment, setSentiment] = useState(initialFilters.sentiment || "");
  const [keyword, setKeyword] = useState(initialFilters.keyword || "");
  const [isExpanded, setIsExpanded] = useState(false);

  const debouncedKeyword = useDebounce(keyword, 500);

  // 카테고리 및 소스 목록 가져오기
  useEffect(() => {
    getCategories();
    getSources();
  }, [getCategories, getSources]);

  // 초기 필터 설정
  useEffect(() => {
    if (initialFilters) {
      setStartDate(initialFilters.startDate || "");
      setEndDate(initialFilters.endDate || "");
      setSource(initialFilters.source || "");
      setCategory(initialFilters.category || "");
      setSentiment(initialFilters.sentiment || "");
      setKeyword(initialFilters.keyword || "");
    }
  }, [initialFilters]);

  // 필터 적용 핸들러
  const handleApplyFilter = () => {
    const filters: FetchNewsParams["filters"] = {};

    if (startDate) filters.startDate = startDate;
    if (endDate) filters.endDate = endDate;
    if (source) filters.source = source;
    if (category) filters.category = category;
    if (sentiment) filters.sentiment = sentiment;
    if (keyword) filters.keyword = keyword;

    onFilter(filters);
  };

  // 필터 초기화 핸들러
  const handleResetFilter = () => {
    setStartDate("");
    setEndDate("");
    setSource("");
    setCategory("");
    setSentiment("");
    setKeyword("");
    onFilter({});
  };

  // 필터 토글 핸들러
  const toggleFilter = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <Card className="news-filter">
      <div className="news-filter-header">
        <h3 className="news-filter-title">뉴스 필터</h3>
        <Button variant="text" onClick={toggleFilter}>
          {isExpanded ? "접기" : "펼치기"}
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
                onChange={(e) => setKeyword(e.target.value)}
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
                onChange={(e) => setStartDate(e.target.value)}
                fullWidth
              />
            </div>

            <div className="news-filter-field">
              <Input
                label="종료일"
                id="endDate"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                fullWidth
              />
            </div>
          </div>

          <div className="news-filter-row">
            <div className="news-filter-field">
              <Dropdown
                label="카테고리"
                value={category}
                onChange={setCategory}
                options={categories.map((cat) => ({ value: cat, label: cat }))}
                placeholder="카테고리 선택"
                fullWidth
              />
            </div>

            <div className="news-filter-field">
              <Dropdown
                label="출처"
                value={source}
                onChange={setSource}
                options={sources.map((src) => ({ value: src, label: src }))}
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
                onChange={setSentiment}
                options={[
                  { value: "", label: "전체" },
                  { value: "positive", label: "긍정적" },
                  { value: "neutral", label: "중립적" },
                  { value: "negative", label: "부정적" },
                ]}
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

export default NewsFilter;
