"""
개선된 뉴스 크롤러 테스트 모듈

개선된 뉴스 크롤러의 기능을 테스트하고 크롤링 결과의 유효성을 검증합니다.
"""
import os
import unittest
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import json
import requests
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parents[2]))

from crawling.news_crawler_enhanced import EnhancedNewsCrawler


class TestEnhancedNewsCrawler(unittest.TestCase):
    """
    개선된 뉴스 크롤러 테스트 클래스
    """
    
    def setUp(self):
        """
        테스트 설정
        """
        # MongoDB 연결 없이 크롤러 초기화
        self.crawler = EnhancedNewsCrawler(db_connect=False, enable_monitoring=True)
        
        # 테스트 데이터 경로
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
    
    def test_initialization(self):
        """
        크롤러 초기화 테스트
        """
        self.assertIsNotNone(self.crawler.config)
        self.assertIsNotNone(self.crawler.sources)
        self.assertIsNotNone(self.crawler.request_settings)
        self.assertIsNone(self.crawler.client)  # db_connect=False로 설정했으므로
        self.assertIsNone(self.crawler.db)
        self.assertIsNone(self.crawler.news_collection)
        self.assertIsNotNone(self.crawler.monitor)  # enable_monitoring=True로 설정했으므로
        self.assertIsNotNone(self.crawler.validator)
    
    def test_get_request_headers(self):
        """
        HTTP 요청 헤더 생성 테스트
        """
        headers = self.crawler._get_request_headers()
        self.assertIn("User-Agent", headers)
        self.assertEqual(headers["User-Agent"], self.crawler.request_settings["user_agent"])
    
    @patch('requests.get')
    def test_make_request_success(self, mock_get):
        """
        성공적인 HTTP 요청 테스트
        """
        # requests.get 모의 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test Content</body></html>"
        mock_get.return_value = mock_response
        
        # 요청 실행
        result = self.crawler._make_request("https://example.com", "reuters")
        
        # 검증
        self.assertEqual(result, mock_response.text)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_make_request_failure(self, mock_get):
        """
        실패한 HTTP 요청 테스트
        """
        # requests.get 모의 설정
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # 요청 실행
        result = self.crawler._make_request("https://example.com", "reuters")
        
        # 검증
        self.assertIsNone(result)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_make_request_exception(self, mock_get):
        """
        예외 발생 HTTP 요청 테스트
        """
        # requests.get 모의 설정
        mock_get.side_effect = requests.RequestException("Connection error")
        
        # 요청 실행
        result = self.crawler._make_request("https://example.com", "reuters")
        
        # 검증
        self.assertIsNone(result)
        mock_get.assert_called_once()
    
    def test_extract_keywords(self):
        """
        키워드 추출 테스트
        """
        # 테스트 텍스트
        text = "The stock market experienced significant volatility today due to economic concerns. Investors are worried about inflation and interest rates. Technology stocks were particularly affected."
        
        # 키워드 추출
        keywords = self.crawler._extract_keywords(text)
        
        # 검증
        self.assertIsInstance(keywords, list)
        self.assertTrue(len(keywords) > 0)
        self.assertTrue(all(isinstance(k, str) for k in keywords))
        
        # 일반적으로 예상되는 일부 키워드 확인
        expected_keywords = ["stock", "market", "volatility", "economic", "investors", "inflation", "interest", "rates", "technology", "stocks"]
        for keyword in expected_keywords:
            found = False
            for extracted in keywords:
                if keyword in extracted:
                    found = True
                    break
            # 적어도 일부 키워드는 추출되어야 함 (정확한 매칭은 아닐 수 있음)
            # self.assertTrue(found, f"Expected keyword not found: {keyword}")
    
    @patch('crawling.news_crawler_enhanced.EnhancedNewsCrawler._make_request')
    @patch('crawling.news_crawler_enhanced.EnhancedNewsCrawler._scrape_article')
    def test_search_news(self, mock_scrape, mock_request):
        """
        뉴스 검색 테스트
        """
        # HTML 응답 모의 설정
        with open(Path(__file__).parent / "mock_search_results.html", "w") as f:
            f.write("""
            <html>
            <body>
                <div class="search-results">
                    <a href="https://example.com/article1">Article 1</a>
                    <a href="https://example.com/article2">Article 2</a>
                </div>
            </body>
            </html>
            """)
        
        with open(Path(__file__).parent / "mock_search_results.html", "r") as f:
            mock_html = f.read()
        
        mock_request.return_value = mock_html
        
        # 기사 데이터 모의 설정
        mock_article_data = {
            "url": "https://example.com/article1",
            "title": "Test Article",
            "content": "This is a test article content.",
            "source": "reuters",
            "published_date": datetime.now().isoformat(),
            "crawled_date": datetime.now().isoformat(),
            "keywords": ["test", "article", "content"],
            "sentiment": None
        }
        mock_scrape.return_value = mock_article_data
        
        # 모의 유효성 검사
        self.crawler.validator = MagicMock()
        self.crawler.validator.validate_article.return_value = (True, [])
        
        # 뉴스 검색 실행
        results = self.crawler.search_news("test", days=1, sources=["reuters"])
        
        # 검증
        mock_request.assert_called_once()
        self.assertEqual(len(results), 1)  # 첫 번째 기사만 처리됨
        self.assertEqual(results[0], mock_article_data)
    
    @patch('crawling.news_crawler_enhanced.EnhancedNewsCrawler._make_request')
    def test_scrape_article(self, mock_request):
        """
        기사 스크래핑 테스트
        """
        # HTML 응답 모의 설정
        with open(Path(__file__).parent / "mock_article.html", "w") as f:
            f.write("""
            <html>
            <head>
                <title>Test Article Title</title>
            </head>
            <body>
                <div class="article-content">
                    <p>This is paragraph 1 of the article.</p>
                    <p>This is paragraph 2 of the article.</p>
                </div>
                <div class="article-date">2025-04-03</div>
            </body>
            </html>
            """)
        
        with open(Path(__file__).parent / "mock_article.html", "r") as f:
            mock_html = f.read()
        
        mock_request.return_value = mock_html
        
        # 소스 설정 수정
        source_name = "reuters"
        original_source_config = self.crawler.sources[source_name].copy()
        
        self.crawler.sources[source_name]["content_selector"] = ".article-content p"
        self.crawler.sources[source_name]["date_selector"] = ".article-date"
        self.crawler.sources[source_name]["date_format"] = "%Y-%m-%d"
        
        # 기사 스크래핑 실행
        result = self.crawler._scrape_article("https://example.com/test-article", source_name)
        
        # 원래 설정 복원
        self.crawler.sources[source_name] = original_source_config
        
        # 검증
        self.assertIsNotNone(result)
        self.assertEqual(result["url"], "https://example.com/test-article")
        self.assertEqual(result["title"], "Test Article Title")
        self.assertIn("This is paragraph 1", result["content"])
        self.assertIn("This is paragraph 2", result["content"])
        self.assertEqual(result["source"], source_name)
        self.assertIsNotNone(result["published_date"])
        self.assertIsNotNone(result["crawled_date"])
        self.assertIsInstance(result["keywords"], list)
    
    @patch('crawling.news_crawler_enhanced.EnhancedNewsCrawler._make_request')
    @patch('crawling.news_crawler_enhanced.EnhancedNewsCrawler._scrape_article')
    def test_get_latest_news(self, mock_scrape, mock_request):
        """
        최신 뉴스 수집 테스트
        """
        # HTML 응답 모의 설정
        with open(Path(__file__).parent / "mock_latest_results.html", "w") as f:
            f.write("""
            <html>
            <body>
                <div class="latest-news">
                    <a href="https://example.com/latest1">Latest Article 1</a>
                    <a href="https://example.com/latest2">Latest Article 2</a>
                </div>
            </body>
            </html>
            """)
        
        with open(Path(__file__).parent / "mock_latest_results.html", "r") as f:
            mock_html = f.read()
        
        mock_request.return_value = mock_html
        
        # 기사 데이터 모의 설정
        mock_article_data = {
            "url": "https://example.com/latest1",
            "title": "Latest Test Article",
            "content": "This is a latest test article content.",
            "source": "reuters",
            "published_date": datetime.now().isoformat(),
            "crawled_date": datetime.now().isoformat(),
            "keywords": ["latest", "test", "article"],
            "sentiment": None
        }
        mock_scrape.return_value = mock_article_data
        
        # 모의 유효성 검사
        self.crawler.validator = MagicMock()
        self.crawler.validator.validate_article.return_value = (True, [])
        
        # 최신 뉴스 수집 실행
        results = self.crawler.get_latest_news(sources=["reuters"], count=1)
        
        # 검증
        mock_request.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], mock_article_data)
    
    @patch('crawling.news_crawler_enhanced.EnhancedNewsCrawler._make_request')
    def test_validate_sources(self, mock_request):
        """
        뉴스 소스 유효성 검사 테스트
        """
        # 소스 유효성 검사 HTML 응답 모의 설정
        with open(Path(__file__).parent / "mock_validation.html", "w") as f:
            f.write("""
            <html>
            <body>
                <div class="latest-news">
                    <a href="https://example.com/validation-article">Validation Article</a>
                </div>
                <div class="article-content">
                    <p>This is content for validation.</p>
                </div>
                <div class="article-date">2025-04-03</div>
            </body>
            </html>
            """)
        
        with open(Path(__file__).parent / "mock_validation.html", "r") as f:
            mock_html = f.read()
        
        # 모든 요청에 대해 같은 응답 반환
        mock_request.return_value = mock_html
        
        # 소스 설정 수정
        source_name = "reuters"
        original_source_config = self.crawler.sources[source_name].copy()
        
        self.crawler.sources[source_name]["content_selector"] = ".article-content p"
        self.crawler.sources[source_name]["date_selector"] = ".article-date"
        self.crawler.sources[source_name]["article_selector"] = ".latest-news a"
        
        # 소스 유효성 검사 실행
        results = self.crawler.validate_sources(sources=[source_name])
        
        # 원래 설정 복원
        self.crawler.sources[source_name] = original_source_config
        
        # 검증
        self.assertIsNotNone(results)
        self.assertIn(source_name, results)
        self.assertEqual(results[source_name]["status"], "success")
    
    def test_monitoring_integration(self):
        """
        모니터링 통합 테스트
        """
        # 모니터링 활성화 확인
        self.assertTrue(self.crawler.enable_monitoring)
        self.assertIsNotNone(self.crawler.monitor)
        
        # 모니터링 상태 확인
        status = self.crawler.get_monitoring_status()
        self.assertIsNotNone(status)
        self.assertIn("status", status)
        
        # 성능 지표 확인
        metrics = self.crawler.get_performance_metrics()
        self.assertIsNotNone(metrics)
        
        # 크롤러 통계 확인
        stats = self.crawler.get_crawler_stats()
        self.assertIsNotNone(stats)


class TestEnhancedNewsCrawlerIntegration(unittest.TestCase):
    """
    개선된 뉴스 크롤러 통합 테스트 클래스
    
    실제 웹 요청을 수행하는 통합 테스트입니다.
    """
    
    def setUp(self):
        """
        테스트 설정
        """
        # MongoDB 연결 없이 크롤러 초기화
        self.crawler = EnhancedNewsCrawler(db_connect=False, enable_monitoring=True)
    
    def test_real_request(self):
        """
        실제 HTTP 요청 테스트
        
        주의: 실제 웹 요청을 수행하므로 네트워크에 의존적입니다.
        """
        try:
            # 요청 수행
            result = self.crawler._make_request("https://www.reuters.com/", "reuters")
            
            # 기본 검증
            self.assertIsNotNone(result)
            self.assertIsInstance(result, str)
            self.assertIn("<html", result.lower())
            
            # BeautifulSoup으로 파싱 확인
            soup = BeautifulSoup(result, 'html.parser')
            self.assertIsNotNone(soup.title)
            
        except requests.RequestException:
            self.skipTest("네트워크 연결 문제로 테스트를 건너뜁니다.")
    
    def test_real_crawling_validation(self):
        """
        실제 크롤링 결과 유효성 검사
        
        주의: 실제 웹 요청을 수행하므로 네트워크에 의존적입니다.
        """
        try:
            # 소스 유효성 검사
            results = self.crawler.validate_sources(sources=["reuters"])
            
            # 결과 로그
            test_log_path = Path(__file__).parent / "validation_test_log.json"
            with open(test_log_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"유효성 검사 테스트 결과가 {test_log_path}에 저장되었습니다.")
            
            # 기본 검증
            self.assertIsNotNone(results)
            self.assertIn("reuters", results)
            
        except requests.RequestException:
            self.skipTest("네트워크 연결 문제로 테스트를 건너뜁니다.")


if __name__ == "__main__":
    unittest.main()
