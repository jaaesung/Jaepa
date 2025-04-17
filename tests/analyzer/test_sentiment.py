"""
감성 분석 테스트 모듈

감성 분석 모듈의 기능을 테스트합니다.
"""
import os
import json
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

import pytest
import torch
import numpy as np

from core.analyzer.sentiment_analyzer_interface import SentimentAnalyzerInterface, SentimentAnalysisResult
from core.analyzer.sentiment_pipeline import (
    SentimentPipeline, TextPreprocessor, ModelInferenceStage, PostProcessorStage
)
from core.analyzer.finbert_analyzer import FinBertSentimentAnalyzer
from core.analyzer.sentiment_enhancer import SentimentEnhancer, SentimentValidator, SentimentEnsemble


class TestSentimentAnalysisResult(unittest.TestCase):
    """SentimentAnalysisResult 클래스 테스트"""
    
    def test_init(self):
        """초기화 테스트"""
        result = SentimentAnalysisResult(
            label="positive",
            score=0.8,
            scores={"positive": 0.8, "negative": 0.1, "neutral": 0.1},
            confidence=0.9,
            language="en"
        )
        
        self.assertEqual(result.label, "positive")
        self.assertEqual(result.score, 0.8)
        self.assertEqual(result.scores, {"positive": 0.8, "negative": 0.1, "neutral": 0.1})
        self.assertEqual(result.confidence, 0.9)
        self.assertEqual(result.language, "en")
    
    def test_to_dict(self):
        """딕셔너리 변환 테스트"""
        result = SentimentAnalysisResult(
            label="positive",
            score=0.8,
            scores={"positive": 0.8, "negative": 0.1, "neutral": 0.1},
            confidence=0.9,
            language="en",
            metadata={"source": "test"}
        )
        
        expected = {
            "label": "positive",
            "score": 0.8,
            "scores": {"positive": 0.8, "negative": 0.1, "neutral": 0.1},
            "confidence": 0.9,
            "language": "en",
            "metadata": {"source": "test"}
        }
        
        self.assertEqual(result.to_dict(), expected)
    
    def test_from_dict(self):
        """딕셔너리에서 생성 테스트"""
        data = {
            "label": "positive",
            "score": 0.8,
            "scores": {"positive": 0.8, "negative": 0.1, "neutral": 0.1},
            "confidence": 0.9,
            "language": "en",
            "metadata": {"source": "test"}
        }
        
        result = SentimentAnalysisResult.from_dict(data)
        
        self.assertEqual(result.label, "positive")
        self.assertEqual(result.score, 0.8)
        self.assertEqual(result.scores, {"positive": 0.8, "negative": 0.1, "neutral": 0.1})
        self.assertEqual(result.confidence, 0.9)
        self.assertEqual(result.language, "en")
        self.assertEqual(result.metadata, {"source": "test"})
    
    def test_neutral(self):
        """중립 결과 생성 테스트"""
        result = SentimentAnalysisResult.neutral()
        
        self.assertEqual(result.label, "neutral")
        self.assertEqual(result.score, 1.0)
        self.assertEqual(result.scores, {"positive": 0.0, "negative": 0.0, "neutral": 1.0})
        self.assertEqual(result.confidence, 1.0)
        self.assertEqual(result.language, "en")


class TestTextPreprocessor(unittest.TestCase):
    """TextPreprocessor 클래스 테스트"""
    
    def test_process(self):
        """텍스트 전처리 테스트"""
        preprocessor = TextPreprocessor(
            remove_urls=True,
            remove_html_tags=True,
            normalize_whitespace=True
        )
        
        text = "Check out https://example.com for <b>more</b> info.   Multiple   spaces."
        expected = "Check out for more info. Multiple spaces."
        
        self.assertEqual(preprocessor.process(text), expected)
    
    def test_process_batch(self):
        """텍스트 배치 전처리 테스트"""
        preprocessor = TextPreprocessor(
            remove_urls=True,
            remove_html_tags=True,
            normalize_whitespace=True
        )
        
        texts = [
            "Check out https://example.com for <b>more</b> info.",
            "Another <span>example</span> with   spaces."
        ]
        
        expected = [
            "Check out for more info.",
            "Another example with spaces."
        ]
        
        self.assertEqual(preprocessor.process_batch(texts), expected)
    
    def test_financial_terms(self):
        """금융 용어 처리 테스트"""
        # 임시 금융 용어 사전 파일 생성
        financial_terms = {
            "bull market": "bullish market",
            "bear market": "bearish market"
        }
        
        with open("temp_financial_terms.json", "w") as f:
            json.dump(financial_terms, f)
        
        try:
            preprocessor = TextPreprocessor(
                financial_terms_path="temp_financial_terms.json"
            )
            
            text = "The stock is in a bull market, not a bear market."
            expected = "The stock is in a bullish market, not a bearish market."
            
            self.assertEqual(preprocessor.process(text), expected)
        finally:
            # 임시 파일 삭제
            os.remove("temp_financial_terms.json")


class TestModelInferenceStage(unittest.TestCase):
    """ModelInferenceStage 클래스 테스트"""
    
    def test_process(self):
        """모델 추론 테스트"""
        # 모의 모델 함수
        def mock_model(text):
            if text == "positive text":
                return "positive", {"positive": 0.8, "negative": 0.1, "neutral": 0.1}, text
            elif text == "negative text":
                return "negative", {"positive": 0.1, "negative": 0.8, "neutral": 0.1}, text
            else:
                return "neutral", {"positive": 0.1, "negative": 0.1, "neutral": 0.8}, text
        
        inference_stage = ModelInferenceStage(model_callable=mock_model)
        
        # 긍정 텍스트 테스트
        result = inference_stage.process("positive text")
        self.assertEqual(result[0], "positive")
        self.assertEqual(result[1], {"positive": 0.8, "negative": 0.1, "neutral": 0.1})
        
        # 부정 텍스트 테스트
        result = inference_stage.process("negative text")
        self.assertEqual(result[0], "negative")
        self.assertEqual(result[1], {"positive": 0.1, "negative": 0.8, "neutral": 0.1})
        
        # 중립 텍스트 테스트
        result = inference_stage.process("neutral text")
        self.assertEqual(result[0], "neutral")
        self.assertEqual(result[1], {"positive": 0.1, "negative": 0.1, "neutral": 0.8})
    
    def test_process_batch(self):
        """모델 배치 추론 테스트"""
        # 모의 모델 함수
        def mock_model(texts):
            results = []
            for text in texts:
                if text == "positive text":
                    results.append(("positive", {"positive": 0.8, "negative": 0.1, "neutral": 0.1}, text))
                elif text == "negative text":
                    results.append(("negative", {"positive": 0.1, "negative": 0.8, "neutral": 0.1}, text))
                else:
                    results.append(("neutral", {"positive": 0.1, "negative": 0.1, "neutral": 0.8}, text))
            return results
        
        inference_stage = ModelInferenceStage(model_callable=mock_model)
        
        texts = ["positive text", "negative text", "neutral text"]
        results = inference_stage.process_batch(texts)
        
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0][0], "positive")
        self.assertEqual(results[1][0], "negative")
        self.assertEqual(results[2][0], "neutral")


class TestPostProcessorStage(unittest.TestCase):
    """PostProcessorStage 클래스 테스트"""
    
    def test_process(self):
        """후처리 테스트"""
        postprocessor = PostProcessorStage(confidence_threshold=0.6)
        
        # 높은 신뢰도 결과 테스트
        result = postprocessor.process(("positive", {"positive": 0.8, "negative": 0.1, "neutral": 0.1}, "good news"))
        self.assertEqual(result.label, "positive")
        self.assertEqual(result.score, 0.8)
        self.assertEqual(result.confidence, 0.8)
        
        # 낮은 신뢰도 결과 테스트
        result = postprocessor.process(("positive", {"positive": 0.5, "negative": 0.3, "neutral": 0.2}, "uncertain news"))
        self.assertEqual(result.label, "neutral")  # 신뢰도가 낮아 중립으로 변경
        self.assertEqual(result.score, 1.0)
        self.assertEqual(result.confidence, 1.0)
    
    def test_process_batch(self):
        """배치 후처리 테스트"""
        postprocessor = PostProcessorStage(confidence_threshold=0.6)
        
        inference_results = [
            ("positive", {"positive": 0.8, "negative": 0.1, "neutral": 0.1}, "good news"),
            ("negative", {"positive": 0.1, "negative": 0.7, "neutral": 0.2}, "bad news"),
            ("positive", {"positive": 0.5, "negative": 0.3, "neutral": 0.2}, "uncertain news")
        ]
        
        results = postprocessor.process_batch(inference_results)
        
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].label, "positive")
        self.assertEqual(results[1].label, "negative")
        self.assertEqual(results[2].label, "neutral")  # 신뢰도가 낮아 중립으로 변경


class TestSentimentPipeline(unittest.TestCase):
    """SentimentPipeline 클래스 테스트"""
    
    def test_process(self):
        """파이프라인 처리 테스트"""
        # 모의 모델 함수
        def mock_model(text):
            if "positive" in text.lower():
                return "positive", {"positive": 0.8, "negative": 0.1, "neutral": 0.1}, text
            elif "negative" in text.lower():
                return "negative", {"positive": 0.1, "negative": 0.8, "neutral": 0.1}, text
            else:
                return "neutral", {"positive": 0.1, "negative": 0.1, "neutral": 0.8}, text
        
        # 파이프라인 구성
        preprocessor = TextPreprocessor()
        inference_stage = ModelInferenceStage(model_callable=mock_model)
        postprocessor = PostProcessorStage()
        
        pipeline = SentimentPipeline(
            preprocessor=preprocessor,
            inference_stage=inference_stage,
            postprocessor=postprocessor
        )
        
        # 긍정 텍스트 테스트
        result = pipeline.process("This is a positive news article.")
        self.assertEqual(result.label, "positive")
        
        # 부정 텍스트 테스트
        result = pipeline.process("This is a negative news article.")
        self.assertEqual(result.label, "negative")
        
        # 중립 텍스트 테스트
        result = pipeline.process("This is a neutral news article.")
        self.assertEqual(result.label, "neutral")
    
    def test_process_batch(self):
        """파이프라인 배치 처리 테스트"""
        # 모의 모델 함수
        def mock_model(texts):
            results = []
            for text in texts:
                if "positive" in text.lower():
                    results.append(("positive", {"positive": 0.8, "negative": 0.1, "neutral": 0.1}, text))
                elif "negative" in text.lower():
                    results.append(("negative", {"positive": 0.1, "negative": 0.8, "neutral": 0.1}, text))
                else:
                    results.append(("neutral", {"positive": 0.1, "negative": 0.1, "neutral": 0.8}, text))
            return results
        
        # 파이프라인 구성
        preprocessor = TextPreprocessor()
        inference_stage = ModelInferenceStage(model_callable=mock_model)
        postprocessor = PostProcessorStage()
        
        pipeline = SentimentPipeline(
            preprocessor=preprocessor,
            inference_stage=inference_stage,
            postprocessor=postprocessor
        )
        
        texts = [
            "This is a positive news article.",
            "This is a negative news article.",
            "This is a neutral news article."
        ]
        
        results = pipeline.process_batch(texts)
        
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].label, "positive")
        self.assertEqual(results[1].label, "negative")
        self.assertEqual(results[2].label, "neutral")


class TestFinBertSentimentAnalyzer(unittest.TestCase):
    """FinBertSentimentAnalyzer 클래스 테스트"""
    
    @patch('transformers.AutoModelForSequenceClassification.from_pretrained')
    @patch('transformers.AutoTokenizer.from_pretrained')
    def test_analyze(self, mock_tokenizer, mock_model):
        """감성 분석 테스트"""
        # 모의 토크나이저 설정
        mock_tokenizer_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_tokenizer_instance.return_value = {"input_ids": torch.tensor([[1, 2, 3]]), "attention_mask": torch.tensor([[1, 1, 1]])}
        
        # 모의 모델 설정
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance
        mock_model_instance.eval.return_value = None
        
        # 모의 출력 설정
        mock_outputs = MagicMock()
        mock_outputs.logits = torch.tensor([[0.1, 0.8, 0.1]])
        mock_model_instance.return_value = mock_outputs
        
        # 분석기 생성
        analyzer = FinBertSentimentAnalyzer(
            model_name="test_model",
            device="cpu",
            use_pipeline=False,
            lazy_loading=False
        )
        
        # 분석 수행
        result = analyzer.analyze("This is a test.")
        
        # 결과 검증
        self.assertIn("label", result)
        self.assertIn("score", result)
        self.assertIn("scores", result)
        self.assertIn("confidence", result)
    
    @patch('transformers.AutoModelForSequenceClassification.from_pretrained')
    @patch('transformers.AutoTokenizer.from_pretrained')
    def test_analyze_batch(self, mock_tokenizer, mock_model):
        """배치 감성 분석 테스트"""
        # 모의 토크나이저 설정
        mock_tokenizer_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_tokenizer_instance.return_value = {"input_ids": torch.tensor([[1, 2, 3], [4, 5, 6]]), "attention_mask": torch.tensor([[1, 1, 1], [1, 1, 1]])}
        
        # 모의 모델 설정
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance
        mock_model_instance.eval.return_value = None
        
        # 모의 출력 설정
        mock_outputs = MagicMock()
        mock_outputs.logits = torch.tensor([[0.1, 0.8, 0.1], [0.8, 0.1, 0.1]])
        mock_model_instance.return_value = mock_outputs
        
        # 분석기 생성
        analyzer = FinBertSentimentAnalyzer(
            model_name="test_model",
            device="cpu",
            use_pipeline=False,
            lazy_loading=False
        )
        
        # 분석 수행
        results = analyzer.analyze_batch(["This is a test.", "Another test."])
        
        # 결과 검증
        self.assertEqual(len(results), 2)
        self.assertIn("label", results[0])
        self.assertIn("score", results[0])
        self.assertIn("scores", results[0])
        self.assertIn("confidence", results[0])


class TestSentimentEnhancer(unittest.TestCase):
    """SentimentEnhancer 클래스 테스트"""
    
    def test_enhance_result(self):
        """감성 분석 결과 개선 테스트"""
        # 임시 키워드 가중치 파일 생성
        keyword_weights = {
            "excellent": {"positive": 1.5, "negative": 0.5, "neutral": 0.8},
            "terrible": {"positive": 0.5, "negative": 1.5, "neutral": 0.8}
        }
        
        with open("temp_keyword_weights.json", "w") as f:
            json.dump(keyword_weights, f)
        
        try:
            enhancer = SentimentEnhancer(
                keyword_weights_path="temp_keyword_weights.json"
            )
            
            # 긍정 키워드가 있는 텍스트
            result = {
                "label": "neutral",
                "score": 0.6,
                "scores": {"positive": 0.3, "negative": 0.1, "neutral": 0.6},
                "confidence": 0.6
            }
            
            enhanced = enhancer.enhance_result(result, "This is an excellent news article.")
            
            # 키워드 가중치 적용으로 긍정으로 변경되어야 함
            self.assertEqual(enhanced["label"], "positive")
            self.assertGreater(enhanced["scores"]["positive"], result["scores"]["positive"])
            
            # 부정 키워드가 있는 텍스트
            result = {
                "label": "neutral",
                "score": 0.6,
                "scores": {"positive": 0.3, "negative": 0.1, "neutral": 0.6},
                "confidence": 0.6
            }
            
            enhanced = enhancer.enhance_result(result, "This is a terrible news article.")
            
            # 키워드 가중치 적용으로 부정으로 변경되어야 함
            self.assertEqual(enhanced["label"], "negative")
            self.assertGreater(enhanced["scores"]["negative"], result["scores"]["negative"])
        finally:
            # 임시 파일 삭제
            os.remove("temp_keyword_weights.json")


class TestSentimentValidator(unittest.TestCase):
    """SentimentValidator 클래스 테스트"""
    
    def test_validate_result(self):
        """감성 분석 결과 검증 테스트"""
        validator = SentimentValidator(confidence_threshold=0.6)
        
        # 유효한 결과 테스트
        result = {
            "label": "positive",
            "score": 0.8,
            "scores": {"positive": 0.8, "negative": 0.1, "neutral": 0.1},
            "confidence": 0.8
        }
        
        validation = validator.validate_result(result)
        
        self.assertTrue(validation["is_valid"])
        self.assertTrue(validation["is_reliable"])
        self.assertEqual(validation["confidence"], 0.8)
        
        # 낮은 신뢰도 결과 테스트
        result = {
            "label": "positive",
            "score": 0.5,
            "scores": {"positive": 0.5, "negative": 0.3, "neutral": 0.2},
            "confidence": 0.5
        }
        
        validation = validator.validate_result(result)
        
        self.assertTrue(validation["is_valid"])
        self.assertFalse(validation["is_reliable"])
        self.assertEqual(validation["confidence"], 0.5)
    
    def test_validate_consistency(self):
        """기사 감성 일관성 검증 테스트"""
        # 모의 감성 분석기
        class MockAnalyzer(SentimentAnalyzerInterface):
            def analyze(self, text):
                if "positive" in text.lower():
                    return {"label": "positive", "confidence": 0.8, "scores": {"positive": 0.8, "negative": 0.1, "neutral": 0.1}}
                elif "negative" in text.lower():
                    return {"label": "negative", "confidence": 0.8, "scores": {"positive": 0.1, "negative": 0.8, "neutral": 0.1}}
                else:
                    return {"label": "neutral", "confidence": 0.8, "scores": {"positive": 0.1, "negative": 0.1, "neutral": 0.8}}
            
            def analyze_batch(self, texts, batch_size=None):
                return [self.analyze(text) for text in texts]
            
            def analyze_news(self, news):
                return news
            
            def analyze_news_batch(self, news_list, batch_size=None):
                return news_list
            
            def get_sentiment_trend(self, news_list, interval='day'):
                return {}
            
            def get_model_info(self):
                return {}
        
        validator = SentimentValidator(
            analyzer=MockAnalyzer(),
            confidence_threshold=0.6,
            consistency_threshold=0.5
        )
        
        # 일관된 기사 테스트
        article = {
            "title": "Positive news title",
            "content": "This is a positive news article."
        }
        
        result = validator.validate_consistency(article)
        
        self.assertTrue(result["is_consistent"])
        self.assertTrue(result["is_reliable"])
        self.assertEqual(result["title_sentiment"], "positive")
        self.assertEqual(result["content_sentiment"], "positive")
        
        # 불일치 기사 테스트
        article = {
            "title": "Positive news title",
            "content": "This is a negative news article."
        }
        
        result = validator.validate_consistency(article)
        
        self.assertFalse(result["is_consistent"])
        self.assertTrue(result["is_reliable"])
        self.assertEqual(result["title_sentiment"], "positive")
        self.assertEqual(result["content_sentiment"], "negative")


class TestSentimentEnsemble(unittest.TestCase):
    """SentimentEnsemble 클래스 테스트"""
    
    def test_analyze(self):
        """앙상블 감성 분석 테스트"""
        # 모의 감성 분석기 1
        class MockAnalyzer1(SentimentAnalyzerInterface):
            def analyze(self, text):
                return {"label": "positive", "score": 0.7, "scores": {"positive": 0.7, "negative": 0.2, "neutral": 0.1}, "confidence": 0.7}
            
            def analyze_batch(self, texts, batch_size=None):
                return [self.analyze(text) for text in texts]
            
            def analyze_news(self, news):
                return news
            
            def analyze_news_batch(self, news_list, batch_size=None):
                return news_list
            
            def get_sentiment_trend(self, news_list, interval='day'):
                return {}
            
            def get_model_info(self):
                return {}
        
        # 모의 감성 분석기 2
        class MockAnalyzer2(SentimentAnalyzerInterface):
            def analyze(self, text):
                return {"label": "neutral", "score": 0.6, "scores": {"positive": 0.3, "negative": 0.1, "neutral": 0.6}, "confidence": 0.6}
            
            def analyze_batch(self, texts, batch_size=None):
                return [self.analyze(text) for text in texts]
            
            def analyze_news(self, news):
                return news
            
            def analyze_news_batch(self, news_list, batch_size=None):
                return news_list
            
            def get_sentiment_trend(self, news_list, interval='day'):
                return {}
            
            def get_model_info(self):
                return {}
        
        # 앙상블 생성
        ensemble = SentimentEnsemble(
            analyzers=[MockAnalyzer1(), MockAnalyzer2()],
            weights=[0.7, 0.3]
        )
        
        # 분석 수행
        result = ensemble.analyze("This is a test.")
        
        # 결과 검증
        self.assertIn("label", result)
        self.assertIn("score", result)
        self.assertIn("scores", result)
        self.assertIn("confidence", result)
        self.assertIn("metadata", result)
        self.assertTrue(result["metadata"]["ensemble"])
        self.assertEqual(result["metadata"]["model_count"], 2)
    
    def test_analyze_batch(self):
        """앙상블 배치 감성 분석 테스트"""
        # 모의 감성 분석기 1
        class MockAnalyzer1(SentimentAnalyzerInterface):
            def analyze(self, text):
                return {"label": "positive", "score": 0.7, "scores": {"positive": 0.7, "negative": 0.2, "neutral": 0.1}, "confidence": 0.7}
            
            def analyze_batch(self, texts, batch_size=None):
                return [self.analyze(text) for text in texts]
            
            def analyze_news(self, news):
                return news
            
            def analyze_news_batch(self, news_list, batch_size=None):
                return news_list
            
            def get_sentiment_trend(self, news_list, interval='day'):
                return {}
            
            def get_model_info(self):
                return {}
        
        # 모의 감성 분석기 2
        class MockAnalyzer2(SentimentAnalyzerInterface):
            def analyze(self, text):
                return {"label": "neutral", "score": 0.6, "scores": {"positive": 0.3, "negative": 0.1, "neutral": 0.6}, "confidence": 0.6}
            
            def analyze_batch(self, texts, batch_size=None):
                return [self.analyze(text) for text in texts]
            
            def analyze_news(self, news):
                return news
            
            def analyze_news_batch(self, news_list, batch_size=None):
                return news_list
            
            def get_sentiment_trend(self, news_list, interval='day'):
                return {}
            
            def get_model_info(self):
                return {}
        
        # 앙상블 생성
        ensemble = SentimentEnsemble(
            analyzers=[MockAnalyzer1(), MockAnalyzer2()],
            weights=[0.7, 0.3]
        )
        
        # 분석 수행
        results = ensemble.analyze_batch(["This is a test.", "Another test."])
        
        # 결과 검증
        self.assertEqual(len(results), 2)
        self.assertIn("label", results[0])
        self.assertIn("score", results[0])
        self.assertIn("scores", results[0])
        self.assertIn("confidence", results[0])
        self.assertIn("metadata", results[0])
        self.assertTrue(results[0]["metadata"]["ensemble"])
        self.assertEqual(results[0]["metadata"]["model_count"], 2)


if __name__ == '__main__':
    unittest.main()
