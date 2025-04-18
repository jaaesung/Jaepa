"""
코어 패키지

JaePa 프로젝트의 핵심 기능을 제공하는 패키지입니다.
"""

from core.di import (
    container, get_container,
    register_mongodb_client, register_http_client,
    register_news_source_manager, register_sentiment_analyzer,
    register_news_crawler, register_sentiment_analysis_service,
    register_stock_data_service
)

__all__ = [
    'container',
    'get_container',
    'register_mongodb_client',
    'register_http_client',
    'register_news_source_manager',
    'register_sentiment_analyzer',
    'register_news_crawler',
    'register_sentiment_analysis_service',
    'register_stock_data_service',
]
