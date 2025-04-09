"""
Finnhub API 테스트 모듈

NewsSourcesHandler 클래스의 Finnhub API 기능을 테스트합니다.
"""
import unittest
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parents[2]))

from crawling.news_sources_enhanced import NewsSourcesHandler


class TestFinnhubAPI(unittest.TestCase):
    """
    Finnhub API 테스트 클래스
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
    
    def test_initialization(self):
        """
        API 핸들러 초기화 테스트
        """
        self.assertIsNotNone(self.handler.config)
        self.assertIsNone(self.handler.client)  # db_connect=False로 설정했으므로
        self.assertIsNone(self.handler.db)
        self.assertIsNone(self.handler.news_collection)
    
    def test_format_finnhub_date(self):
        """
        Finnhub 날짜 형식 변환 테스트
        """
        # 현재 시간의 타임스탬프
        now_timestamp = int(datetime.now().timestamp())
        
        # 변환 실행
        formatted_date = self.handler._format_finnhub_date(now_timestamp)
        
        # 검증 - ISO 형식인지 확인
        self.assertIsInstance(formatted_date, str)
        try:
            datetime.fromisoformat(formatted_date)
        except ValueError:
            self.fail("날짜가 ISO 형식이 아닙니다.")
    
    @patch.object(NewsSourcesHandler, '_format_finnhub_date')
    @patch('finnhub.Client')
    def test_get_news_from_finnhub_with_symbol(self, mock_client, mock_format_date):
        """
        Finnhub API에서 심볼로 뉴스 가져오기 테스트
        """
        # 모의 응답 설정
        mock_news = [
            {
                "headline": "Apple News 1",
                "summary": "This is an Apple news summary 1",
                "url": "https://example.com/apple1",
                "datetime": 1680888600,
                "source": "Finnhub",
                "related": ["AAPL"],
                "category": "technology",
                "image": "https://example.com/image1.jpg"
            },
            {
                "headline": "Apple News 2",
                "summary": "This is an Apple news summary 2",
                "url": "https://example.com/apple2",
                "datetime": 1680892200,
                "source": "Finnhub",
                "related": ["AAPL"],
                "category": "technology",
                "image": "https://example.com/image2.jpg"
            }
        ]
        
        # 날짜 포맷 모의 설정
        mock_format_date.side_effect = lambda timestamp: f"2023-04-08T{timestamp % 1000000:02d}:00:00"
        
        # Finnhub 클라이언트 모의 설정
        mock_finnhub = MagicMock()
        mock_finnhub.company_news.return_value = mock_news
        mock_client.return_value = mock_finnhub
        
        # API 키 설정
        self.handler.finnhub_api_key = "test_api_key"
        self.handler.finnhub_client = mock_finnhub
        
        # 심볼로 뉴스 가져오기
        news = self.handler.get_news_from_finnhub(symbol="AAPL", days=7)
        
        # 검증
        self.assertEqual(len(news), 2)
        self.assertEqual(news[0]["title"], "Apple News 1")
        self.assertEqual(news[1]["title"], "Apple News 2")
        self.assertEqual(news[0]["source_type"], "finnhub")
        self.assertEqual(news[1]["source_type"], "finnhub")
        
        # API 호출 확인
        mock_finnhub.company_news.assert_called_once()
    
    @patch.object(NewsSourcesHandler, '_format_finnhub_date')
    @patch('finnhub.Client')
    def test_get_news_from_finnhub_with_category(self, mock_client, mock_format_date):
        """
        Finnhub API에서 카테고리로 뉴스 가져오기 테스트
        """
        # 모의 응답 설정
        mock_news = [
            {
                "headline": "General News 1",
                "summary": "This is a general news summary 1",
                "url": "https://example.com/general1",
                "datetime": 1680888600,
                "source": "Finnhub",
                "related": [],
                "category": "general",
                "image": "https://example.com/image3.jpg"
            },
            {
                "headline": "General News 2",
                "summary": "This is a general news summary 2",
                "url": "https://example.com/general2",
                "datetime": 1680892200,
                "source": "Finnhub",
                "related": [],
                "category": "general",
                "image": "https://example.com/image4.jpg"
            }
        ]
        
        # 날짜 포맷 모의 설정
        mock_format_date.side_effect = lambda timestamp: f"2023-04-08T{timestamp % 1000000:02d}:00:00"
        
        # Finnhub 클라이언트 모의 설정
        mock_finnhub = MagicMock()
        mock_finnhub.general_news.return_value = mock_news
        mock_client.return_value = mock_finnhub
        
        # API 키 설정
        self.handler.finnhub_api_key = "test_api_key"
        self.handler.finnhub_client = mock_finnhub
        
        # 카테고리로 뉴스 가져오기
        news = self.handler.get_news_from_finnhub(category="general", days=7)
        
        # 검증
        self.assertEqual(len(news), 2)
        self.assertEqual(news[0]["title"], "General News 1")
        self.assertEqual(news[1]["title"], "General News 2")
        self.assertEqual(news[0]["source_type"], "finnhub")
        self.assertEqual(news[1]["source_type"], "finnhub")
        
        # API 호출 확인
        mock_finnhub.general_news.assert_called_once()
    
    @patch.object(NewsSourcesHandler, '_format_finnhub_date')
    @patch('finnhub.Client')
    def test_get_news_from_finnhub_fields_normalization(self, mock_client, mock_format_date):
        """
        Finnhub API 결과 필드 정규화 테스트
        """
        # 모의 응답 설정
        mock_news = [
            {
                "headline": "Test News",
                "summary": "This is a test news summary",
                "url": "https://example.com/test",
                "datetime": 1680888600,
                "source": "Finnhub",
                "related": ["AAPL", "TSLA"],
                "category": "technology,business",
                "image": "https://example.com/image.jpg"
            }
        ]
        
        # 날짜 포맷 모의 설정
        formatted_date = "2023-04-08T10:30:00"
        mock_format_date.return_value = formatted_date
        
        # Finnhub 클라이언트 모의 설정
        mock_finnhub = MagicMock()
        mock_finnhub.company_news.return_value = mock_news
        mock_client.return_value = mock_finnhub
        
        # API 키 설정
        self.handler.finnhub_api_key = "test_api_key"
        self.handler.finnhub_client = mock_finnhub
        
        # 뉴스 가져오기
        news = self.handler.get_news_from_finnhub(symbol="AAPL", days=7)
        
        # 검증
        self.assertEqual(len(news), 1)
        
        # 필드 정규화 검증
        article = news[0]
        self.assertEqual(article["title"], "Test News")
        self.assertEqual(article["summary"], "This is a test news summary")
        self.assertEqual(article["url"], "https://example.com/test")
        self.assertEqual(article["published_date"], formatted_date)
        self.assertEqual(article["source"], "Finnhub")
        self.assertEqual(article["source_type"], "finnhub")
        self.assertIsInstance(article["crawled_date"], str)
        self.assertEqual(article["related_symbols"], ["AAPL", "TSLA"])
        self.assertEqual(article["categories"], ["technology", "business"])
        self.assertEqual(article["image_url"], "https://example.com/image.jpg")
        self.assertIn("keywords", article)
    
    @patch('finnhub.Client')
    def test_finnhub_client_error_handling(self, mock_client):
        """
        Finnhub 클라이언트 오류 처리 테스트
        """
        # Finnhub 클라이언트 예외 설정
        mock_finnhub = MagicMock()
        mock_finnhub.company_news.side_effect = Exception("API 호출 실패")
        mock_client.return_value = mock_finnhub
        
        # API 키 설정
        self.handler.finnhub_api_key = "test_api_key"
        self.handler.finnhub_client = mock_finnhub
        
        # 뉴스 가져오기 시도
        news = self.handler.get_news_from_finnhub(symbol="AAPL", days=7)
        
        # 검증 - 오류 발생해도 빈 목록 반환
        self.assertEqual(len(news), 0)
        mock_finnhub.company_news.assert_called_once()


if __name__ == "__main__":
    unittest.main()
