/**
 * 감성 분석 페이지 컴포넌트
 * 
 * 감성 분석 기능을 제공하는 페이지를 제공합니다.
 */

import React, { useEffect } from 'react';
import { MainLayout } from '../../components/layout';
import { Card } from '../../components/ui';
import { SentimentAnalyzer, SentimentTrendChart } from '../../features/sentiment-analysis';
import { useSentiment } from '../../features/sentiment-analysis';
import './SentimentAnalysisPage.css';

/**
 * 감성 분석 페이지 컴포넌트
 */
const SentimentAnalysisPage: React.FC = () => {
  const { getTrend } = useSentiment();

  // 감성 트렌드 데이터 가져오기
  useEffect(() => {
    // 최근 3개월 데이터 가져오기
    const endDate = new Date().toISOString().split('T')[0];
    const startDate = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split('T')[0];
    
    getTrend({ startDate, endDate, interval: 'day' });
  }, [getTrend]);

  return (
    <MainLayout>
      <div className="sentiment-analysis-page">
        <div className="sentiment-analysis-header">
          <h1 className="sentiment-analysis-title">감성 분석</h1>
          <p className="sentiment-analysis-description">
            텍스트 데이터의 감성을 분석하고 시간에 따른 감성 트렌드를 확인하세요.
          </p>
        </div>

        <div className="sentiment-analysis-content">
          <div className="sentiment-analysis-main">
            <SentimentAnalyzer />
          </div>

          <div className="sentiment-analysis-trend">
            <SentimentTrendChart
              title="최근 3개월 감성 트렌드"
              height={350}
            />
          </div>

          <div className="sentiment-analysis-info">
            <Card className="sentiment-info-card">
              <h3 className="sentiment-info-title">감성 분석이란?</h3>
              <p className="sentiment-info-text">
                감성 분석(Sentiment Analysis)은 텍스트에서 주관적인 정보를 추출하여 글쓴이의 태도, 감정, 의견 등을 파악하는 자연어 처리 기술입니다.
                금융 뉴스의 감성 분석은 시장 동향을 예측하고 투자 결정을 내리는 데 도움이 됩니다.
              </p>
              <h4 className="sentiment-info-subtitle">주요 특징</h4>
              <ul className="sentiment-info-list">
                <li>텍스트의 긍정/부정/중립 감성 식별</li>
                <li>금융 특화 FinBERT 모델 활용</li>
                <li>시간에 따른 감성 변화 추적</li>
                <li>주식 가격과 감성 간의 상관관계 분석</li>
              </ul>
            </Card>

            <Card className="sentiment-info-card">
              <h3 className="sentiment-info-title">사용 방법</h3>
              <p className="sentiment-info-text">
                감성 분석기를 사용하여 텍스트의 감성을 분석하고, 감성 트렌드 차트를 통해 시간에 따른 감성 변화를 확인할 수 있습니다.
              </p>
              <h4 className="sentiment-info-subtitle">분석 단계</h4>
              <ol className="sentiment-info-steps">
                <li>분석할 텍스트 입력</li>
                <li>분석 모델 선택</li>
                <li>'분석하기' 버튼 클릭</li>
                <li>결과 확인 및 해석</li>
              </ol>
            </Card>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default SentimentAnalysisPage;
