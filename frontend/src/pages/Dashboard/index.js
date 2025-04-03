import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchNews } from '../../store/slices/newsSlice';
import { fetchStockData, fetchSentimentAnalysis } from '../../store/slices/stockSlice';
import './Dashboard.css';

/**
 * 대시보드 메인 페이지 컴포넌트
 */
const Dashboard = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const { items: newsItems, isLoading: newsLoading } = useSelector((state) => state.news);
  const { stockData, isLoading: stockLoading } = useSelector((state) => state.stock);
  
  const [selectedPeriod, setSelectedPeriod] = useState('1w');
  const [selectedStocks, setSelectedStocks] = useState(['AAPL', 'MSFT', 'GOOG']);

  useEffect(() => {
    // 뉴스 데이터 가져오기
    dispatch(fetchNews({ limit: 5 }));
    
    // 선택된 주식 데이터 가져오기
    selectedStocks.forEach((symbol) => {
      dispatch(fetchStockData({ symbol, period: selectedPeriod }));
      dispatch(fetchSentimentAnalysis({ symbol }));
    });
  }, [dispatch, selectedPeriod, selectedStocks]);

  const handlePeriodChange = (period) => {
    setSelectedPeriod(period);
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>대시보드</h1>
        <p className="welcome-message">안녕하세요, {user?.name || '사용자'}님!</p>
      </div>
      
      <div className="dashboard-content">
        <div className="dashboard-section">
          <div className="section-header">
            <h2>주요 지표</h2>
            <div className="period-selector">
              <button
                className={selectedPeriod === '1d' ? 'active' : ''}
                onClick={() => handlePeriodChange('1d')}
              >
                1일
              </button>
              <button
                className={selectedPeriod === '1w' ? 'active' : ''}
                onClick={() => handlePeriodChange('1w')}
              >
                1주
              </button>
              <button
                className={selectedPeriod === '1m' ? 'active' : ''}
                onClick={() => handlePeriodChange('1m')}
              >
                1개월
              </button>
              <button
                className={selectedPeriod === '3m' ? 'active' : ''}
                onClick={() => handlePeriodChange('3m')}
              >
                3개월
              </button>
            </div>
          </div>
          
          <div className="metrics-cards">
            {stockLoading ? (
              <div className="loading-indicator">데이터 로딩 중...</div>
            ) : (
              <>
                <div className="metric-card">
                  <h3>S&P 500</h3>
                  <div className="metric-value">4,832.54</div>
                  <div className="metric-change positive">+1.2%</div>
                </div>
                
                <div className="metric-card">
                  <h3>NASDAQ</h3>
                  <div className="metric-value">16,274.94</div>
                  <div className="metric-change positive">+1.5%</div>
                </div>
                
                <div className="metric-card">
                  <h3>KOSPI</h3>
                  <div className="metric-value">2,798.76</div>
                  <div className="metric-change negative">-0.3%</div>
                </div>
                
                <div className="metric-card">
                  <h3>환율 (USD/KRW)</h3>
                  <div className="metric-value">1,189.45</div>
                  <div className="metric-change negative">-0.7%</div>
                </div>
              </>
            )}
          </div>
        </div>
        
        <div className="dashboard-grid">
          <div className="dashboard-section stock-sentiment">
            <h2>관심 종목 감성 분석</h2>
            <div className="sentiment-chart">
              {stockLoading ? (
                <div className="loading-indicator">데이터 로딩 중...</div>
              ) : (
                <div className="sentiment-chart-placeholder">
                  <p>감성 분석 차트가 이곳에 표시됩니다.</p>
                </div>
              )}
            </div>
          </div>
          
          <div className="dashboard-section recent-news">
            <h2>최신 뉴스</h2>
            {newsLoading ? (
              <div className="loading-indicator">뉴스 로딩 중...</div>
            ) : (
              <div className="news-list">
                {newsItems?.length > 0 ? (
                  newsItems.map((news) => (
                    <div key={news.id} className="news-item">
                      <h3 className="news-title">{news.title}</h3>
                      <p className="news-source">{news.source} • {news.published_at}</p>
                      <p className="news-summary">{news.summary}</p>
                      <div className={`news-sentiment ${
                        news.sentiment > 0.3 ? 'positive' : 
                        news.sentiment < -0.3 ? 'negative' : 'neutral'
                      }`}>
                        {news.sentiment > 0.3 ? '긍정적' : 
                         news.sentiment < -0.3 ? '부정적' : '중립적'}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="empty-state">
                    <p>최신 뉴스가 없습니다.</p>
                  </div>
                )}
              </div>
            )}
          </div>
          
          <div className="dashboard-section stock-performance">
            <h2>종목 실적</h2>
            {stockLoading ? (
              <div className="loading-indicator">데이터 로딩 중...</div>
            ) : (
              <div className="stock-chart-placeholder">
                <p>주식 성과 차트가 이곳에 표시됩니다.</p>
              </div>
            )}
          </div>
          
          <div className="dashboard-section keyword-trends">
            <h2>인기 키워드</h2>
            <div className="keyword-cloud-placeholder">
              <p>인기 키워드 클라우드가 이곳에 표시됩니다.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;