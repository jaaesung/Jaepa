"""
개선된 Finnhub API 테스트 모듈

NewsSourcesHandler 클래스의 Finnhub API 기능을 테스트합니다.
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


class TestFinnhubAPIImproved(unittest.TestCase):
    """
    개선된 Finnhub API 테스트 클래스
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
        
        # 모의 Finnhub 뉴스 데이터
        self.mock_finnhub_news = [
            {
                "headline": "Apple Reports Record Quarterly Revenue",
                "summary": "Apple Inc. reported record quarterly revenue of $90.1 billion, up 8% year over year.",
                "url": "https://example.com/apple-revenue",
                "datetime": int(datetime.now().timestamp()),
                "source": "Finnhub",
                "related": ["AAPL"],
                "category": "technology,earnings",
                "image": "https://example.com/apple-image.jpg"
            },
            {
                "headline": "Tesla Delivers Record Number of Vehicles",
                "summary": "Tesla has delivered a record number of vehicles in the latest quarter, exceeding analyst expectations.",
                "url": "https://example.com/tesla-delivery",
                "datetime": int((datetime.now() - timedelta(hours=2)).timestamp()),
                "source": "Finnhub",
                "related": ["TSLA"],
                "category": "automotive,technology",
                "image": "https://example.com/tesla-image.jpg"
            }
        ]
    
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
        self.assertIsNotNone(self.handler.user_agents)
        self.assertIsNotNone(self.handler.rate_limits)
        self.assertIn("finnhub", self.handler.rate_limits)
    
    def test_get_random_user_agent(self):
        """
        랜덤 사용자 에이전트 반환 테스트
        """
        user_agent = self.handler._get_random_user_agent()
        self.assertIsInstance(user_agent, str)
        self.assertIn(user_agent, self.handler.user_agents)
    
    def test_rate_limit_check(self):
        """
        API 레이트 리밋 체크 테스트
        """
        # 첫 호출은 항상 True 반환
        result = self.handler._rate_limit_check("finnhub")
        self.assertTrue(result)
        self.assertEqual(self.handler.rate_limits["finnhub"]["requests_count"], 1)
        
        # 여러 번 호출해도 분당 제한에 도달하지 않으면 True 반환
        for _ in range(self.handler.rate_limits["finnhub"]["requests_per_minute"] - 2):
            result = self.handler._rate_limit_check("finnhub")
            self.assertTrue(result)
        
        # 알 수 없는 API 이름에 대한 체크
        result = self.handler._rate_limit_check("unknown_api")
        self.assertTrue(result)  # 알 수 없는 API이므로 제한 없음
    
    @patch('requests.get')
    def test_make_request_with_retry_success(self, mock_get):
        """
        성공적인 HTTP 요청 테스트
        """
        # Mock 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "success", "data": []}'
        mock_get.return_value = mock_response
        
        # 요청 실행
        status_code, response_text = self.handler._make_request_with_retry(
            "https://example.com/api", params={"key": "value"}
        )
        
        # 검증
        self.assertEqual(status_code, 200)
        self.assertEqual(response_text, '{"status": "success", "data": []}')
        mock_get.assert_called_once_with(
            "https://example.com/api", 
            params={"key": "value"}, 
            headers=ANY, 
            timeout=10
        )
    
    @patch('requests.get')
    def test_make_request_with_retry_rate_limit(self, mock_get):
        """
        레이트 리밋 오류 및 재시도 테스트
        """
        # 429 (Too Many Requests) 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        # 시간 측정 시작
        start_time = datetime.now()
        
        # 요청 실행 (최대 재시도 횟수 1로 설정)
        status_code, response_text = self.handler._make_request_with_retry(
            "https://example.com/api", max_retries=1, backoff_factor=1
        )
        
        # 시간 측정 종료
        end_time = datetime.now()
        
        # 검증
        self.assertEqual(status_code, 429)
        self.assertIsNone(response_text)
        self.assertEqual(mock_get.call_count, 2)  # 최초 요청 + 1회 재시도
        
        # 재시도 시간 검증 (최소 1초 이상 지연)
        time_diff = (end_time - start_time).total_seconds()
        self.assertGreaterEqual(time_diff, 1.0)
    
    @patch('requests.get')
    def test_make_request_with_retry_network_error(self, mock_get):
        """
        네트워크 오류 및 재시도 테스트
        """
        # 타임아웃 오류 설정
        mock_get.side_effect = [
            unittest.mock.Mock(side_effect=Exception("Connection timeout")),
            unittest.mock.Mock(return_value=MagicMock(status_code=200, text='{"status": "success"}'))
        ]
        
        # 요청 실행
        status_code, response_text = self.handler._make_request_with_retry(
            "https://example.com/api", max_retries=1, backoff_factor=1
        )
        
        # 검증
        self.assertEqual(status_code, -1)
        self.assertIsNone(response_text)
    
    @patch('finnhub.Client')
    def test_search_finnhub_news(self, mock_client):
        """
        Finnhub API를 사용한 뉴스 검색 테스트
        """
        # Finnhub 클라이언트 모의 설정
        mock_finnhub = MagicMock()
        mock_finnhub.company_news.return_value = self.mock_finnhub_news
        mock_finnhub.general_news.return_value = self.mock_finnhub_news
        mock_client.return_value = mock_finnhub
        
        # API 키 설정
        self.handler.finnhub_api_key = "test_api_key"
        self.handler.finnhub_client = mock_finnhub
        
        # 뉴스 검색
        news = self.handler._search_finnhub_news("AAPL", days=7)
        
        # 검증
        self.assertEqual(len(news), 2)
        self.assertEqual(news[0]["title"], "Apple Reports Record Quarterly Revenue")
        self.assertEqual(news[1]["title"], "Tesla Delivers Record Number of Vehicles")
        self.assertEqual(news[0]["source_type"], "finnhub")
        self.assertEqual(news[1]["source_type"], "finnhub")
        
        # API 호출 확인
        mock_finnhub.company_news.assert_called_once()
        
        # 일반 뉴스 필터링 확인
        news = self.handler._search_finnhub_news("revenue", days=7)
        self.assertGreaterEqual(len(news), 1)
    
    @patch('requests.get')
    def test_search_news_with_apis(self, mock_get):
        """
        여러 API를 사용한 뉴스 검색 통합 테스트
        """
        # Finnhub 모의 설정
        with patch('finnhub.Client') as mock_client:
            # Finnhub 클라이언트 모의 응답
            mock_finnhub = MagicMock()
            mock_finnhub.company_news.return_value = self.mock_finnhub_news
            mock_finnhub.general_news.return_value = self.mock_finnhub_news
            mock_client.return_value = mock_finnhub
            
            # API 키 설정
            self.handler.finnhub_api_key = "test_finnhub_key"
            self.handler.newsdata_api_key = "test_newsdata_key"
            self.handler.finnhub_client = mock_finnhub
            
            # NewsData.io 모의 응답
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = json.dumps({
                "status": "success",
                "totalResults": 1,
                "results": [
                    {
                        "title": "NewsData Article About Apple",
                        "description": "This is a test article about Apple from NewsData.io",
                        "link": "https://example.com/newsdata-apple",
                        "pubDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "source_id": "newsdata",
                        "category": ["technology", "business"],
                        "country": ["us"]
                    }
                ],
                "nextPage": None
            })
            mock_get.return_value = mock_response
            
            # 뉴스 검색
            news = self.handler.search_news_with_apis("AAPL", days=7)
            
            # 검증
            self.assertGreaterEqual(len(news), 1)
            
            # API 호출 확인
            mock_finnhub.company_news.assert_called_once()
            mock_get.assert_called_once()
    
    @patch('finnhub.Client')
    def test_get_news_from_finnhub_improved(self, mock_client):
        """
        개선된 Finnhub API 뉴스 가져오기 테스트
        """
        # Finnhub 클라이언트 모의 설정
        mock_finnhub = MagicMock()
        mock_finnhub.company_news.return_value = self.mock_finnhub_news
        mock_client.return_value = mock_finnhub
        
        # API 키 설정
        self.handler.finnhub_api_key = "test_api_key"
        self.handler.finnhub_client = mock_finnhub
        
        # 심볼로 뉴스 가져오기
        news = self.handler.get_news_from_finnhub(symbol="AAPL", days=7)
        
        # 검증
        self.assertEqual(len(news), 2)
        
        # 필드 정규화 검증
        article = news[0]
        self.assertEqual(article["title"], "Apple Reports Record Quarterly Revenue")
        self.assertEqual(article["summary"], "Apple Inc. reported record quarterly revenue of $90.1 billion, up 8% year over year.")
        self.assertEqual(article["content"], article["summary"])  # content와 summary 동일
        self.assertEqual(article["url"], "https://example.com/apple-revenue")
        self.assertEqual(article["source"], "Finnhub")
        self.assertEqual(article["source_type"], "finnhub")
        self.assertEqual(article["related_symbols"], ["AAPL"])
        self.assertEqual(article["categories"], ["technology", "earnings"])
        self.assertEqual(article["image_url"], "https://example.com/apple-image.jpg")
        self.assertIn("keywords", article)
        self.assertIn("published_date", article)
        self.assertIn("crawled_date", article)
    
    def test_finnhub_error_handling(self):
        """
        Finnhub API 오류 처리 테스트
        """
        # API 키 없는 경우
        self.handler.finnhub_api_key = None
        self.handler.finnhub_client = None
        
        # 뉴스 가져오기 시도
        news = self.handler.get_news_from_finnhub(symbol="AAPL", days=7)
        
        # 검증 - 빈 목록 반환
        self.assertEqual(len(news), 0)
        
        # 오류 발생 시 예외 처리 테스트
        with patch('finnhub.Client') as mock_client:
            mock_finnhub = MagicMock()
            mock_finnhub.company_news.side_effect = Exception("API 오류")
            mock_client.return_value = mock_finnhub
            
            self.handler.finnhub_api_key = "test_key"
            self.handler.finnhub_client = mock_finnhub
            
            # 오류가 발생해도 예외가 아닌 빈 목록 반환
            news = self.handler.get_news_from_finnhub(symbol="AAPL", days=7)
            self.assertEqual(len(news), 0)


if __name__ == "__main__":
    unittest.main()
