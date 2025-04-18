/**
 * 대시보드 페이지 컴포넌트
 *
 * 사용자 대시보드를 제공합니다.
 */

import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { MainLayout } from "../../components/layout";
import { Card, Button } from "../../components/ui";
import { useAuth } from "../../features/auth";
import { useNews } from "../../features/news";
import { useSentiment } from "../../features/sentiment-analysis";
import { useStock } from "../../features/stock";
import { SentimentTrendChart } from "../../features/sentiment-analysis";
import { StockChart } from "../../features/stock";
import { NewsCard } from "../../features/news";
import "./DashboardPage.css";

/**
 * 대시보드 페이지 컴포넌트
 */
const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const { getNews, articles } = useNews();
  const { getTrend } = useSentiment();
  const { getPopularStocks, popularStocks } = useStock();
  const [isLoading, setIsLoading] = useState(true);
  const [stockSymbol, setStockSymbol] = useState("AAPL");

  // 대시보드 데이터 로드
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        // 뉴스 데이터 로드
        await getNews({ page: 1, limit: 4 });

        // 감성 트렌드 데이터 로드
        const endDate = new Date().toISOString().split("T")[0];
        const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split("T")[0];
        await getTrend({ startDate, endDate, interval: "day" });

        // 인기 주식 데이터 로드
        await getPopularStocks();

        setIsLoading(false);
      } catch (error) {
        console.error("대시보드 데이터 로드 오류:", error);
        setIsLoading(false);
      }
    };

    loadDashboardData();
  }, [getNews, getTrend, getPopularStocks]);

  return (
    <MainLayout>
      <div className="dashboard-page">
        <div className="dashboard-header">
          <h1 className="dashboard-title">대시보드</h1>
          <p className="dashboard-welcome">
            안녕하세요, {user?.name || "사용자"}님! 오늘의 금융 인사이트를
            확인하세요.
          </p>
        </div>

        <div className="dashboard-content">
          {isLoading ? (
            <div className="dashboard-loading">
              <div className="spinner"></div>
              <p>데이터를 불러오는 중입니다...</p>
            </div>
          ) : (
            <>
              <div className="dashboard-summary">
                <Card className="summary-card">
                  <div className="summary-icon">📰</div>
                  <div className="summary-content">
                    <h3 className="summary-title">수집된 뉴스</h3>
                    <p className="summary-value">1,234</p>
                    <p className="summary-change positive">+12% 증가</p>
                  </div>
                </Card>

                <Card className="summary-card">
                  <div className="summary-icon">📈</div>
                  <div className="summary-content">
                    <h3 className="summary-title">분석된 주식</h3>
                    <p className="summary-value">567</p>
                    <p className="summary-change positive">+5% 증가</p>
                  </div>
                </Card>

                <Card className="summary-card">
                  <div className="summary-icon">😊</div>
                  <div className="summary-content">
                    <h3 className="summary-title">긍정적 감성</h3>
                    <p className="summary-value">45%</p>
                    <p className="summary-change negative">-3% 감소</p>
                  </div>
                </Card>

                <Card className="summary-card">
                  <div className="summary-icon">😔</div>
                  <div className="summary-content">
                    <h3 className="summary-title">부정적 감성</h3>
                    <p className="summary-value">32%</p>
                    <p className="summary-change positive">-2% 감소</p>
                  </div>
                </Card>
              </div>

              <div className="dashboard-charts">
                <Card className="chart-card">
                  <div className="chart-header">
                    <h3 className="chart-title">감성 트렌드</h3>
                    <Link to="/sentiment-analysis" className="chart-link">
                      더 보기
                    </Link>
                  </div>
                  <SentimentTrendChart height={250} />
                </Card>

                <Card className="chart-card">
                  <div className="chart-header">
                    <h3 className="chart-title">주식 차트</h3>
                    <Link
                      to={`/stock-analysis/${stockSymbol}`}
                      className="chart-link"
                    >
                      더 보기
                    </Link>
                  </div>
                  <StockChart symbol={stockSymbol} height={250} />
                </Card>
              </div>

              <div className="dashboard-recent">
                <Card className="recent-card">
                  <div className="chart-header">
                    <h3 className="recent-title">최근 뉴스</h3>
                    <Link to="/news-analysis" className="chart-link">
                      더 보기
                    </Link>
                  </div>

                  <div className="recent-list">
                    {articles && articles.length > 0 ? (
                      articles.map((article) => (
                        <div key={article.id} className="dashboard-news-item">
                          <NewsCard article={article} />
                        </div>
                      ))
                    ) : (
                      <div className="dashboard-news-empty">
                        <p>표시할 뉴스가 없습니다.</p>
                      </div>
                    )}
                  </div>

                  <div className="dashboard-actions">
                    <Button
                      variant="outline"
                      onClick={() => window.open("/news-analysis", "_self")}
                    >
                      모든 뉴스 보기
                    </Button>
                  </div>
                </Card>
              </div>
            </>
          )}
        </div>
      </div>
    </MainLayout>
  );
};

export default DashboardPage;
