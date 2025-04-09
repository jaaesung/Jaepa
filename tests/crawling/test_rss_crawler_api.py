"""
RSS 크롤링 API 테스트 모듈

NewsCrawler 클래스의 RSS 기능을 테스트합니다.
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

from crawling.news_crawler import NewsCrawler


class TestRSSCrawlerAPI(unittest.TestCase):
    """
    RSS 크롤링 API 테스트 클래스
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
    
    def tearDown(self):
        """
        테스트 종료 후 정리
        """
        self.crawler.close()
    
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
    
    @patch('feedparser.parse')
    def test_get_news_from_rss(self, mock_parse):
        """
        RSS 피드에서 뉴스 가져오기 테스트
        """
        # 모의 응답 설정
        mock_feed = MagicMock()
        mock_entry1 = MagicMock()
        mock_entry1.title = "Test News 1"
        mock_entry1.link = "https://example.com/news1"
        mock_entry1.summary = "This is a test news summary 1"
        mock_entry1.published_parsed = (2023, 4, 8, 10, 30, 0, 0, 0, 0)
        
        mock_entry2 = MagicMock()
        mock_entry2.title = "Test News 2"
        mock_entry2.link = "https://example.com/news2"
        mock_entry2.summary = "This is a test news summary 2"
        mock_entry2.published_parsed = (2023, 4, 8, 11, 30, 0, 0, 0, 0)
        
        mock_feed.entries = [mock_entry1, mock_entry2]
        mock_parse.return_value = mock_feed
        
        # requests.get 모의 설정
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"<xml></xml>"  # 아무 XML 내용
            mock_get.return_value = mock_response
            
            # RSS 피드에서 뉴스 가져오기
            news = self.crawler.get_news_from_rss(sources=["reuters"], count=2)
            
            # 검증
            self.assertEqual(len(news), 2)
            self.assertEqual(news[0]["title"], "Test News 1")
            self.assertEqual(news[1]["title"], "Test News 2")
            self.assertEqual(news[0]["url"], "https://example.com/news1")
            self.assertEqual(news[1]["url"], "https://example.com/news2")
    
    @patch('feedparser.parse')
    def test_search_news_from_rss(self, mock_parse):
        """
        RSS 피드에서 키워드로 뉴스 검색 테스트
        """
        # 모의 응답 설정
        mock_feed = MagicMock()
        mock_entry1 = MagicMock()
        mock_entry1.title = "Bitcoin Price Surges"
        mock_entry1.link = "https://example.com/bitcoin1"
        mock_entry1.summary = "Bitcoin price reaches new highs"
        mock_entry1.published_parsed = (2023, 4, 8, 10, 30, 0, 0, 0, 0)
        
        mock_entry2 = MagicMock()
        mock_entry2.title = "Ethereum Update"
        mock_entry2.link = "https://example.com/ethereum"
        mock_entry2.summary = "Ethereum network gets a new update"
        mock_entry2.published_parsed = (2023, 4, 8, 11, 30, 0, 0, 0, 0)
        
        mock_feed.entries = [mock_entry1, mock_entry2]
        mock_parse.return_value = mock_feed
        
        # requests.get 모의 설정
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"<xml></xml>"  # 아무 XML 내용
            mock_get.return_value = mock_response
            
            # RSS 피드에서 키워드로 뉴스 검색
            news = self.crawler.search_news_from_rss(keyword="bitcoin", days=7)
            
            # 검증
            self.assertEqual(len(news), 1)  # 제목이나 내용에 'bitcoin'이 포함된 항목만
            self.assertEqual(news[0]["title"], "Bitcoin Price Surges")
            self.assertEqual(news[0]["url"], "https://example.com/bitcoin1")

    @patch('feedparser.parse')
    def test_process_nasdaq_rss(self, mock_parse):
        """
        Nasdaq RSS 처리 함수 테스트
        """
        # 모의 응답 설정
        mock_entry = MagicMock()
        mock_entry.title = "NASDAQ NEWS: Stock Market Update"
        mock_entry.link = "https://nasdaq.com/news1"
        mock_entry.summary = "This is a nasdaq news summary"
        mock_entry.published_parsed = (2023, 4, 8, 10, 30, 0, 0, 0, 0)
        mock_entry.mediaImage = "https://nasdaq.com/image.jpg"
        
        # Nasdaq RSS 처리
        article = self.crawler._process_nasdaq_rss(mock_entry, "Nasdaq")
        
        # 검증
        self.assertEqual(article["title"], "NASDAQ NEWS: Stock Market Update")
        self.assertEqual(article["source"], "Nasdaq")
        self.assertEqual(article["source_type"], "rss")
        self.assertEqual(article["image_url"], "https://nasdaq.com/image.jpg")
        self.assertTrue(article["published_date"].startswith("2023-04-08"))

    @patch('feedparser.parse')
    def test_process_coindesk_rss(self, mock_parse):
        """
        CoinDesk RSS 처리 함수 테스트
        """
        # 모의 응답 설정
        mock_entry = MagicMock()
        mock_entry.title = "Bitcoin News Update"
        mock_entry.link = "https://coindesk.com/news1"
        mock_entry.summary = "This is a coindesk news summary"
        mock_entry.published_parsed = (2023, 4, 8, 10, 30, 0, 0, 0, 0)
        mock_entry.author = "John Doe"
        mock_entry.content = [MagicMock()]
        mock_entry.content[0].value = "<p>Full content of the article</p>"
        
        # CoinDesk RSS 처리
        article = self.crawler._process_coindesk_rss(mock_entry, "CoinDesk")
        
        # 검증
        self.assertEqual(article["title"], "Bitcoin News Update")
        self.assertEqual(article["source"], "CoinDesk")
        self.assertEqual(article["source_type"], "rss")
        self.assertEqual(article["author"], "John Doe")
        self.assertTrue("Full content of the article" in article["content"])
        self.assertTrue(article["published_date"].startswith("2023-04-08"))

    @patch('feedparser.parse')
    def test_process_generic_rss(self, mock_parse):
        """
        일반 RSS 처리 함수 테스트
        """
        # 모의 응답 설정
        mock_entry = MagicMock()
        mock_entry.title = "Generic RSS News"
        mock_entry.link = "https://example.com/news1"
        mock_entry.summary = "This is a generic news summary"
        mock_entry.published_parsed = (2023, 4, 8, 10, 30, 0, 0, 0, 0)
        
        # 일반 RSS 처리
        article = self.crawler._process_generic_rss(mock_entry, "Generic Source")
        
        # 검증
        self.assertEqual(article["title"], "Generic RSS News")
        self.assertEqual(article["source"], "Generic Source")
        self.assertEqual(article["source_type"], "rss")
        self.assertTrue(article["published_date"].startswith("2023-04-08"))


if __name__ == "__main__":
    unittest.main()
