"""
감성 분석 API 테스트 모듈

SentimentAnalyzer 클래스의 API 기능을 테스트합니다.
"""
import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import torch
import numpy as np

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parents[2]))

from crawling.news_crawler import SentimentAnalyzer


class TestSentimentAnalyzerAPI(unittest.TestCase):
    """
    감성 분석기 API 테스트 클래스
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
        
        # 테스트 텍스트
        self.positive_text = "The company reported strong earnings growth, exceeding market expectations. Investors responded positively to the news."
        self.negative_text = "The stock plummeted after the company announced disappointing quarterly results, falling short of analyst estimates."
        self.neutral_text = "The market remained steady today as investors await the Federal Reserve's decision on interest rates."
    
    @patch('torch.nn.functional.softmax')
    def test_analyze_positive(self, mock_softmax):
        """
        긍정 텍스트 분석 테스트
        """
        # 모의 설정
        mock_outputs = MagicMock()
        mock_outputs.logits = torch.tensor([[0.1, 0.3, 0.6]])
        self.mock_model.return_value = mock_outputs
        
        mock_softmax.return_value = torch.tensor([[0.1, 0.3, 0.6]])
        
        # 분석 실행
        result = self.analyzer.analyze(self.positive_text)
        
        # 검증
        self.assertIsNotNone(result)
        self.assertEqual(result["negative"], 0.1)
        self.assertEqual(result["neutral"], 0.3)
        self.assertEqual(result["positive"], 0.6)
    
    @patch('torch.nn.functional.softmax')
    def test_analyze_negative(self, mock_softmax):
        """
        부정 텍스트 분석 테스트
        """
        # 모의 설정
        mock_outputs = MagicMock()
        mock_outputs.logits = torch.tensor([[0.7, 0.2, 0.1]])
        self.mock_model.return_value = mock_outputs
        
        mock_softmax.return_value = torch.tensor([[0.7, 0.2, 0.1]])
        
        # 분석 실행
        result = self.analyzer.analyze(self.negative_text)
        
        # 검증
        self.assertIsNotNone(result)
        self.assertEqual(result["negative"], 0.7)
        self.assertEqual(result["neutral"], 0.2)
        self.assertEqual(result["positive"], 0.1)
    
    @patch('torch.nn.functional.softmax')
    def test_analyze_neutral(self, mock_softmax):
        """
        중립 텍스트 분석 테스트
        """
        # 모의 설정
        mock_outputs = MagicMock()
        mock_outputs.logits = torch.tensor([[0.2, 0.6, 0.2]])
        self.mock_model.return_value = mock_outputs
        
        mock_softmax.return_value = torch.tensor([[0.2, 0.6, 0.2]])
        
        # 분석 실행
        result = self.analyzer.analyze(self.neutral_text)
        
        # 검증
        self.assertIsNotNone(result)
        self.assertEqual(result["negative"], 0.2)
        self.assertEqual(result["neutral"], 0.6)
        self.assertEqual(result["positive"], 0.2)
    
    @patch('torch.nn.functional.softmax')
    def test_analyze_batch(self, mock_softmax):
        """
        텍스트 배치 분석 테스트
        """
        # 모의 설정
        mock_outputs = MagicMock()
        mock_outputs.logits = torch.tensor([
            [0.7, 0.2, 0.1],  # negative
            [0.2, 0.6, 0.2],  # neutral
            [0.1, 0.3, 0.6]   # positive
        ])
        self.mock_model.return_value = mock_outputs
        
        mock_softmax.return_value = torch.tensor([
            [0.7, 0.2, 0.1],
            [0.2, 0.6, 0.2],
            [0.1, 0.3, 0.6]
        ])
        
        # 배치 분석 실행
        texts = [self.negative_text, self.neutral_text, self.positive_text]
        results = self.analyzer.analyze_batch(texts)
        
        # 검증
        self.assertEqual(len(results), 3)
        
        # 첫 번째 텍스트 (부정)
        self.assertEqual(results[0]["negative"], 0.7)
        self.assertEqual(results[0]["neutral"], 0.2)
        self.assertEqual(results[0]["positive"], 0.1)
        
        # 두 번째 텍스트 (중립)
        self.assertEqual(results[1]["negative"], 0.2)
        self.assertEqual(results[1]["neutral"], 0.6)
        self.assertEqual(results[1]["positive"], 0.2)
        
        # 세 번째 텍스트 (긍정)
        self.assertEqual(results[2]["negative"], 0.1)
        self.assertEqual(results[2]["neutral"], 0.3)
        self.assertEqual(results[2]["positive"], 0.6)
    
    def test_analyze_empty_text(self):
        """
        빈 텍스트 분석 테스트
        """
        # 빈 텍스트 분석
        result = self.analyzer.analyze("")
        
        # 검증
        self.assertIsNone(result)
        self.mock_model.assert_not_called()
    
    def test_device_selection(self):
        """
        장치 선택 테스트
        """
        # GPU 사용 가능 시 GPU로 모델 이동
        self.assertIsNotNone(self.analyzer.device)
        self.assertIn(self.analyzer.device.type, ["cpu", "cuda"])


if __name__ == "__main__":
    unittest.main()
