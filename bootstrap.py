"""
애플리케이션 부트스트랩 모듈

애플리케이션 시작 시 필요한 초기화 작업을 수행합니다.
"""
import logging
import importlib
from typing import Dict, Any, List, Type, Optional

from config import settings
from core import (
    container, register_mongodb_client, register_http_client,
    register_news_source_manager, register_sentiment_analyzer,
    register_news_crawler, register_sentiment_analysis_service,
    register_stock_data_service
)
from core.interfaces import (
    DatabaseClient, MongoDBClient, HttpClient, 
    NewsSourceManager, SentimentAnalyzer
)

# 로깅 설정
logger = logging.getLogger(__name__)


def import_class(class_path: str) -> Type:
    """
    문자열 경로에서 클래스 가져오기
    
    Args:
        class_path: 클래스 경로 (예: 'module.submodule.ClassName')
        
    Returns:
        Type: 클래스 객체
        
    Raises:
        ImportError: 클래스를 가져올 수 없는 경우
    """
    try:
        module_path, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to import class {class_path}: {e}")
        raise ImportError(f"Failed to import class {class_path}: {e}")


def setup_logging() -> None:
    """
    로깅 설정
    """
    log_level = getattr(logging, settings.logging.level)
    log_format = settings.logging.format
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
    )
    
    if settings.logging.file_enabled:
        file_handler = logging.FileHandler(settings.logging.file_path)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
    
    logger.info(f"Logging initialized with level: {settings.logging.level}")


def setup_database() -> None:
    """
    데이터베이스 설정
    """
    # MongoDB 클라이언트 등록
    mongodb_client_class = import_class(settings.db.client_class)
    register_mongodb_client(mongodb_client_class)
    
    logger.info(f"Database setup completed with client: {mongodb_client_class.__name__}")


def setup_http_client() -> None:
    """
    HTTP 클라이언트 설정
    """
    # HTTP 클라이언트 등록
    http_client_class = import_class(settings.api.client_class)
    register_http_client(http_client_class)
    
    logger.info(f"HTTP client setup completed with client: {http_client_class.__name__}")


def setup_news_sources() -> None:
    """
    뉴스 소스 설정
    """
    # 뉴스 소스 관리자 등록
    news_source_manager_class = import_class(settings.crawling.source_manager_class)
    register_news_source_manager(news_source_manager_class)
    
    # 뉴스 소스 등록
    news_source_manager = container.news_source_manager()
    
    for source_config in settings.crawling.news_sources.values():
        source_class = import_class(source_config.get('class'))
        source = source_class(
            http_client=container.http_client(),
            **source_config.get('params', {})
        )
        news_source_manager.register_source(source)
    
    logger.info(f"News sources setup completed with {len(settings.crawling.news_sources)} sources")


def setup_sentiment_analyzer() -> None:
    """
    감성 분석기 설정
    """
    # 감성 분석기 등록
    sentiment_analyzer_class = import_class(settings.sentiment.analyzer_class)
    register_sentiment_analyzer(sentiment_analyzer_class)
    
    logger.info(f"Sentiment analyzer setup completed with analyzer: {sentiment_analyzer_class.__name__}")


def setup_services() -> None:
    """
    서비스 설정
    """
    # 뉴스 크롤러 등록
    news_crawler_class = import_class(settings.crawling.crawler_class)
    register_news_crawler(news_crawler_class)
    
    # 감성 분석 서비스 등록
    sentiment_analysis_service_class = import_class(settings.sentiment.service_class)
    register_sentiment_analysis_service(sentiment_analysis_service_class)
    
    # 주식 데이터 서비스 등록
    stock_data_service_class = import_class(settings.stock.service_class)
    register_stock_data_service(stock_data_service_class)
    
    logger.info("Services setup completed")


def bootstrap_app() -> None:
    """
    애플리케이션 부트스트랩
    
    애플리케이션 시작 시 필요한 초기화 작업을 수행합니다.
    """
    try:
        # 로깅 설정
        setup_logging()
        
        # 데이터베이스 설정
        setup_database()
        
        # HTTP 클라이언트 설정
        setup_http_client()
        
        # 뉴스 소스 설정
        setup_news_sources()
        
        # 감성 분석기 설정
        setup_sentiment_analyzer()
        
        # 서비스 설정
        setup_services()
        
        logger.info("Application bootstrap completed successfully")
    except Exception as e:
        logger.error(f"Application bootstrap failed: {e}")
        raise
