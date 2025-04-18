/**
 * 주식 분석 페이지 컴포넌트
 * 
 * 주식 분석 기능을 제공하는 페이지를 제공합니다.
 */

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { MainLayout } from '../../components/layout';
import { Card } from '../../components/ui';
import { StockChart, StockInfo, StockSearch } from '../../features/stock';
import { useStock } from '../../features/stock';
import './StockAnalysisPage.css';

/**
 * 주식 분석 페이지 컴포넌트
 */
const StockAnalysisPage: React.FC = () => {
  const { symbol: urlSymbol } = useParams<{ symbol?: string }>();
  const [selectedSymbol, setSelectedSymbol] = useState<string>(urlSymbol || 'AAPL');
  const { getPopularStocks, popularStocks, popularLoading } = useStock();

  // 인기 주식 데이터 가져오기
  useEffect(() => {
    getPopularStocks();
  }, [getPopularStocks]);

  // 주식 선택 핸들러
  const handleSelectStock = (symbol: string) => {
    setSelectedSymbol(symbol);
  };

  // 인기 주식 선택 핸들러
  const handleSelectPopularStock = (symbol: string) => {
    setSelectedSymbol(symbol);
  };

  return (
    <MainLayout>
      <div className="stock-analysis-page">
        <div className="stock-analysis-header">
          <h1 className="stock-analysis-title">주식 분석</h1>
          <p className="stock-analysis-description">
            주식 데이터를 분석하고 시장 동향을 파악하세요.
          </p>
        </div>

        <div className="stock-analysis-search">
          <StockSearch onSelect={handleSelectStock} />
        </div>

        <div className="stock-analysis-content">
          <div className="stock-analysis-main">
            <div className="stock-chart-container">
              <StockChart symbol={selectedSymbol} height={400} showVolume />
            </div>

            <div className="stock-info-container">
              <StockInfo symbol={selectedSymbol} />
            </div>
          </div>

          <div className="stock-analysis-sidebar">
            <Card className="popular-stocks-card">
              <h3 className="popular-stocks-title">인기 주식</h3>
              
              {popularLoading ? (
                <div className="popular-stocks-loading">
                  <div className="spinner"></div>
                  <p>데이터를 불러오는 중입니다...</p>
                </div>
              ) : popularStocks.length === 0 ? (
                <div className="popular-stocks-empty">
                  <p>표시할 데이터가 없습니다.</p>
                </div>
              ) : (
                <ul className="popular-stocks-list">
                  {popularStocks.slice(0, 10).map((stock) => (
                    <li
                      key={stock.symbol}
                      className={`popular-stock-item ${
                        stock.symbol === selectedSymbol ? 'active' : ''
                      }`}
                    >
                      <button
                        className="popular-stock-button"
                        onClick={() => handleSelectPopularStock(stock.symbol)}
                      >
                        <div className="popular-stock-symbol">{stock.symbol}</div>
                        <div className="popular-stock-name">{stock.name}</div>
                        <div
                          className={`popular-stock-change ${
                            stock.changePercent >= 0 ? 'positive' : 'negative'
                          }`}
                        >
                          {stock.changePercent >= 0 ? '+' : ''}
                          {stock.changePercent.toFixed(2)}%
                        </div>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <Card className="stock-analysis-info-card">
              <h3 className="stock-analysis-info-title">주식 분석이란?</h3>
              <p className="stock-analysis-info-text">
                주식 분석은 주식의 가격 변동, 거래량, 기술적 지표 등을 분석하여 투자 결정을 내리는 데 도움을 주는 과정입니다.
                기술적 분석과 기본적 분석을 통해 주식의 미래 가격 움직임을 예측할 수 있습니다.
              </p>
              <h4 className="stock-analysis-info-subtitle">주요 특징</h4>
              <ul className="stock-analysis-info-list">
                <li>실시간 주식 데이터 조회</li>
                <li>기술적 지표 분석</li>
                <li>감성 분석과의 상관관계 확인</li>
                <li>인기 주식 및 시장 동향 파악</li>
              </ul>
            </Card>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default StockAnalysisPage;
