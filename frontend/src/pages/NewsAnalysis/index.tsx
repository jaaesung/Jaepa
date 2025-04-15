import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../types';
import { fetchNews } from '../../store/slices/newsSlice';
import { useAppDispatch } from '../../hooks';
import './NewsAnalysis.css';

// 컴포넌트 불러오기
import NewsCard from '../../components/news/NewsCard';
import SentimentChart from '../../components/charts/SentimentChart';
import KeywordCloud from '../../components/charts/KeywordCloud';
import { NewsArticle } from '../../types';

interface FilterOptions {
  startDate: string;
  endDate: string;
  source: string;
  sentiment: string;
  keyword: string;
}

const NewsAnalysis: React.FC = () => {
  const dispatch = useAppDispatch();
  const { articles, isLoading, error } = useSelector((state: RootState) => state.news);

  const [selectedArticle, setSelectedArticle] = useState<NewsArticle | null>(null);
  const [view, setView] = useState<'grid' | 'list'>('list');
  const [filters, setFilters] = useState<FilterOptions>({
    startDate: '',
    endDate: '',
    source: '',
    sentiment: '',
    keyword: '',
  });
  const [sortBy, setSortBy] = useState<string>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // 페이지네이션
  const [currentPage, setCurrentPage] = useState(1);
  const articlesPerPage = 10;

  useEffect(() => {
    // 뉴스 데이터 가져오기
    dispatch(fetchNews({ page: currentPage, limit: articlesPerPage }));
  }, [dispatch, currentPage]);

  // 필터 변경 핸들러
  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters({
      ...filters,
      [name]: value,
    });
  };

  // 필터 적용 핸들러
  const applyFilters = () => {
    dispatch(
      fetchNews({
        page: 1,
        limit: articlesPerPage,
        filters: {
          startDate: filters.startDate,
          endDate: filters.endDate,
          source: filters.source,
          sentiment: filters.sentiment,
          keyword: filters.keyword,
        },
      })
    );
    setCurrentPage(1); // 첫 페이지로 리셋
  };

  // 필터 초기화 핸들러
  const resetFilters = () => {
    setFilters({
      startDate: '',
      endDate: '',
      source: '',
      sentiment: '',
      keyword: '',
    });
    dispatch(fetchNews({ page: 1, limit: articlesPerPage }));
    setCurrentPage(1);
  };

  // 정렬 변경 핸들러
  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSortBy(e.target.value);
  };

  // 정렬 순서 변경 핸들러
  const toggleSortOrder = () => {
    setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
  };

  // 페이지 변경 핸들러
  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  // 뉴스 항목 선택 핸들러
  const handleSelectArticle = (article: NewsArticle) => {
    setSelectedArticle(article);
  };

  // 선택 해제 핸들러
  const handleCloseDetail = () => {
    setSelectedArticle(null);
  };

  // 샘플 감성 데이터
  const sampleSentimentData = [
    { date: '2025-04-01', positive: 0.45, neutral: 0.35, negative: 0.2 },
    { date: '2025-04-02', positive: 0.4, neutral: 0.35, negative: 0.25 },
    { date: '2025-04-03', positive: 0.38, neutral: 0.37, negative: 0.25 },
    { date: '2025-04-04', positive: 0.42, neutral: 0.3, negative: 0.28 },
    { date: '2025-04-05', positive: 0.44, neutral: 0.31, negative: 0.25 },
    { date: '2025-04-06', positive: 0.47, neutral: 0.33, negative: 0.2 },
    { date: '2025-04-07', positive: 0.5, neutral: 0.3, negative: 0.2 },
  ];

  // 샘플 키워드 데이터
  const sampleKeywordData = [
    { text: 'AI', value: 100, sentiment: 0.8 },
    { text: '반도체', value: 85, sentiment: 0.6 },
    { text: '클라우드', value: 70, sentiment: 0.7 },
    { text: '자율주행', value: 65, sentiment: 0.5 },
    { text: '가상현실', value: 60, sentiment: 0.4 },
    { text: '블록체인', value: 55, sentiment: 0.2 },
    { text: '양자컴퓨팅', value: 50, sentiment: 0.3 },
    { text: '디지털전환', value: 48, sentiment: 0.4 },
    { text: '사이버보안', value: 45, sentiment: -0.1 },
    { text: '공급망', value: 43, sentiment: -0.2 },
    { text: '인플레이션', value: 40, sentiment: -0.5 },
    { text: '금리인상', value: 38, sentiment: -0.7 },
    { text: '규제', value: 35, sentiment: -0.6 },
    { text: '대체에너지', value: 34, sentiment: 0.3 },
    { text: '지속가능성', value: 33, sentiment: 0.4 },
  ];

  // 샘플 뉴스 소스 목록
  const sampleNewsSources = [
    '한국경제',
    '매일경제',
    '조선비즈',
    '블룸버그',
    '로이터',
    'CNBC',
    'WSJ',
    'FT',
    '니혼게이자이',
  ];

  return (
    <div className="news-analysis-container">
      <div className="news-analysis-header">
        <h1>뉴스 분석</h1>
        <p className="description">
          최신 뉴스 기사와 감성 분석 결과를 확인하세요. 키워드 및 감성 트렌드를 통해 시장 분위기를
          파악할 수 있습니다.
        </p>
      </div>

      <div className="news-analysis-content">
        <div className="news-filters-container">
          <div className="filters-panel">
            <div className="filter-header">
              <h3>필터 및 정렬</h3>
              <div className="view-toggle">
                <button
                  className={view === 'list' ? 'active' : ''}
                  onClick={() => setView('list')}
                  aria-label="리스트 뷰"
                >
                  📋
                </button>
                <button
                  className={view === 'grid' ? 'active' : ''}
                  onClick={() => setView('grid')}
                  aria-label="그리드 뷰"
                >
                  📊
                </button>
              </div>
            </div>

            <div className="filter-form">
              <div className="filter-group">
                <label htmlFor="startDate">날짜 범위</label>
                <div className="date-range">
                  <input
                    type="date"
                    name="startDate"
                    value={filters.startDate}
                    onChange={handleFilterChange}
                    placeholder="시작일"
                  />
                  <span>~</span>
                  <input
                    type="date"
                    name="endDate"
                    value={filters.endDate}
                    onChange={handleFilterChange}
                    placeholder="종료일"
                  />
                </div>
              </div>

              <div className="filter-group">
                <label htmlFor="source">뉴스 소스</label>
                <select name="source" value={filters.source} onChange={handleFilterChange}>
                  <option value="">전체</option>
                  {sampleNewsSources.map(source => (
                    <option key={source} value={source}>
                      {source}
                    </option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label htmlFor="sentiment">감성 분류</label>
                <select name="sentiment" value={filters.sentiment} onChange={handleFilterChange}>
                  <option value="">전체</option>
                  <option value="positive">긍정적</option>
                  <option value="neutral">중립적</option>
                  <option value="negative">부정적</option>
                </select>
              </div>

              <div className="filter-group">
                <label htmlFor="keyword">키워드 검색</label>
                <input
                  type="text"
                  name="keyword"
                  value={filters.keyword}
                  onChange={handleFilterChange}
                  placeholder="키워드 입력"
                />
              </div>
            </div>

            <div className="filter-actions">
              <button className="filter-button apply" onClick={applyFilters}>
                필터 적용
              </button>
              <button className="filter-button reset" onClick={resetFilters}>
                초기화
              </button>
            </div>

            <div className="sort-options">
              <label htmlFor="sortBy">정렬 기준:</label>
              <select id="sortBy" value={sortBy} onChange={handleSortChange}>
                <option value="date">날짜</option>
                <option value="sentiment">감성 점수</option>
                <option value="relevance">관련성</option>
              </select>
              <button
                className="sort-order-toggle"
                onClick={toggleSortOrder}
                aria-label={sortOrder === 'asc' ? '오름차순' : '내림차순'}
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </button>
            </div>
          </div>
        </div>

        <div className="news-content-container">
          {selectedArticle ? (
            <div className="news-detail-view">
              <button className="close-detail-button" onClick={handleCloseDetail} aria-label="닫기">
                ← 목록으로 돌아가기
              </button>

              <div className="news-detail-header">
                <h2>{selectedArticle.title}</h2>
                <div className="news-meta">
                  <span className="news-source">{selectedArticle.source}</span>
                  <span className="news-date">
                    {new Date(selectedArticle.publishedDate).toLocaleDateString('ko-KR')}
                  </span>
                </div>
              </div>

              <div className="news-detail-sentiment">
                <h3>감성 분석 결과</h3>
                <div className="sentiment-score-bars">
                  <div className="sentiment-bar">
                    <span className="label">긍정</span>
                    <div className="bar-container">
                      <div
                        className="bar positive"
                        style={{ width: `${(selectedArticle.sentiment?.positive || 0) * 100}%` }}
                      ></div>
                      <span className="value">
                        {((selectedArticle.sentiment?.positive || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <div className="sentiment-bar">
                    <span className="label">중립</span>
                    <div className="bar-container">
                      <div
                        className="bar neutral"
                        style={{ width: `${(selectedArticle.sentiment?.neutral || 0) * 100}%` }}
                      ></div>
                      <span className="value">
                        {((selectedArticle.sentiment?.neutral || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <div className="sentiment-bar">
                    <span className="label">부정</span>
                    <div className="bar-container">
                      <div
                        className="bar negative"
                        style={{ width: `${(selectedArticle.sentiment?.negative || 0) * 100}%` }}
                      ></div>
                      <span className="value">
                        {((selectedArticle.sentiment?.negative || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="news-detail-keywords">
                <h3>주요 키워드</h3>
                <div className="keywords-container">
                  {selectedArticle.keywords?.map((keyword, index) => (
                    <span key={index} className="keyword-tag">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>

              <div className="news-detail-content">
                <h3>뉴스 본문</h3>
                <div className="news-content">
                  {selectedArticle.content.split('\n').map((paragraph, index) => (
                    <p key={index}>{paragraph}</p>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <>
              {isLoading ? (
                <div className="loading-container">
                  <div className="loading-spinner"></div>
                  <p>뉴스 데이터를 불러오는 중...</p>
                </div>
              ) : error ? (
                <div className="error-container">
                  <p className="error-message">데이터를 불러오는 중 오류가 발생했습니다.</p>
                  <button
                    className="retry-button"
                    onClick={() =>
                      dispatch(fetchNews({ page: currentPage, limit: articlesPerPage }))
                    }
                  >
                    다시 시도
                  </button>
                </div>
              ) : (
                <div className={`news-list-container ${view}`}>
                  {articles.length > 0 ? (
                    articles.map(article => (
                      <div key={article.id} className="news-item-wrapper">
                        <NewsCard article={article} onSelect={handleSelectArticle} />
                      </div>
                    ))
                  ) : (
                    <div className="empty-state">
                      <p>검색 결과가 없습니다.</p>
                      <p>다른 검색어나 필터 옵션을 시도해보세요.</p>
                    </div>
                  )}
                </div>
              )}

              {!isLoading && !error && articles.length > 0 && (
                <div className="pagination">
                  <button
                    disabled={currentPage === 1}
                    onClick={() => handlePageChange(currentPage - 1)}
                    className="pagination-button prev"
                  >
                    이전
                  </button>
                  <span className="current-page">{currentPage}</span>
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    className="pagination-button next"
                  >
                    다음
                  </button>
                </div>
              )}
            </>
          )}
        </div>

        <div className="news-analysis-sidebar">
          <div className="sidebar-section sentiment-trend">
            <h3>감성 트렌드</h3>
            <SentimentChart
              data={sampleSentimentData.map(item => ({
                symbol: item.date.substring(5), // 월-일 형식으로 표시
                positive: item.positive,
                neutral: item.neutral,
                negative: item.negative,
              }))}
              height={250}
            />
          </div>

          <div className="sidebar-section keywords-cloud">
            <h3>인기 키워드</h3>
            <KeywordCloud
              data={sampleKeywordData}
              width={300}
              height={300}
              maxFontSize={36}
              minFontSize={12}
            />
          </div>

          <div className="sidebar-section summary-stats">
            <h3>요약 통계</h3>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-value">65%</div>
                <div className="stat-label">긍정적 뉴스</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">23%</div>
                <div className="stat-label">부정적 뉴스</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">12%</div>
                <div className="stat-label">중립적 뉴스</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">347</div>
                <div className="stat-label">분석된 뉴스</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewsAnalysis;
