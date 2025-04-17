"""
데이터베이스 설정 모듈

데이터베이스 설정 및 초기화 기능을 제공합니다.
"""
import os
import logging
import asyncio
from typing import Dict, List, Optional, Any, Set
from pathlib import Path

from dotenv import load_dotenv

from infrastructure.database.database_client import MongoDBClient
from infrastructure.database.async_database_client import AsyncMongoDBClient
from infrastructure.database.connection_manager import ConnectionManager, AsyncConnectionManager

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
env_path = Path(__file__).parents[2] / '.env'
load_dotenv(dotenv_path=env_path)


def get_mongodb_config() -> Dict[str, Any]:
    """
    MongoDB 설정 가져오기
    
    Returns:
        Dict[str, Any]: MongoDB 설정
    """
    return {
        "uri": os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
        "default_db_name": os.getenv("MONGODB_DB_NAME", "jaepa"),
        "connect_timeout": int(os.getenv("MONGODB_CONNECT_TIMEOUT", "5000")),
        "max_pool_size": int(os.getenv("MONGODB_MAX_POOL_SIZE", "10")),
        "min_pool_size": int(os.getenv("MONGODB_MIN_POOL_SIZE", "1")),
        "max_idle_time_ms": int(os.getenv("MONGODB_MAX_IDLE_TIME_MS", "60000")),
        "retry_writes": os.getenv("MONGODB_RETRY_WRITES", "true").lower() == "true",
        "retry_reads": os.getenv("MONGODB_RETRY_READS", "true").lower() == "true",
        "server_selection_timeout_ms": int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "30000")),
        "socket_timeout_ms": int(os.getenv("MONGODB_SOCKET_TIMEOUT_MS", "30000")),
        "heartbeat_frequency_ms": int(os.getenv("MONGODB_HEARTBEAT_FREQUENCY_MS", "10000")),
        "app_name": os.getenv("MONGODB_APP_NAME", "JaePa")
    }


def create_mongodb_client() -> MongoDBClient:
    """
    MongoDB 클라이언트 생성
    
    Returns:
        MongoDBClient: MongoDB 클라이언트
    """
    config = get_mongodb_config()
    return MongoDBClient(**config)


def create_async_mongodb_client() -> AsyncMongoDBClient:
    """
    비동기 MongoDB 클라이언트 생성
    
    Returns:
        AsyncMongoDBClient: 비동기 MongoDB 클라이언트
    """
    config = get_mongodb_config()
    return AsyncMongoDBClient(**config)


def create_connection_manager() -> ConnectionManager:
    """
    연결 관리자 생성
    
    Returns:
        ConnectionManager: 연결 관리자
    """
    client = create_mongodb_client()
    return ConnectionManager(
        client=client,
        health_check_interval=int(os.getenv("MONGODB_HEALTH_CHECK_INTERVAL", "60")),
        reconnect_interval=int(os.getenv("MONGODB_RECONNECT_INTERVAL", "5")),
        max_reconnect_attempts=int(os.getenv("MONGODB_MAX_RECONNECT_ATTEMPTS", "5"))
    )


def create_async_connection_manager() -> AsyncConnectionManager:
    """
    비동기 연결 관리자 생성
    
    Returns:
        AsyncConnectionManager: 비동기 연결 관리자
    """
    return AsyncConnectionManager(
        client_factory=create_async_mongodb_client,
        health_check_interval=int(os.getenv("MONGODB_HEALTH_CHECK_INTERVAL", "60")),
        reconnect_interval=int(os.getenv("MONGODB_RECONNECT_INTERVAL", "5")),
        max_reconnect_attempts=int(os.getenv("MONGODB_MAX_RECONNECT_ATTEMPTS", "5"))
    )


# 싱글톤 인스턴스
_connection_manager = None
_async_connection_manager = None


def get_connection_manager() -> ConnectionManager:
    """
    연결 관리자 가져오기
    
    Returns:
        ConnectionManager: 연결 관리자
    """
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = create_connection_manager()
        _connection_manager.start()
    return _connection_manager


def get_async_connection_manager() -> AsyncConnectionManager:
    """
    비동기 연결 관리자 가져오기
    
    Returns:
        AsyncConnectionManager: 비동기 연결 관리자
    """
    global _async_connection_manager
    if _async_connection_manager is None:
        _async_connection_manager = create_async_connection_manager()
        # 비동기 시작은 호출자가 처리해야 함
    return _async_connection_manager


def get_mongodb_client() -> MongoDBClient:
    """
    MongoDB 클라이언트 가져오기
    
    Returns:
        MongoDBClient: MongoDB 클라이언트
    """
    return get_connection_manager().get_client()


async def get_async_mongodb_client() -> AsyncMongoDBClient:
    """
    비동기 MongoDB 클라이언트 가져오기
    
    Returns:
        AsyncMongoDBClient: 비동기 MongoDB 클라이언트
    """
    manager = get_async_connection_manager()
    if not hasattr(manager, "_started") or not manager._started:
        await manager.start()
        manager._started = True
    return await manager.get_client()


async def create_indexes() -> Dict[str, List[str]]:
    """
    인덱스 생성
    
    Returns:
        Dict[str, List[str]]: 컬렉션별 생성된 인덱스 이름 목록
    """
    from infrastructure.repository.news_repository import NewsRepository
    from infrastructure.repository.user_repository import UserRepository
    from infrastructure.repository.sentiment_repository import SentimentRepository, SentimentTrendRepository
    
    # 비동기 클라이언트 가져오기
    client = await get_async_mongodb_client()
    db_name = get_mongodb_config()["default_db_name"]
    
    # 저장소 생성
    news_repo = NewsRepository(client, db_name)
    user_repo = UserRepository(client, db_name)
    sentiment_repo = SentimentRepository(client, db_name)
    sentiment_trend_repo = SentimentTrendRepository(client, db_name)
    
    # 인덱스 생성
    results = {}
    
    # 뉴스 인덱스
    news_indexes = await news_repo.create_indexes()
    results["news"] = news_indexes
    
    # 사용자 인덱스
    user_indexes = await user_repo.create_indexes()
    results["users"] = user_indexes
    
    # 감성 분석 인덱스
    sentiment_indexes = await sentiment_repo.create_indexes()
    results["sentiment_analysis"] = sentiment_indexes
    
    # 감성 트렌드 인덱스
    sentiment_trend_indexes = await sentiment_trend_repo.create_indexes()
    results["sentiment_trends"] = sentiment_trend_indexes
    
    return results


async def initialize_database() -> None:
    """
    데이터베이스 초기화
    """
    try:
        # 비동기 클라이언트 가져오기
        client = await get_async_mongodb_client()
        
        # 연결 확인
        if not await client.is_connected():
            logger.error("데이터베이스 연결 실패")
            return
        
        # 상태 확인
        health = await client.health_check()
        logger.info(f"데이터베이스 상태: {health['status']}")
        
        # 인덱스 생성
        indexes = await create_indexes()
        
        # 결과 로깅
        for collection, index_names in indexes.items():
            logger.info(f"컬렉션 '{collection}'에 {len(index_names)}개 인덱스 생성됨")
        
        logger.info("데이터베이스 초기화 완료")
        
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {str(e)}")


def shutdown_database() -> None:
    """
    데이터베이스 연결 종료
    """
    global _connection_manager, _async_connection_manager
    
    try:
        # 동기 연결 관리자 종료
        if _connection_manager is not None:
            _connection_manager.stop()
            _connection_manager = None
        
        # 비동기 연결 관리자 종료는 비동기 함수이므로 여기서 직접 호출할 수 없음
        # 호출자가 shutdown_async_database()를 호출해야 함
        
        logger.info("데이터베이스 연결 종료 완료")
        
    except Exception as e:
        logger.error(f"데이터베이스 연결 종료 실패: {str(e)}")


async def shutdown_async_database() -> None:
    """
    비동기 데이터베이스 연결 종료
    """
    global _async_connection_manager
    
    try:
        # 비동기 연결 관리자 종료
        if _async_connection_manager is not None:
            await _async_connection_manager.stop()
            _async_connection_manager = None
        
        logger.info("비동기 데이터베이스 연결 종료 완료")
        
    except Exception as e:
        logger.error(f"비동기 데이터베이스 연결 종료 실패: {str(e)}")


# 애플리케이션 시작 시 호출
def setup_database() -> None:
    """
    데이터베이스 설정
    """
    # 동기 연결 관리자 시작
    get_connection_manager()
    
    # 비동기 초기화는 비동기 컨텍스트에서 호출해야 함
    logger.info("데이터베이스 설정 완료")


# 애플리케이션 종료 시 호출
def cleanup_database() -> None:
    """
    데이터베이스 정리
    """
    shutdown_database()
    logger.info("데이터베이스 정리 완료")
