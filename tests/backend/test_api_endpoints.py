"""
백엔드 API 엔드포인트 테스트 모듈

이 모듈은 FastAPI로 구현된 백엔드 API 엔드포인트를 테스트합니다.
"""
import sys
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import json

# 상위 디렉토리 추가하여 jaepa 패키지 import 가능하게 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# FastAPI 테스트 클라이언트
from fastapi.testclient import TestClient

# API 앱 경로 (실제 경로에 맞게 조정 필요)
from backend.app.main import app

# 테스트 클라이언트 생성
client = TestClient(app)


class TestAPIEndpoints(unittest.TestCase):
    """백엔드 API 엔드포인트 테스트"""

    def setUp(self):
        """테스트 설정: JWT 토큰 생성, 목 데이터 설정"""
        # 테스트용 JWT 토큰 생성
        self.test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTUxNjIzOTAyMn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        # 헤더 설정
        self.headers = {"Authorization": f"Bearer {self.test_token}"}
        
        # 목 주식 데이터
        self.mock_stock_data = {
            "symbol": "AAPL",
            "data": [
                {
                    "date": "2023-04-01",
                    "open": 150.0,
                    "close": 155.0,
                    "high": 157.0,
                    "low": 149.0,
                    "volume": 1000000
                },
                {
                    "date": "2023-04-02",
                    "open": 155.0,
                    "close": 158.0,
                    "high": 160.0,
                    "low": 154.0,
                    "volume": 1200000
                }
            ]
        }
        
        # 목 뉴스 데이터
        self.mock_news_data = {
            "articles": [
                {
                    "title": "Test Article 1",
                    "url": "https://example.com/article1",
                    "source": "reuters",
                    "published_date": "2023-04-01T00:00:00",
                    "content": "Test content 1"
                },
                {
                    "title": "Test Article 2",
                    "url": "https://example.com/article2",
                    "source": "bloomberg",
                    "published_date": "2023-04-02T00:00:00",
                    "content": "Test content 2"
                }
            ],
            "total": 2
        }

    @patch('backend.app.api.auth_routes.verify_password')
    @patch('backend.app.api.auth_routes.create_access_token')
    def test_login_endpoint(self, mock_create_token, mock_verify_password):
        """로그인 엔드포인트 테스트"""
        # 목 설정
        mock_verify_password.return_value = True
        mock_create_token.return_value = self.test_token
        
        # 테스트 요청 데이터
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        
        # API 요청
        response = client.post("/api/auth/login", json=login_data)
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)
        self.assertEqual(data["token"], self.test_token)
        self.assertIn("token_type", data)
        self.assertEqual(data["token_type"], "bearer")

    @patch('backend.app.api.auth_routes.verify_password')
    def test_login_invalid_credentials(self, mock_verify_password):
        """잘못된 인증 정보로 로그인 테스트"""
        # 잘못된 비밀번호 설정
        mock_verify_password.return_value = False
        
        # 테스트 요청 데이터
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        
        # API 요청
        response = client.post("/api/auth/login", json=login_data)
        
        # 응답 검증 (401 Unauthorized)
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Incorrect username or password")

    @patch('backend.app.api.user_routes.get_current_user')
    def test_get_user_profile(self, mock_get_user):
        """사용자 프로필 조회 테스트"""
        # 목 사용자 설정
        mock_user = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User"
        }
        mock_get_user.return_value = mock_user
        
        # API 요청
        response = client.get("/api/users/me", headers=self.headers)
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data, mock_user)

    @patch('backend.app.api.user_routes.get_current_user')
    def test_get_user_profile_unauthorized(self, mock_get_user):
        """인증되지 않은 사용자 프로필 조회 테스트"""
        # 인증 실패 예외 설정
        mock_get_user.side_effect = Exception("Could not validate credentials")
        
        # API 요청 (헤더 없음)
        response = client.get("/api/users/me")
        
        # 응답 검증 (401 Unauthorized)
        self.assertEqual(response.status_code, 401)

    @patch('backend.app.api.stock_routes.StockDataCrawler')
    def test_get_stock_data(self, mock_crawler_class):
        """주식 데이터 조회 테스트"""
        # 목 크롤러 설정
        mock_crawler = MagicMock()
        mock_crawler_class.return_value = mock_crawler
        mock_crawler.get_stock_data.return_value = self.mock_stock_data["data"]
        
        # API 요청
        response = client.get("/api/stocks/AAPL?period=1mo", headers=self.headers)
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["symbol"], "AAPL")
        self.assertEqual(len(data["data"]), 2)
        
        # 크롤러 호출 검증
        mock_crawler.get_stock_data.assert_called_once_with(
            symbol="AAPL",
            period="1mo",
            interval=None,
            start_date=None,
            end_date=None
        )

    @patch('backend.app.api.news_routes.NewsCrawler')
    def test_search_news(self, mock_crawler_class):
        """뉴스 검색 테스트"""
        # 목 크롤러 설정
        mock_crawler = MagicMock()
        mock_crawler_class.return_value = mock_crawler
        mock_crawler.search_news.return_value = self.mock_news_data["articles"]
        
        # API 요청
        response = client.get(
            "/api/news/search?keyword=test&days=7",
            headers=self.headers
        )
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("articles", data)
        self.assertEqual(len(data["articles"]), 2)
        self.assertIn("total", data)
        
        # 크롤러 호출 검증
        mock_crawler.search_news.assert_called_once_with(
            keyword="test",
            days=7,
            sources=None
        )

    @patch('backend.app.api.news_routes.NewsCrawler')
    def test_get_latest_news(self, mock_crawler_class):
        """최신 뉴스 조회 테스트"""
        # 목 크롤러 설정
        mock_crawler = MagicMock()
        mock_crawler_class.return_value = mock_crawler
        mock_crawler.get_latest_news.return_value = self.mock_news_data["articles"]
        
        # API 요청
        response = client.get(
            "/api/news/latest?count=5&sources=reuters,bloomberg",
            headers=self.headers
        )
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("articles", data)
        self.assertEqual(len(data["articles"]), 2)
        
        # 크롤러 호출 검증
        mock_crawler.get_latest_news.assert_called_once_with(
            count=5,
            sources=['reuters', 'bloomberg']
        )

    def test_health_check(self):
        """API 상태 체크 테스트"""
        # API 요청
        response = client.get("/health")
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")


if __name__ == '__main__':
    unittest.main()
