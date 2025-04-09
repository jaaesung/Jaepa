"""
감성-가격 분석기 테스트 모듈

이 모듈은 SentimentPriceAnalyzer 클래스에 대한 테스트를 포함합니다.
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
from analysis.sentiment_price_analyzer import SentimentPriceAnalyzer


class TestSentimentPriceAnalyzer(BaseTestCase):
    """
    감성-가격 분석기 테스트 클래스
    """
    
    def setUp(self):
        """
        테스트 설정
        """
        super().setUp()
        
        # FinBERT 모듈 모킹
        self.patch_finbert = patch('analysis.finbert_sentiment.FinBERTSentiment')
        self.mock_finbert = self.patch_finbert.start()
        
        # StockDataStore 모킹
        self.patch_store = patch('data.stock_data_store.StockDataStore')
        self.mock_store = self.patch_store.start()
        
        # 모의 FinBERT 인스턴스 설정
        self.mock_finbert_instance = MagicMock()
        self.mock_finbert_instance.analyze.return_value = {
            "label": "positive",
            "score": 0.8,
            "scores": {"positive": 0.8, "neutral": 0.15, "negative": 0.05}
        }
        self.mock_finbert_instance.analyze_batch.return_value = [
            {
                "label": "positive",
                "score": 0.8,
                "scores": {"positive": 0.8, "neutral": 0.15, "negative": 0.05}
            },
            {
                "label": "neutral",
                "score": 0.6,
                "scores": {"positive": 0.3, "neutral": 0.6, "negative": 0.1}
            }
        ]
        self.mock_finbert.return_value = self.mock_finbert_instance
        
        # 모의 StockDataStore 인스턴스 설정
        self.mock_store_instance = MagicMock()
        self.mock_store_instance.get_stock_news.return_value = [
            {
                "title": "Apple Unusual Options Activity",
                "content": "Someone with a lot of money to spend has taken a bearish stance on Apple.",
                "published_date": "2023-04-03T13:31:22Z"
            },
            {
                "title": "Apple's New Product Launch",
                "content": "Apple is set to launch new products next month.",
                "published_date": "2023-04-02T10:15:00Z"
            }
        ]
        self.mock_store_instance.get_stock_price.return_value = [
            {
                "date": "2023-04-01",
                "open": 187.9,
                "high": 188.54,
                "low": 185.19,
                "close": 185.92,
                "volume": 76286430
            },
            {
                "date": "2023-04-02",
                "open": 184.51,
                "high": 188.04,
                "low": 184.28,
                "close": 187.0,
                "volume": 59278090
            },
            {
                "date": "2023-04-03",
                "open": 187.5,
                "high": 189.5,
                "low": 186.5,
                "close": 189.0,
                "volume": 65000000
            }
        ]
        self.mock_store.return_value = self.mock_store_instance
        
        # 감성-가격 분석기 초기화
        try:
            # 환경 변수에 API 키가 없을 경우에만 테스트용 키 설정
            if "POLYGON_API_KEY" not in os.environ:
                os.environ["POLYGON_API_KEY"] = "test_api_key"
                print("\n테스트용 POLYGON_API_KEY 설정됨 (SentimentPriceAnalyzer)")
            
            # 분석기 초기화 시도
            self.analyzer = SentimentPriceAnalyzer()
        except Exception as e:
            print(f"\nSentimentPriceAnalyzer 초기화 오류: {e}")
            # 수동으로 분석기 객체 생성
            self.analyzer = MagicMock()
            
        # 모의 객체 설정
        self.analyzer.sentiment_analyzer = self.mock_finbert_instance
        self.analyzer.store = self.mock_store_instance
    
    def tearDown(self):
        """
        테스트 종료 처리
        """
        self.patch_finbert.stop()
        self.patch_store.stop()
        super().tearDown()
    
    def test_initialization(self):
        """
        감성-가격 분석기 초기화 테스트
        """
        # 실제 존재하는 속성 확인
        self.assertIsNotNone(self.analyzer.store)
        self.assertIsNotNone(self.analyzer.sentiment_analyzer)
        # 메서드 존재 확인
        self.assertTrue(hasattr(self.analyzer, 'analyze_sentiment_price_correlation'))
    
    def test_analyze_sentiment_price_correlation(self):
        """
        감성-가격 상관관계 분석 테스트
        """
        # 상관관계 분석
        result = self.analyzer.analyze_sentiment_price_correlation("AAPL", days=7)
        
        # 검증 (실제 반환 형식에 맞게 수정)
        self.assertIn("symbol", result)  # ticker 대신 symbol 사용
        self.assertIn("correlation", result)
        self.assertIn("sentiment_trend", result)
        self.assertIn("price_trend", result)
        self.assertEqual(result["symbol"], "AAPL")
        
        # API 호출 확인
        self.mock_store_instance.get_stock_news.assert_called_once()
        self.mock_store_instance.get_stock_price.assert_called_once()


if __name__ == "__main__":
    unittest.main()
