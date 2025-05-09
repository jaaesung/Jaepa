/**
 * 뉴스 목록 컴포넌트
 *
 * 뉴스 기사 목록을 표시하는 컴포넌트를 제공합니다.
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Button } from '../../../../components/ui';
import { useNews } from '../../hooks/useNews';
import { NewsArticle, FetchNewsParams } from '../../types';
import NewsCard from '../NewsCard';
import './NewsList.css';

interface NewsListProps {
  filters?: FetchNewsParams['filters'];
  onSelectArticle?: (article: NewsArticle) => void;
}

/**
 * 뉴스 목록 컴포넌트
 */
const NewsList: React.FC<NewsListProps> = ({ filters, onSelectArticle }) => {
  const { getNews, articles, totalItems, isLoading, error } = useNews();
  const [page, setPage] = useState(1);
  const limit = 10;

  // 뉴스 데이터 가져오기
  useEffect(() => {
    const params: FetchNewsParams = { page, pageSize: limit };
    if (filters) {
      params.filters = filters;
    }
    getNews(params);
  }, [getNews, page, limit, filters]);

  // 페이지 변경 핸들러
  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  // 기사 선택 핸들러
  const handleSelectArticle = useCallback(
    (article: NewsArticle) => {
      if (onSelectArticle) {
        onSelectArticle(article);
      }
    },
    [onSelectArticle]
  );

  // 총 페이지 수 계산
  const totalPages = useMemo(() => Math.ceil(totalItems / limit), [totalItems, limit]);

  return (
    <div className="news-list">
      {isLoading && articles.length === 0 ? (
        <div className="news-list-loading">
          <div className="spinner"></div>
          <p>뉴스를 불러오는 중입니다...</p>
        </div>
      ) : error ? (
        <div className="news-list-error">
          <p>{error}</p>
          <Button
            onClick={() => {
              const params: FetchNewsParams = { page, pageSize: limit };
              if (filters) {
                params.filters = filters;
              }
              getNews(params);
            }}
          >
            다시 시도
          </Button>
        </div>
      ) : articles.length === 0 ? (
        <div className="news-list-empty">
          <p>표시할 뉴스가 없습니다.</p>
        </div>
      ) : (
        <>
          <div className="news-list-grid">
            {articles.map((article: NewsArticle) => (
              <div key={article.id} className="news-list-item">
                <NewsCard article={article} onClick={handleSelectArticle} />
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="news-list-pagination">
              <Button
                variant="text"
                onClick={() => handlePageChange(page - 1)}
                disabled={page === 1 || isLoading}
              >
                이전
              </Button>

              <div className="news-list-page-info">
                {page} / {totalPages} 페이지
              </div>

              <Button
                variant="text"
                onClick={() => handlePageChange(page + 1)}
                disabled={page === totalPages || isLoading}
              >
                다음
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default React.memo(NewsList);
