"""
개선된 뉴스 통합 시스템 테스트 모듈

개선된 여러 API 구성요소를 함께 테스트하는 통합 테스트를 수행합니다.
"""
import unittest
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging
from unittest.mock import patch, MagicMock, ANY

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parents[2]))

# 개선된 모듈 가져오기
from crawling.news_integrator_improved import NewsIntegrator
from crawling.news_crawler import NewsCrawler, SentimentAnalyzer
from crawling.news_sources_enhanced_improved import NewsSourcesHandler


class TestNewsIntegratorImproved(unittest.TestCase):
    """
    개선된 뉴스 통합 시스템 테스트 클래스
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
        
        # 감성 분석 모듈 모킹
        self.patch_tokenizer = patch('transformers.AutoTokenizer.from_pretrained')
        self.patch_model = patch('transformers.AutoModelForSequenceClassification.from_pretrained')
        
        self.mock_tokenizer = self.patch_tokenizer.start()
        self.mock_model = self.patch_model.start()
        
        # 모의 데이터 준비
        self.prepare_mock_data()
    
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
    
    def prepare_mock_data(self):
        """
        모의 데이터 준비
        """
        # RSS 피드 모의 응답 설정
        mock_feed = MagicMock()
        mock_entry = MagicMock()
        mock_entry.title = "RSS News: Bitcoin Market Update"
        mock_entry.link = "https://example.com/rss-bitcoin"
        mock_entry.summary = "A summary of the latest Bitcoin market movements."
        mock_entry.published_parsed = (2023, 4, 8, 10, 30, 0, 0, 0, 0)
        mock_feed.entries = [mock_entry]
        self.mock_feedparser.return_value = mock_feed
        
        # Finnhub 모의 응답 설정
        self.mock_finnhub_news = [
            {
                "headline": "Finnhub: Bitcoin Price Analysis",
                "summary": "Analysis of the recent Bitcoin price movements from Finnhub.",
                "url": "https://example.com/finnhub-bitcoin",
                "datetime": int(datetime.now().timestamp()),
                "source": "Finnhub Source",
                "related": ["BTC", "CRYPTO"],
                "category": "cryptocurrency",
                "image": "https://example.com/finnhub-image.jpg"
            }
        ]
        mock_finnhub_client = MagicMock()
        mock_finnhub_client.company_news.return_value = self.mock_finnhub_news
        mock_finnhub_client.general_news.return_value = self.mock_finnhub_news
        self.mock_finnhub.return_value = mock_finnhub_client
        
        # NewsData.io 모의 응답 설정
        self.mock_newsdata_response = {
            "status": "success",
            "totalResults": 1,
            "results": [
                {
                    "title": "NewsData: Latest on Bitcoin",
                    "description": "The latest developments in the Bitcoin world.",
                    "content": "Detailed content about Bitcoin's latest developments.",
                    "link": "https://example.com/newsdata-bitcoin",
                    "pubDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source_id": "NewsData Source",
                    "creator": ["NewsData Author"],
                    "category": ["cryptocurrency"],
                    "image_url": "https://example.com/newsdata-image.jpg",
                    "country": ["us"]
                }
            ],
            "nextPage": None
        }
        
        # requests.get 모의 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps(self.mock_newsdata_response)
        mock_response.content = b"<xml></xml>"
        self.mock_requests.return_value = mock_response
        
        # 감성 분석 결과 모의 설정
        self.mock_sentiment = {"positive": 0.6, "neutral": 0.3, "negative": 0.1}
    
    def test_integrator_initialization(self):
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
    @patch('crawling.news_sources_enhanced_improved.NewsSourcesHandler.search_news_with_apis')
    def test_collect_news_with_apis(self, mock_search_apis, mock_search_rss):
        """
        API 통합 검색 기능을 사용한 뉴스 수집 테스트
        """
        # 모의 응답 설정
        mock_search_rss.return_value = [
            {
                "title": "RSS Bitcoin News",
                "content": "RSS content about Bitcoin",
                "url": "https://example.com/rss-bitcoin",
                "published_date": "2023-04-08T10:30:00",
                "source": "RSS Source",
                "source_type": "rss",
                "keywords": ["bitcoin", "cryptocurrency"]
            }
        ]
        
        mock_search_apis.return_value = [
            {
                "title": "API Bitcoin News",
                "summary": "API summary about Bitcoin",
                "content": "API content about Bitcoin",
                "url": "https://example.com/api-bitcoin",
                "published_date": "2023-04-08T11:30:00",
                "source": "API Source",
                "source_type": "finnhub",
                "keywords": ["bitcoin", "market"]
            }
        ]
        
        # 감성 분석 모의 설정
        with patch('crawling.news_crawler.SentimentAnalyzer.analyze_batch') as mock_analyze_batch:
            mock_analyze_batch.return_value = [self.mock_sentiment, self.mock_sentiment]
            
            # 통합기 초기화 및 뉴스 수집
            integrator = NewsIntegrator(use_rss=True, use_finnhub=True, use_newsdata=True)
            
            # 중복 제거 함수 모킹
            with patch('crawling.news_sources_enhanced_improved.NewsSourcesHandler._deduplicate_news') as mock_deduplicate:
                # 중복 제거 함수가 입력을 그대로 반환하도록 설정
                mock_deduplicate.side_effect = lambda x: x
                
                # 뉴스 수집
                news = integrator.collect_news(keyword="bitcoin", days=7)
                
                # 검증
                self.assertEqual(len(news), 2)
                self.assertEqual(news[0]["title"], "RSS Bitcoin News")
                self.assertEqual(news[1]["title"], "API Bitcoin News")
                
                # API 호출 확인
                mock_search_rss.assert_called_once_with(keyword="bitcoin", days=7)
                mock_search_apis.assert_called_once_with("bitcoin", 7)
                mock_deduplicate.assert_called_once()
                mock_analyze_batch.assert_called_once()
                
                # 자원 정리
                integrator.close()
    
    @patch('crawling.news_crawler.NewsCrawler.search_news_from_rss')
    @patch('crawling.news_sources_enhanced_improved.NewsSourcesHandler.get_news_from_finnhub')
    @patch('crawling.news_sources_enhanced_improved.NewsSourcesHandler.get_news_from_newsdata')
    def test_collect_news_individual_apis(self, mock_newsdata, mock_finnhub, mock_search_rss):
        """
        개별 API를 사용한 뉴스 수집 테스트
        """
        # 모의 응답 설정
        mock_search_rss.return_value = [
            {
                "title": "RSS Bitcoin News",
                "content": "RSS content about Bitcoin",
                "url": "https://example.com/rss-bitcoin",
                "published_date": "2023-04-08T10:30:00",
                "source": "RSS Source",
                "source_type": "rss",
                "keywords": ["bitcoin", "cryptocurrency"]
            }
        ]
        
        mock_finnhub.return_value = [
            {
                "title": "Finnhub Bitcoin News",
                "summary": "Finnhub summary about Bitcoin",
                "content": "Finnhub content about Bitcoin",
                "url": "https://example.com/finnhub-bitcoin",
                "published_date": "2023-04-08T11:30:00",
                "source": "Finnhub",
                "source_type": "finnhub",
                "keywords": ["bitcoin", "market"]
            }
        ]
        
        mock_newsdata.return_value = [
            {
                "title": "NewsData Bitcoin News",
                "summary": "NewsData summary about Bitcoin",
                "content": "NewsData content about Bitcoin",
                "url": "https://example.com/newsdata-bitcoin",
                "published_date": "2023-04-08T12:30:00",
                "source": "NewsData",
                "source_type": "newsdata",
                "keywords": ["bitcoin", "technology"]
            }
        ]
        
        # 감성 분석 모의 설정
        with patch('crawling.news_crawler.SentimentAnalyzer.analyze_batch') as mock_analyze_batch:
            mock_analyze_batch.return_value = [self.mock_sentiment, self.mock_sentiment, self.mock_sentiment]
            
            # API 통합 검색 사용 안함
            with patch('crawling.news_sources_enhanced_improved.NewsSourcesHandler.search_news_with_apis') as mock_search_apis:
                mock_search_apis.return_value = []  # 통합 검색 사용 안함
                
                # 통합기 초기화 및 뉴스 수집
                integrator = NewsIntegrator(use_rss=True, use_finnhub=True, use_newsdata=True)
                
                # API 상태 강제 설정
                integrator.api_status = {"rss": True, "finnhub": True, "newsdata": True}
                
                # 중복 제거 함수 모킹
                with patch('crawling.news_sources_enhanced_improved.NewsSourcesHandler._deduplicate_news') as mock_deduplicate:
                    # 중복 제거 함수가 입력을 그대로 반환하도록 설정
                    mock_deduplicate.side_effect = lambda x: x
                    
                    # 뉴스 수집
                    news = integrator.collect_news(keyword=None, days=7)
                    
                    # 검증
                    self.assertEqual(len(news), 3)
                    
                    # API 호출 확인
                    mock_search_rss.assert_called_once()
                    mock_finnhub.assert_called_once()
                    mock_newsdata.assert_called_once()
                    mock_deduplicate.assert_called_once()
                    mock_analyze_batch.assert_called_once()
                    
                    # 자원 정리
                    integrator.close()
    
    def test_error_handling(self):
        """
        오류 처리 테스트
        """
        # RSS 피드 오류 설정
        with patch('crawling.news_crawler.NewsCrawler.search_news_from_rss') as mock_search_rss:
            mock_search_rss.side_effect = Exception("RSS 오류 발생")
            
            # Finnhub API 오류 설정
            with patch('crawling.news_sources_enhanced_improved.NewsSourcesHandler.get_news_from_finnhub') as mock_finnhub:
                mock_finnhub.side_effect = Exception("Finnhub 오류 발생")
                
                # NewsData.io API 오류 설정
                with patch('crawling.news_sources_enhanced_improved.NewsSourcesHandler.get_news_from_newsdata') as mock_newsdata:
                    mock_newsdata.side_effect = Exception("NewsData 오류 발생")
                    
                    # 통합 검색 오류 설정
                    with patch('crawling.news_sources_enhanced_improved.NewsSourcesHandler.search_news_with_apis') as mock_search_apis:
                        mock_search_apis.side_effect = Exception("통합 검색 오류 발생")
                        
                        # 통합기 초기화 및 뉴스 수집
                        integrator = NewsIntegrator(use_rss=True, use_finnhub=True, use_newsdata=True)
                        
                        # API 상태 강제 설정
                        integrator.api_status = {"rss": True, "finnhub": True, "newsdata": True}
                        
                        # 뉴스 수집 - 모든 API에서 오류가 발생해도 예외가 발생하지 않아야 함
                        news = integrator.collect_news(keyword="bitcoin", days=7)
                        
                        # 검증 - 빈 목록 반환
                        self.assertEqual(len(news), 0)
                        
                        # 자원 정리
                        integrator.close()
    
    def test_ensure_sentiment_analysis(self):
        """
        감성 분석 보장 기능 테스트
        """
        # 테스트용 가상 기사 생성
        test_articles = [
            {
                "title": "Article without Sentiment",
                "content": "This article has no sentiment analysis yet.",
                "url": "https://example.com/article1",
                "published_date": datetime.now().isoformat(),
                "source": "Test Source",
                "source_type": "test",
                "sentiment": None
            },
            {
                "title": "Article with Sentiment",
                "content": "This article already has sentiment analysis.",
                "url": "https://example.com/article2",
                "published_date": datetime.now().isoformat(),
                "source": "Test Source",
                "source_type": "test",
                "sentiment": {"positive": 0.2, "neutral": 0.7, "negative": 0.1}
            }
        ]
        
        # 감성 분석 모의 설정
        with patch('crawling.news_crawler.SentimentAnalyzer.analyze_batch') as mock_analyze_batch:
            mock_analyze_batch.return_value = [self.mock_sentiment]
            
            # 통합기 초기화
            integrator = NewsIntegrator(use_rss=True, use_finnhub=False, use_newsdata=False)
            
            # 감성 분석기 강제 설정
            integrator.rss_crawler.sentiment_analyzer = self.mock_tokenizer.return_value
            
            # 감성 분석 실행
            analyzed_articles = integrator._ensure_sentiment_analysis(test_articles)
            
            # 검증
            self.assertEqual(len(analyzed_articles), 2)
            
            # 첫 번째 기사: 감성 분석이 추가되어야 함
            self.assertIsNotNone(analyzed_articles[0]["sentiment"])
            self.assertEqual(analyzed_articles[0]["sentiment"], self.mock_sentiment)
            
            # 두 번째 기사: 이미 감성 분석이 있으므로 유지되어야 함
            self.assertEqual(analyzed_articles[1]["sentiment"]["positive"], 0.2)
            self.assertEqual(analyzed_articles[1]["sentiment"]["neutral"], 0.7)
            self.assertEqual(analyzed_articles[1]["sentiment"]["negative"], 0.1)
            
            # 자원 정리
            integrator.close()
    
    def test_end_to_end_flow(self):
        """
        전체 흐름 통합 테스트
        """
        # RSS 피드 모의 응답 설정
        with patch('crawling.news_crawler.NewsCrawler.search_news_from_rss') as mock_search_rss:
            mock_search_rss.return_value = [
                {
                    "title": "RSS News About Bitcoin",
                    "content": "RSS news content about Bitcoin",
                    "url": "https://example.com/rss-bitcoin",
                    "published_date": "2023-04-08T10:30:00",
                    "source": "RSS Source",
                    "source_type": "rss",
                    "keywords": ["bitcoin", "crypto"],
                    "sentiment": None
                }
            ]
            
            # API 통합 검색 모의 설정
            with patch('crawling.news_sources_enhanced_improved.NewsSourcesHandler.search_news_with_apis') as mock_search_apis:
                mock_search_apis.return_value = [
                    {
                        "title": "API News About Bitcoin",
                        "summary": "API news summary about Bitcoin",
                        "content": "API news content about Bitcoin",
                        "url": "https://example.com/api-bitcoin",
                        "published_date": "2023-04-08T11:30:00",
                        "source": "API Source",
                        "source_type": "finnhub",
                        "keywords": ["bitcoin", "market"],
                        "sentiment": None
                    }
                ]
                
                # 감성 분석 모의 설정
                with patch('crawling.news_crawler.SentimentAnalyzer.analyze_batch') as mock_analyze_batch:
                    mock_analyze_batch.return_value = [self.mock_sentiment, self.mock_sentiment]
                    
                    # MongoDB 저장 모의 설정
                    with patch('crawling.news_sources_enhanced_improved.NewsSourcesHandler._save_to_mongodb') as mock_save:
                        # 통합기 초기화 및 뉴스 수집
                        integrator = NewsIntegrator(use_rss=True, use_finnhub=True, use_newsdata=True)
                        
                        # 중복 제거 함수 모킹
                        with patch('crawling.news_sources_enhanced_improved.NewsSourcesHandler._deduplicate_news') as mock_deduplicate:
                            # 중복 제거 함수가 입력을 그대로 반환하도록 설정
                            mock_deduplicate.side_effect = lambda x: x
                            
                            # 뉴스 수집
                            news = integrator.collect_news(keyword="bitcoin", days=7)
                            
                            # 검증
                            self.assertEqual(len(news), 2)
                            self.assertEqual(news[0]["title"], "RSS News About Bitcoin")
                            self.assertEqual(news[1]["title"], "API News About Bitcoin")
                            
                            # API 호출 확인
                            mock_search_rss.assert_called_once()
                            mock_search_apis.assert_called_once()
                            mock_deduplicate.assert_called_once()
                            mock_analyze_batch.assert_called_once()
                            mock_save.assert_called_once()
                            
                            # 감성 분석 결과 확인
                            self.assertEqual(news[0]["sentiment"], self.mock_sentiment)
                            self.assertEqual(news[1]["sentiment"], self.mock_sentiment)
                            
                            # 자원 정리
                            integrator.close()


if __name__ == "__main__":
    unittest.main()
