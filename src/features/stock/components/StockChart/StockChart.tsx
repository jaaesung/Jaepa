/**
 * 주식 차트 컴포넌트
 * 
 * 주식 데이터를 시각화하는 차트 컴포넌트를 제공합니다.
 */

import React, { useEffect, useState } from 'react';
import { Card } from '../../../../components/ui';
import { useStock } from '../../hooks/useStock';
import { StockData, PeriodType } from '../../types';
import './StockChart.css';

interface StockChartProps {
  symbol: string;
  period?: PeriodType;
  height?: number;
  showVolume?: boolean;
  showIndicators?: boolean;
  indicators?: string[];
}

/**
 * 주식 차트 컴포넌트
 */
const StockChart: React.FC<StockChartProps> = ({
  symbol,
  period = '1mo',
  height = 400,
  showVolume = true,
  showIndicators = false,
  indicators = ['sma'],
}) => {
  const { getStockData, data, isLoading, error } = useStock();
  const [selectedPeriod, setSelectedPeriod] = useState<PeriodType>(period);
  const [chartData, setChartData] = useState<any>(null);

  // 주식 데이터 가져오기
  useEffect(() => {
    if (symbol) {
      getStockData(symbol, selectedPeriod);
    }
  }, [getStockData, symbol, selectedPeriod]);

  // 차트 데이터 준비
  useEffect(() => {
    if (data[symbol]) {
      // 여기서는 실제 차트 라이브러리를 사용하지 않고 간단한 시각화만 구현
      setChartData(data[symbol]);
    }
  }, [data, symbol]);

  // 기간 변경 핸들러
  const handlePeriodChange = (newPeriod: PeriodType) => {
    setSelectedPeriod(newPeriod);
  };

  // 최대값 및 최소값 계산 (차트 스케일링용)
  const getMinMaxValues = (stockData: StockData) => {
    if (!stockData || !stockData.dataPoints || stockData.dataPoints.length === 0) {
      return { min: 0, max: 0 };
    }

    const prices = stockData.dataPoints.map(point => point.close);
    return {
      min: Math.min(...prices),
      max: Math.max(...prices),
    };
  };

  // 날짜 포맷팅
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
    });
  };

  // 가격 포맷팅
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(price);
  };

  // 주식 데이터 가져오기
  const stockData = data[symbol];
  const { min, max } = stockData ? getMinMaxValues(stockData) : { min: 0, max: 0 };
  const range = max - min;

  return (
    <Card className="stock-chart">
      <div className="stock-chart-header">
        <div className="stock-chart-title">
          <h3>{symbol}</h3>
          {stockData && stockData.dataPoints.length > 0 && (
            <div className="stock-chart-price">
              {formatPrice(stockData.dataPoints[stockData.dataPoints.length - 1].close)}
            </div>
          )}
        </div>

        <div className="stock-chart-periods">
          <button
            className={`period-button ${selectedPeriod === '1d' ? 'active' : ''}`}
            onClick={() => handlePeriodChange('1d')}
          >
            1일
          </button>
          <button
            className={`period-button ${selectedPeriod === '5d' ? 'active' : ''}`}
            onClick={() => handlePeriodChange('5d')}
          >
            5일
          </button>
          <button
            className={`period-button ${selectedPeriod === '1mo' ? 'active' : ''}`}
            onClick={() => handlePeriodChange('1mo')}
          >
            1개월
          </button>
          <button
            className={`period-button ${selectedPeriod === '3mo' ? 'active' : ''}`}
            onClick={() => handlePeriodChange('3mo')}
          >
            3개월
          </button>
          <button
            className={`period-button ${selectedPeriod === '1y' ? 'active' : ''}`}
            onClick={() => handlePeriodChange('1y')}
          >
            1년
          </button>
          <button
            className={`period-button ${selectedPeriod === 'max' ? 'active' : ''}`}
            onClick={() => handlePeriodChange('max')}
          >
            전체
          </button>
        </div>
      </div>

      <div className="stock-chart-content" style={{ height: `${height}px` }}>
        {isLoading ? (
          <div className="stock-chart-loading">
            <div className="spinner"></div>
            <p>데이터를 불러오는 중입니다...</p>
          </div>
        ) : error ? (
          <div className="stock-chart-error">
            <p>{error}</p>
          </div>
        ) : !chartData || !chartData.dataPoints || chartData.dataPoints.length === 0 ? (
          <div className="stock-chart-empty">
            <p>표시할 데이터가 없습니다.</p>
          </div>
        ) : (
          <div className="stock-chart-visualization">
            <div className="stock-chart-container">
              {/* 간단한 선 차트 구현 */}
              <svg width="100%" height="100%" viewBox={`0 0 ${chartData.dataPoints.length} 100`}>
                <path
                  d={chartData.dataPoints
                    .map((point: any, index: number) => {
                      const x = index;
                      const y = 100 - ((point.close - min) / range) * 100;
                      return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
                    })
                    .join(' ')}
                  fill="none"
                  stroke="var(--primary-color)"
                  strokeWidth="2"
                />
              </svg>

              <div className="stock-chart-labels">
                {chartData.dataPoints.map((point: any, index: number) => {
                  // 데이터 포인트가 많을 경우 일부만 표시
                  if (
                    chartData.dataPoints.length <= 10 ||
                    index % Math.ceil(chartData.dataPoints.length / 10) === 0
                  ) {
                    return (
                      <div
                        key={index}
                        className="stock-chart-label"
                        style={{ left: `${(index / (chartData.dataPoints.length - 1)) * 100}%` }}
                      >
                        {formatDate(point.date)}
                      </div>
                    );
                  }
                  return null;
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export default StockChart;
