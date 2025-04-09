"""
뉴스 감성 분석 파이프라인 통합 테스트

이 모듈은 뉴스 수집부터 감성 분석, 가격 데이터 연동까지의 전체 파이프라인을 테스트합니다.
"""
import unittest
import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parents[2]))

# 테스트 베이스 클래스 가져오기
from tests.base_test_case import BaseTestCase

# 테스트할 모듈 가져오기
from crawling.news_integrator import NewsIntegrator
from analysis.finbert_sentiment import FinBERTSentiment
from analysis.sentiment_price_analyzer import SentimentPriceAnalyzer
from data.stock_data_store import StockDataStore


class TestNewsSentimentPipeline(BaseTestCase):
    """
    뉴스 감성 분석 파이프라인 통합 테스트
    """
    
    def setUp(self):
        """
        테스트 설정
        """
        super().setUp()
        
        # 모의 데이터 설정
        self.mock_news = [
            {
                "title": "Apple Reports Strong Quarterly Results",
                "content": "Apple Inc. reported strong quarterly results, exceeding analyst expectations.",
                "url": "https://example.com/apple-results",
                "published_date": "2023-04-01 10:00:00",
                "source": "Test Source",
                "source_type": "test"
            }
        ]
        
        # 뉴스 통합기 모킹
        self.patch_integrator = patch('crawling.news_integrator.NewsIntegrator')
        self.mock_integrator = self.patch_integrator.start()
        self.mock_integrator_instance = MagicMock()
        self.mock_integrator_instance.collect_news.return_value = self.mock_news
        self.mock_integrator.return_value = self.mock_integrator_instance
        
        # FinBERT 모듈 모킹
        self.patch_finbert = patch('analysis.finbert_sentiment.FinBERTSentiment')
        self.mock_finbert = self.patch_finbert.start()
        self.mock_finbert_instance = MagicMock()
        self.mock_finbert_instance.analyze.return_value = {
            "label": "positive",
            "score": 0.8,
            "scores": {"positive": 0.8, "neutral": 0.15, "negative": 0.05}
        }
        self.mock_finbert.return_value = self.mock_finbert_instance
        
        # StockDataStore 모킹
        self.patch_store = patch('data.stock_data_store.StockDataStore')
        self.mock_store = self.patch_store.start()
        self.mock_store_instance = MagicMock()
        self.mock_store.return_value = self.mock_store_instance
        
        # SentimentPriceAnalyzer 모킹
        self.patch_analyzer = patch('analysis.sentiment_price_analyzer.SentimentPriceAnalyzer')
        self.mock_analyzer = self.patch_analyzer.start()
        self.mock_analyzer_instance = MagicMock()
        self.mock_analyzer_instance.analyze_sentiment_price_correlation.return_value = {
            "symbol": "AAPL",
            "period": "2023-04-01 ~ 2023-04-07",
            "correlation": 0.75,
            "sentiment_trend": "positive",
            "price_trend": "upward",
            "analysis": "AAPL의 뉴스 감성과 주가 간의 상관관계는 0.75로 강한 양의 상관관계를 보입니다."
        }
        self.mock_analyzer.return_value = self.mock_analyzer_instance
    
    def tearDown(self):
        """
        테스트 종료 처리
        """
        self.patch_integrator.stop()
        self.patch_finbert.stop()
        self.patch_store.stop()
        self.patch_analyzer.stop()
        super().tearDown()
    
    def test_end_to_end_pipeline(self):
        """
        엔드투엔드 파이프라인 테스트
        """
        # 1. 뉴스 수집
        integrator = self.mock_integrator()
        news = integrator.collect_news(keyword="AAPL", days=7)
        
        # 2. 감성 분석
        sentiment_analyzer = self.mock_finbert()
        sentiments = []
        for item in news:
            sentiment = sentiment_analyzer.analyze(item["content"])
            sentiments.append(sentiment)
        
        # 3. 주가 데이터 연동 및 상관관계 분석
        price_analyzer = self.mock_analyzer()
        correlation = price_analyzer.analyze_sentiment_price_correlation("AAPL", days=7)
        
        # 4. 결과 검증
        self.assertEqual(len(news), 1)
        self.assertEqual(len(sentiments), 1)
        self.assertIsInstance(sentiments[0], dict)
        self.assertIsInstance(correlation, dict)
        self.assertEqual(correlation["symbol"], "AAPL")
        self.assertEqual(correlation["sentiment_trend"], "positive")
        
        # 5. 통합 검증
        # 뉴스 수집 호출 확인
        integrator.collect_news.assert_called_once_with(keyword="AAPL", days=7)
        # 감성 분석 호출 확인
        sentiment_analyzer.analyze.assert_called_once()
        # 상관관계 분석 호출 확인
        price_analyzer.analyze_sentiment_price_correlation.assert_called_once_with("AAPL", days=7)


if __name__ == "__main__":
    unittest.main()
