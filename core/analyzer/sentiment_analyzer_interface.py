"""
감성 분석 인터페이스 모듈

감성 분석기의 공통 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union


class SentimentAnalyzerInterface(ABC):
    """
    감성 분석기 인터페이스
    
    모든 감성 분석기 구현체가 따라야 하는 공통 인터페이스를 정의합니다.
    """
    
    @abstractmethod
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        텍스트의 감성 분석
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            Dict[str, Any]: 감성 분석 결과
            {
                "label": str,  # 감성 레이블 (예: "positive", "negative", "neutral")
                "score": float,  # 감성 점수 (0.0 ~ 1.0)
                "scores": {  # 각 감성 레이블별 점수
                    "positive": float,
                    "negative": float,
                    "neutral": float
                },
                "confidence": float,  # 신뢰도 (0.0 ~ 1.0)
                "language": str  # 감지된 언어 (예: "en", "ko")
            }
        """
        pass
    
    @abstractmethod
    def analyze_batch(self, texts: List[str], batch_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        여러 텍스트의 감성 분석
        
        Args:
            texts: 분석할 텍스트 목록
            batch_size: 배치 크기 (None인 경우 자동 결정)
            
        Returns:
            List[Dict[str, Any]]: 감성 분석 결과 목록
        """
        pass
    
    @abstractmethod
    def analyze_news(self, news: Dict[str, Any]) -> Dict[str, Any]:
        """
        뉴스 기사의 감성 분석
        
        Args:
            news: 뉴스 기사 데이터
            
        Returns:
            Dict[str, Any]: 감성 분석이 추가된 뉴스 기사 데이터
        """
        pass
    
    @abstractmethod
    def analyze_news_batch(self, news_list: List[Dict[str, Any]], batch_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        여러 뉴스 기사의 감성 분석
        
        Args:
            news_list: 뉴스 기사 데이터 목록
            batch_size: 배치 크기 (None인 경우 자동 결정)
            
        Returns:
            List[Dict[str, Any]]: 감성 분석이 추가된 뉴스 기사 데이터 목록
        """
        pass
    
    @abstractmethod
    def get_sentiment_trend(self, news_list: List[Dict[str, Any]], interval: str = 'day') -> Dict[str, Any]:
        """
        뉴스 기사 감성 트렌드 분석
        
        Args:
            news_list: 뉴스 기사 데이터 목록
            interval: 집계 간격 ('hour', 'day', 'week', 'month')
            
        Returns:
            Dict[str, Any]: 감성 트렌드 분석 결과
            {
                "trends": [
                    {
                        "interval": str,  # 시간 간격 (ISO 형식)
                        "sentiment": {
                            "score": float,  # 평균 감성 점수
                            "positive": float,  # 긍정 비율
                            "negative": float,  # 부정 비율
                            "neutral": float,  # 중립 비율
                        },
                        "count": int  # 기사 수
                    },
                    ...
                ],
                "summary": {
                    "average_score": float,  # 전체 평균 감성 점수
                    "positive_ratio": float,  # 전체 긍정 비율
                    "negative_ratio": float,  # 전체 부정 비율
                    "neutral_ratio": float,  # 전체 중립 비율
                    "article_count": int  # 전체 기사 수
                }
            }
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        감성 분석 모델 정보 반환
        
        Returns:
            Dict[str, Any]: 모델 정보
            {
                "name": str,  # 모델 이름
                "version": str,  # 모델 버전
                "description": str,  # 모델 설명
                "language": str,  # 지원 언어
                "provider": str  # 모델 제공자
            }
        """
        pass


class SentimentAnalysisResult:
    """
    감성 분석 결과 클래스
    
    감성 분석 결과를 표준화된 형식으로 제공합니다.
    """
    
    def __init__(self, 
                label: str, 
                score: float, 
                scores: Dict[str, float], 
                confidence: Optional[float] = None,
                language: Optional[str] = None,
                metadata: Optional[Dict[str, Any]] = None):
        """
        SentimentAnalysisResult 초기화
        
        Args:
            label: 감성 레이블 (예: "positive", "negative", "neutral")
            score: 감성 점수 (0.0 ~ 1.0)
            scores: 각 감성 레이블별 점수
            confidence: 신뢰도 (0.0 ~ 1.0)
            language: 감지된 언어 (예: "en", "ko")
            metadata: 추가 메타데이터
        """
        self.label = label
        self.score = score
        self.scores = scores
        self.confidence = confidence or score
        self.language = language or "en"
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        딕셔너리로 변환
        
        Returns:
            Dict[str, Any]: 딕셔너리 형태의 감성 분석 결과
        """
        result = {
            "label": self.label,
            "score": self.score,
            "scores": self.scores,
            "confidence": self.confidence,
            "language": self.language
        }
        
        # 메타데이터가 있는 경우 추가
        if self.metadata:
            result["metadata"] = self.metadata
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SentimentAnalysisResult':
        """
        딕셔너리에서 SentimentAnalysisResult 객체 생성
        
        Args:
            data: 딕셔너리 형태의 감성 분석 결과
            
        Returns:
            SentimentAnalysisResult: 감성 분석 결과 객체
        """
        return cls(
            label=data.get("label", "neutral"),
            score=data.get("score", 0.0),
            scores=data.get("scores", {"positive": 0.0, "negative": 0.0, "neutral": 0.0}),
            confidence=data.get("confidence"),
            language=data.get("language"),
            metadata=data.get("metadata")
        )
    
    @classmethod
    def neutral(cls) -> 'SentimentAnalysisResult':
        """
        중립 감성 결과 생성
        
        Returns:
            SentimentAnalysisResult: 중립 감성 분석 결과 객체
        """
        return cls(
            label="neutral",
            score=1.0,
            scores={"positive": 0.0, "negative": 0.0, "neutral": 1.0},
            confidence=1.0
        )
