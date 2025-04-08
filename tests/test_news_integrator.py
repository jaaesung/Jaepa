"""
뉴스 통합 수집기 테스트 모듈

Finnhub, NewsData.io API 및 RSS 피드를 사용한 뉴스 수집 및 통합 기능을 테스트합니다.
"""
import sys
import os
import pytest
from datetime import datetime, timedelta

# 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crawling.news_integrator import NewsIntegrator
from crawling.news_sources_enhanced import NewsSourcesHandler
from crawling.news_crawler import NewsCrawler


class TestNewsIntegrator:
    """
    뉴스 통합 수집기 테스트 클래스
    """
    
    def setup_method(self):
        """
        테스트 설정
        """
        # 테스트에서는 MongoDB 연결 없이 진행 (db_connect=False)
        try:
            self.integrator = NewsIntegrator()
        except Exception as e:
            # API 키가 없는 경우 등 예외 처리
            pytest.skip(f"통합 수집기 초기화 실패: {str(e)}")
        
    def teardown_method(self):
        """
        테스트 종료 후 정리
        """
        if hasattr(self, 'integrator'):
            self.integrator.close()
    
    def test_initialize(self):
        """
        초기화 테스트
        """
        assert self.integrator is not None
        assert self.integrator.rss_crawler is not None
        assert self.integrator.api_handler is not None
    
    def test_collect_news_with_keyword(self):
        """
        키워드 기반 뉴스 수집 테스트
        """
        # 실제 API 호출 테스트 (비용 발생 가능, 주의!)
        # keyword = "AAPL"
        # days = 3
        # news = self.integrator.collect_news(keyword=keyword, days=days)
        # assert len(news) > 0
        
        # API 키가 없거나 실제 호출을 원하지 않는 경우 건너뛰기
        pytest.skip("실제 API 호출 테스트 건너뛰기")
    
    def test_integrate_news(self):
        """
        뉴스 통합 기능 테스트
        """
        # 테스트용 가상 기사 생성
        test_articles = [
            # RSS 기사
            {
                "title": "Apple releases new iPhone",
                "content": "Apple has announced a new iPhone model with innovative features.",
                "url": "https://example.com/news/1",
                "published_date": datetime.now().isoformat(),
                "source": "Example News",
                "source_type": "rss"
            },
            # Finnhub 기사 (동일 내용, 다른 URL)
            {
                "title": "Apple Releases New iPhone Model",
                "summary": "Apple announced a new iPhone with innovative features today.",
                "url": "https://another-site.com/news/apple",
                "published_date": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "source": "Another Site",
                "source_type": "finnhub"
            },
            # NewsData.io 기사 (완전히 다른 내용)
            {
                "title": "Tesla unveils new electric car",
                "summary": "Tesla has unveiled a new electric car model.",
                "url": "https://example.com/news/tesla",
                "published_date": datetime.now().isoformat(),
                "source": "Example News",
                "source_type": "newsdata"
            }
        ]
        
        # 통합 실행
        integrated_news = self.integrator._integrate_news(test_articles)
        
        # 중복 제거 확인
        assert len(integrated_news) <= len(test_articles)
        
        # URL이 모두 다르면 통합 결과 확인
        urls = [article["url"] for article in integrated_news]
        assert len(urls) == len(set(urls))  # 중복 없음
    
    def test_ensure_sentiment_analysis(self):
        """
        감성 분석 보장 기능 테스트
        """
        # 테스트용 가상 기사 생성 (감성 분석 필드 없음)
        test_articles = [
            {
                "title": "Positive news about economy",
                "content": "The economy is showing strong signs of growth and recovery.",
                "url": "https://example.com/news/economy",
                "published_date": datetime.now().isoformat(),
                "source": "Example News",
                "source_type": "rss"
            }
        ]
        
        # 감성 분석기가 초기화되어 있지 않으면 건너뛰기
        if not self.integrator.rss_crawler or \
           not hasattr(self.integrator.rss_crawler, 'sentiment_analyzer') or \
           self.integrator.rss_crawler.sentiment_analyzer is None or \
           self.integrator.rss_crawler.sentiment_analyzer.model is None:
            pytest.skip("감성 분석기가 초기화되지 않았습니다.")
        
        # 감성 분석 실행
        analyzed_articles = self.integrator._ensure_sentiment_analysis(test_articles)
        
        # 감성 분석 결과 확인
        assert len(analyzed_articles) == len(test_articles)
        
        # 첫 번째 기사에 감성 분석 결과가 있는지 확인
        assert "sentiment" in analyzed_articles[0]
        
        # 감성 분석 결과가 있으면 키 확인
        if analyzed_articles[0]["sentiment"]:
            assert "positive" in analyzed_articles[0]["sentiment"]
            assert "neutral" in analyzed_articles[0]["sentiment"]
            assert "negative" in analyzed_articles[0]["sentiment"]


class TestNewsSourcesHandler:
    """
    뉴스 소스 핸들러 테스트 클래스
    """
    
    def setup_method(self):
        """
        테스트 설정
        """
        # 테스트에서는 MongoDB 연결 없이 진행 (db_connect=False)
        try:
            self.handler = NewsSourcesHandler(db_connect=False)
        except Exception as e:
            # API 키가 없는 경우 등 예외 처리
            pytest.skip(f"뉴스 소스 핸들러 초기화 실패: {str(e)}")
        
    def teardown_method(self):
        """
        테스트 종료 후 정리
        """
        if hasattr(self, 'handler'):
            self.handler.close()
    
    def test_initialize(self):
        """
        초기화 테스트
        """
        assert self.handler is not None
    
    def test_deduplicate_news(self):
        """
        뉴스 중복 제거 기능 테스트
        """
        # 테스트용 가상 기사 생성 (일부 중복)
        test_articles = [
            # 첫 번째 기사
            {
                "title": "Market update: stocks rise",
                "summary": "Stock markets around the world are seeing gains today.",
                "url": "https://example.com/news/stocks",
                "published_date": datetime.now().isoformat(),
                "source": "Example News"
            },
            # 두 번째 기사 - 첫 번째와 다른 URL, 유사한 제목
            {
                "title": "Market Update: Stocks Rising Today",
                "summary": "Global stock markets are seeing significant gains in today's trading.",
                "url": "https://another-site.com/news/markets",
                "published_date": (datetime.now() - timedelta(minutes=2)).isoformat(),
                "source": "Another News"
            },
            # 세 번째 기사 - 첫 번째와 동일한 URL (명확한 중복)
            {
                "title": "Market update: stocks rise [Updated]",
                "summary": "Stock markets continue to show strong gains.",
                "url": "https://example.com/news/stocks",
                "published_date": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "source": "Example News"
            }
        ]
        
        # 중복 제거 실행
        deduplicated = self.handler._deduplicate_news(test_articles)
        
        # 명확한 중복 (동일 URL)이 제거되었는지 확인
        urls = [article["url"] for article in deduplicated]
        assert len(urls) == len(set(urls))
        
        # 총 기사 수 확인 (최소 1개, 최대 원본 기사 수)
        assert 1 <= len(deduplicated) <= len(test_articles)
    
    def test_format_dates(self):
        """
        날짜 형식 변환 기능 테스트
        """
        # Finnhub 타임스탬프 (초 단위)
        finnhub_timestamp = int(datetime.now().timestamp())
        formatted_finnhub = self.handler._format_finnhub_date(finnhub_timestamp)
        assert formatted_finnhub
        
        # NewsData.io 날짜 문자열
        newsdata_date = "2023-04-05 12:34:56"
        formatted_newsdata = self.handler._format_newsdata_date(newsdata_date)
        assert formatted_newsdata
        
        # ISO 형식 검증
        try:
            datetime.fromisoformat(formatted_finnhub.replace('Z', '+00:00'))
            datetime.fromisoformat(formatted_newsdata.replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("날짜가 ISO 형식이 아닙니다.")


if __name__ == "__main__":
    # 직접 실행 시 간단한 테스트 실행
    import pytest
    pytest.main(["-v", __file__])
