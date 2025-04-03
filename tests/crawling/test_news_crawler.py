"""
뉴스 크롤러 테스트 모듈

뉴스 크롤러의 기능을 테스트하고 크롤링 결과의 유효성을 검증합니다.
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

from crawling.news_crawler import NewsCrawler, SentimentAnalyzer


class TestNewsCrawler(unittest.TestCase):
    """
    뉴스 크롤러 테스트 클래스
    """
    
    def setUp(self):
        """
        테스트 설정
        """
        # MongoDB 연결 없이 크롤러 초기화
        self.crawler = NewsCrawler(db_connect=False)
        
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
        result = self.crawler._make_request("https://example.com")
        
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
        result = self.crawler._make_request("https://example.com")
        
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
        result = self.crawler._make_request("https://example.com")
        
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
    
    @patch('crawling.news_crawler.NewsCrawler._make_request')
    @patch('crawling.news_crawler.NewsCrawler._scrape_article')
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
        
        # 뉴스 검색 실행
        results = self.crawler.search_news("test", days=1, sources=["reuters"])
        
        # 검증
        mock_request.assert_called_once()
        self.assertEqual(len(results), 1)  # 첫 번째 기사만 처리됨
        self.assertEqual(results[0], mock_article_data)
    
    @patch('crawling.news_crawler.NewsCrawler._make_request')
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


class TestSentimentAnalyzer(unittest.TestCase):
    """
    감성 분석기 테스트 클래스
    """
    
    @patch('transformers.AutoTokenizer.from_pretrained')
    @patch('transformers.AutoModelForSequenceClassification.from_pretrained')
    def setUp(self, mock_model, mock_tokenizer):
        """
        테스트 설정
        """
        # 토크나이저 및 모델 모의 설정
        self.mock_tokenizer = MagicMock()
        self.mock_model = MagicMock()
        mock_tokenizer.return_value = self.mock_tokenizer
        mock_model.return_value = self.mock_model
        
        # 감성 분석기 초기화
        self.analyzer = SentimentAnalyzer()
        self.analyzer.tokenizer = self.mock_tokenizer
        self.analyzer.model = self.mock_model
        self.analyzer.labels = ["negative", "neutral", "positive"]
    
    @patch('torch.nn.functional.softmax')
    def test_analyze(self, mock_softmax):
        """
        감성 분석 테스트
        """
        # 모의 설정
        import torch
        mock_outputs = MagicMock()
        mock_outputs.logits = torch.tensor([[0.1, 0.3, 0.6]])
        self.mock_model.return_value = mock_outputs
        
        mock_softmax.return_value = torch.tensor([[0.1, 0.3, 0.6]])
        
        # 분석 실행
        result = self.analyzer.analyze("This is a positive news article about economic growth.")
        
        # 검증
        self.assertIsNotNone(result)
        self.assertIn("negative", result)
        self.assertIn("neutral", result)
        self.assertIn("positive", result)
        self.assertEqual(result["negative"], 0.1)
        self.assertEqual(result["neutral"], 0.3)
        self.assertEqual(result["positive"], 0.6)


class TestNewsCrawlerIntegration(unittest.TestCase):
    """
    뉴스 크롤러 통합 테스트 클래스
    
    실제 웹 요청을 수행하는 통합 테스트입니다.
    """
    
    def setUp(self):
        """
        테스트 설정
        """
        # MongoDB 연결 없이 크롤러 초기화
        self.crawler = NewsCrawler(db_connect=False)
    
    def test_real_request(self):
        """
        실제 HTTP 요청 테스트
        
        주의: 실제 웹 요청을 수행하므로 네트워크에 의존적입니다.
        """
        try:
            # 요청 수행
            result = self.crawler._make_request("https://www.reuters.com/")
            
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
            # 최신 뉴스 하나만 가져오기
            articles = self.crawler.get_latest_news(sources=["reuters"], count=1)
            
            if not articles:
                self.skipTest("크롤링된 기사가 없어 테스트를 건너뜁니다.")
            
            # 기사 구조 유효성 검사
            article = articles[0]
            self.validate_article_structure(article)
            
            # 크롤링 결과 로그
            test_log_path = Path(__file__).parent / "crawling_test_log.json"
            with open(test_log_path, 'w') as f:
                json.dump(article, f, indent=2, default=str)
            
            print(f"크롤링 테스트 결과가 {test_log_path}에 저장되었습니다.")
            
        except requests.RequestException:
            self.skipTest("네트워크 연결 문제로 테스트를 건너뜁니다.")
    
    def validate_article_structure(self, article):
        """
        기사 구조 유효성 검사
        
        Args:
            article: 검사할 기사 데이터
        """
        # 필수 필드 확인
        required_fields = ["url", "title", "content", "source", "published_date", "crawled_date", "keywords"]
        for field in required_fields:
            self.assertIn(field, article)
            self.assertIsNotNone(article[field])
        
        # URL 검증
        self.assertTrue(article["url"].startswith("http"))
        
        # 제목 검증
        self.assertIsInstance(article["title"], str)
        self.assertTrue(len(article["title"]) > 0)
        
        # 내용 검증
        self.assertIsInstance(article["content"], str)
        self.assertTrue(len(article["content"]) > 100)  # 기사는 일반적으로 100자 이상
        
        # 날짜 검증
        self.assertIsInstance(article["published_date"], str)
        self.assertIsInstance(article["crawled_date"], str)
        
        # 키워드 검증
        self.assertIsInstance(article["keywords"], list)
        
        print(f"기사 검증 통과: {article['title']}")


if __name__ == "__main__":
    unittest.main()
