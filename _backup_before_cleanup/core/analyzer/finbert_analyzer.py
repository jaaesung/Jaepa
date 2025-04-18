"""
FinBERT 감성 분석기 모듈

FinBERT 모델을 사용하여 금융 텍스트의 감성을 분석합니다.
"""
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from collections import defaultdict

import torch
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from dotenv import load_dotenv

from core.analyzer.sentiment_analyzer_interface import SentimentAnalyzerInterface, SentimentAnalysisResult
from core.analyzer.sentiment_pipeline import (
    SentimentPipeline, TextPreprocessor, ModelInferenceStage, PostProcessorStage
)

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
env_path = Path(__file__).parents[2] / '.env'
load_dotenv(dotenv_path=env_path)


class FinBertSentimentAnalyzer(SentimentAnalyzerInterface):
    """
    FinBERT 모델을 사용한 금융 텍스트 감성 분석
    
    이 클래스는 FinBERT 모델을 사용하여 금융 뉴스 및 텍스트의 감성을 분석합니다.
    """
    
    def __init__(self, 
                model_name: Optional[str] = None, 
                device: Optional[str] = None,
                use_pipeline: bool = True,
                lazy_loading: bool = True,
                financial_terms_path: Optional[str] = None,
                keyword_weights_path: Optional[str] = None,
                confidence_threshold: float = 0.6):
        """
        FinBERT 감성 분석기 초기화
        
        Args:
            model_name: 사용할 모델 이름 (기본값: 환경 변수에서 가져옴)
            device: 사용할 장치 ('cuda' 또는 'cpu', 기본값: 자동 감지)
            use_pipeline: 파이프라인 사용 여부
            lazy_loading: 지연 로딩 사용 여부
            financial_terms_path: 금융 용어 사전 파일 경로
            keyword_weights_path: 키워드 가중치 파일 경로
            confidence_threshold: 신뢰도 임계값
        """
        # 모델 이름 설정
        self.model_name = model_name or os.getenv("FINBERT_MODEL_PATH", "yiyanghkust/finbert-tone")
        
        # 장치 설정 (GPU 또는 CPU)
        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 지연 로딩 설정
        self.lazy_loading = lazy_loading
        
        # 모델 및 토크나이저 초기화
        self._tokenizer = None
        self._model = None
        self._is_model_loaded = False
        
        # 레이블 설정
        self.labels = ["negative", "neutral", "positive"]
        
        # 파이프라인 설정
        self.use_pipeline = use_pipeline
        self.pipeline = None
        
        # 파이프라인 구성 요소 경로
        self.financial_terms_path = financial_terms_path
        self.keyword_weights_path = keyword_weights_path
        self.confidence_threshold = confidence_threshold
        
        # 지연 로딩을 사용하지 않는 경우 즉시 모델 로드
        if not lazy_loading:
            self._load_model()
            
            # 파이프라인 초기화
            if use_pipeline:
                self._initialize_pipeline()
        
        logger.info(f"FinBERT 감성 분석기 초기화 완료 (모델: {self.model_name}, 장치: {self.device}, 지연 로딩: {lazy_loading})")
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        텍스트의 감성 분석
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            Dict[str, Any]: 감성 분석 결과
        """
        if not text or len(text.strip()) == 0:
            return SentimentAnalysisResult.neutral().to_dict()
        
        try:
            # 모델이 로드되지 않은 경우 로드
            if not self._is_model_loaded:
                self._load_model()
                
                # 파이프라인 초기화
                if self.use_pipeline and not self.pipeline:
                    self._initialize_pipeline()
            
            # 파이프라인 사용
            if self.use_pipeline and self.pipeline:
                result = self.pipeline.process(text)
                return result.to_dict()
            
            # 직접 모델 사용
            return self._analyze_with_model(text)
            
        except Exception as e:
            logger.error(f"감성 분석 중 오류 발생: {str(e)}")
            return SentimentAnalysisResult.neutral().to_dict()
    
    def analyze_batch(self, texts: List[str], batch_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        여러 텍스트의 감성 분석
        
        Args:
            texts: 분석할 텍스트 목록
            batch_size: 배치 크기 (None인 경우 자동 결정)
            
        Returns:
            List[Dict[str, Any]]: 감성 분석 결과 목록
        """
        if not texts:
            return []
        
        try:
            # 모델이 로드되지 않은 경우 로드
            if not self._is_model_loaded:
                self._load_model()
                
                # 파이프라인 초기화
                if self.use_pipeline and not self.pipeline:
                    self._initialize_pipeline()
            
            # 배치 크기 결정
            if batch_size is None:
                # GPU 메모리에 따라 배치 크기 자동 조정
                if self.device == "cuda":
                    # 텍스트 길이에 따라 배치 크기 조정
                    avg_length = sum(len(text.split()) for text in texts) / len(texts)
                    if avg_length > 500:
                        batch_size = 4
                    elif avg_length > 200:
                        batch_size = 8
                    else:
                        batch_size = 16
                else:
                    batch_size = 32
            
            # 파이프라인 사용
            if self.use_pipeline and self.pipeline:
                results = self.pipeline.process_batch(texts, batch_size)
                return [result.to_dict() for result in results]
            
            # 직접 모델 사용
            results = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                batch_results = self._analyze_batch_with_model(batch)
                results.extend(batch_results)
            
            return results
            
        except Exception as e:
            logger.error(f"배치 감성 분석 중 오류 발생: {str(e)}")
            return [SentimentAnalysisResult.neutral().to_dict()] * len(texts)
    
    def analyze_news(self, news: Dict[str, Any]) -> Dict[str, Any]:
        """
        뉴스 기사의 감성 분석
        
        Args:
            news: 뉴스 기사 데이터
            
        Returns:
            Dict[str, Any]: 감성 분석이 추가된 뉴스 기사 데이터
        """
        # 뉴스 기사 복사
        news_with_sentiment = news.copy()
        
        # 분석할 텍스트 준비
        title = news.get("title", "")
        content = news.get("content", "")
        summary = news.get("summary", "")
        
        # 제목과 내용 또는 요약을 결합하여 분석
        if content:
            text = f"{title}. {content}"
        elif summary:
            text = f"{title}. {summary}"
        else:
            text = title
        
        # 감성 분석 수행
        sentiment = self.analyze(text)
        
        # 결과 추가
        news_with_sentiment["sentiment"] = sentiment
        
        return news_with_sentiment
    
    def analyze_news_batch(self, news_list: List[Dict[str, Any]], batch_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        여러 뉴스 기사의 감성 분석
        
        Args:
            news_list: 뉴스 기사 데이터 목록
            batch_size: 배치 크기 (None인 경우 자동 결정)
            
        Returns:
            List[Dict[str, Any]]: 감성 분석이 추가된 뉴스 기사 데이터 목록
        """
        # 뉴스 기사 복사
        news_with_sentiment = [news.copy() for news in news_list]
        
        # 분석할 텍스트 준비
        texts = []
        for news in news_list:
            title = news.get("title", "")
            content = news.get("content", "")
            summary = news.get("summary", "")
            
            if content:
                text = f"{title}. {content}"
            elif summary:
                text = f"{title}. {summary}"
            else:
                text = title
                
            texts.append(text)
        
        # 감성 분석 수행
        sentiments = self.analyze_batch(texts, batch_size)
        
        # 결과 추가
        for i, sentiment in enumerate(sentiments):
            news_with_sentiment[i]["sentiment"] = sentiment
        
        return news_with_sentiment
    
    def get_sentiment_trend(self, news_list: List[Dict[str, Any]], interval: str = 'day') -> Dict[str, Any]:
        """
        뉴스 기사 감성 트렌드 분석
        
        Args:
            news_list: 뉴스 기사 데이터 목록
            interval: 집계 간격 ('hour', 'day', 'week', 'month')
            
        Returns:
            Dict[str, Any]: 감성 트렌드 분석 결과
        """
        if not news_list:
            return {
                "trends": [],
                "summary": {
                    "average_score": 0.0,
                    "positive_ratio": 0.0,
                    "negative_ratio": 0.0,
                    "neutral_ratio": 0.0,
                    "article_count": 0
                }
            }
        
        # 감성 분석이 없는 뉴스 기사 분석
        news_to_analyze = []
        for i, news in enumerate(news_list):
            if "sentiment" not in news:
                news_to_analyze.append((i, news))
        
        if news_to_analyze:
            analyzed_news = self.analyze_news_batch([news for _, news in news_to_analyze])
            for i, (idx, _) in enumerate(news_to_analyze):
                news_list[idx] = analyzed_news[i]
        
        # 날짜별 감성 집계
        interval_sentiments = defaultdict(list)
        
        for news in news_list:
            # 발행일 추출
            published_date = news.get("published_date", "")
            if not published_date:
                continue
            
            # 날짜 파싱
            try:
                if isinstance(published_date, str):
                    date_obj = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                else:
                    date_obj = published_date
            except (ValueError, TypeError):
                continue
            
            # 간격에 따라 날짜 포맷 결정
            if interval == 'hour':
                interval_key = date_obj.strftime('%Y-%m-%dT%H:00:00')
            elif interval == 'day':
                interval_key = date_obj.strftime('%Y-%m-%d')
            elif interval == 'week':
                # 주의 시작일(월요일)로 설정
                week_start = date_obj - timedelta(days=date_obj.weekday())
                interval_key = week_start.strftime('%Y-%m-%d')
            elif interval == 'month':
                interval_key = date_obj.strftime('%Y-%m-01')
            else:
                interval_key = date_obj.strftime('%Y-%m-%d')
            
            # 감성 정보 추출
            sentiment = news.get("sentiment", {})
            if not sentiment:
                continue
            
            # 감성 점수 계산
            scores = sentiment.get("scores", {})
            if not scores:
                continue
            
            # 간격별 감성 저장
            interval_sentiments[interval_key].append({
                "label": sentiment.get("label", "neutral"),
                "score": sentiment.get("score", 0.0),
                "scores": scores
            })
        
        # 트렌드 생성
        trends = []
        
        # 감성 통계
        total_score = 0.0
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_count = 0
        
        for interval_key, sentiments in sorted(interval_sentiments.items()):
            # 간격별 감성 통계
            interval_scores = {
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 0.0
            }
            
            interval_score = 0.0
            
            # 감성 집계
            for sentiment in sentiments:
                label = sentiment.get("label", "neutral")
                score = sentiment.get("score", 0.0)
                scores = sentiment.get("scores", {})
                
                # 레이블별 카운트 증가
                if label == "positive":
                    positive_count += 1
                elif label == "negative":
                    negative_count += 1
                else:
                    neutral_count += 1
                
                # 전체 점수 누적
                total_score += score
                interval_score += score
                
                # 레이블별 점수 누적
                for label, score in scores.items():
                    interval_scores[label] += score
            
            # 간격별 평균 계산
            count = len(sentiments)
            total_count += count
            
            if count > 0:
                interval_score /= count
                for label in interval_scores:
                    interval_scores[label] /= count
            
            # 트렌드 추가
            trends.append({
                "interval": interval_key,
                "sentiment": {
                    "score": interval_score,
                    "positive": interval_scores["positive"],
                    "negative": interval_scores["negative"],
                    "neutral": interval_scores["neutral"]
                },
                "count": count
            })
        
        # 요약 통계
        summary = {
            "average_score": total_score / total_count if total_count > 0 else 0.0,
            "positive_ratio": positive_count / total_count if total_count > 0 else 0.0,
            "negative_ratio": negative_count / total_count if total_count > 0 else 0.0,
            "neutral_ratio": neutral_count / total_count if total_count > 0 else 0.0,
            "article_count": total_count
        }
        
        return {
            "trends": trends,
            "summary": summary
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        감성 분석 모델 정보 반환
        
        Returns:
            Dict[str, Any]: 모델 정보
        """
        return {
            "name": "FinBERT",
            "version": "1.0",
            "description": "금융 도메인에 특화된 BERT 기반 감성 분석 모델",
            "language": "en",
            "provider": "yiyanghkust/finbert-tone",
            "labels": self.labels,
            "device": self.device
        }
    
    def _load_model(self) -> None:
        """
        모델 및 토크나이저 로드
        """
        try:
            logger.info(f"FinBERT 모델 로드 중: {self.model_name} (장치: {self.device})")
            
            # 토크나이저 로드
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # 모델 로드
            self._model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            
            # 모델을 지정된 장치로 이동
            self._model.to(self.device)
            
            # 평가 모드로 설정
            self._model.eval()
            
            self._is_model_loaded = True
            
            logger.info("FinBERT 모델 로드 완료")
        except Exception as e:
            logger.error(f"FinBERT 모델 로드 실패: {str(e)}")
            raise
    
    def _initialize_pipeline(self) -> None:
        """
        감성 분석 파이프라인 초기화
        """
        try:
            logger.info("감성 분석 파이프라인 초기화 중")
            
            # 텍스트 전처리기 생성
            preprocessor = TextPreprocessor(
                financial_terms_path=self.financial_terms_path
            )
            
            # 모델 추론 단계 생성
            inference_stage = ModelInferenceStage(
                model_callable=self._model_inference
            )
            
            # 후처리 단계 생성
            postprocessor = PostProcessorStage(
                confidence_threshold=self.confidence_threshold,
                keyword_weights_path=self.keyword_weights_path
            )
            
            # 파이프라인 생성
            self.pipeline = SentimentPipeline(
                preprocessor=preprocessor,
                inference_stage=inference_stage,
                postprocessor=postprocessor
            )
            
            logger.info("감성 분석 파이프라인 초기화 완료")
        except Exception as e:
            logger.error(f"감성 분석 파이프라인 초기화 실패: {str(e)}")
            self.pipeline = None
    
    def _model_inference(self, texts: Union[str, List[str]]) -> Union[Tuple[str, Dict[str, float], str], List[Tuple[str, Dict[str, float], str]]]:
        """
        모델 추론 함수
        
        Args:
            texts: 추론할 텍스트 또는 텍스트 목록
            
        Returns:
            Union[Tuple[str, Dict[str, float], str], List[Tuple[str, Dict[str, float], str]]]: 
                추론 결과 (레이블, 점수 딕셔너리, 원본 텍스트) 또는 결과 목록
        """
        # 단일 텍스트 처리
        if isinstance(texts, str):
            return self._inference_single(texts)
        
        # 텍스트 목록 처리
        return [self._inference_single(text) for text in texts]
    
    def _inference_single(self, text: str) -> Tuple[str, Dict[str, float], str]:
        """
        단일 텍스트 추론
        
        Args:
            text: 추론할 텍스트
            
        Returns:
            Tuple[str, Dict[str, float], str]: 추론 결과 (레이블, 점수 딕셔너리, 원본 텍스트)
        """
        # 텍스트 토큰화
        inputs = self._tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # 모델 추론
        with torch.no_grad():
            outputs = self._model(**inputs)
        
        # 결과 처리
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        probabilities = probabilities.cpu().numpy()[0]
        
        # 가장 높은 확률의 레이블 찾기
        label_idx = np.argmax(probabilities)
        label = self.labels[label_idx]
        
        # 점수 딕셔너리 생성
        scores = {self.labels[i]: float(probabilities[i]) for i in range(len(self.labels))}
        
        return label, scores, text
    
    def _analyze_with_model(self, text: str) -> Dict[str, Any]:
        """
        모델을 직접 사용한 감성 분석
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            Dict[str, Any]: 감성 분석 결과
        """
        # 텍스트 토큰화
        inputs = self._tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # 모델 추론
        with torch.no_grad():
            outputs = self._model(**inputs)
        
        # 결과 처리
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        probabilities = probabilities.cpu().numpy()[0]
        
        # 가장 높은 확률의 레이블 찾기
        label_idx = np.argmax(probabilities)
        label = self.labels[label_idx]
        score = probabilities[label_idx]
        
        # 결과 반환
        return {
            "label": label,
            "score": float(score),
            "scores": {
                self.labels[i]: float(probabilities[i]) for i in range(len(self.labels))
            },
            "confidence": float(score),
            "language": "en"
        }
    
    def _analyze_batch_with_model(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        모델을 직접 사용한 배치 감성 분석
        
        Args:
            texts: 분석할 텍스트 목록
            
        Returns:
            List[Dict[str, Any]]: 감성 분석 결과 목록
        """
        # 텍스트 토큰화
        inputs = self._tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # 모델 추론
        with torch.no_grad():
            outputs = self._model(**inputs)
        
        # 결과 처리
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        probabilities = probabilities.cpu().numpy()
        
        # 결과 목록 생성
        results = []
        for i, probs in enumerate(probabilities):
            # 가장 높은 확률의 레이블 찾기
            label_idx = np.argmax(probs)
            label = self.labels[label_idx]
            score = probs[label_idx]
            
            # 결과 추가
            results.append({
                "label": label,
                "score": float(score),
                "scores": {
                    self.labels[j]: float(probs[j]) for j in range(len(self.labels))
                },
                "confidence": float(score),
                "language": "en"
            })
        
        return results
