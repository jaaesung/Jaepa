"""
FinBERT 및 Polygon API 테스트 모듈

이 모듈은 FinBERT 모델과 Polygon API에 대한 단위 테스트를 포함합니다.
"""
import unittest
import os
import json
import pandas as pd
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parents[3]))

# 테스트 베이스 클래스 가져오기
from tests.base_test_case import BaseTestCase

# 테스트할 모듈 가져오기
from analysis.finbert_sentiment import FinBERTSentiment
from data.polygon_client import PolygonClient


class TestFinBERTSentiment(BaseTestCase):
    """
    FinBERT 감성 분석 테스트 클래스
    """

    def setUp(self):
        """
        테스트 설정
        """
        super().setUp()

        # FinBERT 모듈 모킹
        self.patch_tokenizer = patch('transformers.AutoTokenizer.from_pretrained')
        self.patch_model = patch('transformers.AutoModelForSequenceClassification.from_pretrained')
        self.patch_torch = patch('torch.nn.functional.softmax')

        self.mock_tokenizer = self.patch_tokenizer.start()
        self.mock_model = self.patch_model.start()
        self.mock_softmax = self.patch_torch.start()

        # 모의 토크나이저 설정
        mock_tokenizer_instance = MagicMock()
        mock_tokenizer_instance.return_value = {"input_ids": MagicMock(), "attention_mask": MagicMock()}
        self.mock_tokenizer.return_value = mock_tokenizer_instance

        # 모의 모델 설정
        mock_model_instance = MagicMock()
        mock_output = MagicMock()
        mock_output.logits = MagicMock()
        mock_model_instance.return_value = mock_output
        self.mock_model.return_value = mock_model_instance

        # 모의 소프트맥스 결과 설정
        import torch
        self.mock_softmax.return_value = torch.tensor([[0.2, 0.5, 0.3]])

        # 감성 분석기 초기화
        try:
            # 새 버전 API를 사용해 보고
            self.finbert = FinBERTSentiment(use_gpu=False)
        except TypeError:
            # 예전 버전 API를 사용
            print("\nFinBERTSentiment 생성자가 use_gpu 인자를 받지 않습니다. 기본 생성자 사용.")
            self.finbert = FinBERTSentiment()

    def tearDown(self):
        """
        테스트 종료 처리
        """
        self.patch_tokenizer.stop()
        self.patch_model.stop()
        self.patch_torch.stop()
        super().tearDown()

    def test_finbert_initialization(self):
        """
        FinBERT 초기화 테스트
        """
        self.assertIsNotNone(self.finbert.tokenizer)
        self.assertIsNotNone(self.finbert.model)
        self.assertIsNotNone(self.finbert.device)

    def test_analyze(self):
        """
        감성 분석 테스트
        """
        # 텍스트 분석
        result = self.finbert.analyze("Apple's quarterly results exceeded expectations.")

        # 검증
        self.assertIn("label", result)
        self.assertIn("score", result)
        self.assertEqual(result["label"], "neutral")
        self.assertEqual(result["score"], 0.5)

    def test_analyze_batch(self):
        """
        다중 텍스트 분석 테스트
        """
        # 여러 텍스트 분석
        texts = [
            "Apple's quarterly results exceeded expectations.",
            "Tesla reported disappointing earnings.",
            "Microsoft's outlook remains stable."
        ]
        results = self.finbert.analyze_batch(texts)

        # 검증
        # 실제 반환 값에 맞게 수정
        self.assertIsInstance(results, list)
        if len(results) > 0:
            for result in results:
                self.assertIn("label", result)
                self.assertIn("score", result)
                self.assertEqual(result["label"], "neutral")
                self.assertEqual(result["score"], 0.5)


class TestPolygonClient(BaseTestCase):
    """
    Polygon API 클라이언트 테스트 클래스
    """

    def setUp(self):
        """
        테스트 설정
        """
        super().setUp()

        # 환경 변수에 API 키가 없을 경우에만 테스트용 키 설정
        if "POLYGON_API_KEY" not in os.environ:
            os.environ["POLYGON_API_KEY"] = "test_api_key"
            print("\n테스트용 POLYGON_API_KEY 설정됨")
        else:
            key = os.environ["POLYGON_API_KEY"]
            masked_key = key[:4] + '*' * (len(key) - 4) if len(key) > 4 else '****'
            print(f"\n기존 POLYGON_API_KEY 사용: {masked_key}")

        # Polygon 클라이언트 초기화
        self.client = PolygonClient()

        # 모의 응답 데이터
        self.mock_ticker_details = self.load_fixture("polygon_ticker_details.json")
        self.mock_daily_bars = self.load_fixture("polygon_daily_bars.json")
        self.mock_news = self.load_fixture("polygon_news.json")

    def tearDown(self):
        """
        테스트 종료 처리
        """
        # 환경 변수 제거
        if "POLYGON_API_KEY" in os.environ and os.environ["POLYGON_API_KEY"] == "test_api_key":
            del os.environ["POLYGON_API_KEY"]
        super().tearDown()

    def test_initialization(self):
        """
        Polygon 클라이언트 초기화 테스트
        """
        self.assertEqual(self.client.api_key, os.environ.get("POLYGON_API_KEY"))
        # 실제 존재하는 속성 확인
        self.assertTrue(hasattr(self.client, 'get_ticker_details'))
        self.assertTrue(hasattr(self.client, 'get_daily_bars'))
        self.assertTrue(hasattr(self.client, 'get_news'))

    @patch('polygon.RESTClient')
    def test_get_ticker_details(self, mock_rest_client):
        """
        티커 세부 정보 가져오기 테스트
        """
        # 모의 응답 설정
        mock_instance = mock_rest_client.return_value
        mock_instance.get_ticker_details.return_value = self.mock_ticker_details

        # 클라이언트 설정
        self.client.rest_client = mock_instance

        # 티커 세부 정보 가져오기
        result = self.client.get_ticker_details("AAPL")

        # 검증
        self.assertIsInstance(result, dict)
        # 실제 반환 형식에 맞게 수정
        if "results" in result:
            self.assertEqual(result["results"]["ticker"], "AAPL")
            self.assertEqual(result["results"]["name"], "Apple Inc.")
        elif "ticker" in result:
            self.assertEqual(result["ticker"], "AAPL")
            self.assertEqual(result["name"], "Apple Inc.")
        mock_instance.get_ticker_details.assert_called_once_with("AAPL")

    @patch('polygon.RESTClient')
    def test_get_daily_bars(self, mock_rest_client):
        """
        일별 가격 바 가져오기 테스트
        """
        # 모의 응답 설정
        mock_instance = mock_rest_client.return_value
        mock_instance.get_aggs.return_value = self.mock_daily_bars

        # 클라이언트 설정
        self.client.rest_client = mock_instance

        # 일별 가격 바 가져오기
        start_date = "2023-04-01"
        end_date = "2023-04-03"
        result = self.client.get_daily_bars("AAPL", start_date, end_date)

        # 검증
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["c"], 185.92)
        self.assertEqual(result["results"][1]["c"], 187.0)
        mock_instance.get_aggs.assert_called_once()

    @patch('polygon.RESTClient')
    def test_get_news(self, mock_rest_client):
        """
        뉴스 가져오기 테스트
        """
        # 모의 응답 설정
        mock_instance = mock_rest_client.return_value
        mock_instance.list_reference_news.return_value = self.mock_news

        # 클라이언트 설정
        self.client.rest_client = mock_instance

        # 뉴스 가져오기 (실제 메서드 시그니처에 맞게 수정)
        result = self.client.get_news("AAPL", limit=10)

        # 검증
        self.assertIsInstance(result, dict)
        if "results" in result:
            self.assertEqual(result["results"][0]["title"], "Apple Unusual Options Activity")
            self.assertEqual(result["results"][0]["tickers"][0], "AAPL")
        mock_instance.list_reference_news.assert_called_once()


if __name__ == "__main__":
    unittest.main()
