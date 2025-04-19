/**
 * 뉴스 카드 컴포넌트
 *
 * 뉴스 기사를 카드 형태로 표시하는 컴포넌트를 제공합니다.
 */

import React, { useCallback, useMemo } from 'react';
import { Card } from '../../../../components/ui';
import { NewsArticle } from '../../types';
import './NewsCard.css';

interface NewsCardProps {
  article: NewsArticle;
  onClick?: (article: NewsArticle) => void;
}

/**
 * 뉴스 카드 컴포넌트
 */
const NewsCard: React.FC<NewsCardProps> = ({ article, onClick }) => {
  // 날짜 포맷팅
  const formatDate = useCallback((dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }, []);

  // 내용 요약
  const truncateContent = useCallback((content: string, maxLength = 150) => {
    if (content.length <= maxLength) return content;
    return content.slice(0, maxLength) + '...';
  }, []);

  // 감성 레이블 클래스 이름
  const getSentimentClass = useCallback(() => {
    if (!article.sentiment || !article.sentiment.label) return '';

    switch (article.sentiment.label) {
      case 'positive':
        return 'sentiment-positive';
      case 'negative':
        return 'sentiment-negative';
      case 'neutral':
      default:
        return 'sentiment-neutral';
    }
  }, [article.sentiment]);

  // 감성 레이블 텍스트
  const getSentimentText = useCallback(() => {
    if (!article.sentiment || !article.sentiment.label) return '';

    switch (article.sentiment.label) {
      case 'positive':
        return '긍정적';
      case 'negative':
        return '부정적';
      case 'neutral':
      default:
        return '중립적';
    }
  }, [article.sentiment]);

  // 클릭 핸들러
  const handleClick = useCallback(() => {
    if (onClick) {
      onClick(article);
    }
  }, [onClick, article]);

  return (
    <Card
      className="news-card"
      onClick={handleClick}
      tabIndex={0}
      role="article"
      aria-label={`뉴스 기사: ${article.title}`}
      onKeyDown={e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleClick();
        }
      }}
    >
      <div className="news-card-header">
        <h3 className="news-card-title">{article.title}</h3>
        {article.sentiment && article.sentiment.label && (
          <div className={`news-card-sentiment ${getSentimentClass()}`}>{getSentimentText()}</div>
        )}
      </div>

      <div className="news-card-content">
        <p className="news-card-summary">{truncateContent(article.content)}</p>
      </div>

      <div className="news-card-footer">
        <div className="news-card-source">{article.source}</div>
        <div className="news-card-date">
          {formatDate(article.publishedDate || article.publishedAt)}
        </div>
      </div>

      {article.keywords && article.keywords.length > 0 && (
        <div className="news-card-keywords">
          {article.keywords.slice(0, 3).map((keyword, index) => (
            <span key={index} className="news-card-keyword">
              {keyword}
            </span>
          ))}
        </div>
      )}
    </Card>
  );
};

export default React.memo(NewsCard);
