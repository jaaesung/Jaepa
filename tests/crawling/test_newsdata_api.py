"""
NewsData.io API 테스트 모듈

NewsSourcesHandler 클래스의 NewsData.io API 기능을 테스트합니다.
"""
import unittest
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock
import requests

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parents[2]))

from crawling.news_sources_enhanced import NewsSourcesHandler


class TestNewsDataAPI(unittest.TestCase):
    """
    NewsData.io API 테스트 클래스
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
    
    def tearDown(self):
        """
        테스트 종료 후 정리
        """
        self.handler.close()
    
    def test_format_newsdata_date(self):
        """
        NewsData.io 날짜 형식 변환 테스트
        """
        # 테스트 날짜 문자열
        test_date = "2023-04-08 10:30:00"
        
        # 변환 실행
        formatted_date = self.handler._format_newsdata_date(test_date)
        
        # 검증 - ISO 형식인지 확인
        self.assertIsInstance(formatted_date, str)
        try:
            datetime.fromisoformat(formatted_date)
        except ValueError:
            self.fail("날짜가 ISO 형식이 아닙니다.")
    
    @patch('requests.get')
    def test_get_news_from_newsdata_keyword(self, mock_get):
        """
        NewsData.io API에서 키워드로 뉴스 가져오기 테스트
        """
        # 모의 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "totalResults": 2,
            "results": [
                {
                    "title": "Bitcoin News 1",
                    "description": "This is a Bitcoin news summary 1",
                    "link": "https://example.com/bitcoin1",
                    "pubDate": "2023-04-08 10:30:00",
                    "source_id": "example",
                    "creator": ["John Doe"],
                    "category": ["business", "cryptocurrency"],
                    "image_url": "https://example.com/image1.jpg",
                    "country": ["us"]
                },
                {
                    "title": "Bitcoin News 2",
                    "description": "This is a Bitcoin news summary 2",
                    "link": "https://example.com/bitcoin2",
                    "pubDate": "2023-04-08 11:30:00",
                    "source_id": "example",
                    "creator": ["Jane Smith"],
                    "category": ["technology", "cryptocurrency"],
                    "image_url": "https://example.com/image2.jpg",
                    "country": ["uk"]
                }
            ],
            "nextPage": None
        }
        mock_get.return_value = mock_response
        
        # API 키 설정
        self.handler.newsdata_api_key = "test_api_key"
        
        # 뉴스 가져오기
        news = self.handler.get_news_from_newsdata(keyword="bitcoin", category="business", days=7)
        
        # 검증
        self.assertEqual(len(news), 2)
        self.assertEqual(news[0]["title"], "Bitcoin News 1")
        self.assertEqual(news[1]["title"], "Bitcoin News 2")
        self.assertEqual(news[0]["source_type"], "newsdata")
        self.assertEqual(news[1]["source_type"], "newsdata")
        
        # API 호출 확인
        mock_get.assert_called_once()
        
        # URL 및 파라미터 확인
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://newsdata.io/api/1/news")
        self.assertIn("params", kwargs)
        self.assertEqual(kwargs["params"]["q"], "bitcoin")
        self.assertEqual(kwargs["params"]["category"], "business")
    
    @patch('requests.get')
    def test_get_news_from_newsdata_with_pagination(self, mock_get):
        """
        NewsData.io API에서 페이지네이션 처리 테스트
        """
        # 첫 번째 페이지 응답 설정
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            "status": "success",
            "totalResults": 4,
            "results": [
                {
                    "title": "News 1",
                    "description": "This is a news summary 1",
                    "link": "https://example.com/news1",
                    "pubDate": "2023-04-08 10:30:00",
                    "source_id": "example",
                    "category": ["business"],
                    "country": ["us"]
                },
                {
                    "title": "News 2",
                    "description": "This is a news summary 2",
                    "link": "https://example.com/news2",
                    "pubDate": "2023-04-08 11:30:00",
                    "source_id": "example",
                    "category": ["business"],
                    "country": ["us"]
                }
            ],
            "nextPage": "next_page_token"
        }
        
        # 두 번째 페이지 응답 설정
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "status": "success",
            "totalResults": 4,
            "results": [
                {
                    "title": "News 3",
                    "description": "This is a news summary 3",
                    "link": "https://example.com/news3",
                    "pubDate": "2023-04-08 12:30:00",
                    "source_id": "example",
                    "category": ["business"],
                    "country": ["us"]
                },
                {
                    "title": "News 4",
                    "description": "This is a news summary 4",
                    "link": "https://example.com/news4",
                    "pubDate": "2023-04-08 13:30:00",
                    "source_id": "example",
                    "category": ["business"],
                    "country": ["us"]
                }
            ],
            "nextPage": None
        }
        
        # 연속 호출에 대한 응답 설정
        mock_get.side_effect = [mock_response1, mock_response2]
        
        # API 키 설정
        self.handler.newsdata_api_key = "test_api_key"
        
        # 뉴스 가져오기
        news = self.handler.get_news_from_newsdata(category="business", days=7)
        
        # 검증
        self.assertEqual(len(news), 4)
        self.assertEqual(news[0]["title"], "News 1")
        self.assertEqual(news[1]["title"], "News 2")
        self.assertEqual(news[2]["title"], "News 3")
        self.assertEqual(news[3]["title"], "News 4")
        
        # API 호출 확인
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('requests.get')
    def test_get_news_from_newsdata_error_handling(self, mock_get):
        """
        NewsData.io API 오류 처리 테스트
        """
        # 오류 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Invalid API key"
        mock_get.return_value = mock_response
        
        # API 키 설정
        self.handler.newsdata_api_key = "test_api_key"
        
        # 뉴스 가져오기 시도
        news = self.handler.get_news_from_newsdata(keyword="bitcoin", days=7)
        
        # 검증 - 오류 발생해도 빈 목록 반환
        self.assertEqual(len(news), 0)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_news_from_newsdata_network_error(self, mock_get):
        """
        NewsData.io API 네트워크 오류 처리 테스트
        """
        # 네트워크 예외 설정
        mock_get.side_effect = requests.RequestException("네트워크 오류")
        
        # API 키 설정
        self.handler.newsdata_api_key = "test_api_key"
        
        # 뉴스 가져오기 시도
        news = self.handler.get_news_from_newsdata(keyword="bitcoin", days=7)
        
        # 검증 - 오류 발생해도 빈 목록 반환
        self.assertEqual(len(news), 0)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_news_from_newsdata_fields_normalization(self, mock_get):
        """
        NewsData.io API 결과 필드 정규화 테스트
        """
        # 모의 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "totalResults": 1,
            "results": [
                {
                    "title": "Test News",
                    "description": "This is a test news summary",
                    "link": "https://example.com/test",
                    "pubDate": "2023-04-08 10:30:00",
                    "source_id": "example",
                    "creator": ["John Doe"],
                    "category": ["business", "technology"],
                    "image_url": "https://example.com/image.jpg",
                    "country": ["us", "uk"],
                    "keywords": ["test", "news", "api"]
                }
            ],
            "nextPage": None
        }
        mock_get.return_value = mock_response
        
        # API 키 설정
        self.handler.newsdata_api_key = "test_api_key"
        
        # 날짜 포맷 메서드 모킹
        with patch.object(self.handler, '_format_newsdata_date') as mock_format_date:
            formatted_date = "2023-04-08T10:30:00"
            mock_format_date.return_value = formatted_date
            
            # 뉴스 가져오기
            news = self.handler.get_news_from_newsdata(keyword="test", days=7)
            
            # 검증
            self.assertEqual(len(news), 1)
            
            # 필드 정규화 검증
            article = news[0]
            self.assertEqual(article["title"], "Test News")
            self.assertEqual(article["summary"], "This is a test news summary")
            self.assertEqual(article["url"], "https://example.com/test")
            self.assertEqual(article["published_date"], formatted_date)
            self.assertEqual(article["source"], "example")
            self.assertEqual(article["source_type"], "newsdata")
            self.assertIsInstance(article["crawled_date"], str)
            self.assertEqual(article["creator"], ["John Doe"])
            self.assertEqual(article["categories"], ["business", "technology"])
            self.assertEqual(article["image_url"], "https://example.com/image.jpg")
            self.assertEqual(article["country"], ["us", "uk"])
            self.assertEqual(article["keywords"], ["test", "news", "api"])


if __name__ == "__main__":
    unittest.main()
