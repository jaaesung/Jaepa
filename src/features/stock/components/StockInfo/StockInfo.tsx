/**
 * 주식 정보 컴포넌트
 * 
 * 주식의 상세 정보를 표시하는 컴포넌트를 제공합니다.
 */

import React, { useEffect } from 'react';
import { Card } from '../../../../components/ui';
import { useStock } from '../../hooks/useStock';
import './StockInfo.css';

interface StockInfoProps {
  symbol: string;
}

/**
 * 주식 정보 컴포넌트
 */
const StockInfo: React.FC<StockInfoProps> = ({ symbol }) => {
  const { getStockInfo, info, isLoading, error, watchlist, addStockToWatchlist, removeStockFromWatchlist } = useStock();

  // 주식 정보 가져오기
  useEffect(() => {
    if (symbol) {
      getStockInfo(symbol);
    }
  }, [getStockInfo, symbol]);

  // 주식 정보
  const stockInfo = info[symbol];
  const isInWatchlist = watchlist.includes(symbol);

  // 관심 목록 토글 핸들러
  const handleWatchlistToggle = () => {
    if (isInWatchlist) {
      removeStockFromWatchlist(symbol);
    } else {
      addStockToWatchlist(symbol);
    }
  };

  // 가격 포맷팅
  const formatPrice = (price?: number) => {
    if (price === undefined) return '-';
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(price);
  };

  // 퍼센트 포맷팅
  const formatPercent = (percent?: number) => {
    if (percent === undefined) return '-';
    return new Intl.NumberFormat('ko-KR', {
      style: 'percent',
      minimumFractionDigits: 2,
    }).format(percent / 100);
  };

  // 숫자 포맷팅
  const formatNumber = (num?: number) => {
    if (num === undefined) return '-';
    return new Intl.NumberFormat('ko-KR').format(num);
  };

  // 시가총액 포맷팅
  const formatMarketCap = (marketCap?: number) => {
    if (marketCap === undefined) return '-';
    
    if (marketCap >= 1_000_000_000_000) {
      return `${(marketCap / 1_000_000_000_000).toFixed(2)}T`;
    } else if (marketCap >= 1_000_000_000) {
      return `${(marketCap / 1_000_000_000).toFixed(2)}B`;
    } else if (marketCap >= 1_000_000) {
      return `${(marketCap / 1_000_000).toFixed(2)}M`;
    } else {
      return formatNumber(marketCap);
    }
  };

  return (
    <Card className="stock-info">
      {isLoading ? (
        <div className="stock-info-loading">
          <div className="spinner"></div>
          <p>데이터를 불러오는 중입니다...</p>
        </div>
      ) : error ? (
        <div className="stock-info-error">
          <p>{error}</p>
        </div>
      ) : !stockInfo ? (
        <div className="stock-info-empty">
          <p>표시할 데이터가 없습니다.</p>
        </div>
      ) : (
        <>
          <div className="stock-info-header">
            <div className="stock-info-title">
              <h3>{stockInfo.name}</h3>
              <div className="stock-info-symbol">{stockInfo.symbol}</div>
              <div className="stock-info-exchange">{stockInfo.exchange}</div>
            </div>
            
            <button
              className={`watchlist-button ${isInWatchlist ? 'active' : ''}`}
              onClick={handleWatchlistToggle}
            >
              {isInWatchlist ? '관심 목록에서 제거' : '관심 목록에 추가'}
            </button>
          </div>
          
          <div className="stock-info-price">
            <div className="stock-info-current-price">{formatPrice(stockInfo.price)}</div>
            <div className={`stock-info-change ${stockInfo.change >= 0 ? 'positive' : 'negative'}`}>
              {formatPrice(stockInfo.change)} ({formatPercent(stockInfo.changePercent)})
            </div>
          </div>
          
          <div className="stock-info-details">
            <div className="stock-info-row">
              <div className="stock-info-item">
                <div className="stock-info-label">시가총액</div>
                <div className="stock-info-value">{formatMarketCap(stockInfo.marketCap)}</div>
              </div>
              <div className="stock-info-item">
                <div className="stock-info-label">거래량</div>
                <div className="stock-info-value">{formatNumber(stockInfo.volume)}</div>
              </div>
              <div className="stock-info-item">
                <div className="stock-info-label">평균 거래량</div>
                <div className="stock-info-value">{formatNumber(stockInfo.avgVolume)}</div>
              </div>
            </div>
            
            <div className="stock-info-row">
              <div className="stock-info-item">
                <div className="stock-info-label">시가</div>
                <div className="stock-info-value">{formatPrice(stockInfo.open)}</div>
              </div>
              <div className="stock-info-item">
                <div className="stock-info-label">전일 종가</div>
                <div className="stock-info-value">{formatPrice(stockInfo.previousClose)}</div>
              </div>
              <div className="stock-info-item">
                <div className="stock-info-label">통화</div>
                <div className="stock-info-value">{stockInfo.currency}</div>
              </div>
            </div>
            
            <div className="stock-info-row">
              <div className="stock-info-item">
                <div className="stock-info-label">52주 최고</div>
                <div className="stock-info-value">{formatPrice(stockInfo.high52Week)}</div>
              </div>
              <div className="stock-info-item">
                <div className="stock-info-label">52주 최저</div>
                <div className="stock-info-value">{formatPrice(stockInfo.low52Week)}</div>
              </div>
            </div>
          </div>
          
          {stockInfo.description && (
            <div className="stock-info-description">
              <h4>회사 소개</h4>
              <p>{stockInfo.description}</p>
            </div>
          )}
        </>
      )}
    </Card>
  );
};

export default StockInfo;
