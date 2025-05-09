"""
인터페이스 패키지

JaePa 프로젝트의 인터페이스를 정의하는 패키지입니다.
"""

from core.interfaces.database import DatabaseClient, MongoDBClient, SQLClient
from core.interfaces.http_client import HttpClient, HttpClientError
from core.interfaces.news_source import NewsSource, NewsSourceManager
from core.interfaces.sentiment_analyzer import SentimentAnalyzer

__all__ = [
    'DatabaseClient',
    'MongoDBClient',
    'SQLClient',
    'HttpClient',
    'HttpClientError',
    'NewsSource',
    'NewsSourceManager',
    'SentimentAnalyzer',
]
