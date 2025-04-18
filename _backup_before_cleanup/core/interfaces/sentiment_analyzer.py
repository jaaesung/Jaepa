"""
감성 분석기 인터페이스 모듈

텍스트 감성 분석을 위한 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class SentimentAnalyzer(ABC):
    """
    감성 분석기 인터페이스
    
    텍스트 감성 분석을 위한 공통 인터페이스를 정의합니다.
    """
    
    @abstractmethod
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        텍스트 감성 분석
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            Dict[str, Any]: 감성 분석 결과
            {
                'score': float,  # 감성 점수 (-1.0 ~ 1.0)
                'positive': float,  # 긍정 확률 (0.0 ~ 1.0)
                'negative': float,  # 부정 확률 (0.0 ~ 1.0)
                'neutral': float,  # 중립 확률 (0.0 ~ 1.0)
                'label': str,  # 감성 레이블 ('positive', 'negative', 'neutral')
                'confidence': float  # 신뢰도 (0.0 ~ 1.0)
            }
        """
        pass
    
    @abstractmethod
    def analyze_texts(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        여러 텍스트 감성 분석
        
        Args:
            texts: 분석할 텍스트 목록
            
        Returns:
            List[Dict[str, Any]]: 감성 분석 결과 목록
        """
        pass
    
    @abstractmethod
    def analyze_news(self, news: Dict[str, Any]) -> Dict[str, Any]:
        """
        뉴스 기사 감성 분석
        
        Args:
            news: 분석할 뉴스 기사
            
        Returns:
            Dict[str, Any]: 감성 분석 결과가 포함된 뉴스 기사
        """
        pass
    
    @abstractmethod
    def analyze_news_batch(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        여러 뉴스 기사 감성 분석
        
        Args:
            news_list: 분석할 뉴스 기사 목록
            
        Returns:
            List[Dict[str, Any]]: 감성 분석 결과가 포함된 뉴스 기사 목록
        """
        pass
    
    @abstractmethod
    def get_sentiment_trend(self, news_list: List[Dict[str, Any]], 
                           interval: str = 'day') -> Dict[str, Any]:
        """
        뉴스 기사 감성 트렌드 분석
        
        Args:
            news_list: 분석할 뉴스 기사 목록
            interval: 집계 간격 ('hour', 'day', 'week', 'month')
            
        Returns:
            Dict[str, Any]: 감성 트렌드 분석 결과
            {
                'trends': [
                    {
                        'interval': str,  # 시간 간격 (ISO 형식)
                        'sentiment': {
                            'score': float,  # 평균 감성 점수
                            'positive': float,  # 긍정 비율
                            'negative': float,  # 부정 비율
                            'neutral': float,  # 중립 비율
                        },
                        'count': int  # 기사 수
                    },
                    ...
                ],
                'summary': {
                    'average_score': float,  # 전체 평균 감성 점수
                    'positive_ratio': float,  # 전체 긍정 비율
                    'negative_ratio': float,  # 전체 부정 비율
                    'neutral_ratio': float,  # 전체 중립 비율
                    'article_count': int  # 전체 기사 수
                }
            }
        """
        pass
    
    @abstractmethod
    def get_sentiment_distribution(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        뉴스 기사 감성 분포 분석
        
        Args:
            news_list: 분석할 뉴스 기사 목록
            
        Returns:
            Dict[str, Any]: 감성 분포 분석 결과
            {
                'positive': int,  # 긍정 기사 수
                'negative': int,  # 부정 기사 수
                'neutral': int,  # 중립 기사 수
                'total': int,  # 전체 기사 수
                'positive_ratio': float,  # 긍정 비율
                'negative_ratio': float,  # 부정 비율
                'neutral_ratio': float,  # 중립 비율
                'average_score': float  # 평균 감성 점수
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
                'name': str,  # 모델 이름
                'version': str,  # 모델 버전
                'description': str,  # 모델 설명
                'language': str,  # 지원 언어
                'provider': str  # 모델 제공자
            }
        """
        pass
