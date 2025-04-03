"""
뉴스 크롤러 단계별 테스트 모듈

이 모듈은 NewsCrawler 클래스의 기능을 단계별로 테스트합니다.
"""
import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# 상위 디렉토리 추가하여 jaepa 패키지 import 가능하게 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from crawling.news_crawler import NewsCrawler, SentimentAnalyzer

class TestNewsCrawlerStepByStep(unittest.TestCase):
    """NewsCrawler 클래스 단계별 테스트"""

    def setUp(self):
        """테스트 셋업: 크롤러 및 목 데이터 초기화"""
        # DB 연결 없이 크롤러 객체 생성
        self.crawler = NewsCrawler(db_connect=False)
        
        # 테스트 기사 HTML 로드
        test_article_path = os.path.join(os.path.dirname(__file__), 'mock_article.html')
        if os.path.exists(test_article_path):
            with open(test_article_path, 'r', encoding='utf-8') as f:
                self.mock_article_html = f.read()
        else:
            # 목 HTML이 없는 경우 간단한 HTML 생성
            self.mock_article_html = """
            <html>
                <head><title>Test Article Title</title></head>
                <body>
                    <div class="article-content">
                        <p>This is a test article paragraph 1.</p>
                        <p>This is a test article paragraph 2.</p>
                    </div>
                    <div class="article-date">2023-04-01</div>
                </body>
            </html>
            """
            
        # 테스트 검색 결과 HTML 로드
        test_search_path = os.path.join(os.path.dirname(__file__), 'mock_search_results.html')
        if os.path.exists(test_search_path):
            with open(test_search_path, 'r', encoding='utf-8') as f:
                self.mock_search_html = f.read()
        else:
            # 목 HTML이 없는 경우 간단한 HTML 생성
            self.mock_search_html = """
            <html>
                <body>
                    <div class="search-results">
                        <div class="search-result-title">
                            <a href="/article1">Test Article 1</a>
                        </div>
                        <div class="search-result-title">
                            <a href="/article2">Test Article 2</a>
                        </div>
                    </div>
                </body>
            </html>
            """

    def test_get_request_headers(self):
        """요청 헤더 생성 테스트"""
        headers = self.crawler._get_request_headers()
        self.assertIsInstance(headers, dict)
        self.assertIn('User-Agent', headers)
        self.assertEqual(headers['User-Agent'], self.crawler.request_settings['user_agent'])

    @patch('requests.get')
    def test_make_request_success(self, mock_get):
        """HTTP 요청 성공 테스트"""
        # 성공적인 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = self.mock_article_html
        mock_get.return_value = mock_response
        
        # 함수 호출
        result = self.crawler._make_request("https://example.com/test")
        
        # 결과 검증
        self.assertEqual(result, self.mock_article_html)
        mock_get.assert_called_once()
        
        # 헤더와 타임아웃 설정 검증
        call_kwargs = mock_get.call_args[1]
        self.assertIn('headers', call_kwargs)
        self.assertIn('timeout', call_kwargs)

    @patch('requests.get')
    def test_make_request_http_error(self, mock_get):
        """HTTP 오류 처리 테스트"""
        # HTTP 오류 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # 함수 호출
        result = self.crawler._make_request("https://example.com/not-found")
        
        # 결과 검증: 오류 시 None 반환
        self.assertIsNone(result)

    @patch('requests.get')
    def test_make_request_network_error(self, mock_get):
        """네트워크 오류 처리 테스트"""
        # 네트워크 예외 발생 설정
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        # 함수 호출
        result = self.crawler._make_request("https://example.com/test")
        
        # 결과 검증: 오류 시 None 반환
        self.assertIsNone(result)
        
        # 재시도 횟수 검증
        self.assertEqual(mock_get.call_count, self.crawler.request_settings['retries'] + 1)

    @patch.object(NewsCrawler, '_make_request')
    @patch.object(NewsCrawler, '_scrape_article')
    def test_search_news(self, mock_scrape, mock_request):
        """뉴스 검색 테스트"""
        # 목 응답 설정
        mock_request.return_value = self.mock_search_html
        
        # 목 기사 데이터 설정
        mock_article = {
            "url": "https://reuters.com/article1",
            "title": "Test Article 1",
            "content": "Test content",
            "source": "reuters",
            "published_date": "2023-04-01T00:00:00",
            "keywords": ["test", "article"]
        }
        mock_scrape.return_value = mock_article
        
        # 함수 호출
        result = self.crawler.search_news("test", days=1, sources=["reuters"])
        
        # 결과 검증
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)  # 목 HTML에는 2개 기사 링크 있음
        
        # 스크래핑 호출 검증
        self.assertEqual(mock_scrape.call_count, 2)

    @patch.object(NewsCrawler, '_make_request')
    def test_scrape_article(self, mock_request):
        """기사 스크래핑 테스트"""
        # 목 응답 설정
        mock_request.return_value = self.mock_article_html
        
        # 소스 설정 수정
        self.crawler.sources["reuters"]["content_selector"] = ".article-content p"
        self.crawler.sources["reuters"]["date_selector"] = ".article-date"
        self.crawler.sources["reuters"]["date_format"] = "%Y-%m-%d"
        
        # 함수 호출
        result = self.crawler._scrape_article("https://reuters.com/test-article", "reuters")
        
        # 결과 검증
        self.assertIsInstance(result, dict)
        self.assertEqual(result["url"], "https://reuters.com/test-article")
        self.assertEqual(result["source"], "reuters")
        self.assertIn("title", result)
        self.assertIn("content", result)
        self.assertIn("published_date", result)
        self.assertIn("keywords", result)

    def test_extract_keywords(self):
        """키워드 추출 테스트"""
        # 테스트 텍스트
        text = "The Federal Reserve raised interest rates by 0.25 percentage points on Wednesday. This marks the tenth consecutive rate hike as the central bank continues its fight against inflation."
        
        # 함수 호출
        keywords = self.crawler._extract_keywords(text)
        
        # 결과 검증
        self.assertIsInstance(keywords, list)
        self.assertLessEqual(len(keywords), 10)  # 최대 10개 키워드
        
        # 흔한 단어 포함 검증
        common_words = ["federal", "reserve", "interest", "rates", "inflation"]
        for word in common_words:
            if word in keywords:
                break
        else:
            self.fail("None of the expected common words found in keywords")

    @patch('requests.get')
    def test_end_to_end_workflow(self, mock_get):
        """전체 워크플로우 테스트"""
        # 검색 페이지 응답 설정
        search_response = MagicMock()
        search_response.status_code = 200
        search_response.text = self.mock_search_html
        
        # 기사 페이지 응답 설정
        article_response = MagicMock()
        article_response.status_code = 200
        article_response.text = self.mock_article_html
        
        # mock_get가 URL에 따라 다른 응답 반환하도록 설정
        def mock_get_side_effect(*args, **kwargs):
            url = args[0]
            if "search" in url:
                return search_response
            else:
                return article_response
                
        mock_get.side_effect = mock_get_side_effect
        
        # 소스 설정 수정
        self.crawler.sources["reuters"]["content_selector"] = ".article-content p"
        self.crawler.sources["reuters"]["date_selector"] = ".article-date"
        self.crawler.sources["reuters"]["date_format"] = "%Y-%m-%d"
        
        # 함수 호출
        results = self.crawler.search_news("test", days=1, sources=["reuters"])
        
        # 결과 검증
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def tearDown(self):
        """테스트 완료 후 정리"""
        self.crawler.close()


class TestSentimentAnalyzer(unittest.TestCase):
    """SentimentAnalyzer 클래스 테스트"""
    
    @patch('transformers.AutoModelForSequenceClassification.from_pretrained')
    @patch('transformers.AutoTokenizer.from_pretrained')
    @patch('torch.device')
    def test_sentiment_analyzer_init(self, mock_device, mock_tokenizer, mock_model):
        """감성 분석기 초기화 테스트"""
        # 목 설정
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance
        mock_tokenizer_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_device.return_value = "cpu"
        
        # 분석기 초기화
        analyzer = SentimentAnalyzer()
        
        # 초기화 검증
        self.assertIsNotNone(analyzer.model)
        self.assertIsNotNone(analyzer.tokenizer)
        self.assertEqual(analyzer.labels, ["negative", "neutral", "positive"])
        
        # model.to() 호출 검증
        mock_model_instance.to.assert_called_once()

    @patch.object(SentimentAnalyzer, '__init__', return_value=None)
    def test_analyze_method(self, mock_init):
        """감성 분석 메서드 테스트"""
        # 목 설정
        analyzer = SentimentAnalyzer()
        analyzer.model = MagicMock()
        analyzer.tokenizer = MagicMock()
        analyzer.device = "cpu"
        analyzer.labels = ["negative", "neutral", "positive"]
        
        # 토크나이저 반환값 설정
        mock_inputs = {"input_ids": MagicMock(), "attention_mask": MagicMock()}
        analyzer.tokenizer.return_value = mock_inputs
        
        # 모델 출력 설정
        mock_outputs = MagicMock()
        mock_outputs.logits = MagicMock()
        analyzer.model.return_value = mock_outputs
        
        # torch 함수 목 패치
        with patch('torch.nn.functional.softmax', return_value=MagicMock()):
            with patch.object(mock_outputs.logits, 'cpu', return_value=mock_outputs.logits):
                with patch.object(mock_outputs.logits, 'numpy', return_value=[[0.2, 0.3, 0.5]]):
                    # 함수 호출
                    result = analyzer.analyze("Test text")
                    
                    # 결과 검증
                    self.assertIsInstance(result, dict)
                    self.assertEqual(len(result), 3)
                    self.assertIn("positive", result)
                    self.assertIn("neutral", result)
                    self.assertIn("negative", result)
                    self.assertEqual(result["positive"], 0.5)
                    self.assertEqual(result["neutral"], 0.3)
                    self.assertEqual(result["negative"], 0.2)


if __name__ == '__main__':
    unittest.main()
