/**
 * 뉴스 분석 페이지 컴포넌트
 * 
 * 뉴스 분석 기능을 제공하는 페이지를 제공합니다.
 */

import React, { useState } from 'react';
import { MainLayout } from '../../components/layout';
import { Card } from '../../components/ui';
import { NewsList, NewsDetail, NewsFilter } from '../../features/news';
import { NewsArticle, FetchNewsParams } from '../../features/news/types';
import { SentimentTrendChart } from '../../features/sentiment-analysis';
import './NewsAnalysisPage.css';

/**
 * 뉴스 분석 페이지 컴포넌트
 */
const NewsAnalysisPage: React.FC = () => {
  const [selectedArticle, setSelectedArticle] = useState<NewsArticle | null>(null);
  const [filters, setFilters] = useState<FetchNewsParams['filters']>({});

  // 기사 선택 핸들러
  const handleSelectArticle = (article: NewsArticle) => {
    setSelectedArticle(article);
  };

  // 기사 닫기 핸들러
  const handleCloseArticle = () => {
    setSelectedArticle(null);
  };

  // 필터 적용 핸들러
  const handleFilter = (newFilters: FetchNewsParams['filters']) => {
    setFilters(newFilters);
  };

  return (
    <MainLayout>
      <div className="news-analysis-page">
        <div className="news-analysis-header">
          <h1 className="news-analysis-title">뉴스 분석</h1>
          <p className="news-analysis-description">
            최신 금융 뉴스를 확인하고 감성 분석 결과를 통해 시장 동향을 파악하세요.
          </p>
        </div>

        <div className="news-analysis-content">
          <div className="news-analysis-main">
            <NewsFilter onFilter={handleFilter} initialFilters={filters} />

            {selectedArticle ? (
              <NewsDetail article={selectedArticle} onClose={handleCloseArticle} />
            ) : (
              <NewsList filters={filters} onSelectArticle={handleSelectArticle} />
            )}
          </div>

          <div className="news-analysis-sidebar">
            <Card className="news-analysis-trend-card">
              <h3 className="news-analysis-trend-title">뉴스 감성 트렌드</h3>
              <SentimentTrendChart height={300} />
            </Card>

            <Card className="news-analysis-info-card">
              <h3 className="news-analysis-info-title">뉴스 분석이란?</h3>
              <p className="news-analysis-info-text">
                뉴스 분석은 금융 뉴스 기사를 수집하고 분석하여 시장 동향을 파악하는 과정입니다.
                감성 분석을 통해 뉴스의 긍정/부정/중립 감성을 식별하고, 이를 통해 시장 움직임을 예측할 수 있습니다.
              </p>
              <h4 className="news-analysis-info-subtitle">주요 특징</h4>
              <ul className="news-analysis-info-list">
                <li>실시간 금융 뉴스 수집</li>
                <li>FinBERT 모델을 활용한 감성 분석</li>
                <li>키워드 추출 및 분석</li>
                <li>시간에 따른 감성 트렌드 확인</li>
              </ul>
            </Card>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default NewsAnalysisPage;
