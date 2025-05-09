"""
뉴스 소스 관리자 인터페이스 모듈

뉴스 소스 관리 및 뉴스 수집을 위한 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


class NewsSource(ABC):
    """
    뉴스 소스 인터페이스
    
    개별 뉴스 소스에 대한 인터페이스를 정의합니다.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """
        뉴스 소스 이름 반환
        
        Returns:
            str: 뉴스 소스 이름
        """
        pass
    
    @abstractmethod
    def get_latest_news(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        최신 뉴스 가져오기
        
        Args:
            count: 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        pass
    
    @abstractmethod
    def search_news(self, keyword: str, days: int = 7, count: int = 10) -> List[Dict[str, Any]]:
        """
        키워드로 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            days: 검색할 기간(일)
            count: 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        pass
    
    @abstractmethod
    def get_news_by_date(self, start_date: datetime, end_date: datetime, count: int = 10) -> List[Dict[str, Any]]:
        """
        날짜 범위로 뉴스 가져오기
        
        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
            count: 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        pass


class NewsSourceManager(ABC):
    """
    뉴스 소스 관리자 인터페이스
    
    여러 뉴스 소스를 관리하고 통합 검색을 제공하는 인터페이스를 정의합니다.
    """
    
    @abstractmethod
    def register_source(self, source: NewsSource) -> None:
        """
        뉴스 소스 등록
        
        Args:
            source: 등록할 뉴스 소스
        """
        pass
    
    @abstractmethod
    def unregister_source(self, source_name: str) -> bool:
        """
        뉴스 소스 등록 해제
        
        Args:
            source_name: 등록 해제할 뉴스 소스 이름
            
        Returns:
            bool: 등록 해제 성공 여부
        """
        pass
    
    @abstractmethod
    def get_source(self, source_name: str) -> Optional[NewsSource]:
        """
        뉴스 소스 가져오기
        
        Args:
            source_name: 뉴스 소스 이름
            
        Returns:
            Optional[NewsSource]: 뉴스 소스 또는 None
        """
        pass
    
    @abstractmethod
    def get_all_sources(self) -> List[NewsSource]:
        """
        모든 뉴스 소스 가져오기
        
        Returns:
            List[NewsSource]: 뉴스 소스 목록
        """
        pass
    
    @abstractmethod
    def get_latest_news(self, sources: Optional[List[str]] = None, count: int = 10) -> List[Dict[str, Any]]:
        """
        최신 뉴스 가져오기
        
        Args:
            sources: 뉴스 소스 이름 목록 (None인 경우 모든 소스)
            count: 각 소스별 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        pass
    
    @abstractmethod
    def search_news(self, keyword: str, days: int = 7, sources: Optional[List[str]] = None, 
                   count: int = 10) -> List[Dict[str, Any]]:
        """
        키워드로 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            days: 검색할 기간(일)
            sources: 뉴스 소스 이름 목록 (None인 경우 모든 소스)
            count: 각 소스별 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        pass
    
    @abstractmethod
    def get_news_by_date(self, start_date: datetime, end_date: datetime, 
                        sources: Optional[List[str]] = None, count: int = 10) -> List[Dict[str, Any]]:
        """
        날짜 범위로 뉴스 가져오기
        
        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
            sources: 뉴스 소스 이름 목록 (None인 경우 모든 소스)
            count: 각 소스별 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        pass
    
    @abstractmethod
    def get_news_by_symbol(self, symbol: str, days: int = 7, 
                          sources: Optional[List[str]] = None, count: int = 10) -> List[Dict[str, Any]]:
        """
        주식 심볼로 뉴스 가져오기
        
        Args:
            symbol: 주식 심볼 (예: AAPL)
            days: 가져올 기간(일)
            sources: 뉴스 소스 이름 목록 (None인 경우 모든 소스)
            count: 각 소스별 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        pass
