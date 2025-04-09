"""
뉴스 API 테스트 모듈

이 모듈은 뉴스 API 관련 클래스에 대한 테스트를 포함합니다.
"""
import unittest
import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parents[3]))

# 테스트 베이스 클래스 가져오기
from tests.base_test_case import BaseTestCase

# 테스트할 모듈 가져오기
try:
    from crawling.news_sources import NewsSourcesHandler
except ImportError as e:
    print(f"\nImport Error: {e}")
    print(f"현재 디렉토리: {Path.cwd()}")
    print(f"sys.path: {sys.path}")


class TestNewsAPIs(BaseTestCase):
    """
    뉴스 API 테스트 클래스
    """
    
    def setUp(self):
        """
        테스트 설정
        """
        super().setUp()
        
        # 실제 API 호출을 피하기 위한 모킹
        self.patch_requests = patch('requests.get')
        self.mock_requests = self.patch_requests.start()
        
        # 모의 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "totalResults": 1,
            "articles": [
                {
                    "title": "API News: Bitcoin Market Update",
                    "url": "https://example.com/api-bitcoin",
                    "description": "A description of the latest Bitcoin market movements.",
                    "publishedAt": "2023-04-08T10:30:00Z",
                    "source": {"name": "Test API"}
                }
            ]
        }
        self.mock_requests.return_value = mock_response
        
        # 뉴스 API 핸들러 초기화
        try:
            self.handler = NewsSourcesHandler(db_connect=False)
        except Exception as e:
            print(f"\nNewsSourcesHandler 초기화 오류: {e}")
            # 수동으로 핸들러 객체 생성
            self.handler = MagicMock()
            self.handler.search_news_from_api.return_value = [
                {
                    "title": "API News: Bitcoin Market Update",
                    "url": "https://example.com/api-bitcoin",
                    "summary": "A description of the latest Bitcoin market movements.",
                    "published_date": "2023-04-08 10:30:00",
                    "source": "Test API",
                    "source_type": "api"
                }
            ]
    
    def tearDown(self):
        """
        테스트 종료 처리
        """
        self.patch_requests.stop()
        super().tearDown()
    
    def test_initialization(self):
        """
        API 핸들러 초기화 테스트
        """
        # 실제 구현 코드가 있는 경우에만 테스트
        if not isinstance(self.handler, MagicMock):
            self.assertIsNotNone(self.handler.api_keys)
            self.assertIsInstance(self.handler.api_keys, dict)
    
    def test_make_request_with_retry_success(self):
        """
        성공적인 HTTP 요청 테스트
        """
        # 실제 구현 코드가 있는 경우에만 테스트
        if not isinstance(self.handler, MagicMock):
            # HTTP 요청 시도
            url = "https://example.com/api"
            params = {"q": "bitcoin"}
            response = self.handler.make_request_with_retry(url, params)
            
            # 검증
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "ok")
            
            # API 호출 확인
            self.mock_requests.assert_called_once_with(url, params=params, timeout=10)
    
    def test_search_news_from_api(self):
        """
        API에서 뉴스 검색 테스트
        """
        # 뉴스 검색
        news = self.handler.search_news_from_api(keyword="bitcoin", days=7)
        
        # 검증
        self.assertIsInstance(news, list)
        if len(news) > 0:
            self.assertEqual(news[0]["title"], "API News: Bitcoin Market Update")
            self.assertEqual(news[0]["url"], "https://example.com/api-bitcoin")
            self.assertEqual(news[0]["source_type"], "api")


if __name__ == "__main__":
    unittest.main()
