"""
뉴스 크롤링 모듈 인터페이스

뉴스 크롤링 모듈의 주요 컴포넌트에 대한 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, AsyncIterator, Tuple


class HttpClientInterface(ABC):
    """HTTP 요청 처리 인터페이스"""
    
    @abstractmethod
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None, 
                 headers: Optional[Dict[str, str]] = None, 
                 timeout: Optional[float] = None) -> Tuple[int, str]:
        """
        GET 요청 수행
        
        Args:
            url: 요청 URL
            params: 쿼리 파라미터
            headers: 요청 헤더
            timeout: 타임아웃 (초)
            
        Returns:
            Tuple[int, str]: 상태 코드와 응답 내용
            
        Raises:
            HttpClientException: HTTP 요청 실패 시
        """
        pass
    
    @abstractmethod
    async def post(self, url: str, data: Optional[Dict[str, Any]] = None, 
                  json_data: Optional[Dict[str, Any]] = None, 
                  headers: Optional[Dict[str, str]] = None, 
                  timeout: Optional[float] = None) -> Tuple[int, str]:
        """
        POST 요청 수행
        
        Args:
            url: 요청 URL
            data: 폼 데이터
            json_data: JSON 데이터
            headers: 요청 헤더
            timeout: 타임아웃 (초)
            
        Returns:
            Tuple[int, str]: 상태 코드와 응답 내용
            
        Raises:
            HttpClientException: HTTP 요청 실패 시
        """
        pass
    
    @abstractmethod
    async def get_with_retry(self, url: str, params: Optional[Dict[str, Any]] = None, 
                            headers: Optional[Dict[str, str]] = None, 
                            max_retries: int = 3, backoff_factor: float = 1.5, 
                            timeout: Optional[float] = None) -> Tuple[int, str]:
        """
        재시도 로직이 포함된 GET 요청 수행
        
        Args:
            url: 요청 URL
            params: 쿼리 파라미터
            headers: 요청 헤더
            max_retries: 최대 재시도 횟수
            backoff_factor: 백오프 계수
            timeout: 타임아웃 (초)
            
        Returns:
            Tuple[int, str]: 상태 코드와 응답 내용
            
        Raises:
            HttpClientException: 모든 재시도 실패 시
        """
        pass
    
    @abstractmethod
    def set_default_headers(self, headers: Dict[str, str]) -> None:
        """
        기본 요청 헤더 설정
        
        Args:
            headers: 기본 요청 헤더
        """
        pass
    
    @abstractmethod
    def set_rate_limit(self, requests_per_minute: int) -> None:
        """
        요청 속도 제한 설정
        
        Args:
            requests_per_minute: 분당 최대 요청 수
        """
        pass


class NewsSourceInterface(ABC):
    """뉴스 소스 인터페이스"""
    
    @property
    @abstractmethod
    def source_id(self) -> str:
        """소스 ID"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """소스 이름"""
        pass
    
    @abstractmethod
    async def get_latest_news(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        최신 뉴스 가져오기
        
        Args:
            count: 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
            
        Raises:
            SourceException: 뉴스 가져오기 실패 시
        """
        pass
    
    @abstractmethod
    async def search_news(self, keyword: str, days: int = 7, count: int = 10) -> List[Dict[str, Any]]:
        """
        키워드로 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            days: 검색할 기간(일)
            count: 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
            
        Raises:
            SourceException: 뉴스 검색 실패 시
        """
        pass


class NewsSourceManagerInterface(ABC):
    """뉴스 소스 관리자 인터페이스"""
    
    @abstractmethod
    def register_source(self, source: NewsSourceInterface) -> None:
        """
        뉴스 소스 등록
        
        Args:
            source: 등록할 뉴스 소스
            
        Raises:
            ConfigurationException: 소스 등록 실패 시
        """
        pass
    
    @abstractmethod
    def get_source(self, source_id: str) -> Optional[NewsSourceInterface]:
        """
        뉴스 소스 가져오기
        
        Args:
            source_id: 소스 ID
            
        Returns:
            Optional[NewsSourceInterface]: 뉴스 소스 또는 None
        """
        pass
    
    @abstractmethod
    def get_all_sources(self) -> List[NewsSourceInterface]:
        """
        모든 뉴스 소스 가져오기
        
        Returns:
            List[NewsSourceInterface]: 뉴스 소스 목록
        """
        pass
    
    @abstractmethod
    async def get_latest_news(self, sources: Optional[List[str]] = None, count: int = 10) -> List[Dict[str, Any]]:
        """
        최신 뉴스 가져오기
        
        Args:
            sources: 뉴스 소스 ID 목록 (None인 경우 모든 소스)
            count: 각 소스별 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        pass
    
    @abstractmethod
    async def search_news(self, keyword: str, days: int = 7, sources: Optional[List[str]] = None, 
                         count: int = 10) -> List[Dict[str, Any]]:
        """
        키워드로 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            days: 검색할 기간(일)
            sources: 뉴스 소스 ID 목록 (None인 경우 모든 소스)
            count: 각 소스별 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        pass


class RssProcessorInterface(ABC):
    """RSS 피드 처리 인터페이스"""
    
    @abstractmethod
    async def parse_feed(self, feed_url: str) -> Dict[str, Any]:
        """
        RSS 피드 파싱
        
        Args:
            feed_url: RSS 피드 URL
            
        Returns:
            Dict[str, Any]: 파싱된 피드 정보
            
        Raises:
            ParsingException: 피드 파싱 실패 시
        """
        pass
    
    @abstractmethod
    async def process_entry(self, entry: Dict[str, Any], source_name: str) -> Dict[str, Any]:
        """
        RSS 항목 처리
        
        Args:
            entry: RSS 항목
            source_name: 소스 이름
            
        Returns:
            Dict[str, Any]: 처리된 뉴스 기사 정보
            
        Raises:
            ParsingException: 항목 처리 실패 시
        """
        pass
    
    @abstractmethod
    async def process_entries_batch(self, entries: List[Dict[str, Any]], source_name: str) -> List[Dict[str, Any]]:
        """
        RSS 항목 배치 처리
        
        Args:
            entries: RSS 항목 목록
            source_name: 소스 이름
            
        Returns:
            List[Dict[str, Any]]: 처리된 뉴스 기사 정보 목록
        """
        pass


class ArticleProcessorInterface(ABC):
    """기사 처리 인터페이스"""
    
    @abstractmethod
    async def extract_content(self, url: str, html: Optional[str] = None) -> Dict[str, Any]:
        """
        기사 내용 추출
        
        Args:
            url: 기사 URL
            html: HTML 내용 (None인 경우 URL에서 가져옴)
            
        Returns:
            Dict[str, Any]: 추출된 기사 정보
            
        Raises:
            ParsingException: 내용 추출 실패 시
        """
        pass
    
    @abstractmethod
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        텍스트에서 키워드 추출
        
        Args:
            text: 분석할 텍스트
            max_keywords: 최대 키워드 수
            
        Returns:
            List[str]: 추출된 키워드 목록
        """
        pass
    
    @abstractmethod
    async def normalize_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        기사 정보 정규화
        
        Args:
            article: 원본 기사 정보
            
        Returns:
            Dict[str, Any]: 정규화된 기사 정보
        """
        pass
    
    @abstractmethod
    async def deduplicate_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        중복 기사 제거
        
        Args:
            articles: 기사 목록
            
        Returns:
            List[Dict[str, Any]]: 중복이 제거된 기사 목록
        """
        pass


class ArticleRepositoryInterface(ABC):
    """기사 저장소 인터페이스"""
    
    @abstractmethod
    async def save(self, article: Dict[str, Any]) -> str:
        """
        기사 저장
        
        Args:
            article: 저장할 기사 정보
            
        Returns:
            str: 저장된 기사 ID
            
        Raises:
            StorageException: 저장 실패 시
        """
        pass
    
    @abstractmethod
    async def save_many(self, articles: List[Dict[str, Any]]) -> List[str]:
        """
        여러 기사 저장
        
        Args:
            articles: 저장할 기사 목록
            
        Returns:
            List[str]: 저장된 기사 ID 목록
            
        Raises:
            StorageException: 저장 실패 시
        """
        pass
    
    @abstractmethod
    async def find_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        URL로 기사 찾기
        
        Args:
            url: 기사 URL
            
        Returns:
            Optional[Dict[str, Any]]: 찾은 기사 또는 None
        """
        pass
    
    @abstractmethod
    async def find_by_keyword(self, keyword: str, days: int = 7, limit: int = 100) -> List[Dict[str, Any]]:
        """
        키워드로 기사 찾기
        
        Args:
            keyword: 검색 키워드
            days: 검색할 기간(일)
            limit: 최대 결과 수
            
        Returns:
            List[Dict[str, Any]]: 찾은 기사 목록
        """
        pass
    
    @abstractmethod
    async def find_latest(self, days: int = 7, limit: int = 100) -> List[Dict[str, Any]]:
        """
        최신 기사 찾기
        
        Args:
            days: 검색할 기간(일)
            limit: 최대 결과 수
            
        Returns:
            List[Dict[str, Any]]: 찾은 기사 목록
        """
        pass
    
    @abstractmethod
    async def find_by_source(self, source: str, days: int = 7, limit: int = 100) -> List[Dict[str, Any]]:
        """
        소스별 기사 찾기
        
        Args:
            source: 뉴스 소스
            days: 검색할 기간(일)
            limit: 최대 결과 수
            
        Returns:
            List[Dict[str, Any]]: 찾은 기사 목록
        """
        pass
