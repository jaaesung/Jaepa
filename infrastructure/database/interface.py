"""
데이터베이스 인터페이스 모듈

데이터베이스 접근을 위한 인터페이스를 정의합니다.
모든 데이터베이스 구현체는 이 인터페이스를 구현해야 합니다.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, TypeVar, Generic, Type


T = TypeVar('T')


class DatabaseClientInterface(ABC):
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


class RepositoryInterface(Generic[T], ABC):
    """
    저장소 인터페이스
    
    모든 저장소는 이 인터페이스를 구현해야 합니다.
    """
    
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[T]:
        """
        ID로 항목 조회
        
        Args:
            id: 항목 ID
            
        Returns:
            Optional[T]: 항목 또는 None
        """
        pass
    
    @abstractmethod
    def find_one(self, filter: Dict[str, Any]) -> Optional[T]:
        """
        필터로 단일 항목 조회
        
        Args:
            filter: 필터
            
        Returns:
            Optional[T]: 항목 또는 None
        """
        pass
    
    @abstractmethod
    def find_many(self, filter: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[T]:
        """
        필터로 여러 항목 조회
        
        Args:
            filter: 필터
            skip: 건너뛸 항목 수 (기본값: 0)
            limit: 최대 항목 수 (기본값: 100)
            
        Returns:
            List[T]: 항목 목록
        """
        pass
    
    @abstractmethod
    def create(self, item: T) -> T:
        """
        항목 생성
        
        Args:
            item: 생성할 항목
            
        Returns:
            T: 생성된 항목
        """
        pass
    
    @abstractmethod
    def update(self, id: str, item: T) -> Optional[T]:
        """
        항목 업데이트
        
        Args:
            id: 항목 ID
            item: 업데이트할 항목
            
        Returns:
            Optional[T]: 업데이트된 항목 또는 None
        """
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """
        항목 삭제
        
        Args:
            id: 항목 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        pass
    
    @abstractmethod
    def count(self, filter: Dict[str, Any]) -> int:
        """
        항목 수 조회
        
        Args:
            filter: 필터
            
        Returns:
            int: 항목 수
        """
        pass


class AsyncDatabaseClientInterface(ABC):
    """
    비동기 데이터베이스 클라이언트 인터페이스
    
    모든 비동기 데이터베이스 클라이언트는 이 인터페이스를 구현해야 합니다.
    """
    
    @abstractmethod
    async def connect(self) -> None:
        """
        데이터베이스에 연결
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """
        데이터베이스 연결 종료
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            bool: 연결 상태
        """
        pass
    
    @abstractmethod
    async def get_database(self, db_name: Optional[str] = None) -> Any:
        """
        데이터베이스 객체 반환
        
        Args:
            db_name: 데이터베이스 이름 (기본값: None)
            
        Returns:
            Any: 데이터베이스 객체
        """
        pass
    
    @abstractmethod
    async def get_collection(self, collection_name: str, db_name: Optional[str] = None) -> Any:
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
    async def health_check(self) -> Dict[str, Any]:
        """
        상태 확인
        
        Returns:
            Dict[str, Any]: 상태 정보
        """
        pass


class AsyncRepositoryInterface(Generic[T], ABC):
    """
    비동기 저장소 인터페이스
    
    모든 비동기 저장소는 이 인터페이스를 구현해야 합니다.
    """
    
    @abstractmethod
    async def find_by_id(self, id: str) -> Optional[T]:
        """
        ID로 항목 조회
        
        Args:
            id: 항목 ID
            
        Returns:
            Optional[T]: 항목 또는 None
        """
        pass
    
    @abstractmethod
    async def find_one(self, filter: Dict[str, Any]) -> Optional[T]:
        """
        필터로 단일 항목 조회
        
        Args:
            filter: 필터
            
        Returns:
            Optional[T]: 항목 또는 None
        """
        pass
    
    @abstractmethod
    async def find_many(self, filter: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[T]:
        """
        필터로 여러 항목 조회
        
        Args:
            filter: 필터
            skip: 건너뛸 항목 수 (기본값: 0)
            limit: 최대 항목 수 (기본값: 100)
            
        Returns:
            List[T]: 항목 목록
        """
        pass
    
    @abstractmethod
    async def create(self, item: T) -> T:
        """
        항목 생성
        
        Args:
            item: 생성할 항목
            
        Returns:
            T: 생성된 항목
        """
        pass
    
    @abstractmethod
    async def update(self, id: str, item: T) -> Optional[T]:
        """
        항목 업데이트
        
        Args:
            id: 항목 ID
            item: 업데이트할 항목
            
        Returns:
            Optional[T]: 업데이트된 항목 또는 None
        """
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """
        항목 삭제
        
        Args:
            id: 항목 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        pass
    
    @abstractmethod
    async def count(self, filter: Dict[str, Any]) -> int:
        """
        항목 수 조회
        
        Args:
            filter: 필터
            
        Returns:
            int: 항목 수
        """
        pass
