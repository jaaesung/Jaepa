"""
뉴스 통합 시스템 통합 테스트 모듈

모든 API 구성요소를 함께 테스트하는 통합 테스트를 수행합니다.
"""
import unittest
import sys
from datetime import datetime
from pathlib import Path
import json
import logging
from unittest.mock import patch, MagicMock

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parents[2]))

from crawling.news_integrator import NewsIntegrator
from crawling.news_crawler import NewsCrawler, SentimentAnalyzer
from crawling.news_sources_enhanced import NewsSourcesHandler


class TestNewsIntegratorSystem(unittest.TestCase):
    """
    뉴스 통합 시스템 통합 테스트 클래스
    """
    
    @classmethod
    def setUpClass(cls):
        """
        테스트 클래스 셋업
        """
        # 로그 레벨 설정
        logging.basicConfig(level=logging.ERROR)
        
        # 테스트 데이터 경로
        cls.test_data_dir = Path(__file__).parent / "test_data"
        cls.test_data_dir.mkdir(exist_ok=True)
    
    def setUp(self):
        """
        테스트 설정
        """
        # 실제 API 호출을 피하기 위한 모킹
        self.patch_finnhub = patch('finnhub.Client')
        self.patch_mongodb = patch('pymongo.MongoClient')
        self.patch_requests = patch('requests.get')
        self.patch_feedparser = patch('feedparser.parse')
        
        self.mock_finnhub = self.patch_finnhub.start()
        self.mock_mongodb = self.patch_mongodb.start()
        self.mock_requests = self.patch_requests.start()
        self.mock_feedparser = self.patch_feedparser.start()
        
        # 응답 모의 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<xml></xml>"
        mock_response.json.return_value = {"status": "success", "results": []}
        self.mock_requests.return_value = mock_response
        
        # 감성 분석 모듈 모킹
        self.patch_tokenizer = patch('transformers.AutoTokenizer.from_pretrained')
        self.patch_model = patch('transformers.AutoModelForSequenceClassification.from_pretrained')
        
        self.mock_tokenizer = self.patch_tokenizer.start()
        self.mock_model = self.patch_model.start()
        
        # 피드파서 모의 설정
        mock_feed = MagicMock()
        mock_entry = MagicMock()
        mock_entry.title = "Test Feed Entry"
        mock_entry.link = "https://example.com/feed"
        mock_entry.summary = "Test feed summary"
        mock_entry.published_parsed = (2023, 4, 8, 10, 30, 0, 0, 0, 0)
        mock_feed.entries = [mock_entry]
        self.mock_feedparser.return_value = mock_feed
    
    def tearDown(self):
        """
        테스트 종료 처리
        """
        self.patch_finnhub.stop()
        self.patch_mongodb.stop()
        self.patch_requests.stop()
        self.patch_feedparser.stop()
        self.patch_tokenizer.stop()
        self.patch_model.stop()
    
    def test_full_integration_flow(self):
        """
        전체 통합 플로우 테스트
        """
        # RSS 피드 모의 응답 설정
        mock_rss_articles = [
            {
                "title": "RSS News Title",
                "content": "RSS news content",
                "url": "https://example.com/rss",
                "published_date": "2023-04-08T10:30:00",
                "source": "RSS Source",
                "source_type": "rss",
                "keywords": ["rss", "news"],
                "sentiment": None
            }
        ]
        
        # Finnhub 모의 응답 설정
        mock_finnhub_articles = [
            {
                "title": "Finnhub News Title",
                "summary": "Finnhub news summary",
                "content": "Finnhub news content",
                "url": "https://example.com/finnhub",
                "published_date": "2023-04-08T11:30:00",
                "source": "Finnhub Source",
                "source_type": "finnhub",
                "keywords": ["finnhub", "news"],
                "sentiment": None
            }
        ]
        
        # NewsData.io 모의 응답 설정
        mock_newsdata_articles = [
            {
                "title": "NewsData News Title",
                "summary": "NewsData news summary",
                "content": "NewsData news content",
                "url": "https://example.com/newsdata",
                "published_date": "2023-04-08T12:30:00",
                "source": "NewsData Source",
                "source_type": "newsdata",
                "keywords": ["newsdata", "news"],
                "sentiment": None
            }
        ]
        
        # 감성 분석 결과 모의 설정
        mock_sentiment = {"positive": 0.6, "neutral": 0.3, "negative": 0.1}
        
        # API 및 서비스 메서드 모킹
        with patch('crawling.news_crawler.NewsCrawler.search_news_from_rss') as mock_search_rss, \
             patch('crawling.news_sources_enhanced.NewsSourcesHandler.get_news_from_finnhub') as mock_finnhub_news, \
             patch('crawling.news_sources_enhanced.NewsSourcesHandler.get_news_from_newsdata') as mock_newsdata_news, \
             patch('crawling.news_crawler.SentimentAnalyzer.analyze_batch') as mock_analyze_batch:
            
            # 모의 응답 설정
            mock_search_rss.return_value = mock_rss_articles
            mock_finnhub_news.return_value = mock_finnhub_articles
            mock_newsdata_news.return_value = mock_newsdata_articles
            mock_analyze_batch.return_value = [mock_sentiment, mock_sentiment, mock_sentiment]
            
            # 통합기 초기화 및 뉴스 수집
            integrator = NewsIntegrator(use_rss=True, use_finnhub=True, use_newsdata=True)
            
            # API 호출
            news = integrator.collect_news(keyword="test", days=7)
            
            # 검증
            self.assertEqual(len(news), 3)  # 모든 소스의 기사 포함
            
            # 결과 저장 (디버깅 및 검증 목적)
            with open(self.test_data_dir / "full_integration_test_results.json", "w") as f:
                json.dump(news, f, indent=2, default=str)
            
            # API 호출 확인
            mock_search_rss.assert_called_once()
            mock_finnhub_news.assert_called_once()
            mock_newsdata_news.assert_called_once()
            mock_analyze_batch.assert_called_once()
            
            # 자원 정리
            integrator.close()
    
    def test_rss_only_flow(self):
        """
        RSS만 사용하는 통합 플로우 테스트
        """
        # RSS 피드 모의 응답 설정
        mock_rss_articles = [
            {
                "title": "RSS News 1",
                "content": "RSS news content 1",
                "url": "https://example.com/rss1",
                "published_date": "2023-04-08T10:30:00",
                "source": "RSS Source",
                "source_type": "rss",
                "keywords": ["rss", "news"],
                "sentiment": None
            },
            {
                "title": "RSS News 2",
                "content": "RSS news content 2",
                "url": "https://example.com/rss2",
                "published_date": "2023-04-08T11:30:00",
                "source": "RSS Source 2",
                "source_type": "rss",
                "keywords": ["rss", "article"],
                "sentiment": None
            }
        ]
        
        # 감성 분석 결과 모의 설정
        mock_sentiment = {"positive": 0.4, "neutral": 0.5, "negative": 0.1}
        
        # API 및 서비스 메서드 모킹
        with patch('crawling.news_crawler.NewsCrawler.search_news_from_rss') as mock_search_rss, \
             patch('crawling.news_crawler.SentimentAnalyzer.analyze_batch') as mock_analyze_batch:
            
            # 모의 응답 설정
            mock_search_rss.return_value = mock_rss_articles
            mock_analyze_batch.return_value = [mock_sentiment, mock_sentiment]
            
            # RSS만 사용하는 통합기 초기화 및 뉴스 수집
            integrator = NewsIntegrator(use_rss=True, use_finnhub=False, use_newsdata=False)
            
            # API 호출
            news = integrator.collect_news(keyword="test", days=7)
            
            # 검증
            self.assertEqual(len(news), 2)  # RSS 기사만 포함
            
            # 감성 분석 확인
            self.assertIn("sentiment", news[0])
            self.assertIn("sentiment", news[1])
            self.assertEqual(news[0]["sentiment"], mock_sentiment)
            self.assertEqual(news[1]["sentiment"], mock_sentiment)
            
            # API 호출 확인
            mock_search_rss.assert_called_once()
            mock_analyze_batch.assert_called_once()
            
            # 자원 정리
            integrator.close()
    
    def test_api_only_flow(self):
        """
        API만 사용하는 통합 플로우 테스트
        """
        # Finnhub 모의 응답 설정
        mock_finnhub_articles = [
            {
                "title": "Finnhub News",
                "summary": "Finnhub news summary",
                "content": "Finnhub news content",
                "url": "https://example.com/finnhub",
                "published_date": "2023-04-08T11:30:00",
                "source": "Finnhub Source",
                "source_type": "finnhub",
                "keywords": ["finnhub", "news"],
                "sentiment": None
            }
        ]
        
        # NewsData.io 모의 응답 설정
        mock_newsdata_articles = [
            {
                "title": "NewsData News",
                "summary": "NewsData news summary",
                "content": "NewsData news content",
                "url": "https://example.com/newsdata",
                "published_date": "2023-04-08T12:30:00",
                "source": "NewsData Source",
                "source_type": "newsdata",
                "keywords": ["newsdata", "news"],
                "sentiment": None
            }
        ]
        
        # 감성 분석 결과 모의 설정
        mock_sentiment = {"positive": 0.6, "neutral": 0.3, "negative": 0.1}
        
        # API 및 서비스 메서드 모킹
        with patch('crawling.news_sources_enhanced.NewsSourcesHandler.get_news_from_finnhub') as mock_finnhub_news, \
             patch('crawling.news_sources_enhanced.NewsSourcesHandler.get_news_from_newsdata') as mock_newsdata_news, \
             patch('crawling.news_crawler.SentimentAnalyzer.analyze_batch') as mock_analyze_batch:
            
            # 모의 응답 설정
            mock_finnhub_news.return_value = mock_finnhub_articles
            mock_newsdata_news.return_value = mock_newsdata_articles
            mock_analyze_batch.return_value = [mock_sentiment, mock_sentiment]
            
            # API만 사용하는 통합기 초기화 및 뉴스 수집
            integrator = NewsIntegrator(use_rss=False, use_finnhub=True, use_newsdata=True)
            
            # API 호출
            news = integrator.collect_news(keyword="test", days=7)
            
            # 검증
            self.assertEqual(len(news), 2)  # API 기사만 포함
            
            # 감성 분석 확인
            self.assertIn("sentiment", news[0])
            self.assertIn("sentiment", news[1])
            self.assertEqual(news[0]["sentiment"], mock_sentiment)
            self.assertEqual(news[1]["sentiment"], mock_sentiment)
            
            # API 호출 확인
            mock_finnhub_news.assert_called_once()
            mock_newsdata_news.assert_called_once()
            mock_analyze_batch.assert_called_once()
            
            # 자원 정리
            integrator.close()
    
    def test_deduplication_flow(self):
        """
        중복 제거 플로우 테스트
        """
        # 중복 기사가 포함된 테스트 데이터
        duplicate_articles = [
            # 기사 1
            {
                "title": "Test News Title",
                "content": "Test news content",
                "url": "https://example.com/test1",
                "published_date": "2023-04-08T10:30:00",
                "source": "Source A",
                "source_type": "rss",
                "keywords": ["test", "news"],
                "sentiment": None
            },
            # 기사 2 (기사 1과 제목 유사)
            {
                "title": "Test News Title Update",
                "summary": "Test news content updated",
                "content": "Test news content updated",
                "url": "https://example.com/test2",
                "published_date": "2023-04-08T10:35:00",
                "source": "Source B",
                "source_type": "finnhub",
                "keywords": ["test", "update"],
                "sentiment": None
            },
            # 기사 3 (완전히 다른 내용)
            {
                "title": "Different News Title",
                "content": "Different news content",
                "url": "https://example.com/different",
                "published_date": "2023-04-08T11:30:00",
                "source": "Source C",
                "source_type": "newsdata",
                "keywords": ["different", "news"],
                "sentiment": None
            }
        ]
        
        # 감성 분석 결과 모의 설정
        mock_sentiment = {"positive": 0.5, "neutral": 0.3, "negative": 0.2}
        
        # API 및 서비스 메서드 모킹
        with patch('crawling.news_crawler.NewsCrawler.search_news_from_rss') as mock_search_rss, \
             patch('crawling.news_sources_enhanced.NewsSourcesHandler.get_combined_news') as mock_combined_news, \
             patch('crawling.news_sources_enhanced.NewsSourcesHandler._deduplicate_news') as mock_deduplicate, \
             patch('crawling.news_crawler.SentimentAnalyzer.analyze_batch') as mock_analyze_batch:
            
            # 모의 응답 설정
            mock_search_rss.return_value = [duplicate_articles[0]]
            mock_combined_news.return_value = [duplicate_articles[1], duplicate_articles[2]]
            
            # 중복 제거 모의 설정 (첫 번째와 세 번째 기사만 남김)
            mock_deduplicate.return_value = [duplicate_articles[0], duplicate_articles[2]]
            
            # 감성 분석 모의 설정
            mock_analyze_batch.return_value = [mock_sentiment, mock_sentiment]
            
            # 통합기 초기화 및 뉴스 수집
            integrator = NewsIntegrator(use_rss=True, use_finnhub=True, use_newsdata=True)
            
            # API 호출
            news = integrator.collect_news(keyword="test", days=7)
            
            # 검증
            self.assertEqual(len(news), 2)  # 중복 제거 후 2개 기사만 남아야 함
            
            # 남은 기사 확인
            self.assertEqual(news[0]["title"], "Test News Title")
            self.assertEqual(news[1]["title"], "Different News Title")
            
            # API 호출 확인
            mock_search_rss.assert_called_once()
            mock_combined_news.assert_called_once()
            mock_deduplicate.assert_called_once()
            mock_analyze_batch.assert_called_once()
            
            # 자원 정리
            integrator.close()


if __name__ == "__main__":
    unittest.main()
