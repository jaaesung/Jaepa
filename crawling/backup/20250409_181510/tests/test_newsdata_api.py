"""
개선된 NewsData.io API 테스트 모듈

NewsSourcesHandler 클래스의 NewsData.io API 기능을 테스트합니다.
"""
import unittest
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock, ANY

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parents[2]))

# 개선된 모듈 가져오기
from crawling.news_sources_enhanced_improved import NewsSourcesHandler


class TestNewsDataAPIImproved(unittest.TestCase):
    """
    개선된 NewsData.io API 테스트 클래스
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
        
        # 모의 NewsData.io 응답 데이터
        self.mock_newsdata_response = {
            "status": "success",
            "totalResults": 2,
            "results": [
                {
                    "title": "Bitcoin Price Analysis: BTC Reaches New High",
                    "description": "Bitcoin has reached a new all-time high as institutional investors continue to show interest.",
                    "content": "Bitcoin has reached a new all-time high as institutional investors continue to show interest.",
                    "link": "https://example.com/bitcoin-analysis",
                    "pubDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source_id": "CryptoNews",
                    "creator": ["John Analyst"],
                    "category": ["cryptocurrency", "finance"],
                    "image_url": "https://example.com/bitcoin-image.jpg",
                    "country": ["us", "uk"],
                    "language": "en"
                },
                {
                    "title": "Ethereum Update Coming: What Investors Need to Know",
                    "description": "The upcoming Ethereum update will bring significant changes to the network.",
                    "content": "The upcoming Ethereum update will bring significant changes to the network.",
                    "link": "https://example.com/ethereum-update",
                    "pubDate": (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
                    "source_id": "CryptoNews",
                    "creator": ["Jane Expert"],
                    "category": ["cryptocurrency", "technology"],
                    "image_url": "https://example.com/ethereum-image.jpg",
                    "country": ["us"],
                    "language": "en"
                }
            ],
            "nextPage": "some-next-page-token"
        }
    
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
    def test_make_request_with_retry(self, mock_get):
        """
        재시도 로직이 포함된 HTTP 요청 테스트
        """
        # 성공 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps(self.mock_newsdata_response)
        mock_get.return_value = mock_response
        
        # 요청 실행
        status_code, response_text = self.handler._make_request_with_retry(
            "https://newsdata.io/api/1/news",
            params={"apikey": "test_key", "q": "bitcoin"}
        )
        
        # 검증
        self.assertEqual(status_code, 200)
        self.assertIsNotNone(response_text)
        mock_get.assert_called_once_with(
            "https://newsdata.io/api/1/news",
            params={"apikey": "test_key", "q": "bitcoin"},
            headers=ANY,
            timeout=10
        )
    
    @patch('requests.get')
    def test_search_newsdata_news(self, mock_get):
        """
        NewsData.io API를 사용한 뉴스 검색 테스트
        """
        # 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps(self.mock_newsdata_response)
        
        # 다음 페이지 응답 설정
        mock_next_response = MagicMock()
        mock_next_response.status_code = 200
        next_page_response = self.mock_newsdata_response.copy()
        next_page_response["nextPage"] = None  # 마지막 페이지
        mock_next_response.text = json.dumps(next_page_response)
        
        # 순차적 호출에 대한 응답 설정
        mock_get.side_effect = [mock_response, mock_next_response]
        
        # API 키 설정
        self.handler.newsdata_api_key = "test_api_key"
        
        # 뉴스 검색
        news = self.handler._search_newsdata_news("bitcoin", days=7)
        
        # 검증
        self.assertEqual(len(news), 4)  # 첫 번째 페이지 2개 + 두 번째 페이지 2개
        self.assertEqual(news[0]["title"], "Bitcoin Price Analysis: BTC Reaches New High")
        self.assertEqual(news[1]["title"], "Ethereum Update Coming: What Investors Need to Know")
        self.assertEqual(news[0]["source_type"], "newsdata")
        self.assertEqual(news[1]["source_type"], "newsdata")
        
        # API 호출 확인
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('requests.get')
    def test_get_news_from_newsdata_improved(self, mock_get):
        """
        개선된 NewsData.io API 뉴스 가져오기 테스트
        """
        # 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps(self.mock_newsdata_response)
        mock_get.return_value = mock_response
        
        # API 키 설정
        self.handler.newsdata_api_key = "test_api_key"
        
        # 뉴스 가져오기
        news = self.handler.get_news_from_newsdata(keyword="bitcoin", category="cryptocurrency", days=7)
        
        # 검증
        self.assertEqual(len(news), 2)
        
        # 필드 정규화 검증
        article = news[0]
        self.assertEqual(article["title"], "Bitcoin Price Analysis: BTC Reaches New High")
        self.assertEqual(article["summary"], "Bitcoin has reached a new all-time high as institutional investors continue to show interest.")
        self.assertEqual(article["content"], "Bitcoin has reached a new all-time high as institutional investors continue to show interest.")
        self.assertEqual(article["url"], "https://example.com/bitcoin-analysis")
        self.assertEqual(article["source"], "CryptoNews")
        self.assertEqual(article["source_type"], "newsdata")
        self.assertEqual(article["creator"], ["John Analyst"])
        self.assertEqual(article["categories"], ["cryptocurrency", "finance"])
        self.assertEqual(article["image_url"], "https://example.com/bitcoin-image.jpg")
        self.assertEqual(article["country"], ["us", "uk"])
        self.assertIn("keywords", article)
        self.assertIn("published_date", article)
        self.assertIn("crawled_date", article)
    
    @patch('requests.get')
    def test_newsdata_error_handling(self, mock_get):
        """
        NewsData.io API 오류 처리 테스트
        """
        # API 키 없는 경우
        self.handler.newsdata_api_key = None
        
        # 뉴스 가져오기 시도
        news = self.handler.get_news_from_newsdata(keyword="bitcoin", days=7)
        
        # 검증 - 빈 목록 반환
        self.assertEqual(len(news), 0)
        
        # API 키 설정 후 오류 응답 테스트
        self.handler.newsdata_api_key = "test_api_key"
        
        # 오류 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = json.dumps({"status": "error", "message": "Invalid API key"})
        mock_get.return_value = mock_response
        
        # 뉴스 가져오기 시도
        news = self.handler.get_news_from_newsdata(keyword="bitcoin", days=7)
        
        # 검증 - 빈 목록 반환
        self.assertEqual(len(news), 0)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_newsdata_rate_limit(self, mock_get):
        """
        NewsData.io API 레이트 리밋 처리 테스트
        """
        # 레이트 리밋 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = json.dumps({"status": "error", "message": "Rate limit exceeded"})
        mock_get.return_value = mock_response
        
        # API 키 설정
        self.handler.newsdata_api_key = "test_api_key"
        
        # 레이트 리밋 카운터 강제 설정
        self.handler.rate_limits["newsdata"]["requests_count"] = \
            self.handler.rate_limits["newsdata"]["requests_per_day"]
        
        # 뉴스 가져오기 시도
        news = self.handler.get_news_from_newsdata(keyword="bitcoin", days=7)
        
        # 검증 - 빈 목록 반환
        self.assertEqual(len(news), 0)
    
    @patch('requests.get')
    def test_pagination_handling(self, mock_get):
        """
        페이지네이션 처리 테스트
        """
        # 첫 번째 페이지 응답 설정
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.text = json.dumps(self.mock_newsdata_response)
        
        # 두 번째 페이지 응답 설정
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        page2_response = self.mock_newsdata_response.copy()
        page2_response["results"] = [
            {
                "title": "Another Bitcoin Article",
                "description": "More news about Bitcoin and cryptocurrency market.",
                "link": "https://example.com/more-bitcoin",
                "pubDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source_id": "CryptoNews",
                "category": ["cryptocurrency"]
            }
        ]
        page2_response["nextPage"] = None  # 마지막 페이지
        mock_response2.text = json.dumps(page2_response)
        
        # 연속 호출에 대한 응답 설정
        mock_get.side_effect = [mock_response1, mock_response2]
        
        # API 키 설정
        self.handler.newsdata_api_key = "test_api_key"
        
        # 뉴스 가져오기
        news = self.handler._search_newsdata_news("bitcoin", days=7)
        
        # 검증
        self.assertEqual(len(news), 3)  # 첫 번째 페이지 2개 + 두 번째 페이지 1개
        self.assertEqual(mock_get.call_count, 2)


if __name__ == "__main__":
    unittest.main()
