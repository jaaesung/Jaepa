"""
데이터베이스 인터페이스 모듈

데이터베이스 연결 및 조작을 위한 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class DatabaseClient(ABC):
    """
    데이터베이스 클라이언트 인터페이스
    
    데이터베이스 연결 및 조작을 위한 공통 인터페이스를 정의합니다.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """
        데이터베이스에 연결
        
        Returns:
            bool: 연결 성공 여부
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
        데이터베이스 연결 상태 확인
        
        Returns:
            bool: 연결 상태
        """
        pass


class MongoDBClient(DatabaseClient):
    """
    MongoDB 클라이언트 인터페이스
    
    MongoDB 데이터베이스 연결 및 조작을 위한 인터페이스를 정의합니다.
    """
    
    @abstractmethod
    def get_database(self, db_name: Optional[str] = None) -> Any:
        """
        데이터베이스 객체 가져오기
        
        Args:
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)
            
        Returns:
            Any: 데이터베이스 객체
        """
        pass
    
    @abstractmethod
    def get_collection(self, collection_name: str, db_name: Optional[str] = None) -> Any:
        """
        컬렉션 객체 가져오기
        
        Args:
            collection_name: 컬렉션 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)
            
        Returns:
            Any: 컬렉션 객체
        """
        pass
    
    @abstractmethod
    def find_one(self, collection_name: str, query: Dict[str, Any], db_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        단일 문서 조회
        
        Args:
            collection_name: 컬렉션 이름
            query: 쿼리 조건
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)
            
        Returns:
            Optional[Dict[str, Any]]: 조회된 문서 또는 None
        """
        pass
    
    @abstractmethod
    def find_many(self, collection_name: str, query: Dict[str, Any], limit: int = 0, 
                 sort: Optional[List[tuple]] = None, db_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        여러 문서 조회
        
        Args:
            collection_name: 컬렉션 이름
            query: 쿼리 조건
            limit: 최대 결과 수 (0인 경우 제한 없음)
            sort: 정렬 조건 [(필드명, 방향), ...] 형식
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)
            
        Returns:
            List[Dict[str, Any]]: 조회된 문서 목록
        """
        pass
    
    @abstractmethod
    def insert_one(self, collection_name: str, document: Dict[str, Any], db_name: Optional[str] = None) -> str:
        """
        단일 문서 삽입
        
        Args:
            collection_name: 컬렉션 이름
            document: 삽입할 문서
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)
            
        Returns:
            str: 삽입된 문서의 ID
        """
        pass
    
    @abstractmethod
    def insert_many(self, collection_name: str, documents: List[Dict[str, Any]], db_name: Optional[str] = None) -> List[str]:
        """
        여러 문서 삽입
        
        Args:
            collection_name: 컬렉션 이름
            documents: 삽입할 문서 목록
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)
            
        Returns:
            List[str]: 삽입된 문서의 ID 목록
        """
        pass
    
    @abstractmethod
    def update_one(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any], 
                  db_name: Optional[str] = None) -> int:
        """
        단일 문서 업데이트
        
        Args:
            collection_name: 컬렉션 이름
            query: 쿼리 조건
            update: 업데이트 내용
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)
            
        Returns:
            int: 업데이트된 문서 수
        """
        pass
    
    @abstractmethod
    def update_many(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any], 
                   db_name: Optional[str] = None) -> int:
        """
        여러 문서 업데이트
        
        Args:
            collection_name: 컬렉션 이름
            query: 쿼리 조건
            update: 업데이트 내용
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)
            
        Returns:
            int: 업데이트된 문서 수
        """
        pass
    
    @abstractmethod
    def delete_one(self, collection_name: str, query: Dict[str, Any], db_name: Optional[str] = None) -> int:
        """
        단일 문서 삭제
        
        Args:
            collection_name: 컬렉션 이름
            query: 쿼리 조건
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)
            
        Returns:
            int: 삭제된 문서 수
        """
        pass
    
    @abstractmethod
    def delete_many(self, collection_name: str, query: Dict[str, Any], db_name: Optional[str] = None) -> int:
        """
        여러 문서 삭제
        
        Args:
            collection_name: 컬렉션 이름
            query: 쿼리 조건
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)
            
        Returns:
            int: 삭제된 문서 수
        """
        pass
    
    @abstractmethod
    def create_index(self, collection_name: str, keys: List[tuple], unique: bool = False, 
                    name: Optional[str] = None, db_name: Optional[str] = None) -> str:
        """
        인덱스 생성
        
        Args:
            collection_name: 컬렉션 이름
            keys: 인덱스 키 [(필드명, 방향), ...] 형식
            unique: 고유 인덱스 여부
            name: 인덱스 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)
            
        Returns:
            str: 생성된 인덱스 이름
        """
        pass


class SQLClient(DatabaseClient):
    """
    SQL 클라이언트 인터페이스
    
    SQL 데이터베이스 연결 및 조작을 위한 인터페이스를 정의합니다.
    """
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[Union[Dict[str, Any], List[Any]]] = None) -> Any:
        """
        SQL 쿼리 실행
        
        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터
            
        Returns:
            Any: 쿼리 결과
        """
        pass
    
    @abstractmethod
    def fetch_one(self, query: str, params: Optional[Union[Dict[str, Any], List[Any]]] = None) -> Optional[Dict[str, Any]]:
        """
        단일 레코드 조회
        
        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터
            
        Returns:
            Optional[Dict[str, Any]]: 조회된 레코드 또는 None
        """
        pass
    
    @abstractmethod
    def fetch_all(self, query: str, params: Optional[Union[Dict[str, Any], List[Any]]] = None) -> List[Dict[str, Any]]:
        """
        여러 레코드 조회
        
        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터
            
        Returns:
            List[Dict[str, Any]]: 조회된 레코드 목록
        """
        pass
    
    @abstractmethod
    def execute(self, query: str, params: Optional[Union[Dict[str, Any], List[Any]]] = None) -> int:
        """
        SQL 쿼리 실행 (INSERT, UPDATE, DELETE)
        
        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터
            
        Returns:
            int: 영향받은 레코드 수
        """
        pass
    
    @abstractmethod
    def begin_transaction(self) -> None:
        """
        트랜잭션 시작
        """
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """
        트랜잭션 커밋
        """
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """
        트랜잭션 롤백
        """
        pass
