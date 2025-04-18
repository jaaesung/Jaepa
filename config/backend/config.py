"""
설정 모듈

애플리케이션 설정을 관리합니다.
"""
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import Field


class LoggingSettings(BaseSettings):
    """
    로깅 설정
    """
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_enabled: bool = Field(default=True)
    file_path: str = Field(default="jaepa.log")


class DatabaseSettings(BaseSettings):
    """
    데이터베이스 설정
    """
    client_class: str = Field(default="implementations.mongodb_client.MongoDBClientImpl")
    mongo_uri: str = Field(default="mongodb://localhost:27017/")
    mongo_db_name: str = Field(default="jaepa")
    mongo_connect_timeout: int = Field(default=5000)
    mongo_max_pool_size: int = Field(default=10)
    sqlite_url: str = Field(default="sqlite:///./jaepa.db")
    sqlite_connect_args: Dict[str, Any] = Field(default={"check_same_thread": False})


class ApiSettings(BaseSettings):
    """
    API 설정
    """
    client_class: str = Field(default="implementations.http_client.RequestsHttpClientImpl")
    base_url: str = Field(default="")
    timeout: int = Field(default=30)
    max_retries: int = Field(default=3)
    retry_delay: int = Field(default=1)
    user_agent: str = Field(default="JaePa/0.1.0")


class CrawlingSettings(BaseSettings):
    """
    크롤링 설정
    """
    crawler_class: str = Field(default="crawling.integrated_news_collector.IntegratedNewsCollector")
    source_manager_class: str = Field(default="implementations.news_source.NewsSourceManagerImpl")
    news_sources: Dict[str, Dict[str, Any]] = Field(default={
        "rss": {
            "class": "implementations.news_source.RssNewsSourceImpl",
            "params": {
                "name": "rss",
                "feeds": {
                    "reuters": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
                    "yahoo_finance": "https://finance.yahoo.com/news/rssindex",
                    "cnbc": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
                    "marketwatch": "https://www.marketwatch.com/rss/topstories",
                    "bloomberg": "https://www.bloomberg.com/feed/technology/feed.xml"
                }
            }
        },
        "gdelt": {
            "class": "implementations.news_source.GdeltNewsSourceImpl",
            "params": {
                "name": "gdelt",
                "api_url": "https://api.gdeltproject.org/api/v2/doc/doc"
            }
        },
        "newsapi": {
            "class": "implementations.news_source.NewsApiSourceImpl",
            "params": {
                "name": "newsapi",
                "api_key": os.getenv("NEWSAPI_KEY", "")
            }
        }
    })


class SentimentSettings(BaseSettings):
    """
    감성 분석 설정
    """
    analyzer_class: str = Field(default="implementations.sentiment_analyzer.FinBERTSentimentImpl")
    service_class: str = Field(default="services.sentiment_service.SentimentAnalysisService")
    model_name: str = Field(default="ProsusAI/finbert")
    cache_dir: str = Field(default="./.cache/models")
    batch_size: int = Field(default=8)
    max_length: int = Field(default=512)


class StockSettings(BaseSettings):
    """
    주식 데이터 설정
    """
    service_class: str = Field(default="services.stock_service.StockDataService")
    api_key: str = Field(default=os.getenv("POLYGON_API_KEY", ""))
    cache_dir: str = Field(default="./.cache/stock_data")
    cache_expiry: int = Field(default=86400)  # 24시간


class Settings(BaseSettings):
    """
    애플리케이션 설정
    """
    app_name: str = Field(default="JaePa")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=True)
    environment: str = Field(default="development")
    
    # 하위 설정
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)
    crawling: CrawlingSettings = Field(default_factory=CrawlingSettings)
    sentiment: SentimentSettings = Field(default_factory=SentimentSettings)
    stock: StockSettings = Field(default_factory=StockSettings)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


# 설정 인스턴스 생성
settings = Settings()


# 환경 변수에서 설정 로드
def load_settings_from_env() -> Settings:
    """
    환경 변수에서 설정 로드
    
    Returns:
        Settings: 설정 인스턴스
    """
    return Settings()


# 파일에서 설정 로드
def load_settings_from_file(file_path: str) -> Settings:
    """
    파일에서 설정 로드
    
    Args:
        file_path: 설정 파일 경로
        
    Returns:
        Settings: 설정 인스턴스
    """
    return Settings(_env_file=file_path)


# 설정 업데이트
def update_settings(new_settings: Dict[str, Any]) -> None:
    """
    설정 업데이트
    
    Args:
        new_settings: 새 설정 값
    """
    global settings
    
    for key, value in new_settings.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
