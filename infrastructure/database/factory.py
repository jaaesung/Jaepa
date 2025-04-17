"""
데이터베이스 팩토리 모듈

설정에 따라 적절한 데이터베이스 클라이언트를 생성하는 팩토리를 제공합니다.
"""
import logging
from typing import Dict, Any, Optional, Union, Type

from core.config import settings
from .interface import DatabaseClientInterface, AsyncDatabaseClientInterface
from .mongodb import MongoDBClient, AsyncMongoDBClient
from .sqlalchemy import SQLAlchemyClient, AsyncSQLAlchemyClient

# 로깅 설정
logger = logging.getLogger(__name__)


class DatabaseFactory:
    """
    데이터베이스 팩토리
    
    설정에 따라 적절한 데이터베이스 클라이언트를 생성합니다.
    """
    
    @staticmethod
    def create_client(
        engine: Optional[str] = None,
        **kwargs
    ) -> DatabaseClientInterface:
        """
        데이터베이스 클라이언트 생성
        
        Args:
            engine: 데이터베이스 엔진 (기본값: None, 설정에서 가져옴)
            **kwargs: 추가 인자
            
        Returns:
            DatabaseClientInterface: 데이터베이스 클라이언트
            
        Raises:
            ValueError: 지원하지 않는 데이터베이스 엔진
        """
        # 엔진이 지정되지 않은 경우 설정에서 가져옴
        if engine is None:
            engine = settings.db.engine
        
        # MongoDB 클라이언트 생성
        if engine == "mongodb":
            return DatabaseFactory._create_mongodb_client(**kwargs)
        
        # SQLite 클라이언트 생성
        elif engine == "sqlite":
            return DatabaseFactory._create_sqlite_client(**kwargs)
        
        # 지원하지 않는 엔진
        else:
            raise ValueError(f"Unsupported database engine: {engine}")
    
    @staticmethod
    def create_async_client(
        engine: Optional[str] = None,
        **kwargs
    ) -> AsyncDatabaseClientInterface:
        """
        비동기 데이터베이스 클라이언트 생성
        
        Args:
            engine: 데이터베이스 엔진 (기본값: None, 설정에서 가져옴)
            **kwargs: 추가 인자
            
        Returns:
            AsyncDatabaseClientInterface: 비동기 데이터베이스 클라이언트
            
        Raises:
            ValueError: 지원하지 않는 데이터베이스 엔진
        """
        # 엔진이 지정되지 않은 경우 설정에서 가져옴
        if engine is None:
            engine = settings.db.engine
        
        # MongoDB 클라이언트 생성
        if engine == "mongodb":
            return DatabaseFactory._create_async_mongodb_client(**kwargs)
        
        # SQLite 클라이언트 생성
        elif engine == "sqlite":
            return DatabaseFactory._create_async_sqlite_client(**kwargs)
        
        # 지원하지 않는 엔진
        else:
            raise ValueError(f"Unsupported database engine: {engine}")
    
    @staticmethod
    def _create_mongodb_client(**kwargs) -> MongoDBClient:
        """
        MongoDB 클라이언트 생성
        
        Args:
            **kwargs: 추가 인자
            
        Returns:
            MongoDBClient: MongoDB 클라이언트
        """
        # 기본 설정
        config = {
            "uri": settings.db.mongo_uri,
            "default_db_name": settings.db.mongo_db_name,
            "connect_timeout": settings.db.mongo_connect_timeout,
            "max_pool_size": settings.db.mongo_max_pool_size,
            "min_pool_size": settings.db.mongo_min_pool_size,
            "max_idle_time_ms": settings.db.mongo_max_idle_time_ms,
            "retry_writes": settings.db.mongo_retry_writes,
            "retry_reads": settings.db.mongo_retry_reads,
            "server_selection_timeout_ms": settings.db.mongo_server_selection_timeout_ms,
            "socket_timeout_ms": settings.db.mongo_socket_timeout_ms,
            "heartbeat_frequency_ms": settings.db.mongo_heartbeat_frequency_ms,
            "app_name": settings.app_name
        }
        
        # 추가 인자로 설정 업데이트
        config.update(kwargs)
        
        logger.debug(f"Creating MongoDB client with URI: {config['uri']}")
        return MongoDBClient(**config)
    
    @staticmethod
    def _create_async_mongodb_client(**kwargs) -> AsyncMongoDBClient:
        """
        비동기 MongoDB 클라이언트 생성
        
        Args:
            **kwargs: 추가 인자
            
        Returns:
            AsyncMongoDBClient: 비동기 MongoDB 클라이언트
        """
        # 기본 설정
        config = {
            "uri": settings.db.mongo_uri,
            "default_db_name": settings.db.mongo_db_name,
            "connect_timeout": settings.db.mongo_connect_timeout,
            "max_pool_size": settings.db.mongo_max_pool_size,
            "min_pool_size": settings.db.mongo_min_pool_size,
            "max_idle_time_ms": settings.db.mongo_max_idle_time_ms,
            "retry_writes": settings.db.mongo_retry_writes,
            "retry_reads": settings.db.mongo_retry_reads,
            "server_selection_timeout_ms": settings.db.mongo_server_selection_timeout_ms,
            "socket_timeout_ms": settings.db.mongo_socket_timeout_ms,
            "heartbeat_frequency_ms": settings.db.mongo_heartbeat_frequency_ms,
            "app_name": settings.app_name
        }
        
        # 추가 인자로 설정 업데이트
        config.update(kwargs)
        
        logger.debug(f"Creating async MongoDB client with URI: {config['uri']}")
        return AsyncMongoDBClient(**config)
    
    @staticmethod
    def _create_sqlite_client(**kwargs) -> SQLAlchemyClient:
        """
        SQLite 클라이언트 생성
        
        Args:
            **kwargs: 추가 인자
            
        Returns:
            SQLAlchemyClient: SQLite 클라이언트
        """
        # 기본 설정
        config = {
            "url": settings.db.sqlite_url,
            "connect_args": settings.db.sqlite_connect_args,
            "echo": settings.debug
        }
        
        # 추가 인자로 설정 업데이트
        config.update(kwargs)
        
        logger.debug(f"Creating SQLite client with URL: {config['url']}")
        return SQLAlchemyClient(**config)
    
    @staticmethod
    def _create_async_sqlite_client(**kwargs) -> AsyncSQLAlchemyClient:
        """
        비동기 SQLite 클라이언트 생성
        
        Args:
            **kwargs: 추가 인자
            
        Returns:
            AsyncSQLAlchemyClient: 비동기 SQLite 클라이언트
        """
        # SQLite URL을 비동기 형식으로 변환
        url = settings.db.sqlite_url
        if url.startswith("sqlite:///"):
            url = url.replace("sqlite:///", "sqlite+aiosqlite:///")
        
        # 기본 설정
        config = {
            "url": url,
            "connect_args": settings.db.sqlite_connect_args,
            "echo": settings.debug
        }
        
        # 추가 인자로 설정 업데이트
        config.update(kwargs)
        
        logger.debug(f"Creating async SQLite client with URL: {config['url']}")
        return AsyncSQLAlchemyClient(**config)
