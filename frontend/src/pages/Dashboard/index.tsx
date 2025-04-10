import React, { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { fetchNews } from "../../store/slices/newsSlice";
import { fetchStockData } from "../../store/slices/stockSlice";
import { RootState } from "../../types";
import "./Dashboard.css";

// 차트 컴포넌트들 가져오기
import SentimentChart from "../../components/charts/SentimentChart";
import StockPerformanceChart from "../../components/charts/StockPerformanceChart";
import KeywordCloud from "../../components/charts/KeywordCloud";
import CorrelationChart from "../../components/charts/CorrelationChart";
import NewsCard from "../../components/news/NewsCard";

type PeriodType = "1d" | "1w" | "1m" | "3m";

/**
 * 대시보드 메인 페이지 컴포넌트
 */
const Dashboard: React.FC = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state: RootState) => state.auth);
  const { articles: newsItems, isLoading: newsLoading } = useSelector(
    (state: RootState) => state.news
  );
  const { stocks: stockData, isLoading: stockLoading } = useSelector(
    (state: RootState) => state.stocks
  );

  const [selectedPeriod, setSelectedPeriod] = useState<PeriodType>("1w");
  const [selectedStocks, setSelectedStocks] = useState<string[]>([
    "AAPL",
    "MSFT",
    "GOOG",
  ]);

  useEffect(() => {
    // 뉴스 데이터 가져오기
    dispatch(fetchNews({ limit: 5 }));

    // 선택된 주식 데이터 가져오기
    selectedStocks.forEach((symbol) => {
      dispatch(fetchStockData({ symbol, period: selectedPeriod }));
      // 감성 분석 데이터는 샘플 데이터로 대체
      // dispatch(fetchSentimentAnalysis({ symbol }));
    });
  }, [dispatch, selectedPeriod, selectedStocks]);

  const handlePeriodChange = (period: PeriodType): void => {
    setSelectedPeriod(period);
  };

  // 샘플 데이터 (실제 앱에서는 API에서 가져온 데이터를 사용)
  const sampleSentimentData = [
    { symbol: "AAPL", positive: 0.45, neutral: 0.35, negative: 0.2 },
    { symbol: "MSFT", positive: 0.6, neutral: 0.3, negative: 0.1 },
    { symbol: "GOOG", positive: 0.3, neutral: 0.3, negative: 0.4 },
    { symbol: "AMZN", positive: 0.35, neutral: 0.45, negative: 0.2 },
    { symbol: "TSLA", positive: 0.25, neutral: 0.25, negative: 0.5 },
  ];

  const sampleStockPerformanceData = [
    {
      date: "2025-03-01",
      AAPL: 190000,
      MSFT: 430000,
      GOOG: 172000,
      AMZN: 182000,
    },
    {
      date: "2025-03-02",
      AAPL: 187000,
      MSFT: 427000,
      GOOG: 169000,
      AMZN: 179000,
    },
    {
      date: "2025-03-03",
      AAPL: 192000,
      MSFT: 435000,
      GOOG: 170000,
      AMZN: 183000,
    },
    {
      date: "2025-03-04",
      AAPL: 196000,
      MSFT: 440000,
      GOOG: 175000,
      AMZN: 185000,
    },
    {
      date: "2025-03-05",
      AAPL: 198000,
      MSFT: 442000,
      GOOG: 176000,
      AMZN: 187000,
    },
    {
      date: "2025-03-06",
      AAPL: 201000,
      MSFT: 445000,
      GOOG: 178000,
      AMZN: 189000,
    },
    {
      date: "2025-03-07",
      AAPL: 203000,
      MSFT: 447000,
      GOOG: 177000,
      AMZN: 190000,
    },
    {
      date: "2025-03-08",
      AAPL: 200000,
      MSFT: 442000,
      GOOG: 174000,
      AMZN: 188000,
    },
    {
      date: "2025-03-09",
      AAPL: 204000,
      MSFT: 448000,
      GOOG: 176000,
      AMZN: 191000,
    },
    {
      date: "2025-03-10",
      AAPL: 205000,
      MSFT: 450000,
      GOOG: 178000,
      AMZN: 193000,
    },
  ];

  const sampleKeywordData = [
    { text: "AI", value: 100, sentiment: 0.8 },
    { text: "반도체", value: 85, sentiment: 0.6 },
    { text: "클라우드", value: 70, sentiment: 0.7 },
    { text: "자율주행", value: 65, sentiment: 0.5 },
    { text: "가상현실", value: 60, sentiment: 0.4 },
    { text: "블록체인", value: 55, sentiment: 0.2 },
    { text: "양자컴퓨팅", value: 50, sentiment: 0.3 },
    { text: "디지털전환", value: 48, sentiment: 0.4 },
    { text: "사이버보안", value: 45, sentiment: -0.1 },
    { text: "공급망", value: 43, sentiment: -0.2 },
    { text: "인플레이션", value: 40, sentiment: -0.5 },
    { text: "금리인상", value: 38, sentiment: -0.7 },
    { text: "규제", value: 35, sentiment: -0.6 },
    { text: "대체에너지", value: 34, sentiment: 0.3 },
    { text: "지속가능성", value: 33, sentiment: 0.4 },
  ];

  const sampleCorrelationData = [
    { date: "2025-03-01", price: 190000, sentiment: 0.4, volume: 2000000 },
    { date: "2025-03-02", price: 187000, sentiment: 0.3, volume: 1800000 },
    { date: "2025-03-03", price: 192000, sentiment: 0.5, volume: 2500000 },
    { date: "2025-03-04", price: 196000, sentiment: 0.6, volume: 2700000 },
    { date: "2025-03-05", price: 198000, sentiment: 0.7, volume: 3000000 },
    { date: "2025-03-06", price: 201000, sentiment: 0.8, volume: 3200000 },
    { date: "2025-03-07", price: 203000, sentiment: 0.7, volume: 2900000 },
    { date: "2025-03-08", price: 200000, sentiment: 0.5, volume: 2300000 },
    { date: "2025-03-09", price: 204000, sentiment: 0.6, volume: 2600000 },
    { date: "2025-03-10", price: 205000, sentiment: 0.7, volume: 2800000 },
  ];

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>대시보드</h1>
        <p className="welcome-message">
          안녕하세요, {user?.username || "사용자"}님!
        </p>
      </div>

      <div className="dashboard-content">
        <div className="dashboard-section">
          <div className="section-header">
            <h2>주요 지표</h2>
            <div className="period-selector">
              <button
                className={selectedPeriod === "1d" ? "active" : ""}
                onClick={() => handlePeriodChange("1d")}
              >
                1일
              </button>
              <button
                className={selectedPeriod === "1w" ? "active" : ""}
                onClick={() => handlePeriodChange("1w")}
              >
                1주
              </button>
              <button
                className={selectedPeriod === "1m" ? "active" : ""}
                onClick={() => handlePeriodChange("1m")}
              >
                1개월
              </button>
              <button
                className={selectedPeriod === "3m" ? "active" : ""}
                onClick={() => handlePeriodChange("3m")}
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
                <SentimentChart data={sampleSentimentData} />
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
                    <NewsCard key={news.id} article={news} />
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
              <StockPerformanceChart
                data={sampleStockPerformanceData}
                symbols={["AAPL", "MSFT", "GOOG", "AMZN"]}
              />
            )}
          </div>

          <div className="dashboard-section keyword-trends">
            <h2>인기 키워드</h2>
            <KeywordCloud data={sampleKeywordData} width={500} height={300} />
          </div>

          <div className="dashboard-section stock-sentiment-correlation">
            <h2>AAPL 주가-감성 상관관계</h2>
            <CorrelationChart
              data={sampleCorrelationData}
              symbol="AAPL"
              height={350}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
