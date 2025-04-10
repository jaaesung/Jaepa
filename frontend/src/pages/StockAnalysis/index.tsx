import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../types';
import { fetchStockData, fetchMultipleStocks, fetchStockCorrelation, searchStocks } from '../../store/slices/stockSlice';
import { StockData } from '../../types';
import './StockAnalysis.css';

// 컴포넌트 불러오기
import StockPerformanceChart from '../../components/charts/StockPerformanceChart';
import CorrelationChart from '../../components/charts/CorrelationChart';
import { format } from 'date-fns';

interface TechnicalIndicator {
  name: string;
  symbol: string;
  value: string | number;
  change: number;
  status: 'positive' | 'negative' | 'neutral';
}

interface Watchlist {
  name: string;
  symbols: string[];
}

const StockAnalysis: React.FC = () => {
  const dispatch = useDispatch();
  const { stocks, selectedStock, correlationData, searchResults, isLoading, error } = useSelector((state: RootState) => state.stocks);
  
  // 상태 관리
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>(['AAPL', 'MSFT', 'GOOG', 'AMZN']);
  const [timeRange, setTimeRange] = useState<string>('1m');
  const [showCorrelation, setShowCorrelation] = useState<boolean>(false);
  const [selectedWatchlist, setSelectedWatchlist] = useState<string>('default');
  const [customIndicators, setCustomIndicators] = useState<string[]>(['SMA', 'RSI', 'MACD']);
  
  // 예제 데이터
  const sampleWatchlists: Watchlist[] = [
    { name: 'default', symbols: ['AAPL', 'MSFT', 'GOOG', 'AMZN'] },
    { name: 'Tech Giants', symbols: ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META', 'NFLX'] },
    { name: 'Korean Stocks', symbols: ['005930.KS', '000660.KS', '035720.KS'] }, // 삼성전자, SK하이닉스, 카카오
    { name: 'Crypto', symbols: ['BTC-USD', 'ETH-USD', 'SOL-USD'] },
  ];
  
  // 주식 정보를 시간 순으로 포맷팅하기 위한 샘플 데이터
  const sampleHistoricalData = [
    { date: '2025-03-01', AAPL: 190000, MSFT: 430000, GOOG: 172000, AMZN: 182000 },
    { date: '2025-03-02', AAPL: 187000, MSFT: 427000, GOOG: 169000, AMZN: 179000 },
    { date: '2025-03-03', AAPL: 192000, MSFT: 435000, GOOG: 170000, AMZN: 183000 },
    { date: '2025-03-04', AAPL: 196000, MSFT: 440000, GOOG: 175000, AMZN: 185000 },
    { date: '2025-03-05', AAPL: 198000, MSFT: 442000, GOOG: 176000, AMZN: 187000 },
    { date: '2025-03-06', AAPL: 201000, MSFT: 445000, GOOG: 178000, AMZN: 189000 },
    { date: '2025-03-07', AAPL: 203000, MSFT: 447000, GOOG: 177000, AMZN: 190000 },
    { date: '2025-03-08', AAPL: 200000, MSFT: 442000, GOOG: 174000, AMZN: 188000 },
    { date: '2025-03-09', AAPL: 204000, MSFT: 448000, GOOG: 176000, AMZN: 191000 },
    { date: '2025-03-10', AAPL: 205000, MSFT: 450000, GOOG: 178000, AMZN: 193000 },
  ];
  
  // 감성 상관관계 데이터 샘플
  const sampleCorrelationData = [
    { date: '2025-03-01', price: 190000, sentiment: 0.4, volume: 2000000 },
    { date: '2025-03-02', price: 187000, sentiment: 0.3, volume: 1800000 },
    { date: '2025-03-03', price: 192000, sentiment: 0.5, volume: 2500000 },
    { date: '2025-03-04', price: 196000, sentiment: 0.6, volume: 2700000 },
    { date: '2025-03-05', price: 198000, sentiment: 0.7, volume: 3000000 },
    { date: '2025-03-06', price: 201000, sentiment: 0.8, volume: 3200000 },
    { date: '2025-03-07', price: 203000, sentiment: 0.7, volume: 2900000 },
    { date: '2025-03-08', price: 200000, sentiment: 0.5, volume: 2300000 },
    { date: '2025-03-09', price: 204000, sentiment: 0.6, volume: 2600000 },
    { date: '2025-03-10', price: 205000, sentiment: 0.7, volume: 2800000 },
  ];
  
  // 기술적 지표 샘플 데이터
  const sampleTechnicalIndicators: TechnicalIndicator[] = [
    { name: 'SMA (20)', symbol: 'AAPL', value: '203,142', change: 0.75, status: 'positive' },
    { name: 'EMA (20)', symbol: 'AAPL', value: '204,567', change: 0.81, status: 'positive' },
    { name: 'RSI (14)', symbol: 'AAPL', value: 68.5, change: 2.3, status: 'neutral' },
    { name: 'MACD', symbol: 'AAPL', value: '1.234', change: 0.12, status: 'positive' },
    { name: 'Bollinger Band Upper', symbol: 'AAPL', value: '215,432', change: 0.5, status: 'positive' },
    { name: 'Bollinger Band Lower', symbol: 'AAPL', value: '195,876', change: 0.45, status: 'positive' },
    { name: 'Stochastic Oscillator', symbol: 'AAPL', value: 82.3, change: 3.1, status: 'negative' },
    { name: 'OBV', symbol: 'AAPL', value: '15.4M', change: 0.28, status: 'positive' },
  ];
  
  useEffect(() => {
    // 선택된 주식 데이터 가져오기
    if (selectedSymbols.length > 0) {
      dispatch(fetchMultipleStocks({ symbols: selectedSymbols, period: timeRange }));
    }
    
    // 첫 번째 주식에 대한 감성 상관관계 가져오기
    if (showCorrelation && selectedSymbols.length > 0) {
      dispatch(fetchStockCorrelation({ symbol: selectedSymbols[0] }));
    }
  }, [dispatch, selectedSymbols, timeRange, showCorrelation]);
  
  // 검색 핸들러
  const handleSearch = () => {
    if (searchQuery.trim()) {
      dispatch(searchStocks(searchQuery));
    }
  };
  
  // 엔터 키로 검색 실행
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };
  
  // 주식 심볼 선택/해제 핸들러
  const toggleStockSymbol = (symbol: string) => {
    if (selectedSymbols.includes(symbol)) {
      setSelectedSymbols(selectedSymbols.filter(s => s !== symbol));
    } else {
      setSelectedSymbols([...selectedSymbols, symbol]);
    }
  };
  
  // 워치리스트 변경 핸들러
  const handleWatchlistChange = (watchlistName: string) => {
    const watchlist = sampleWatchlists.find(w => w.name === watchlistName);
    if (watchlist) {
      setSelectedSymbols(watchlist.symbols);
      setSelectedWatchlist(watchlistName);
    }
  };
  
  // 기술 지표 표시 여부 관리
  const toggleIndicator = (indicator: string) => {
    if (customIndicators.includes(indicator)) {
      setCustomIndicators(customIndicators.filter(i => i !== indicator));
    } else {
      setCustomIndicators([...customIndicators, indicator]);
    }
  };
  
  // 현재 날짜 포맷
  const currentDate = format(new Date(), 'yyyy-MM-dd');
  
  return (
    <div className="stock-analysis-container">
      <div className="stock-analysis-header">
        <h1>주식 분석</h1>
        <p className="description">
          주식 데이터를 분석하고 뉴스 감성과의 상관관계를 확인하세요.
        </p>
      </div>
      
      <div className="stock-analysis-content">
        <div className="stock-sidebar">
          <div className="search-section">
            <h3>주식 검색</h3>
            <div className="search-box">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="심볼 또는 회사명 검색"
              />
              <button onClick={handleSearch}>검색</button>
            </div>
            
            {isLoading && <div className="loading-indicator">검색 중...</div>}
            
            {searchResults.length > 0 && (
              <div className="search-results">
                <h4>검색 결과</h4>
                <ul>
                  {searchResults.map((result) => (
                    <li key={result.symbol}>
                      <button 
                        onClick={() => toggleStockSymbol(result.symbol)}
                        className={selectedSymbols.includes(result.symbol) ? 'selected' : ''}
                      >
                        <span className="stock-symbol">{result.symbol}</span>
                        <span className="stock-name">{result.name}</span>
                        {selectedSymbols.includes(result.symbol) ? 
                          <span className="check-icon">✓</span> : 
                          <span className="add-icon">+</span>
                        }
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          
          <div className="watchlist-section">
            <h3>워치리스트</h3>
            <select
              value={selectedWatchlist}
              onChange={(e) => handleWatchlistChange(e.target.value)}
            >
              {sampleWatchlists.map(list => (
                <option key={list.name} value={list.name}>
                  {list.name}
                </option>
              ))}
            </select>
            
            <div className="watchlist-symbols">
              {selectedSymbols.map(symbol => (
                <div className="watchlist-symbol" key={symbol}>
                  <span>{symbol}</span>
                  <button 
                    className="remove-btn"
                    onClick={() => toggleStockSymbol(symbol)}
                    title="제거"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </div>
          
          <div className="time-range-section">
            <h3>기간 설정</h3>
            <div className="time-range-options">
              <button 
                className={timeRange === '1d' ? 'active' : ''}
                onClick={() => setTimeRange('1d')}
              >
                1일
              </button>
              <button 
                className={timeRange === '1w' ? 'active' : ''}
                onClick={() => setTimeRange('1w')}
              >
                1주
              </button>
              <button 
                className={timeRange === '1m' ? 'active' : ''}
                onClick={() => setTimeRange('1m')}
              >
                1개월
              </button>
              <button 
                className={timeRange === '3m' ? 'active' : ''}
                onClick={() => setTimeRange('3m')}
              >
                3개월
              </button>
              <button 
                className={timeRange === '6m' ? 'active' : ''}
                onClick={() => setTimeRange('6m')}
              >
                6개월
              </button>
              <button 
                className={timeRange === '1y' ? 'active' : ''}
                onClick={() => setTimeRange('1y')}
              >
                1년
              </button>
            </div>
          </div>
          
          <div className="indicators-section">
            <h3>기술적 지표</h3>
            <div className="indicator-options">
              <label>
                <input
                  type="checkbox"
                  checked={customIndicators.includes('SMA')}
                  onChange={() => toggleIndicator('SMA')}
                />
                이동평균선(SMA)
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={customIndicators.includes('EMA')}
                  onChange={() => toggleIndicator('EMA')}
                />
                지수이동평균선(EMA)
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={customIndicators.includes('RSI')}
                  onChange={() => toggleIndicator('RSI')}
                />
                상대강도지수(RSI)
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={customIndicators.includes('MACD')}
                  onChange={() => toggleIndicator('MACD')}
                />
                MACD
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={customIndicators.includes('BB')}
                  onChange={() => toggleIndicator('BB')}
                />
                볼린저 밴드
              </label>
            </div>
          </div>
          
          <div className="correlation-section">
            <h3>감성 분석 상관관계</h3>
            <label>
              <input
                type="checkbox"
                checked={showCorrelation}
                onChange={() => setShowCorrelation(!showCorrelation)}
              />
              뉴스 감성과 주가 상관관계 표시
            </label>
          </div>
        </div>
        
        <div className="stock-main-content">
          <div className="stock-header-section">
            <div className="date-info">
              <h2>주식 가격 및 분석</h2>
              <span className="current-date">{currentDate} 기준</span>
            </div>
            <div className="stock-overview">
              {selectedSymbols.slice(0, 4).map(symbol => {
                const stockInfo = stocks.find(stock => stock.symbol === symbol);
                return (
                  <div className="stock-overview-card" key={symbol}>
                    <div className="stock-symbol-name">
                      <span className="symbol">{symbol}</span>
                      <span className="name">{stockInfo?.name || 'Loading...'}</span>
                    </div>
                    <div className="stock-price">
                      {stockInfo ? (
                        <>
                          <div className="current-price">
                            {new Intl.NumberFormat('ko-KR', {
                              style: 'currency',
                              currency: 'KRW',
                              maximumFractionDigits: 0,
                            }).format(stockInfo.price)}
                          </div>
                          <div className={`price-change ${stockInfo.change >= 0 ? 'positive' : 'negative'}`}>
                            {stockInfo.change > 0 ? '+' : ''}{stockInfo.change.toFixed(2)} ({stockInfo.changePercent.toFixed(2)}%)
                          </div>
                        </>
                      ) : (
                        <div className="loading-placeholder">Loading...</div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          
          <div className="chart-container">
            <div className="section-header">
              <h3>가격 차트</h3>
            </div>
            {isLoading ? (
              <div className="loading-indicator">차트 로딩 중...</div>
            ) : (
              <StockPerformanceChart 
                data={sampleHistoricalData}
                symbols={selectedSymbols}
                height={400}
              />
            )}
          </div>
          
          {showCorrelation && selectedSymbols.length > 0 && (
            <div className="correlation-container">
              <div className="section-header">
                <h3>{selectedSymbols[0]} 주가-감성 상관관계</h3>
              </div>
              <CorrelationChart 
                data={sampleCorrelationData}
                symbol={selectedSymbols[0]}
                height={350}
              />
            </div>
          )}
          
          <div className="technical-indicators-container">
            <div className="section-header">
              <h3>기술적 지표</h3>
            </div>
            <div className="technical-indicators-grid">
              {sampleTechnicalIndicators
                .filter(indicator => 
                  customIndicators.some(selected => 
                    indicator.name.includes(selected)
                  )
                )
                .map((indicator, index) => (
                  <div className="indicator-card" key={index}>
                    <div className="indicator-name">{indicator.name}</div>
                    <div className="indicator-value">{indicator.value}</div>
                    <div className={`indicator-change ${indicator.status}`}>
                      {indicator.change > 0 ? '+' : ''}{indicator.change.toFixed(2)}%
                    </div>
                  </div>
                ))
              }
            </div>
          </div>
          
          <div className="stock-analysis-summary">
            <div className="section-header">
              <h3>분석 요약</h3>
            </div>
            <div className="summary-content">
              <p>
                <strong>기술적 분석:</strong> 이동평균선(SMA)은 상승 추세를 보이고 있으며, RSI 지표는 68.5로 약간 과매수 상태를 나타내고 있습니다. 
                MACD는 양수 값을 유지하며 상승 모멘텀을 확인해주고 있습니다.
              </p>
              <p>
                <strong>뉴스 감성 분석:</strong> 최근 7일간의 뉴스 감성은 평균 0.65로 긍정적인 경향을 보이고 있습니다. 
                주가와 뉴스 감성 간의 상관계수는 0.72로 강한 양의 상관관계를 나타내고 있습니다.
              </p>
              <p>
                <strong>거래량 분석:</strong> 거래량은 최근 5일 평균 대비 15% 증가했으며, 가격 상승과 함께 거래량이 증가하는 건전한 상승 추세를 보이고 있습니다.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockAnalysis;