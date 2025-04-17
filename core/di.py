"""
의존성 주입 컨테이너 모듈

dependency_injector 라이브러리를 사용하여 의존성 주입 컨테이너를 구현합니다.
"""
import logging
from typing import Dict, Any, Optional

from dependency_injector import containers, providers

from core.config import settings
from core.interfaces import (
    DatabaseClient, MongoDBClient, HttpClient,
    NewsSourceManager, SentimentAnalyzer
)

# 로깅 설정
logger = logging.getLogger(__name__)


class Container(containers.DeclarativeContainer):
    """
    의존성 주입 컨테이너

    JaePa 프로젝트의 의존성 주입 컨테이너를 정의합니다.
    """

    # 설정 제공자
    config = providers.Configuration()

    # 설정 로드
    config.from_dict(settings.model_dump())

    # 로깅 제공자
    logging = providers.Resource(
        logging.basicConfig,
        level=getattr(logging, config.logging.level),
        format=config.logging.format,
    )

    # 데이터베이스 클라이언트 제공자 (싱글톤)
    mongodb_client = providers.Singleton(
        lambda: None,  # 실제 구현체는 나중에 등록
        config=config.db,
    )

    # HTTP 클라이언트 제공자 (싱글톤)
    http_client = providers.Singleton(
        lambda: None,  # 실제 구현체는 나중에 등록
        config=config.api,
    )

    # 뉴스 소스 관리자 제공자 (싱글톤)
    news_source_manager = providers.Singleton(
        lambda: None,  # 실제 구현체는 나중에 등록
        http_client=http_client,
        config=config.crawling,
    )

    # 감성 분석기 제공자 (싱글톤)
    sentiment_analyzer = providers.Singleton(
        lambda: None,  # 실제 구현체는 나중에 등록
        config=config.sentiment,
    )

    # 뉴스 크롤러 제공자 (팩토리)
    news_crawler = providers.Factory(
        lambda: None,  # 실제 구현체는 나중에 등록
        http_client=http_client,
        news_source_manager=news_source_manager,
        mongodb_client=mongodb_client,
        config=config.crawling,
    )

    # 감성 분석 서비스 제공자 (팩토리)
    sentiment_analysis_service = providers.Factory(
        lambda: None,  # 실제 구현체는 나중에 등록
        sentiment_analyzer=sentiment_analyzer,
        mongodb_client=mongodb_client,
        config=config.sentiment,
    )

    # 주식 데이터 서비스 제공자 (팩토리)
    stock_data_service = providers.Factory(
        lambda: None,  # 실제 구현체는 나중에 등록
        mongodb_client=mongodb_client,
        http_client=http_client,
        config=config.stock,
    )


# 전역 컨테이너 인스턴스
container = Container()


def register_mongodb_client(client_class):
    """
    MongoDB 클라이언트 구현체 등록

    Args:
        client_class: MongoDBClient 인터페이스를 구현한 클래스
    """
    if not issubclass(client_class, MongoDBClient):
        raise TypeError(f"{client_class.__name__} is not a subclass of MongoDBClient")

    container.mongodb_client.override(
        providers.Singleton(
            client_class,
            config=container.config.db,
        )
    )
    logger.info(f"Registered MongoDB client: {client_class.__name__}")


def register_http_client(client_class):
    """
    HTTP 클라이언트 구현체 등록

    Args:
        client_class: HttpClient 인터페이스를 구현한 클래스
    """
    if not issubclass(client_class, HttpClient):
        raise TypeError(f"{client_class.__name__} is not a subclass of HttpClient")

    container.http_client.override(
        providers.Singleton(
            client_class,
            config=container.config.api,
        )
    )
    logger.info(f"Registered HTTP client: {client_class.__name__}")


def register_news_source_manager(manager_class):
    """
    뉴스 소스 관리자 구현체 등록

    Args:
        manager_class: NewsSourceManager 인터페이스를 구현한 클래스
    """
    if not issubclass(manager_class, NewsSourceManager):
        raise TypeError(f"{manager_class.__name__} is not a subclass of NewsSourceManager")

    container.news_source_manager.override(
        providers.Singleton(
            manager_class,
            http_client=container.http_client,
            config=container.config.crawling,
        )
    )
    logger.info(f"Registered news source manager: {manager_class.__name__}")


def register_sentiment_analyzer(analyzer_class):
    """
    감성 분석기 구현체 등록

    Args:
        analyzer_class: SentimentAnalyzer 인터페이스를 구현한 클래스
    """
    if not issubclass(analyzer_class, SentimentAnalyzer):
        raise TypeError(f"{analyzer_class.__name__} is not a subclass of SentimentAnalyzer")

    container.sentiment_analyzer.override(
        providers.Singleton(
            analyzer_class,
            config=container.config.sentiment,
        )
    )
    logger.info(f"Registered sentiment analyzer: {analyzer_class.__name__}")


def register_news_crawler(crawler_class):
    """
    뉴스 크롤러 구현체 등록

    Args:
        crawler_class: 뉴스 크롤러 클래스
    """
    container.news_crawler.override(
        providers.Factory(
            crawler_class,
            http_client=container.http_client,
            news_source_manager=container.news_source_manager,
            mongodb_client=container.mongodb_client,
            config=container.config.crawling,
        )
    )
    logger.info(f"Registered news crawler: {crawler_class.__name__}")


def register_sentiment_analysis_service(service_class):
    """
    감성 분석 서비스 구현체 등록

    Args:
        service_class: 감성 분석 서비스 클래스
    """
    container.sentiment_analysis_service.override(
        providers.Factory(
            service_class,
            sentiment_analyzer=container.sentiment_analyzer,
            mongodb_client=container.mongodb_client,
            config=container.config.sentiment,
        )
    )
    logger.info(f"Registered sentiment analysis service: {service_class.__name__}")


def register_stock_data_service(service_class):
    """
    주식 데이터 서비스 구현체 등록

    Args:
        service_class: 주식 데이터 서비스 클래스
    """
    container.stock_data_service.override(
        providers.Factory(
            service_class,
            mongodb_client=container.mongodb_client,
            http_client=container.http_client,
            config=container.config.stock,
        )
    )
    logger.info(f"Registered stock data service: {service_class.__name__}")


def get_container() -> Container:
    """
    컨테이너 인스턴스 반환

    Returns:
        Container: 컨테이너 인스턴스
    """
    return container
