"""
감성 분석 파이프라인 모듈

텍스트 전처리, 모델 추론, 결과 후처리 등의 단계를 포함하는 감성 분석 파이프라인을 제공합니다.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Callable, Tuple

from core.analyzer.sentiment_analyzer_interface import SentimentAnalysisResult

# 로깅 설정
logger = logging.getLogger(__name__)


class PipelineStage(ABC):
    """
    파이프라인 단계 인터페이스
    
    감성 분석 파이프라인의 각 단계를 정의하는 인터페이스입니다.
    """
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """
        입력 데이터 처리
        
        Args:
            input_data: 처리할 입력 데이터
            
        Returns:
            Any: 처리된 출력 데이터
        """
        pass
    
    @abstractmethod
    def process_batch(self, input_batch: List[Any]) -> List[Any]:
        """
        입력 데이터 배치 처리
        
        Args:
            input_batch: 처리할 입력 데이터 배치
            
        Returns:
            List[Any]: 처리된 출력 데이터 배치
        """
        pass


class TextPreprocessor(PipelineStage):
    """
    텍스트 전처리 단계
    
    텍스트 정규화, 특수 문자 처리, 금융 용어 처리 등을 수행합니다.
    """
    
    def __init__(self, 
                remove_urls: bool = True, 
                remove_html_tags: bool = True,
                normalize_whitespace: bool = True,
                financial_terms_path: Optional[str] = None):
        """
        TextPreprocessor 초기화
        
        Args:
            remove_urls: URL 제거 여부
            remove_html_tags: HTML 태그 제거 여부
            normalize_whitespace: 공백 정규화 여부
            financial_terms_path: 금융 용어 사전 파일 경로
        """
        self.remove_urls = remove_urls
        self.remove_html_tags = remove_html_tags
        self.normalize_whitespace = normalize_whitespace
        
        # 금융 용어 사전 로드
        self.financial_terms = {}
        if financial_terms_path:
            try:
                self._load_financial_terms(financial_terms_path)
                logger.info(f"금융 용어 사전 로드 완료: {len(self.financial_terms)}개 용어")
            except Exception as e:
                logger.error(f"금융 용어 사전 로드 실패: {str(e)}")
    
    def process(self, text: str) -> str:
        """
        텍스트 전처리
        
        Args:
            text: 전처리할 텍스트
            
        Returns:
            str: 전처리된 텍스트
        """
        if not text:
            return ""
        
        # 텍스트 정규화
        processed_text = text
        
        # URL 제거
        if self.remove_urls:
            import re
            processed_text = re.sub(r'https?://\S+|www\.\S+', ' ', processed_text)
        
        # HTML 태그 제거
        if self.remove_html_tags:
            import re
            processed_text = re.sub(r'<.*?>', ' ', processed_text)
        
        # 공백 정규화
        if self.normalize_whitespace:
            import re
            processed_text = re.sub(r'\s+', ' ', processed_text).strip()
        
        # 금융 용어 처리
        processed_text = self._process_financial_terms(processed_text)
        
        return processed_text
    
    def process_batch(self, texts: List[str]) -> List[str]:
        """
        텍스트 배치 전처리
        
        Args:
            texts: 전처리할 텍스트 목록
            
        Returns:
            List[str]: 전처리된 텍스트 목록
        """
        return [self.process(text) for text in texts]
    
    def _load_financial_terms(self, file_path: str) -> None:
        """
        금융 용어 사전 로드
        
        Args:
            file_path: 금융 용어 사전 파일 경로
        """
        import json
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.financial_terms = json.load(f)
        except Exception as e:
            logger.error(f"금융 용어 사전 로드 실패: {str(e)}")
            self.financial_terms = {}
    
    def _process_financial_terms(self, text: str) -> str:
        """
        금융 용어 처리
        
        Args:
            text: 처리할 텍스트
            
        Returns:
            str: 처리된 텍스트
        """
        if not self.financial_terms:
            return text
        
        processed_text = text
        
        # 금융 용어 치환
        for term, replacement in self.financial_terms.items():
            processed_text = processed_text.replace(term, replacement)
        
        return processed_text


class ModelInferenceStage(PipelineStage):
    """
    모델 추론 단계
    
    모델을 사용하여 텍스트의 감성을 분석합니다.
    """
    
    def __init__(self, model_callable: Callable[[Union[str, List[str]]], Any]):
        """
        ModelInferenceStage 초기화
        
        Args:
            model_callable: 모델 추론 함수
        """
        self.model_callable = model_callable
    
    def process(self, text: str) -> Any:
        """
        모델 추론
        
        Args:
            text: 추론할 텍스트
            
        Returns:
            Any: 모델 추론 결과
        """
        try:
            return self.model_callable(text)
        except Exception as e:
            logger.error(f"모델 추론 실패: {str(e)}")
            return None
    
    def process_batch(self, texts: List[str]) -> List[Any]:
        """
        모델 배치 추론
        
        Args:
            texts: 추론할 텍스트 목록
            
        Returns:
            List[Any]: 모델 추론 결과 목록
        """
        try:
            return self.model_callable(texts)
        except Exception as e:
            logger.error(f"모델 배치 추론 실패: {str(e)}")
            return [None] * len(texts)


class PostProcessorStage(PipelineStage):
    """
    후처리 단계
    
    모델 추론 결과를 표준화된 형식으로 변환합니다.
    """
    
    def __init__(self, 
                confidence_threshold: float = 0.6,
                apply_keyword_weights: bool = True,
                keyword_weights_path: Optional[str] = None):
        """
        PostProcessorStage 초기화
        
        Args:
            confidence_threshold: 신뢰도 임계값
            apply_keyword_weights: 키워드 가중치 적용 여부
            keyword_weights_path: 키워드 가중치 파일 경로
        """
        self.confidence_threshold = confidence_threshold
        self.apply_keyword_weights = apply_keyword_weights
        
        # 키워드 가중치 로드
        self.keyword_weights = {}
        if apply_keyword_weights and keyword_weights_path:
            try:
                self._load_keyword_weights(keyword_weights_path)
                logger.info(f"키워드 가중치 로드 완료: {len(self.keyword_weights)}개 키워드")
            except Exception as e:
                logger.error(f"키워드 가중치 로드 실패: {str(e)}")
    
    def process(self, inference_result: Tuple[str, Dict[str, float], Optional[str]]) -> SentimentAnalysisResult:
        """
        추론 결과 후처리
        
        Args:
            inference_result: 모델 추론 결과 (레이블, 점수 딕셔너리, 원본 텍스트)
            
        Returns:
            SentimentAnalysisResult: 표준화된 감성 분석 결과
        """
        if inference_result is None:
            return SentimentAnalysisResult.neutral()
        
        label, scores, original_text = inference_result
        
        # 신뢰도 계산
        confidence = scores.get(label, 0.0)
        
        # 키워드 가중치 적용
        if self.apply_keyword_weights and original_text:
            adjusted_scores = self._apply_keyword_weights(scores, original_text)
            
            # 가중치 적용 후 레이블 재결정
            if adjusted_scores != scores:
                label = max(adjusted_scores, key=adjusted_scores.get)
                confidence = adjusted_scores.get(label, 0.0)
                scores = adjusted_scores
        
        # 신뢰도 임계값 적용
        if confidence < self.confidence_threshold:
            metadata = {"original_label": label, "original_confidence": confidence}
            return SentimentAnalysisResult(
                label="neutral",
                score=1.0,
                scores={"positive": 0.0, "negative": 0.0, "neutral": 1.0},
                confidence=1.0,
                metadata=metadata
            )
        
        return SentimentAnalysisResult(
            label=label,
            score=scores.get(label, 0.0),
            scores=scores,
            confidence=confidence
        )
    
    def process_batch(self, inference_results: List[Tuple[str, Dict[str, float], Optional[str]]]) -> List[SentimentAnalysisResult]:
        """
        추론 결과 배치 후처리
        
        Args:
            inference_results: 모델 추론 결과 목록
            
        Returns:
            List[SentimentAnalysisResult]: 표준화된 감성 분석 결과 목록
        """
        return [self.process(result) for result in inference_results]
    
    def _load_keyword_weights(self, file_path: str) -> None:
        """
        키워드 가중치 로드
        
        Args:
            file_path: 키워드 가중치 파일 경로
        """
        import json
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.keyword_weights = json.load(f)
        except Exception as e:
            logger.error(f"키워드 가중치 로드 실패: {str(e)}")
            self.keyword_weights = {}
    
    def _apply_keyword_weights(self, scores: Dict[str, float], text: str) -> Dict[str, float]:
        """
        키워드 가중치 적용
        
        Args:
            scores: 감성 점수 딕셔너리
            text: 원본 텍스트
            
        Returns:
            Dict[str, float]: 가중치가 적용된 감성 점수 딕셔너리
        """
        if not self.keyword_weights:
            return scores
        
        adjusted_scores = scores.copy()
        
        # 텍스트를 소문자로 변환
        text_lower = text.lower()
        
        # 키워드 가중치 적용
        for keyword, weights in self.keyword_weights.items():
            if keyword.lower() in text_lower:
                for sentiment, weight in weights.items():
                    if sentiment in adjusted_scores:
                        adjusted_scores[sentiment] *= weight
        
        # 점수 정규화
        total = sum(adjusted_scores.values())
        if total > 0:
            adjusted_scores = {k: v / total for k, v in adjusted_scores.items()}
        
        return adjusted_scores


class SentimentPipeline:
    """
    감성 분석 파이프라인
    
    텍스트 전처리, 모델 추론, 결과 후처리 등의 단계를 포함하는 파이프라인을 제공합니다.
    """
    
    def __init__(self, 
                preprocessor: Optional[TextPreprocessor] = None,
                inference_stage: Optional[ModelInferenceStage] = None,
                postprocessor: Optional[PostProcessorStage] = None):
        """
        SentimentPipeline 초기화
        
        Args:
            preprocessor: 텍스트 전처리 단계
            inference_stage: 모델 추론 단계
            postprocessor: 후처리 단계
        """
        self.preprocessor = preprocessor or TextPreprocessor()
        self.inference_stage = inference_stage
        self.postprocessor = postprocessor or PostProcessorStage()
    
    def process(self, text: str) -> SentimentAnalysisResult:
        """
        텍스트 처리
        
        Args:
            text: 처리할 텍스트
            
        Returns:
            SentimentAnalysisResult: 감성 분석 결과
        """
        if not text or not self.inference_stage:
            return SentimentAnalysisResult.neutral()
        
        try:
            # 텍스트 전처리
            preprocessed_text = self.preprocessor.process(text)
            
            # 모델 추론
            inference_result = self.inference_stage.process(preprocessed_text)
            
            # 추론 결과가 없는 경우
            if inference_result is None:
                return SentimentAnalysisResult.neutral()
            
            # 후처리
            result = self.postprocessor.process((inference_result[0], inference_result[1], text))
            
            return result
            
        except Exception as e:
            logger.error(f"텍스트 처리 중 오류 발생: {str(e)}")
            return SentimentAnalysisResult.neutral()
    
    def process_batch(self, texts: List[str], batch_size: Optional[int] = None) -> List[SentimentAnalysisResult]:
        """
        텍스트 배치 처리
        
        Args:
            texts: 처리할 텍스트 목록
            batch_size: 배치 크기 (None인 경우 자동 결정)
            
        Returns:
            List[SentimentAnalysisResult]: 감성 분석 결과 목록
        """
        if not texts or not self.inference_stage:
            return [SentimentAnalysisResult.neutral()] * len(texts)
        
        try:
            # 배치 크기 결정
            if batch_size is None:
                batch_size = len(texts)
            
            results = []
            
            # 배치 단위로 처리
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                
                # 텍스트 전처리
                preprocessed_batch = self.preprocessor.process_batch(batch)
                
                # 모델 추론
                inference_results = self.inference_stage.process_batch(preprocessed_batch)
                
                # 추론 결과가 없는 경우
                if inference_results is None:
                    results.extend([SentimentAnalysisResult.neutral()] * len(batch))
                    continue
                
                # 후처리
                batch_results = self.postprocessor.process_batch([
                    (result[0], result[1], text) for result, text in zip(inference_results, batch)
                ])
                
                results.extend(batch_results)
            
            return results
            
        except Exception as e:
            logger.error(f"텍스트 배치 처리 중 오류 발생: {str(e)}")
            return [SentimentAnalysisResult.neutral()] * len(texts)
