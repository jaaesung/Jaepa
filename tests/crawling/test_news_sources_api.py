"""
뉴스 소스 핸들러 API 테스트 모듈

NewsSourcesHandler 클래스의 API 기능을 테스트합니다.
"""
import unittest
import sys
from datetime import datetime
from pathlib import Path
import json
from unittest.mock import patch, MagicMock
import requests

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parents[2]))

from crawling.news_sources_enhanced import NewsSourcesHandler


class TestNewsSourcesHandlerAPI(unittest.TestCase):
    """
    뉴스 소스 핸들러 API 테스트 클래스
    """
    
    def setUp(self):
        """
        테스트 설정
        """
        # MongoDB 연결 없이 핸들러 초기화
        self.handler = NewsSourcesHandler(db_connect=False)
        
        # 테스트 데이터 경로
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
    
    def test_initialization(self):
        """
        핸들러 초기화 테스트
        """
        self.assertIsNotNone(self.handler.config)
        self.assertIsNone(self.handler.client)  # db_connect=False로 설정했으므로
        self.assertIsNone(self.handler.db)
        self.assertIsNone(self.handler.news_collection)
    
    @patch.object(NewsSourcesHandler, '_format_finnhub_date')
    @patch('finnhub.Client')
    def test_get_news_from_finnhub(self, mock_client, mock_format_date):
        """
        Finnhub API에서 뉴스 가져오기 테스트
        """
        # 모의 응답 설정
        mock_news = [
            {
                "headline": "Test News 1",
                "summary": "This is a test news summary 1",
                "url": "https://example.com/news1",
                "datetime": 1680888600,
                "source": "Finnhub",
                "related": ["AAPL"],
                "category": "technology",
                "image": "https://example.com/image1.jpg"
            },
            {
                "headline": "Test News 2",
                "summary": "This is a test news summary 2",
                "url": "https://example.com/news2",
                "datetime": 1680892200,
                "source": "Finnhub",
                "related": ["TSLA"],
                "category": "automotive",
                "image": "https://example.com/image2.jpg"
            }
        ]
        
        # 날짜 포맷 모의 설정
        mock_format_date.side_effect = lambda timestamp: f"2023-04-08T{timestamp % 1000000:02d}:00:00"
        
        # Finnhub 클라이언트 모의 설정
        mock_finnhub = MagicMock()
        mock_finnhub.company_news.return_value = mock_news
        mock_finnhub.general_news.return_value = mock_news
        mock_client.return_value = mock_finnhub
        
        # API 키 설정
        self.handler.finnhub_api_key = "test_api_key"
        self.handler.finnhub_client = mock_finnhub
        
        # 심볼로 뉴스 가져오기
        news_by_symbol = self.handler.get_news_from_finnhub(symbol="AAPL", days=7)
        
        # 검증
        self.assertEqual(len(news_by_symbol), 2)
        self.assertEqual(news_by_symbol[0]["title"], "Test News 1")
        self.assertEqual(news_by_symbol[1]["title"], "Test News 2")
        mock_finnhub.company_news.assert_called_once()
        
        # 카테고리로 뉴스 가져오기
        mock_finnhub.company_news.reset_mock()
        news_by_category = self.handler.get_news_from_finnhub(category="general", days=7)
        
        # 검증
        self.assertEqual(len(news_by_category), 2)
        self.assertEqual(news_by_category[0]["title"], "Test News 1")
        self.assertEqual(news_by_category[1]["title"], "Test News 2")
        mock_finnhub.general_news.assert_called_once()
    
    @patch('requests.get')
    def test_get_news_from_newsdata(self, mock_get):
        """
        NewsData.io API에서 뉴스 가져오기 테스트
        """
        # 모의 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "totalResults": 2,
            "results": [
                {
                    "title": "Test News 1",
                    "description": "This is a test news summary 1",
                    "link": "https://example.com/news1",
                    "pubDate": "2023-04-08 10:30:00",
                    "source_id": "example",
                    "creator": ["John Doe"],
                    "category": ["business"],
                    "image_url": "https://example.com/image1.jpg",
                    "country": ["us"]
                },
                {
                    "title": "Test News 2",
                    "description": "This is a test news summary 2",
                    "link": "https://example.com/news2",
                    "pubDate": "2023-04-08 11:30:00",
                    "source_id": "example",
                    "creator": ["Jane Smith"],
                    "category": ["technology"],
                    "image_url": "https://example.com/image2.jpg",
                    "country": ["uk"]
                }
            ],
            "nextPage": None
        }
        mock_get.return_value = mock_response
        
        # API 키 설정
        self.handler.newsdata_api_key = "test_api_key"
        
        # 날짜 포맷 메서드 모킹
        with patch.object(self.handler, '_format_newsdata_date') as mock_format_date:
            mock_format_date.side_effect = lambda date_str: f"2023-04-08T{date_str[-8:-3].replace(':', '')}"
            
            # 뉴스 가져오기
            news = self.handler.get_news_from_newsdata(keyword="business", category="business", days=7)
            
            # 검증
            self.assertEqual(len(news), 2)
            self.assertEqual(news[0]["title"], "Test News 1")
            self.assertEqual(news[1]["title"], "Test News 2")
            mock_get.assert_called_once()
    
    @patch.object(NewsSourcesHandler, 'get_news_from_finnhub')
    @patch.object(NewsSourcesHandler, 'get_news_from_newsdata')
    @patch.object(NewsSourcesHandler, '_deduplicate_news')
    def test_get_combined_news(self, mock_deduplicate, mock_newsdata, mock_finnhub):
        """
        Finnhub와 NewsData.io에서 통합 뉴스 가져오기 테스트
        """
        # 모의 응답 설정
        finnhub_news = [
            {
                "title": "Finnhub News 1",
                "summary": "This is a test news summary 1",
                "url": "https://example.com/news1",
                "published_date": "2023-04-08T10:30:00",
                "source": "Finnhub",
                "source_type": "finnhub",
                "related_symbols": ["AAPL"],
                "categories": ["technology"],
                "keywords": ["apple", "tech"]
            }
        ]
        
        newsdata_news = [
            {
                "title": "NewsData News 1",
                "summary": "This is a test news summary 2",
                "url": "https://example.com/news2",
                "published_date": "2023-04-08T11:30:00",
                "source": "NewsData",
                "source_type": "newsdata",
                "creator": ["Jane Smith"],
                "categories": ["business"],
                "keywords": ["business", "finance"]
            }
        ]
        
        combined_news = finnhub_news + newsdata_news
        
        # 메서드 모킹
        mock_finnhub.return_value = finnhub_news
        mock_newsdata.return_value = newsdata_news
        mock_deduplicate.return_value = combined_news
        
        # API 키 설정
        self.handler.finnhub_api_key = "test_finnhub_key"
        self.handler.newsdata_api_key = "test_newsdata_key"
        self.handler.finnhub_client = MagicMock()
        
        # 통합 뉴스 가져오기
        news = self.handler.get_combined_news(keyword="AAPL", days=7, save_to_db=False)
        
        # 검증
        self.assertEqual(len(news), 2)
        self.assertEqual(news[0]["title"], "Finnhub News 1")
        self.assertEqual(news[1]["title"], "NewsData News 1")
        
        # 메서드 호출 확인
        mock_finnhub.assert_called_once_with(symbol="AAPL", days=7)
        mock_newsdata.assert_called_once_with(keyword="AAPL", category="business", days=7)
        mock_deduplicate.assert_called_once_with(finnhub_news + newsdata_news)
    
    def test_calculate_text_hash(self):
        """
        텍스트 해시값 계산 테스트
        """
        # 텍스트 해시값 계산
        text = "This is a test text"
        hash1 = self.handler._calculate_text_hash(text)
        
        # 다른 텍스트 해시값 계산
        different_text = "This is a different text"
        hash2 = self.handler._calculate_text_hash(different_text)
        
        # 검증
        self.assertIsInstance(hash1, str)
        self.assertNotEqual(hash1, hash2)
        
        # 동일 텍스트 해시값 계산
        hash3 = self.handler._calculate_text_hash(text)
        
        # 검증 - 동일 텍스트는 동일 해시값을 가져야 함
        self.assertEqual(hash1, hash3)
    
    def test_deduplicate_news(self):
        """
        뉴스 기사 중복 제거 테스트
        """
        # 테스트 기사 데이터
        articles = [
            {
                "title": "Test News 1",
                "summary": "This is a test news summary 1",
                "url": "https://example.com/news1",
                "published_date": "2023-04-08T10:30:00",
                "source": "Source A",
                "keywords": ["test", "news"]
            },
            {
                "title": "Test News 1",  # 제목 동일
                "summary": "This is a test news summary 1 with slight difference",
                "url": "https://example.com/news2",  # URL 다름
                "published_date": "2023-04-08T10:31:00",  # 1분 차이
                "source": "Source B",
                "keywords": ["test", "article"]
            },
            {
                "title": "Completely Different News",
                "summary": "This is a completely different news summary",
                "url": "https://example.com/news3",
                "published_date": "2023-04-08T11:30:00",
                "source": "Source A",
                "keywords": ["different", "news"]
            }
        ]
        
        # 중복 제거
        deduplicated = self.handler._deduplicate_news(articles, title_threshold=90, time_threshold=120)
        
        # 검증 - 첫 번째와 두 번째 기사는 유사하므로 하나로 통합되어야 함
        self.assertEqual(len(deduplicated), 2)
        
        # URL 기준으로 정렬
        sorted_results = sorted(deduplicated, key=lambda x: x["url"])
        
        # 첫 번째 기사는 source와 keywords가 병합되어야 함
        if "sources" in sorted_results[0]:
            self.assertTrue(len(sorted_results[0]["sources"]) >= 1)
        
        # 세 번째 기사는 그대로 유지되어야 함
        self.assertEqual(sorted_results[1]["title"], "Completely Different News")


if __name__ == "__main__":
    unittest.main()
