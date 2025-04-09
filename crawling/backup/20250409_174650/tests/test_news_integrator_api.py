"""
뉴스 통합 API 테스트 모듈

NewsIntegrator 클래스의 API 기능을 테스트합니다.
"""
import unittest
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import json
from unittest.mock import patch, MagicMock

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parents[2]))

from crawling.news_integrator import NewsIntegrator
from crawling.news_crawler import NewsCrawler
from crawling.news_sources_enhanced import NewsSourcesHandler


class TestNewsIntegratorAPI(unittest.TestCase):
    """
    뉴스 통합 API 테스트 클래스
    """
    
    def setUp(self):
        """
        테스트 설정
        """
        # 테스트 데이터 경로
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        
        # MongoDB 및 API 클라이언트 모킹
        self.patch_mongodb = patch('pymongo.MongoClient')
        self.patch_finnhub = patch('finnhub.Client')
        self.patch_sentiment = patch('crawling.news_crawler.SentimentAnalyzer')
        
        self.mock_mongodb = self.patch_mongodb.start()
        self.mock_finnhub = self.patch_finnhub.start()
        self.mock_sentiment = self.patch_sentiment.start()
    
    def tearDown(self):
        """
        테스트 종료 후 정리
        """
        self.patch_mongodb.stop()
        self.patch_finnhub.stop()
        self.patch_sentiment.stop()
    
    def test_initialize_integrator(self):
        """
        통합기 초기화 테스트
        """
        # 다양한 설정으로 초기화
        integrator1 = NewsIntegrator(use_rss=True, use_finnhub=True, use_newsdata=True)
        integrator2 = NewsIntegrator(use_rss=True, use_finnhub=False, use_newsdata=False)
        integrator3 = NewsIntegrator(use_rss=False, use_finnhub=True, use_newsdata=True)
        
        # 검증
        self.assertIsNotNone(integrator1.rss_crawler)
        self.assertIsNotNone(integrator1.api_handler)
        
        self.assertIsNotNone(integrator2.rss_crawler)
        self.assertIsNone(integrator2.api_handler)
        
        self.assertIsNone(integrator3.rss_crawler)
        self.assertIsNotNone(integrator3.api_handler)
        
        # 자원 정리
        integrator1.close()
        integrator2.close()
        integrator3.close()
    
    @patch('crawling.news_crawler.NewsCrawler.search_news_from_rss')
    @patch('crawling.news_sources_enhanced.NewsSourcesHandler.get_combined_news')
    def test_collect_news(self, mock_combined_news, mock_search_rss):
        """
        통합 뉴스 수집 테스트
        """
        # 모의 응답 설정
        rss_news = [
            {
                "title": "RSS News",
                "content": "RSS news content",
                "url": "https://example.com/rss",
                "published_date": "2023-04-08T10:30:00",
                "source": "RSS Source",
                "source_type": "rss",
                "keywords": ["bitcoin", "crypto"],
                "sentiment": None
            }
        ]
        
        api_news = [
            {
                "title": "API News",
                "summary": "API news summary",
                "content": "API news content",
                "url": "https://example.com/api",
                "published_date": "2023-04-08T11:30:00",
                "source": "API Source",
                "source_type": "finnhub",
                "keywords": ["bitcoin", "market"],
                "sentiment": None
            }
        ]
        
        mock_search_rss.return_value = rss_news
        mock_combined_news.return_value = api_news
        
        # 감성 분석 모의 설정
        mock_sentiment_analyze = MagicMock()
        mock_sentiment_analyze.return_value = {"positive": 0.6, "neutral": 0.3, "negative": 0.1}
        self.mock_sentiment.return_value.analyze = mock_sentiment_analyze
        self.mock_sentiment.return_value.analyze_batch = MagicMock(return_value=[mock_sentiment_analyze.return_value])
        
        # 통합기 초기화 및 뉴스 수집
        integrator = NewsIntegrator(use_rss=True, use_finnhub=True, use_newsdata=True)
        
        # 중복 제거 함수 모킹
        with patch('crawling.news_sources_enhanced.NewsSourcesHandler._deduplicate_news') as mock_deduplicate:
            # 모든 기사 유지 (중복 제거 없음)
            mock_deduplicate.side_effect = lambda x: x
            
            # API 호출
            news = integrator.collect_news(keyword="bitcoin", days=7)
            
            # 검증
            self.assertEqual(len(news), 2)  # RSS와 API 뉴스 모두 포함
            self.assertEqual(news[0]["title"], "RSS News")
            self.assertEqual(news[1]["title"], "API News")
            
            # API 호출 확인
            mock_search_rss.assert_called_once_with(keyword="bitcoin", days=7)
            mock_combined_news.assert_called_once_with(keyword="bitcoin", days=7, save_to_db=False)
        
        # 자원 정리
        integrator.close()
    
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
            # Finnhub 기사 (다른 내용)
            {
                "title": "Apple Releases New iPhone Model",
                "summary": "Apple announced a new iPhone with innovative features today.",
                "url": "https://another-site.com/news/apple",
                "published_date": datetime.now().isoformat(),
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
        
        # 통합기 초기화
        integrator = NewsIntegrator(use_rss=True, use_finnhub=True, use_newsdata=True)
        
        # 중복 제거 함수 모킹
        with patch('crawling.news_sources_enhanced.NewsSourcesHandler._deduplicate_news') as mock_deduplicate:
            # 중복 제거 후 결과 (여기서는 테스트를 위해 원본 유지)
            mock_deduplicate.return_value = test_articles
            
            # 통합 실행
            integrated_news = integrator._integrate_news(test_articles)
            
            # 검증
            self.assertEqual(len(integrated_news), 3)
            
            # 필드 정규화 검증
            for article in integrated_news:
                self.assertIn("title", article)
                self.assertIn("content", article)
                self.assertIn("url", article)
                self.assertIn("published_date", article)
                self.assertIn("source", article)
                self.assertIn("source_type", article)
                self.assertIn("crawled_date", article)
                self.assertIn("keywords", article)
                self.assertIn("sentiment", article)
        
        # 자원 정리
        integrator.close()
    
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
            },
            {
                "title": "Negative news about market",
                "content": "Markets experienced significant downturn due to economic concerns.",
                "url": "https://example.com/news/market",
                "published_date": datetime.now().isoformat(),
                "source": "Example News",
                "source_type": "rss",
                "sentiment": {"positive": 0.1, "neutral": 0.2, "negative": 0.7}  # 이미 감성 분석이 있음
            }
        ]
        
        # 감성 분석 모의 설정
        mock_sentiment_analyze = MagicMock()
        mock_sentiment_analyze.return_value = {"positive": 0.6, "neutral": 0.3, "negative": 0.1}
        self.mock_sentiment.return_value.analyze = mock_sentiment_analyze
        self.mock_sentiment.return_value.analyze_batch = MagicMock(return_value=[mock_sentiment_analyze.return_value])
        
        # 통합기 초기화
        integrator = NewsIntegrator(use_rss=True, use_finnhub=False, use_newsdata=False)
        
        # RSS 크롤러 감성 분석기 설정
        integrator.rss_crawler.sentiment_analyzer = self.mock_sentiment.return_value
        
        # 감성 분석 실행
        analyzed_articles = integrator._ensure_sentiment_analysis(test_articles)
        
        # 검증
        self.assertEqual(len(analyzed_articles), 2)
        
        # 첫 번째 기사: 감성 분석이 추가되어야 함
        self.assertIn("sentiment", analyzed_articles[0])
        self.assertEqual(analyzed_articles[0]["sentiment"]["positive"], 0.6)
        self.assertEqual(analyzed_articles[0]["sentiment"]["neutral"], 0.3)
        self.assertEqual(analyzed_articles[0]["sentiment"]["negative"], 0.1)
        
        # 두 번째 기사: 이미 감성 분석이 있으므로 유지되어야 함
        self.assertIn("sentiment", analyzed_articles[1])
        self.assertEqual(analyzed_articles[1]["sentiment"]["positive"], 0.1)
        self.assertEqual(analyzed_articles[1]["sentiment"]["neutral"], 0.2)
        self.assertEqual(analyzed_articles[1]["sentiment"]["negative"], 0.7)
        
        # 자원 정리
        integrator.close()
    
    def test_error_handling(self):
        """
        오류 처리 테스트
        """
        # API 예외 발생 모의 설정
        with patch('crawling.news_crawler.NewsCrawler.search_news_from_rss') as mock_search_rss:
            mock_search_rss.side_effect = Exception("API 호출 실패")
            
            # 통합기 초기화 및 뉴스 수집
            integrator = NewsIntegrator(use_rss=True, use_finnhub=False, use_newsdata=False)
            
            # API 호출 - 예외가 발생해도 계속 진행되어야 함
            news = integrator.collect_news(keyword="bitcoin", days=7)
            
            # 검증 - 빈 목록 반환
            self.assertEqual(len(news), 0)
            
            # 자원 정리
            integrator.close()


if __name__ == "__main__":
    unittest.main()
