"""
감성 분석 도메인 모델 모듈

감성 분석 관련 도메인 모델을 제공합니다.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class SentimentAnalysis:
    """
    감성 분석 모델
    
    감성 분석 결과를 나타냅니다.
    """
    
    text_id: str  # 분석 대상 텍스트 ID (뉴스 ID 등)
    label: str  # 감성 레이블 (positive, negative, neutral)
    score: float  # 감성 점수 (0.0 ~ 1.0)
    scores: Dict[str, float]  # 각 감성 레이블별 점수
    text_type: str  # 텍스트 유형 (news, comment, etc.)
    analyzed_at: datetime = field(default_factory=datetime.now)
    model: Optional[str] = None  # 사용된 모델
    confidence: Optional[float] = None  # 신뢰도
    language: Optional[str] = None  # 언어
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None
    
    def __post_init__(self):
        """
        초기화 후처리
        """
        # 문자열 날짜를 datetime으로 변환
        if isinstance(self.analyzed_at, str):
            try:
                # ISO 형식 (예: "2023-01-01T12:00:00Z")
                self.analyzed_at = datetime.fromisoformat(self.analyzed_at.replace('Z', '+00:00'))
            except ValueError:
                # 기본값: 현재 시간
                self.analyzed_at = datetime.now()
        
        # 신뢰도 기본값: 점수
        if self.confidence is None:
            self.confidence = self.score
    
    def to_dict(self) -> Dict[str, Any]:
        """
        딕셔너리로 변환
        
        Returns:
            Dict[str, Any]: 딕셔너리 표현
        """
        result = {
            "text_id": self.text_id,
            "label": self.label,
            "score": self.score,
            "scores": self.scores,
            "text_type": self.text_type,
            "analyzed_at": self.analyzed_at.isoformat(),
            "metadata": self.metadata
        }
        
        # 선택적 필드 추가
        if self.model:
            result["model"] = self.model
            
        if self.confidence is not None:
            result["confidence"] = self.confidence
            
        if self.language:
            result["language"] = self.language
            
        if self.id:
            result["id"] = self.id
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SentimentAnalysis':
        """
        딕셔너리에서 생성
        
        Args:
            data: 딕셔너리 데이터
            
        Returns:
            SentimentAnalysis: 생성된 감성 분석 객체
        """
        # 필수 필드 확인
        required_fields = ["text_id", "label", "score", "scores", "text_type"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"필수 필드 누락: {field}")
        
        # ID 처리
        id_value = data.get("id") or data.get("_id")
        
        # 객체 생성
        return cls(
            text_id=data["text_id"],
            label=data["label"],
            score=data["score"],
            scores=data["scores"],
            text_type=data["text_type"],
            analyzed_at=data.get("analyzed_at", datetime.now()),
            model=data.get("model"),
            confidence=data.get("confidence"),
            language=data.get("language"),
            metadata=data.get("metadata", {}),
            id=id_value
        )


@dataclass
class SentimentTrend:
    """
    감성 트렌드 모델
    
    시간에 따른 감성 변화를 나타냅니다.
    """
    
    symbol: str  # 주식 심볼
    date: datetime  # 날짜
    positive_count: int  # 긍정 기사 수
    negative_count: int  # 부정 기사 수
    neutral_count: int  # 중립 기사 수
    total_count: int  # 전체 기사 수
    average_score: float  # 평균 감성 점수
    positive_ratio: float  # 긍정 비율
    negative_ratio: float  # 부정 비율
    neutral_ratio: float  # 중립 비율
    news_ids: List[str] = field(default_factory=list)  # 관련 뉴스 ID 목록
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None
    
    def __post_init__(self):
        """
        초기화 후처리
        """
        # 문자열 날짜를 datetime으로 변환
        if isinstance(self.date, str):
            try:
                # ISO 형식 (예: "2023-01-01T12:00:00Z")
                self.date = datetime.fromisoformat(self.date.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # 날짜만 있는 형식 (예: "2023-01-01")
                    self.date = datetime.strptime(self.date, "%Y-%m-%d")
                except ValueError:
                    # 기본값: 현재 시간
                    self.date = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        딕셔너리로 변환
        
        Returns:
            Dict[str, Any]: 딕셔너리 표현
        """
        result = {
            "symbol": self.symbol,
            "date": self.date.isoformat(),
            "positive_count": self.positive_count,
            "negative_count": self.negative_count,
            "neutral_count": self.neutral_count,
            "total_count": self.total_count,
            "average_score": self.average_score,
            "positive_ratio": self.positive_ratio,
            "negative_ratio": self.negative_ratio,
            "neutral_ratio": self.neutral_ratio,
            "news_ids": self.news_ids,
            "metadata": self.metadata
        }
        
        # ID 추가
        if self.id:
            result["id"] = self.id
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SentimentTrend':
        """
        딕셔너리에서 생성
        
        Args:
            data: 딕셔너리 데이터
            
        Returns:
            SentimentTrend: 생성된 감성 트렌드 객체
        """
        # 필수 필드 확인
        required_fields = [
            "symbol", "date", "positive_count", "negative_count", 
            "neutral_count", "total_count", "average_score", 
            "positive_ratio", "negative_ratio", "neutral_ratio"
        ]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"필수 필드 누락: {field}")
        
        # ID 처리
        id_value = data.get("id") or data.get("_id")
        
        # 객체 생성
        return cls(
            symbol=data["symbol"],
            date=data["date"],
            positive_count=data["positive_count"],
            negative_count=data["negative_count"],
            neutral_count=data["neutral_count"],
            total_count=data["total_count"],
            average_score=data["average_score"],
            positive_ratio=data["positive_ratio"],
            negative_ratio=data["negative_ratio"],
            neutral_ratio=data["neutral_ratio"],
            news_ids=data.get("news_ids", []),
            metadata=data.get("metadata", {}),
            id=id_value
        )
