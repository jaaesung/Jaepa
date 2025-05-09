"""
애플리케이션 부트스트랩 모듈

애플리케이션 시작 시 필요한 초기화 작업을 수행합니다.
"""
import logging
from typing import Dict, Any, List, Optional, Type, Union

from core.config import settings
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
    # 데이터베이스 엔진 확인
    db_engine = settings.db.engine.lower()

    if db_engine == "mongodb":
        # MongoDB 클라이언트 등록
        from infrastructure.database.mongodb import MongoDBClient, AsyncMongoDBClient
        register_mongodb_client(MongoDBClient)
        logger.info(f"Database setup completed with MongoDB client")
    elif db_engine == "sqlite":
        # SQLite 클라이언트 등록
        from infrastructure.database.sqlalchemy import SQLAlchemyClient, AsyncSQLAlchemyClient
        register_mongodb_client(SQLAlchemyClient)
        logger.info(f"Database setup completed with SQLite client")
    else:
        # 기본 MongoDB 클라이언트 등록
        from infrastructure.database.mongodb import MongoDBClient
        register_mongodb_client(MongoDBClient)
        logger.info(f"Database setup completed with default MongoDB client")


def setup_http_client() -> None:
    """
    HTTP 클라이언트 설정
    """
    # HTTP 클라이언트 등록
    try:
        from infrastructure.http.aiohttp_client import AioHttpClient
        register_http_client(AioHttpClient)
        logger.info(f"HTTP client setup completed with AioHttpClient")
    except ImportError:
        logger.warning(f"AioHttpClient not found, using default HTTP client")

        # 기본 HTTP 클라이언트 등록
        class DefaultHttpClient(HttpClient):
            async def get(self, url, params=None, headers=None, **kwargs):
                raise NotImplementedError("DefaultHttpClient is a placeholder")

            async def post(self, url, data=None, json=None, headers=None, **kwargs):
                raise NotImplementedError("DefaultHttpClient is a placeholder")

            async def put(self, url, data=None, json=None, headers=None, **kwargs):
                raise NotImplementedError("DefaultHttpClient is a placeholder")

            async def delete(self, url, params=None, headers=None, **kwargs):
                raise NotImplementedError("DefaultHttpClient is a placeholder")

            async def close(self):
                pass

        register_http_client(DefaultHttpClient)
        logger.info(f"HTTP client setup completed with DefaultHttpClient")


def setup_news_sources() -> None:
    """
    뉴스 소스 설정
    """
    # 뉴스 소스 관리자 등록
    try:
        from crawling.news_source_manager import DefaultNewsSourceManager
        register_news_source_manager(DefaultNewsSourceManager)
        logger.info(f"News source manager setup completed with DefaultNewsSourceManager")

        # 뉴스 소스 등록
        news_source_manager = container.news_source_manager()

        # RSS 피드 소스 등록
        try:
            from crawling.news_sources.rss_source import RssNewsSource

            for name, config in settings.crawling.rss_feeds.items():
                source = RssNewsSource(
                    name=config.get("name", name),
                    url=config.get("url", ""),
                    fallback_url=config.get("fallback_url", ""),
                    http_client=container.http_client()
                )
                news_source_manager.register_source(source)
                logger.info(f"Registered RSS news source: {source.name}")
        except ImportError:
            logger.warning(f"RssNewsSource not found, skipping RSS sources")

        # API 소스 등록
        try:
            from crawling.news_sources.api_source import ApiNewsSource

            for name, config in settings.crawling.api_sources.items():
                source = ApiNewsSource(
                    name=name,
                    http_client=container.http_client(),
                    **config
                )
                news_source_manager.register_source(source)
                logger.info(f"Registered API news source: {name}")
        except ImportError:
            logger.warning(f"ApiNewsSource not found, skipping API sources")

        logger.info(f"News sources setup completed")
    except ImportError:
        logger.warning(f"DefaultNewsSourceManager not found, using placeholder")

        # 기본 뉴스 소스 관리자 등록
        class DefaultNewsSourceManager(NewsSourceManager):
            def __init__(self, http_client=None, config=None):
                self.sources = {}

            def register_source(self, source):
                self.sources[source.name] = source

            def get_source(self, name):
                return self.sources.get(name)

            def get_all_sources(self):
                return list(self.sources.values())

            async def get_latest_news_from_all(self, limit=10):
                return []

            async def search_news_from_all(self, keyword, limit=10):
                return []

        register_news_source_manager(DefaultNewsSourceManager)
        logger.info(f"News source manager setup completed with placeholder")


def setup_sentiment_analyzer() -> None:
    """
    감성 분석기 설정
    """
    # 감성 분석기 등록
    try:
        from analysis.finbert_sentiment import FinBERTSentiment
        register_sentiment_analyzer(FinBERTSentiment)
        logger.info(f"Sentiment analyzer setup completed with FinBERTSentiment")
    except ImportError:
        logger.warning(f"FinBERTSentiment not found, using placeholder")

        # 기본 감성 분석기 등록
        class DefaultSentimentAnalyzer(SentimentAnalyzer):
            def __init__(self, config=None):
                self.config = config or {}

            def analyze(self, text):
                return {
                    "label": "neutral",
                    "score": 0.5,
                    "scores": {"positive": 0.3, "neutral": 0.5, "negative": 0.2}
                }

            def analyze_batch(self, texts):
                return [self.analyze(text) for text in texts]

            def analyze_news(self, news):
                news["sentiment"] = self.analyze(news.get("title", "") + " " + news.get("content", ""))
                return news

            def analyze_news_batch(self, news_list):
                return [self.analyze_news(news) for news in news_list]

        register_sentiment_analyzer(DefaultSentimentAnalyzer)
        logger.info(f"Sentiment analyzer setup completed with placeholder")


def setup_services() -> None:
    """
    서비스 설정
    """
    # 뉴스 크롤러 등록
    try:
        from crawling.news_crawler import NewsCrawler
        register_news_crawler(NewsCrawler)
        logger.info(f"News crawler setup completed with NewsCrawler")
    except ImportError:
        logger.warning(f"NewsCrawler not found, using placeholder")

        # 기본 뉴스 크롤러 등록
        class DefaultNewsCrawler:
            def __init__(self, http_client=None, news_source_manager=None, mongodb_client=None, config=None):
                self.http_client = http_client
                self.news_source_manager = news_source_manager
                self.mongodb_client = mongodb_client
                self.config = config or {}

            async def crawl(self):
                logger.info("DefaultNewsCrawler.crawl() called (placeholder)")
                return {"crawled": 0}

            async def crawl_source(self, source_name):
                logger.info(f"DefaultNewsCrawler.crawl_source({source_name}) called (placeholder)")
                return {"crawled": 0}

        register_news_crawler(DefaultNewsCrawler)
        logger.info(f"News crawler setup completed with placeholder")

    # 감성 분석 서비스 등록
    try:
        from analysis.sentiment_service import SentimentAnalysisService
        register_sentiment_analysis_service(SentimentAnalysisService)
        logger.info(f"Sentiment analysis service setup completed with SentimentAnalysisService")
    except ImportError:
        logger.warning(f"SentimentAnalysisService not found, using placeholder")

        # 기본 감성 분석 서비스 등록
        class DefaultSentimentAnalysisService:
            def __init__(self, sentiment_analyzer=None, mongodb_client=None, config=None):
                self.sentiment_analyzer = sentiment_analyzer
                self.mongodb_client = mongodb_client
                self.config = config or {}

            async def analyze_news(self, news_id=None, news_data=None):
                logger.info(f"DefaultSentimentAnalysisService.analyze_news() called (placeholder)")
                return {"analyzed": 0}

            async def analyze_all_news(self, limit=100):
                logger.info(f"DefaultSentimentAnalysisService.analyze_all_news() called (placeholder)")
                return {"analyzed": 0}

        register_sentiment_analysis_service(DefaultSentimentAnalysisService)
        logger.info(f"Sentiment analysis service setup completed with placeholder")

    # 주식 데이터 서비스 등록
    try:
        from data.stock_data_store import StockDataStore
        register_stock_data_service(StockDataStore)
        logger.info(f"Stock data service setup completed with StockDataStore")
    except ImportError:
        logger.warning(f"StockDataStore not found, using placeholder")

        # 기본 주식 데이터 서비스 등록
        class DefaultStockDataService:
            def __init__(self, mongodb_client=None, http_client=None, config=None):
                self.mongodb_client = mongodb_client
                self.http_client = http_client
                self.config = config or {}

            def get_stock_data(self, symbol, period="1y", interval="1d"):
                return {
                    "symbol": symbol,
                    "period": period,
                    "interval": interval,
                    "data": []
                }

            def get_stock_news(self, symbol, limit=10):
                return []

            def close(self):
                pass

        register_stock_data_service(DefaultStockDataService)
        logger.info(f"Stock data service setup completed with placeholder")

    logger.info(f"Services setup completed")


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
