import React from 'react';
import { truncateText } from '../../utils/formatUtils';
import { NewsArticle } from '../../types';

interface NewsCardProps {
  article: NewsArticle;
  onSelect?: (article: NewsArticle) => void;
}

const NewsCard: React.FC<NewsCardProps> = ({ article, onSelect }) => {
  // 감성 점수에 따른 스타일 결정
  const getSentimentStyle = () => {
    if (!article.sentiment) return 'neutral';
    
    if (article.sentiment.positive > 0.3) return 'positive';
    if (article.sentiment.negative > 0.3) return 'negative';
    return 'neutral';
  };

  const getSentimentText = () => {
    if (!article.sentiment) return '감성 분석 없음';
    
    if (article.sentiment.positive > 0.3) return '긍정적';
    if (article.sentiment.negative > 0.3) return '부정적';
    return '중립적';
  };

  // 날짜 포맷팅
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleClick = () => {
    if (onSelect) {
      onSelect(article);
    }
  };

  const sentimentClass = getSentimentStyle();

  return (
    <div 
      className={`news-card ${sentimentClass}`} 
      onClick={handleClick}
      style={{
        border: '1px solid #f0f0f0',
        borderRadius: '8px',
        padding: '16px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
        marginBottom: '16px',
        cursor: onSelect ? 'pointer' : 'default',
        transition: 'transform 0.2s, box-shadow 0.2s',
        backgroundColor: '#fff',
      }}
    >
      <h3 style={{ 
        margin: '0 0 8px 0', 
        fontSize: '18px', 
        lineHeight: '1.4',
        fontWeight: 'bold'
      }}>
        {article.title}
      </h3>
      
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        marginBottom: '12px',
        color: '#666',
        fontSize: '14px'
      }}>
        <span>{article.source}</span>
        <span>{formatDate(article.publishedDate)}</span>
      </div>
      
      <p style={{
        margin: '0 0 16px 0',
        color: '#333',
        lineHeight: '1.6'
      }}>
        {truncateText(article.content, 150)}
      </p>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ 
          display: 'flex', 
          flexWrap: 'wrap', 
          gap: '8px',
        }}>
          {article.keywords?.slice(0, 3).map((keyword, index) => (
            <span key={index} style={{
              backgroundColor: '#f0f0f0',
              padding: '4px 8px',
              borderRadius: '4px',
              fontSize: '12px',
              color: '#666'
            }}>
              {keyword}
            </span>
          ))}
        </div>
        
        <div style={{
          padding: '4px 12px',
          borderRadius: '4px',
          fontSize: '14px',
          fontWeight: 'bold',
          color: sentimentClass === 'positive' ? '#52c41a' : 
                 sentimentClass === 'negative' ? '#ff4d4f' : '#faad14',
          backgroundColor: sentimentClass === 'positive' ? 'rgba(82, 196, 26, 0.1)' : 
                          sentimentClass === 'negative' ? 'rgba(255, 77, 79, 0.1)' : 'rgba(250, 173, 20, 0.1)',
        }}>
          {getSentimentText()}
        </div>
      </div>
    </div>
  );
};

export default NewsCard;