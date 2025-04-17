"""
SQLAlchemy 데이터베이스 모듈

SQLAlchemy를 사용한 데이터베이스 접근을 위한 클라이언트 및 저장소 구현체를 제공합니다.
"""
import time
import logging
from typing import Dict, Any, List, Optional, Union, TypeVar, Generic, Type, cast
from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, select, insert, update, delete, func
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncConnection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, Session

from pydantic import BaseModel

from .interface import (
    DatabaseClientInterface, RepositoryInterface,
    AsyncDatabaseClientInterface, AsyncRepositoryInterface
)

# 로깅 설정
logger = logging.getLogger(__name__)

# 타입 변수
T = TypeVar('T', bound=BaseModel)


class SQLAlchemyClient(DatabaseClientInterface):
    """
    SQLAlchemy 클라이언트 구현체
    """
    
    def __init__(
        self,
        url: str,
        connect_args: Dict[str, Any] = None,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False
    ):
        """
        초기화
        
        Args:
            url: 데이터베이스 URL
            connect_args: 연결 인자
            pool_size: 풀 크기
            max_overflow: 최대 오버플로우
            pool_timeout: 풀 타임아웃
            pool_recycle: 풀 재활용 시간
            echo: SQL 로깅 여부
        """
        self.url = url
        self.connect_args = connect_args or {}
        self.engine_options = {
            "pool_size": pool_size,
            "max_overflow": max_overflow,
            "pool_timeout": pool_timeout,
            "pool_recycle": pool_recycle,
            "echo": echo
        }
        self.engine = None
        self.metadata = MetaData()
        self._connected = False
        self._last_connection_check = 0
        
        logger.debug(f"SQLAlchemy client initialized with URL: {url}")
    
    def connect(self) -> None:
        """
        데이터베이스에 연결
        """
        try:
            if not self.engine:
                logger.debug("Creating new SQLAlchemy engine")
                self.engine = create_engine(
                    self.url,
                    connect_args=self.connect_args,
                    **self.engine_options
                )
            
            # 연결 테스트
            with self.engine.connect() as conn:
                conn.execute(select(1))
            
            self._connected = True
            logger.info(f"Connected to database at {self.url}")
        except SQLAlchemyError as e:
            self._connected = False
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def close(self) -> None:
        """
        데이터베이스 연결 종료
        """
        if self.engine:
            logger.debug("Closing SQLAlchemy engine")
            self.engine.dispose()
            self.engine = None
            self._connected = False
            logger.info("Database connection closed")
    
    def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            bool: 연결 상태
        """
        # 캐싱된 상태가 있고 최근에 확인한 경우 (10초 이내)
        current_time = time.time()
        if self._connected and (current_time - self._last_connection_check) < 10:
            return self._connected
        
        # 연결 상태 확인
        if not self.engine:
            self._connected = False
            return False
        
        try:
            with self.engine.connect() as conn:
                conn.execute(select(1))
            self._connected = True
        except SQLAlchemyError:
            self._connected = False
        
        # 마지막 확인 시간 업데이트
        self._last_connection_check = current_time
        return self._connected
    
    def get_database(self, db_name: Optional[str] = None) -> Engine:
        """
        데이터베이스 객체 반환
        
        Args:
            db_name: 데이터베이스 이름 (기본값: None)
            
        Returns:
            Engine: 데이터베이스 엔진
        """
        if not self.is_connected():
            self.connect()
        
        return self.engine
    
    def get_connection(self) -> Connection:
        """
        데이터베이스 연결 반환
        
        Returns:
            Connection: 데이터베이스 연결
        """
        if not self.is_connected():
            self.connect()
        
        return self.engine.connect()
    
    def get_session(self) -> Session:
        """
        세션 반환
        
        Returns:
            Session: 세션
        """
        if not self.is_connected():
            self.connect()
        
        session_factory = sessionmaker(bind=self.engine)
        return session_factory()
    
    def get_collection(self, collection_name: str, db_name: Optional[str] = None) -> Table:
        """
        테이블 객체 반환
        
        Args:
            collection_name: 테이블 이름
            db_name: 데이터베이스 이름 (기본값: None)
            
        Returns:
            Table: 테이블 객체
        """
        if not self.is_connected():
            self.connect()
        
        # 테이블이 이미 메타데이터에 있는지 확인
        if collection_name in self.metadata.tables:
            return self.metadata.tables[collection_name]
        
        # 테이블 반영
        self.metadata.reflect(bind=self.engine, only=[collection_name])
        
        # 테이블이 메타데이터에 있는지 다시 확인
        if collection_name in self.metadata.tables:
            return self.metadata.tables[collection_name]
        
        # 테이블이 없으면 예외 발생
        raise ValueError(f"Table {collection_name} not found in database")
    
    def health_check(self) -> Dict[str, Any]:
        """
        상태 확인
        
        Returns:
            Dict[str, Any]: 상태 정보
        """
        result = {
            "status": "disconnected",
            "details": {}
        }
        
        if not self.engine:
            return result
        
        try:
            # 응답 시간 측정
            start_time = time.time()
            with self.engine.connect() as conn:
                conn.execute(select(1))
            end_time = time.time()
            
            # 상태 정보 구성
            result["status"] = "connected"
            result["details"] = {
                "response_time_ms": round((end_time - start_time) * 1000, 2),
                "dialect": self.engine.dialect.name,
                "driver": self.engine.dialect.driver,
                "pool_size": self.engine.pool.size(),
                "pool_overflow": self.engine.pool.overflow(),
                "pool_checkedin": self.engine.pool.checkedin(),
                "pool_checkedout": self.engine.pool.checkedout()
            }
        except Exception as e:
            result["status"] = "error"
            result["details"] = {
                "error": str(e)
            }
        
        return result


class AsyncSQLAlchemyClient(AsyncDatabaseClientInterface):
    """
    비동기 SQLAlchemy 클라이언트 구현체
    """
    
    def __init__(
        self,
        url: str,
        connect_args: Dict[str, Any] = None,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False
    ):
        """
        초기화
        
        Args:
            url: 데이터베이스 URL
            connect_args: 연결 인자
            pool_size: 풀 크기
            max_overflow: 최대 오버플로우
            pool_timeout: 풀 타임아웃
            pool_recycle: 풀 재활용 시간
            echo: SQL 로깅 여부
        """
        self.url = url
        self.connect_args = connect_args or {}
        self.engine_options = {
            "pool_size": pool_size,
            "max_overflow": max_overflow,
            "pool_timeout": pool_timeout,
            "pool_recycle": pool_recycle,
            "echo": echo
        }
        self.engine = None
        self.metadata = MetaData()
        self._connected = False
        self._last_connection_check = 0
        
        logger.debug(f"Async SQLAlchemy client initialized with URL: {url}")
    
    async def connect(self) -> None:
        """
        데이터베이스에 연결
        """
        try:
            if not self.engine:
                logger.debug("Creating new async SQLAlchemy engine")
                self.engine = create_async_engine(
                    self.url,
                    connect_args=self.connect_args,
                    **self.engine_options
                )
            
            # 연결 테스트
            async with self.engine.connect() as conn:
                await conn.execute(select(1))
            
            self._connected = True
            logger.info(f"Connected to database at {self.url}")
        except SQLAlchemyError as e:
            self._connected = False
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def close(self) -> None:
        """
        데이터베이스 연결 종료
        """
        if self.engine:
            logger.debug("Closing async SQLAlchemy engine")
            await self.engine.dispose()
            self.engine = None
            self._connected = False
            logger.info("Database connection closed")
    
    async def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            bool: 연결 상태
        """
        # 캐싱된 상태가 있고 최근에 확인한 경우 (10초 이내)
        current_time = time.time()
        if self._connected and (current_time - self._last_connection_check) < 10:
            return self._connected
        
        # 연결 상태 확인
        if not self.engine:
            self._connected = False
            return False
        
        try:
            async with self.engine.connect() as conn:
                await conn.execute(select(1))
            self._connected = True
        except SQLAlchemyError:
            self._connected = False
        
        # 마지막 확인 시간 업데이트
        self._last_connection_check = current_time
        return self._connected
    
    async def get_database(self, db_name: Optional[str] = None) -> AsyncEngine:
        """
        데이터베이스 객체 반환
        
        Args:
            db_name: 데이터베이스 이름 (기본값: None)
            
        Returns:
            AsyncEngine: 데이터베이스 엔진
        """
        if not await self.is_connected():
            await self.connect()
        
        return self.engine
    
    async def get_connection(self) -> AsyncConnection:
        """
        데이터베이스 연결 반환
        
        Returns:
            AsyncConnection: 데이터베이스 연결
        """
        if not await self.is_connected():
            await self.connect()
        
        return self.engine.connect()
    
    async def get_session(self) -> AsyncSession:
        """
        세션 반환
        
        Returns:
            AsyncSession: 세션
        """
        if not await self.is_connected():
            await self.connect()
        
        async_session = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        return async_session()
    
    async def get_collection(self, collection_name: str, db_name: Optional[str] = None) -> Table:
        """
        테이블 객체 반환
        
        Args:
            collection_name: 테이블 이름
            db_name: 데이터베이스 이름 (기본값: None)
            
        Returns:
            Table: 테이블 객체
        """
        if not await self.is_connected():
            await self.connect()
        
        # 테이블이 이미 메타데이터에 있는지 확인
        if collection_name in self.metadata.tables:
            return self.metadata.tables[collection_name]
        
        # 테이블 반영
        async with self.engine.connect() as conn:
            await conn.run_sync(lambda sync_conn: self.metadata.reflect(
                bind=sync_conn, only=[collection_name]
            ))
        
        # 테이블이 메타데이터에 있는지 다시 확인
        if collection_name in self.metadata.tables:
            return self.metadata.tables[collection_name]
        
        # 테이블이 없으면 예외 발생
        raise ValueError(f"Table {collection_name} not found in database")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        상태 확인
        
        Returns:
            Dict[str, Any]: 상태 정보
        """
        result = {
            "status": "disconnected",
            "details": {}
        }
        
        if not self.engine:
            return result
        
        try:
            # 응답 시간 측정
            start_time = time.time()
            async with self.engine.connect() as conn:
                await conn.execute(select(1))
            end_time = time.time()
            
            # 상태 정보 구성
            result["status"] = "connected"
            result["details"] = {
                "response_time_ms": round((end_time - start_time) * 1000, 2),
                "dialect": self.engine.dialect.name,
                "driver": self.engine.dialect.driver
            }
        except Exception as e:
            result["status"] = "error"
            result["details"] = {
                "error": str(e)
            }
        
        return result


class BaseSQLAlchemyRepository(RepositoryInterface[T]):
    """
    기본 SQLAlchemy 저장소 구현체
    """
    
    def __init__(self, client: SQLAlchemyClient, table_name: str, model_class: Type[T]):
        """
        초기화
        
        Args:
            client: SQLAlchemy 클라이언트
            table_name: 테이블 이름
            model_class: 모델 클래스
        """
        self.client = client
        self.table_name = table_name
        self.model_class = model_class
        self._table = None
        
        logger.debug(f"SQLAlchemy repository initialized for table: {table_name}")
    
    def _get_table(self) -> Table:
        """
        테이블 객체 반환
        
        Returns:
            Table: 테이블 객체
        """
        if not self._table:
            self._table = self.client.get_collection(self.table_name)
        return self._table
    
    def _to_model(self, data: Dict[str, Any]) -> Optional[T]:
        """
        데이터를 모델로 변환
        
        Args:
            data: 데이터
            
        Returns:
            Optional[T]: 모델 또는 None
        """
        if not data:
            return None
        
        return self.model_class(**data)
    
    def _to_document(self, item: T) -> Dict[str, Any]:
        """
        모델을 문서로 변환
        
        Args:
            item: 모델
            
        Returns:
            Dict[str, Any]: 문서
        """
        # 모델을 딕셔너리로 변환
        return item.model_dump(exclude_unset=True)
    
    def find_by_id(self, id: str) -> Optional[T]:
        """
        ID로 항목 조회
        
        Args:
            id: 항목 ID
            
        Returns:
            Optional[T]: 항목 또는 None
        """
        table = self._get_table()
        
        with self.client.get_connection() as conn:
            result = conn.execute(
                select(table).where(table.c.id == id)
            ).first()
        
        if not result:
            return None
        
        return self._to_model(dict(result))
    
    def find_one(self, filter: Dict[str, Any]) -> Optional[T]:
        """
        필터로 단일 항목 조회
        
        Args:
            filter: 필터
            
        Returns:
            Optional[T]: 항목 또는 None
        """
        table = self._get_table()
        
        # 필터 조건 구성
        conditions = []
        for key, value in filter.items():
            if hasattr(table.c, key):
                conditions.append(getattr(table.c, key) == value)
        
        with self.client.get_connection() as conn:
            result = conn.execute(
                select(table).where(*conditions)
            ).first()
        
        if not result:
            return None
        
        return self._to_model(dict(result))
    
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
        table = self._get_table()
        
        # 필터 조건 구성
        conditions = []
        for key, value in filter.items():
            if hasattr(table.c, key):
                conditions.append(getattr(table.c, key) == value)
        
        with self.client.get_connection() as conn:
            query = select(table).where(*conditions).offset(skip).limit(limit)
            results = conn.execute(query).fetchall()
        
        return [self._to_model(dict(row)) for row in results]
    
    def create(self, item: T) -> T:
        """
        항목 생성
        
        Args:
            item: 생성할 항목
            
        Returns:
            T: 생성된 항목
        """
        table = self._get_table()
        document = self._to_document(item)
        
        # 생성 시간 추가
        if 'created_at' not in document:
            document['created_at'] = datetime.utcnow()
        
        # 업데이트 시간 추가
        document['updated_at'] = datetime.utcnow()
        
        with self.client.get_connection() as conn:
            result = conn.execute(
                insert(table).values(**document)
            )
            conn.commit()
        
        # 생성된 항목 반환
        if 'id' in document:
            return self.find_by_id(document['id'])
        elif result.inserted_primary_key:
            return self.find_by_id(str(result.inserted_primary_key[0]))
        else:
            return item
    
    def update(self, id: str, item: T) -> Optional[T]:
        """
        항목 업데이트
        
        Args:
            id: 항목 ID
            item: 업데이트할 항목
            
        Returns:
            Optional[T]: 업데이트된 항목 또는 None
        """
        table = self._get_table()
        document = self._to_document(item)
        
        # 업데이트 시간 추가
        document['updated_at'] = datetime.utcnow()
        
        with self.client.get_connection() as conn:
            result = conn.execute(
                update(table).where(table.c.id == id).values(**document)
            )
            conn.commit()
        
        if result.rowcount == 0:
            return None
        
        # 업데이트된 항목 반환
        return self.find_by_id(id)
    
    def delete(self, id: str) -> bool:
        """
        항목 삭제
        
        Args:
            id: 항목 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        table = self._get_table()
        
        with self.client.get_connection() as conn:
            result = conn.execute(
                delete(table).where(table.c.id == id)
            )
            conn.commit()
        
        return result.rowcount > 0
    
    def count(self, filter: Dict[str, Any]) -> int:
        """
        항목 수 조회
        
        Args:
            filter: 필터
            
        Returns:
            int: 항목 수
        """
        table = self._get_table()
        
        # 필터 조건 구성
        conditions = []
        for key, value in filter.items():
            if hasattr(table.c, key):
                conditions.append(getattr(table.c, key) == value)
        
        with self.client.get_connection() as conn:
            result = conn.execute(
                select(func.count()).select_from(table).where(*conditions)
            ).scalar()
        
        return result or 0


class AsyncBaseSQLAlchemyRepository(AsyncRepositoryInterface[T]):
    """
    비동기 기본 SQLAlchemy 저장소 구현체
    """
    
    def __init__(self, client: AsyncSQLAlchemyClient, table_name: str, model_class: Type[T]):
        """
        초기화
        
        Args:
            client: 비동기 SQLAlchemy 클라이언트
            table_name: 테이블 이름
            model_class: 모델 클래스
        """
        self.client = client
        self.table_name = table_name
        self.model_class = model_class
        self._table = None
        
        logger.debug(f"Async SQLAlchemy repository initialized for table: {table_name}")
    
    async def _get_table(self) -> Table:
        """
        테이블 객체 반환
        
        Returns:
            Table: 테이블 객체
        """
        if not self._table:
            self._table = await self.client.get_collection(self.table_name)
        return self._table
    
    def _to_model(self, data: Dict[str, Any]) -> Optional[T]:
        """
        데이터를 모델로 변환
        
        Args:
            data: 데이터
            
        Returns:
            Optional[T]: 모델 또는 None
        """
        if not data:
            return None
        
        return self.model_class(**data)
    
    def _to_document(self, item: T) -> Dict[str, Any]:
        """
        모델을 문서로 변환
        
        Args:
            item: 모델
            
        Returns:
            Dict[str, Any]: 문서
        """
        # 모델을 딕셔너리로 변환
        return item.model_dump(exclude_unset=True)
    
    async def find_by_id(self, id: str) -> Optional[T]:
        """
        ID로 항목 조회
        
        Args:
            id: 항목 ID
            
        Returns:
            Optional[T]: 항목 또는 None
        """
        table = await self._get_table()
        
        async with self.client.get_connection() as conn:
            result = await conn.execute(
                select(table).where(table.c.id == id)
            )
            row = result.first()
        
        if not row:
            return None
        
        return self._to_model(dict(row))
    
    async def find_one(self, filter: Dict[str, Any]) -> Optional[T]:
        """
        필터로 단일 항목 조회
        
        Args:
            filter: 필터
            
        Returns:
            Optional[T]: 항목 또는 None
        """
        table = await self._get_table()
        
        # 필터 조건 구성
        conditions = []
        for key, value in filter.items():
            if hasattr(table.c, key):
                conditions.append(getattr(table.c, key) == value)
        
        async with self.client.get_connection() as conn:
            result = await conn.execute(
                select(table).where(*conditions)
            )
            row = result.first()
        
        if not row:
            return None
        
        return self._to_model(dict(row))
    
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
        table = await self._get_table()
        
        # 필터 조건 구성
        conditions = []
        for key, value in filter.items():
            if hasattr(table.c, key):
                conditions.append(getattr(table.c, key) == value)
        
        async with self.client.get_connection() as conn:
            query = select(table).where(*conditions).offset(skip).limit(limit)
            result = await conn.execute(query)
            rows = result.fetchall()
        
        return [self._to_model(dict(row)) for row in rows]
    
    async def create(self, item: T) -> T:
        """
        항목 생성
        
        Args:
            item: 생성할 항목
            
        Returns:
            T: 생성된 항목
        """
        table = await self._get_table()
        document = self._to_document(item)
        
        # 생성 시간 추가
        if 'created_at' not in document:
            document['created_at'] = datetime.utcnow()
        
        # 업데이트 시간 추가
        document['updated_at'] = datetime.utcnow()
        
        async with self.client.get_connection() as conn:
            result = await conn.execute(
                insert(table).values(**document)
            )
            await conn.commit()
        
        # 생성된 항목 반환
        if 'id' in document:
            return await self.find_by_id(document['id'])
        elif result.inserted_primary_key:
            return await self.find_by_id(str(result.inserted_primary_key[0]))
        else:
            return item
    
    async def update(self, id: str, item: T) -> Optional[T]:
        """
        항목 업데이트
        
        Args:
            id: 항목 ID
            item: 업데이트할 항목
            
        Returns:
            Optional[T]: 업데이트된 항목 또는 None
        """
        table = await self._get_table()
        document = self._to_document(item)
        
        # 업데이트 시간 추가
        document['updated_at'] = datetime.utcnow()
        
        async with self.client.get_connection() as conn:
            result = await conn.execute(
                update(table).where(table.c.id == id).values(**document)
            )
            await conn.commit()
        
        if result.rowcount == 0:
            return None
        
        # 업데이트된 항목 반환
        return await self.find_by_id(id)
    
    async def delete(self, id: str) -> bool:
        """
        항목 삭제
        
        Args:
            id: 항목 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        table = await self._get_table()
        
        async with self.client.get_connection() as conn:
            result = await conn.execute(
                delete(table).where(table.c.id == id)
            )
            await conn.commit()
        
        return result.rowcount > 0
    
    async def count(self, filter: Dict[str, Any]) -> int:
        """
        항목 수 조회
        
        Args:
            filter: 필터
            
        Returns:
            int: 항목 수
        """
        table = await self._get_table()
        
        # 필터 조건 구성
        conditions = []
        for key, value in filter.items():
            if hasattr(table.c, key):
                conditions.append(getattr(table.c, key) == value)
        
        async with self.client.get_connection() as conn:
            result = await conn.execute(
                select(func.count()).select_from(table).where(*conditions)
            )
            count = result.scalar()
        
        return count or 0
