/**
 * 뉴스 상세 컴포넌트
 * 
 * 뉴스 기사의 상세 정보를 표시하는 컴포넌트를 제공합니다.
 */

import React from 'react';
import { Card, Button } from '../../../../components/ui';
import { NewsArticle } from '../../types';
import { SentimentResult } from '../../../sentiment-analysis';
import './NewsDetail.css';

interface NewsDetailProps {
  article: NewsArticle;
  onClose?: () => void;
}

/**
 * 뉴스 상세 컴포넌트
 */
const NewsDetail: React.FC<NewsDetailProps> = ({ article, onClose }) => {
  // 날짜 포맷팅
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // 원본 기사로 이동
  const handleOpenOriginal = () => {
    if (article.url) {
      window.open(article.url, '_blank');
    }
  };

  // 감성 분석 결과 변환
  const getSentimentResult = () => {
    if (!article.sentiment) return null;

    const { label, score, scores, positive, neutral, negative } = article.sentiment;
    
    return {
      text: article.title,
      label: label || 'neutral',
      score: score || 0,
      scores: scores || {
        positive: positive || 0,
        neutral: neutral || 0,
        negative: negative || 0,
      },
      model: 'FinBERT',
      language: 'en',
      timestamp: article.publishedDate,
    };
  };

  const sentimentResult = getSentimentResult();

  return (
    <Card className="news-detail">
      <div className="news-detail-header">
        <h2 className="news-detail-title">{article.title}</h2>
        <Button variant="text" onClick={onClose}>
          닫기
        </Button>
      </div>

      <div className="news-detail-meta">
        <div className="news-detail-source">{article.source}</div>
        <div className="news-detail-date">{formatDate(article.publishedDate)}</div>
      </div>

      <div className="news-detail-content">
        <p>{article.content}</p>
      </div>

      {article.keywords && article.keywords.length > 0 && (
        <div className="news-detail-keywords">
          <h3 className="news-detail-section-title">키워드</h3>
          <div className="news-detail-keyword-list">
            {article.keywords.map((keyword, index) => (
              <span key={index} className="news-detail-keyword">
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      {sentimentResult && (
        <div className="news-detail-sentiment">
          <h3 className="news-detail-section-title">감성 분석 결과</h3>
          <SentimentResult result={sentimentResult} />
        </div>
      )}

      <div className="news-detail-actions">
        <Button onClick={handleOpenOriginal} disabled={!article.url}>
          원본 기사 보기
        </Button>
      </div>
    </Card>
  );
};

export default NewsDetail;
