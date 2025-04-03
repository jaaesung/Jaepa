"""
감성 분석 테스트 모듈

금융 뉴스 감성 분석 기능을 테스트합니다.
"""
import unittest
import sys
from pathlib import Path
import json
import numpy as np
from unittest.mock import patch, MagicMock

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parents[2]))

from crawling.sentiment_analysis import FinancialSentimentAnalyzer, SentimentAnalysisResultValidator


class TestFinancialSentimentAnalyzer(unittest.TestCase):
    """
    금융 감성 분석기 테스트 클래스
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
        self.analyzer = FinancialSentimentAnalyzer(model_name="test-model")
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
        import torch
        mock_outputs = MagicMock()
        mock_outputs.logits = torch.tensor([[0.1, 0.2, 0.7]])
        self.mock_model.return_value = mock_outputs
        
        mock_softmax.return_value = torch.tensor([[0.1, 0.2, 0.7]])
        
        # 분석 실행
        result = self.analyzer.analyze(self.positive_text)
        
        # 검증
        self.assertIsNotNone(result)
        self.assertEqual(result["sentiment"], "positive")
        self.assertAlmostEqual(result["confidence"], 0.7)
        self.assertTrue(result["is_reliable"])
    
    @patch('torch.nn.functional.softmax')
    def test_analyze_negative(self, mock_softmax):
        """
        부정 텍스트 분석 테스트
        """
        # 모의 설정
        import torch
        mock_outputs = MagicMock()
        mock_outputs.logits = torch.tensor([[0.8, 0.1, 0.1]])
        self.mock_model.return_value = mock_outputs
        
        mock_softmax.return_value = torch.tensor([[0.8, 0.1, 0.1]])
        
        # 분석 실행
        result = self.analyzer.analyze(self.negative_text)
        
        # 검증
        self.assertIsNotNone(result)
        self.assertEqual(result["sentiment"], "negative")
        self.assertAlmostEqual(result["confidence"], 0.8)
        self.assertTrue(result["is_reliable"])
    
    @patch('torch.nn.functional.softmax')
    def test_analyze_neutral(self, mock_softmax):
        """
        중립 텍스트 분석 테스트
        """
        # 모의 설정
        import torch
        mock_outputs = MagicMock()
        mock_outputs.logits = torch.tensor([[0.2, 0.6, 0.2]])
        self.mock_model.return_value = mock_outputs
        
        mock_softmax.return_value = torch.tensor([[0.2, 0.6, 0.2]])
        
        # 분석 실행
        result = self.analyzer.analyze(self.neutral_text)
        
        # 검증
        self.assertIsNotNone(result)
        self.assertEqual(result["sentiment"], "neutral")
        self.assertAlmostEqual(result["confidence"], 0.6)
        self.assertFalse(result["is_reliable"])  # 0.6 < 0.7 임계값
    
    @patch('torch.nn.functional.softmax')
    def test_analyze_empty_text(self, mock_softmax):
        """
        빈 텍스트 분석 테스트
        """
        # 빈 텍스트 분석
        result = self.analyzer.analyze("")
        
        # 검증
        self.assertIsNone(result)
        mock_softmax.assert_not_called()
    
    @patch('torch.nn.functional.softmax')
    def test_analyze_batch(self, mock_softmax):
        """
        텍스트 배치 분석 테스트
        """
        # 모의 설정
        import torch
        mock_outputs = MagicMock()
        mock_outputs.logits = torch.tensor([
            [0.8, 0.1, 0.1],  # negative
            [0.2, 0.6, 0.2],  # neutral
            [0.1, 0.2, 0.7]   # positive
        ])
        self.mock_model.return_value = mock_outputs
        
        mock_softmax.return_value = torch.tensor([
            [0.8, 0.1, 0.1],
            [0.2, 0.6, 0.2],
            [0.1, 0.2, 0.7]
        ])
        
        # 배치 분석 실행
        texts = [self.negative_text, self.neutral_text, self.positive_text]
        results = self.analyzer.analyze_batch(texts)
        
        # 검증
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["sentiment"], "negative")
        self.assertEqual(results[1]["sentiment"], "neutral")
        self.assertEqual(results[2]["sentiment"], "positive")
    
    @patch('torch.nn.functional.softmax')
    def test_analyze_with_context(self, mock_softmax):
        """
        헤드라인과 문맥을 함께 고려한 분석 테스트
        """
        # 모의 설정
        import torch
        
        # 첫 번째 호출 (헤드라인 분석)에 대한 응답
        first_mock_outputs = MagicMock()
        first_mock_outputs.logits = torch.tensor([[0.1, 0.2, 0.7]])  # positive
        
        # 두 번째 호출 (내용 분석)에 대한 응답
        second_mock_outputs = MagicMock()
        second_mock_outputs.logits = torch.tensor([[0.2, 0.1, 0.7]])  # positive
        
        self.mock_model.side_effect = [first_mock_outputs, second_mock_outputs]
        
        mock_softmax.side_effect = [
            torch.tensor([[0.1, 0.2, 0.7]]),
            torch.tensor([[0.2, 0.1, 0.7]])
        ]
        
        # 분석 실행
        headline = "Company reports record earnings"
        result = self.analyzer.analyze_with_context(self.positive_text, headline)
        
        # 검증
        self.assertIsNotNone(result)
        self.assertEqual(result["headline_sentiment"], "positive")
        self.assertEqual(result["content_sentiment"], "positive")
        self.assertEqual(result["sentiment"], "positive")
        
        # 다른 감성의 경우
        # 첫 번째 호출 (헤드라인 분석)에 대한 응답 재설정
        self.mock_model.side_effect = None
        third_mock_outputs = MagicMock()
        third_mock_outputs.logits = torch.tensor([[0.7, 0.2, 0.1]])  # negative
        
        # 두 번째 호출 (내용 분석)에 대한 응답 재설정
        fourth_mock_outputs = MagicMock()
        fourth_mock_outputs.logits = torch.tensor([[0.2, 0.1, 0.7]])  # positive
        
        self.mock_model.side_effect = [third_mock_outputs, fourth_mock_outputs]
        
        mock_softmax.side_effect = [
            torch.tensor([[0.7, 0.2, 0.1]]),
            torch.tensor([[0.2, 0.1, 0.7]])
        ]
        
        # 분석 실행
        negative_headline = "Despite growth, company faces challenges"
        result = self.analyzer.analyze_with_context(self.positive_text, negative_headline)
        
        # 검증 - 가중 평균에 따른 결과 확인
        self.assertIsNotNone(result)
        self.assertEqual(result["headline_sentiment"], "negative")
        self.assertEqual(result["content_sentiment"], "positive")
        # 헤드라인이 부정적이고 더 높은 가중치를 가지므로, 최종 감성은 부정적일 가능성이 높음


class TestSentimentAnalysisResultValidator(unittest.TestCase):
    """
    감성 분석 결과 검증기 테스트 클래스
    """
    
    def setUp(self):
        """
        테스트 설정
        """
        # 금융 감성 분석기 모의 설정
        self.mock_analyzer = MagicMock()
        
        # 감성 분석 결과 검증기 초기화
        self.validator = SentimentAnalysisResultValidator(analyzer=self.mock_analyzer)
        
        # 테스트 기사 데이터
        self.article = {
            "title": "Stock Market Surges to New Highs",
            "content": "The stock market reached record highs today as investors reacted positively to economic data.",
            "url": "https://example.com/article1"
        }
    
    def test_validate_consistency_both_positive(self):
        """
        둘 다 긍정적인 경우 일관성 검증 테스트
        """
        # 모의 분석 결과
        self.mock_analyzer.analyze.side_effect = [
            {
                "sentiment": "positive",
                "confidence": 0.8,
                "is_reliable": True
            },
            {
                "sentiment": "positive",
                "confidence": 0.9,
                "is_reliable": True
            }
        ]
        
        # 일관성 검증 실행
        result = self.validator.validate_consistency(self.article)
        
        # 검증
        self.assertTrue(result["is_consistent"])
        self.assertTrue(result["is_reliable"])
        self.assertEqual(result["title_sentiment"], "positive")
        self.assertEqual(result["content_sentiment"], "positive")
    
    def test_validate_consistency_different_sentiments(self):
        """
        서로 다른 감성의 경우 일관성 검증 테스트
        """
        # 모의 분석 결과
        self.mock_analyzer.analyze.side_effect = [
            {
                "sentiment": "positive",
                "confidence": 0.8,
                "is_reliable": True
            },
            {
                "sentiment": "negative",
                "confidence": 0.9,
                "is_reliable": True
            }
        ]
        
        # 일관성 검증 실행
        result = self.validator.validate_consistency(self.article)
        
        # 검증
        self.assertFalse(result["is_consistent"])
        self.assertTrue(result["is_reliable"])
        self.assertEqual(result["title_sentiment"], "positive")
        self.assertEqual(result["content_sentiment"], "negative")
    
    def test_validate_consistency_unreliable(self):
        """
        신뢰도가 낮은 경우 일관성 검증 테스트
        """
        # 모의 분석 결과
        self.mock_analyzer.analyze.side_effect = [
            {
                "sentiment": "positive",
                "confidence": 0.6,
                "is_reliable": False
            },
            {
                "sentiment": "positive",
                "confidence": 0.9,
                "is_reliable": True
            }
        ]
        
        # 일관성 검증 실행
        result = self.validator.validate_consistency(self.article)
        
        # 검증
        self.assertTrue(result["is_consistent"])
        self.assertFalse(result["is_reliable"])
    
    def test_validate_batch(self):
        """
        여러 기사 일괄 검증 테스트
        """
        # 테스트 기사 데이터
        articles = [
            {
                "title": "Stock Market Surges to New Highs",
                "content": "The stock market reached record highs today as investors reacted positively to economic data.",
                "url": "https://example.com/article1"
            },
            {
                "title": "Company Announces Layoffs",
                "content": "The company announced significant layoffs due to economic downturn.",
                "url": "https://example.com/article2"
            },
            {
                "title": "Market Remains Steady",
                "content": "The market showed little movement today as investors await economic reports.",
                "url": "https://example.com/article3"
            }
        ]
        
        # 모의 분석 결과
        self.mock_analyzer.analyze.side_effect = [
            # 첫 번째 기사 (일관된 긍정)
            {
                "sentiment": "positive",
                "confidence": 0.8,
                "is_reliable": True
            },
            {
                "sentiment": "positive",
                "confidence": 0.9,
                "is_reliable": True
            },
            # 두 번째 기사 (일관된 부정)
            {
                "sentiment": "negative",
                "confidence": 0.8,
                "is_reliable": True
            },
            {
                "sentiment": "negative",
                "confidence": 0.9,
                "is_reliable": True
            },
            # 세 번째 기사 (비일관적)
            {
                "sentiment": "neutral",
                "confidence": 0.8,
                "is_reliable": True
            },
            {
                "sentiment": "positive",
                "confidence": 0.6,
                "is_reliable": False
            }
        ]
        
        # 일괄 검증 실행
        result = self.validator.validate_batch(articles)
        
        # 검증
        self.assertEqual(result["total_articles"], 3)
        self.assertEqual(result["consistent_count"], 2)  # 첫 번째 및 두 번째 기사만 일관적
        self.assertEqual(result["reliable_count"], 2)    # 첫 번째 및 두 번째 기사만 신뢰할 수 있음
        self.assertAlmostEqual(result["consistency_ratio"], 2/3)
        self.assertAlmostEqual(result["reliability_ratio"], 2/3)
        
        # 감성 분포 확인
        self.assertIn("sentiment_distribution", result)
        
        # 상세 결과 확인
        self.assertEqual(len(result["detailed_results"]), 3)
    
    def test_validate_invalid_article(self):
        """
        유효하지 않은 기사 데이터 검증 테스트
        """
        # 유효하지 않은 기사 데이터
        invalid_article = {
            "title": "Stock Market News",
            # 내용 누락
            "url": "https://example.com/article"
        }
        
        # 일관성 검증 실행
        result = self.validator.validate_consistency(invalid_article)
        
        # 검증
        self.assertFalse(result["is_consistent"])
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
