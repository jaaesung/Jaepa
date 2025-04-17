"""
데이터베이스 모듈

데이터베이스 접근을 위한 클라이언트 및 저장소 구현체를 제공합니다.
"""
from .interface import (
    DatabaseClientInterface, RepositoryInterface,
    AsyncDatabaseClientInterface, AsyncRepositoryInterface
)
from .mongodb import (
    MongoDBClient, AsyncMongoDBClient,
    BaseMongoRepository, AsyncBaseMongoRepository
)
from .sqlalchemy import (
    SQLAlchemyClient, AsyncSQLAlchemyClient,
    BaseSQLAlchemyRepository, AsyncBaseSQLAlchemyRepository
)
from .factory import DatabaseFactory


__all__ = [
    # 인터페이스
    "DatabaseClientInterface",
    "RepositoryInterface",
    "AsyncDatabaseClientInterface",
    "AsyncRepositoryInterface",

    # MongoDB 구현체
    "MongoDBClient",
    "AsyncMongoDBClient",
    "BaseMongoRepository",
    "AsyncBaseMongoRepository",

    # SQLAlchemy 구현체
    "SQLAlchemyClient",
    "AsyncSQLAlchemyClient",
    "BaseSQLAlchemyRepository",
    "AsyncBaseSQLAlchemyRepository",

    # 팩토리
    "DatabaseFactory"
]
