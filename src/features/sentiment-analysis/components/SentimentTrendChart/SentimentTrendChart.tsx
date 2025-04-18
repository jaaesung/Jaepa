/**
 * 감성 트렌드 차트 컴포넌트
 * 
 * 시간에 따른 감성 분석 결과 트렌드를 시각화하는 컴포넌트를 제공합니다.
 */

import React, { useEffect, useState } from 'react';
import { Card } from '../../../../components/ui';
import { useSentiment } from '../../hooks/useSentiment';
import './SentimentTrendChart.css';

interface SentimentTrendChartProps {
  startDate?: string;
  endDate?: string;
  interval?: 'day' | 'week' | 'month';
  title?: string;
  height?: number;
}

/**
 * 감성 트렌드 차트 컴포넌트
 */
const SentimentTrendChart: React.FC<SentimentTrendChartProps> = ({
  startDate,
  endDate,
  interval = 'day',
  title = '감성 트렌드',
  height = 300,
}) => {
  const { getTrend, trend, trendLoading, trendError } = useSentiment();
  const [chartData, setChartData] = useState<any>(null);

  // 트렌드 데이터 가져오기
  useEffect(() => {
    getTrend({ startDate, endDate, interval });
  }, [getTrend, startDate, endDate, interval]);

  // 차트 데이터 준비
  useEffect(() => {
    if (trend && trend.length > 0) {
      // 여기서는 실제 차트 라이브러리를 사용하지 않고 간단한 시각화만 구현
      setChartData(trend);
    }
  }, [trend]);

  // 최대값 계산 (차트 스케일링용)
  const getMaxValue = () => {
    if (!chartData) return 0;
    return Math.max(
      ...chartData.map((item: any) => Math.max(item.positive, item.neutral, item.negative))
    );
  };

  // 날짜 포맷팅
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <Card className="sentiment-trend-chart">
      <div className="sentiment-trend-chart-header">
        <h3 className="sentiment-trend-chart-title">{title}</h3>
      </div>

      <div className="sentiment-trend-chart-content" style={{ height: `${height}px` }}>
        {trendLoading ? (
          <div className="sentiment-trend-chart-loading">
            <div className="spinner"></div>
            <p>데이터를 불러오는 중입니다...</p>
          </div>
        ) : trendError ? (
          <div className="sentiment-trend-chart-error">
            <p>{trendError}</p>
          </div>
        ) : !chartData || chartData.length === 0 ? (
          <div className="sentiment-trend-chart-empty">
            <p>표시할 데이터가 없습니다.</p>
          </div>
        ) : (
          <div className="sentiment-trend-chart-visualization">
            <div className="sentiment-trend-chart-legend">
              <div className="sentiment-trend-chart-legend-item">
                <div className="sentiment-trend-chart-legend-color sentiment-positive"></div>
                <div className="sentiment-trend-chart-legend-label">긍정적</div>
              </div>
              <div className="sentiment-trend-chart-legend-item">
                <div className="sentiment-trend-chart-legend-color sentiment-neutral"></div>
                <div className="sentiment-trend-chart-legend-label">중립적</div>
              </div>
              <div className="sentiment-trend-chart-legend-item">
                <div className="sentiment-trend-chart-legend-color sentiment-negative"></div>
                <div className="sentiment-trend-chart-legend-label">부정적</div>
              </div>
            </div>

            <div className="sentiment-trend-chart-container">
              {/* 간단한 막대 차트 구현 */}
              {chartData.map((item: any, index: number) => (
                <div key={index} className="sentiment-trend-chart-bar-group">
                  <div className="sentiment-trend-chart-bars">
                    <div
                      className="sentiment-trend-chart-bar sentiment-positive"
                      style={{
                        height: `${(item.positive / getMaxValue()) * 100}%`,
                      }}
                      title={`긍정적: ${Math.round(item.positive * 100)}%`}
                    ></div>
                    <div
                      className="sentiment-trend-chart-bar sentiment-neutral"
                      style={{
                        height: `${(item.neutral / getMaxValue()) * 100}%`,
                      }}
                      title={`중립적: ${Math.round(item.neutral * 100)}%`}
                    ></div>
                    <div
                      className="sentiment-trend-chart-bar sentiment-negative"
                      style={{
                        height: `${(item.negative / getMaxValue()) * 100}%`,
                      }}
                      title={`부정적: ${Math.round(item.negative * 100)}%`}
                    ></div>
                  </div>
                  <div className="sentiment-trend-chart-label">{formatDate(item.date)}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export default SentimentTrendChart;
