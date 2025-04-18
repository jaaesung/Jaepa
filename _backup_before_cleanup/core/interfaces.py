"""
인터페이스 모듈

애플리케이션에서 사용하는 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union


class DatabaseClient(ABC):
    """
    데이터베이스 클라이언트 인터페이스
    
    모든 데이터베이스 클라이언트는 이 인터페이스를 구현해야 합니다.
    """
    
    @abstractmethod
    def connect(self) -> None:
        """
        데이터베이스에 연결
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """
        데이터베이스 연결 종료
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            bool: 연결 상태
        """
        pass
    
    @abstractmethod
    def get_database(self, db_name: Optional[str] = None) -> Any:
        """
        데이터베이스 객체 반환
        
        Args:
            db_name: 데이터베이스 이름 (기본값: None)
            
        Returns:
            Any: 데이터베이스 객체
        """
        pass
    
    @abstractmethod
    def get_collection(self, collection_name: str, db_name: Optional[str] = None) -> Any:
        """
        컬렉션 객체 반환
        
        Args:
            collection_name: 컬렉션 이름
            db_name: 데이터베이스 이름 (기본값: None)
            
        Returns:
            Any: 컬렉션 객체
        """
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        상태 확인
        
        Returns:
            Dict[str, Any]: 상태 정보
        """
        pass


class MongoDBClient(DatabaseClient):
    """
    MongoDB 클라이언트 인터페이스
    
    MongoDB 클라이언트는 이 인터페이스를 구현해야 합니다.
    """
    pass


class HttpClient(ABC):
    """
    HTTP 클라이언트 인터페이스
    
    모든 HTTP 클라이언트는 이 인터페이스를 구현해야 합니다.
    """
    
    @abstractmethod
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """
        GET 요청
        
        Args:
            url: URL
            params: 쿼리 파라미터
            headers: 헤더
            **kwargs: 추가 인자
            
        Returns:
            Dict[str, Any]: 응답
        """
        pass
    
    @abstractmethod
    async def post(self, url: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """
        POST 요청
        
        Args:
            url: URL
            data: 폼 데이터
            json: JSON 데이터
            headers: 헤더
            **kwargs: 추가 인자
            
        Returns:
            Dict[str, Any]: 응답
        """
        pass
    
    @abstractmethod
    async def put(self, url: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """
        PUT 요청
        
        Args:
            url: URL
            data: 폼 데이터
            json: JSON 데이터
            headers: 헤더
            **kwargs: 추가 인자
            
        Returns:
            Dict[str, Any]: 응답
        """
        pass
    
    @abstractmethod
    async def delete(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """
        DELETE 요청
        
        Args:
            url: URL
            params: 쿼리 파라미터
            headers: 헤더
            **kwargs: 추가 인자
            
        Returns:
            Dict[str, Any]: 응답
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """
        클라이언트 종료
        """
        pass


class NewsSource(ABC):
    """
    뉴스 소스 인터페이스
    
    모든 뉴스 소스는 이 인터페이스를 구현해야 합니다.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        뉴스 소스 이름
        
        Returns:
            str: 뉴스 소스 이름
        """
        pass
    
    @property
    @abstractmethod
    def base_url(self) -> str:
        """
        기본 URL
        
        Returns:
            str: 기본 URL
        """
        pass
    
    @abstractmethod
    async def get_latest_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 뉴스 가져오기
        
        Args:
            limit: 최대 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 목록
        """
        pass
    
    @abstractmethod
    async def search_news(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        뉴스 검색
        
        Args:
            keyword: 검색 키워드
            limit: 최대 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 목록
        """
        pass


class NewsSourceManager(ABC):
    """
    뉴스 소스 관리자 인터페이스
    
    모든 뉴스 소스 관리자는 이 인터페이스를 구현해야 합니다.
    """
    
    @abstractmethod
    def register_source(self, source: NewsSource) -> None:
        """
        뉴스 소스 등록
        
        Args:
            source: 뉴스 소스
        """
        pass
    
    @abstractmethod
    def get_source(self, name: str) -> Optional[NewsSource]:
        """
        뉴스 소스 가져오기
        
        Args:
            name: 뉴스 소스 이름
            
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
    async def get_latest_news_from_all(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        모든 소스에서 최신 뉴스 가져오기
        
        Args:
            limit: 소스별 최대 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 목록
        """
        pass
    
    @abstractmethod
    async def search_news_from_all(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        모든 소스에서 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            limit: 소스별 최대 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 목록
        """
        pass


class SentimentAnalyzer(ABC):
    """
    감성 분석기 인터페이스
    
    모든 감성 분석기는 이 인터페이스를 구현해야 합니다.
    """
    
    @abstractmethod
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        텍스트 감성 분석
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            Dict[str, Any]: 감성 분석 결과
        """
        pass
    
    @abstractmethod
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        텍스트 배치 감성 분석
        
        Args:
            texts: 분석할 텍스트 목록
            
        Returns:
            List[Dict[str, Any]]: 감성 분석 결과 목록
        """
        pass
    
    @abstractmethod
    def analyze_news(self, news: Dict[str, Any]) -> Dict[str, Any]:
        """
        뉴스 감성 분석
        
        Args:
            news: 분석할 뉴스
            
        Returns:
            Dict[str, Any]: 감성 분석 결과가 포함된 뉴스
        """
        pass
    
    @abstractmethod
    def analyze_news_batch(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        뉴스 배치 감성 분석
        
        Args:
            news_list: 분석할 뉴스 목록
            
        Returns:
            List[Dict[str, Any]]: 감성 분석 결과가 포함된 뉴스 목록
        """
        pass
