"""
크롤링 패키지

뉴스 크롤링 관련 모듈을 포함합니다.
"""

from core.crawler.http_client import AsyncHttpClient
from core.crawler.news_source_manager import NewsSourceManager
from core.crawler.rss_processor import RssProcessor
from core.crawler.article_processor import ArticleProcessor
from core.crawler.interfaces import (
    HttpClientInterface, NewsSourceInterface, NewsSourceManagerInterface,
    RssProcessorInterface, ArticleProcessorInterface, ArticleRepositoryInterface
)
from core.crawler.exceptions import (
    CrawlerException, HttpClientException, RateLimitException,
    TimeoutException, ConnectionException, ParsingException,
    SourceException, StorageException, ConfigurationException,
    AuthenticationException
)

__all__ = [
    'AsyncHttpClient',
    'NewsSourceManager',
    'RssProcessor',
    'ArticleProcessor',
    'HttpClientInterface',
    'NewsSourceInterface',
    'NewsSourceManagerInterface',
    'RssProcessorInterface',
    'ArticleProcessorInterface',
    'ArticleRepositoryInterface',
    'CrawlerException',
    'HttpClientException',
    'RateLimitException',
    'TimeoutException',
    'ConnectionException',
    'ParsingException',
    'SourceException',
    'StorageException',
    'ConfigurationException',
    'AuthenticationException'
]
