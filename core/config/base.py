"""
기본 설정 모듈

애플리케이션의 기본 설정 클래스를 정의합니다.
모든 환경별 설정 클래스는 이 기본 클래스를 상속받습니다.
"""
import os
from typing import Dict, Any, List, Optional, Set
from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings as PydanticBaseSettings


class LoggingSettings(PydanticBaseSettings):
    """
    로깅 설정
    """
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_enabled: bool = Field(default=False)
    file_path: str = Field(default="logs/jaepa.log")
    rotation: str = Field(default="1 day")
    retention: str = Field(default="30 days")
    mask_sensitive_data: bool = Field(default=True)
    sensitive_fields: Set[str] = Field(default={
        "password", "secret", "token", "key", "auth", "credential"
    })
    
    @field_validator("file_path")
    def validate_file_path(cls, v):
        """파일 경로 유효성 검사"""
        if v:
            # 디렉토리 생성
            path = Path(v)
            path.parent.mkdir(parents=True, exist_ok=True)
        return v


class DatabaseSettings(PydanticBaseSettings):
    """
    데이터베이스 설정
    """
    # 공통 설정
    engine: str = Field(default="mongodb")  # mongodb 또는 sqlite
    
    # MongoDB 설정
    mongo_uri: str = Field(default="mongodb://localhost:27017/")
    mongo_db_name: str = Field(default="jaepa")
    mongo_connect_timeout: int = Field(default=5000)
    mongo_max_pool_size: int = Field(default=10)
    mongo_min_pool_size: int = Field(default=1)
    mongo_max_idle_time_ms: int = Field(default=10000)
    mongo_retry_writes: bool = Field(default=True)
    mongo_retry_reads: bool = Field(default=True)
    mongo_server_selection_timeout_ms: int = Field(default=5000)
    mongo_socket_timeout_ms: int = Field(default=5000)
    mongo_heartbeat_frequency_ms: int = Field(default=5000)
    
    # SQLite 설정
    sqlite_url: str = Field(default="sqlite:///./jaepa.db")
    sqlite_connect_args: Dict[str, Any] = Field(default={"check_same_thread": False})
    
    # 컬렉션/테이블 설정
    news_collection: str = Field(default="financial_news")
    sentiment_collection: str = Field(default="news_sentiment")
    stock_data_collection: str = Field(default="stock_data")
    crypto_data_collection: str = Field(default="crypto_data")
    user_collection: str = Field(default="users")


class ApiSettings(PydanticBaseSettings):
    """
    API 설정
    """
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=False)
    prefix: str = Field(default="/api")
    version: str = Field(default="v1")
    timeout: int = Field(default=30)
    max_retries: int = Field(default=3)
    retry_delay: int = Field(default=1)
    user_agent: str = Field(default="JaePa/0.1.0")
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:80"])
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: List[str] = Field(default=["*"])
    cors_allow_headers: List[str] = Field(default=["*"])


class CrawlingSettings(PydanticBaseSettings):
    """
    크롤링 설정
    """
    # 일반 설정
    timeout: int = Field(default=30)
    retries: int = Field(default=3)
    retry_delay: int = Field(default=2)
    user_agent: str = Field(default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    requests_per_minute: int = Field(default=10)
    pause_between_requests: int = Field(default=6)
    
    # RSS 피드 설정
    rss_feeds: Dict[str, Dict[str, str]] = Field(default={
        "nasdaq": {
            "name": "Nasdaq",
            "url": "https://www.nasdaq.com/feed/rssoutbound?category=Markets",
            "fallback_url": "https://www.nasdaq.com/feed/rssoutbound"
        },
        "yahoo_finance": {
            "name": "Yahoo Finance",
            "url": "https://finance.yahoo.com/news/rssindex",
            "fallback_url": "https://finance.yahoo.com/rss/topstories"
        },
        "coindesk": {
            "name": "CoinDesk",
            "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "fallback_url": "https://www.coindesk.com/feed"
        },
        "cointelegraph": {
            "name": "CoinTelegraph",
            "url": "https://cointelegraph.com/rss",
            "fallback_url": "https://cointelegraph.com/feed"
        },
        "investing": {
            "name": "Investing.com",
            "url": "https://www.investing.com/rss/news.rss",
            "fallback_url": "https://www.investing.com/rss/news_285.rss"
        }
    })
    
    # 뉴스 소스 설정
    news_sources: Dict[str, Dict[str, Any]] = Field(default={
        "yahoo_finance": {
            "base_url": "https://finance.yahoo.com",
            "search_url": "https://finance.yahoo.com/search?q={keyword}",
            "latest_url": "https://finance.yahoo.com/news/",
            "article_selector": ".js-content-viewer h3 a",
            "content_selector": ".caas-body p",
            "date_selector": "time",
            "date_format": "%Y-%m-%d"
        },
        "reuters": {
            "base_url": "https://www.reuters.com",
            "search_url": "https://www.reuters.com/search/news?blob={keyword}&sortBy=date&dateRange={date_range}",
            "latest_url": "https://www.reuters.com/business/finance",
            "article_selector": ".search-result-title a",
            "content_selector": ".article-body__content__17Yit p",
            "date_selector": ".article-header__meta__1i0gl time",
            "date_format": "%B %d, %Y"
        },
        "bloomberg": {
            "base_url": "https://www.bloomberg.com",
            "search_url": "https://www.bloomberg.com/search?query={keyword}&time={date_range}",
            "latest_url": "https://www.bloomberg.com/markets",
            "article_selector": ".search-result-story__headline a",
            "content_selector": ".body-copy p",
            "date_selector": ".article-stamp time",
            "date_format": "%Y-%m-%d"
        },
        "financial_times": {
            "base_url": "https://www.ft.com",
            "search_url": "https://www.ft.com/search?q={keyword}&dateTo={date_to}&dateFrom={date_from}",
            "latest_url": "https://www.ft.com/markets",
            "article_selector": ".o-teaser__heading a",
            "content_selector": ".article__content p",
            "date_selector": ".o-date",
            "date_format": "%Y-%m-%d"
        },
        "cnbc": {
            "base_url": "https://www.cnbc.com",
            "search_url": "https://www.cnbc.com/search/?query={keyword}&qsearchterm={keyword}",
            "latest_url": "https://www.cnbc.com/finance/",
            "article_selector": ".resultlink a",
            "content_selector": ".group p",
            "date_selector": ".DateTimeDisplay",
            "date_format": "%Y-%m-%d"
        },
        "wsj": {
            "base_url": "https://www.wsj.com",
            "search_url": "https://www.wsj.com/search?query={keyword}&page={page}&isToggleOn=true&operator=AND&sort=date-desc&duration={date_range}",
            "latest_url": "https://www.wsj.com/finance",
            "article_selector": ".headline a",
            "content_selector": ".article-content p",
            "date_selector": ".timestamp",
            "date_format": "%Y-%m-%d"
        }
    })
    
    # API 소스 설정
    api_sources: Dict[str, Dict[str, Any]] = Field(default={
        "finnhub": {
            "default_categories": ["general", "forex", "crypto", "merger"],
            "rate_limit": {
                "requests_per_minute": 30,
                "pause_between_requests": 2
            }
        },
        "newsdata": {
            "default_categories": ["business", "technology"],
            "default_country": "us",
            "rate_limit": {
                "requests_per_minute": 10,
                "pause_between_requests": 6
            }
        }
    })
    
    # GDELT 설정
    gdelt_api_base_url: str = Field(default="https://api.gdeltproject.org/api/v2/")
    gdelt_doc_api_url: str = Field(default="doc/doc")
    gdelt_gkg_api_url: str = Field(default="gkg/gkg")
    gdelt_events_api_url: str = Field(default="events/events")
    gdelt_request_interval: float = Field(default=1.0)
    gdelt_max_records: int = Field(default=250)
    
    # 데이터 정규화 설정
    title_similarity_threshold: int = Field(default=85)
    time_difference_seconds: int = Field(default=300)
    field_mapping: Dict[str, Dict[str, str]] = Field(default={
        "rss": {
            "title": "title",
            "content": "content",
            "summary": "summary",
            "link": "url",
            "published": "published_date"
        },
        "finnhub": {
            "headline": "title",
            "summary": "summary",
            "url": "url",
            "datetime": "published_date",
            "source": "source"
        },
        "newsdata": {
            "title": "title",
            "description": "summary",
            "link": "url",
            "pubDate": "published_date",
            "source_id": "source"
        }
    })
    
    # 스케줄러 설정
    news_update_interval: str = Field(default="6h")
    stock_data_update_interval: str = Field(default="24h")
    sentiment_analysis_interval: str = Field(default="6h")


class SentimentSettings(PydanticBaseSettings):
    """
    감성 분석 설정
    """
    model: str = Field(default="finbert")
    model_path: str = Field(default="models/finbert")
    batch_size: int = Field(default=16)
    max_length: int = Field(default=512)
    positive_threshold: float = Field(default=0.6)
    negative_threshold: float = Field(default=0.6)
    multilingual: bool = Field(default=False)
    languages: List[str] = Field(default=["en"])
    
    @field_validator("model_path")
    def validate_model_path(cls, v):
        """모델 경로 유효성 검사"""
        if v:
            # 디렉토리 생성
            path = Path(v)
            path.parent.mkdir(parents=True, exist_ok=True)
        return v


class StockSettings(PydanticBaseSettings):
    """
    주식 데이터 설정
    """
    default_period: str = Field(default="1y")
    default_interval: str = Field(default="1d")
    technical_indicators: List[str] = Field(default=[
        "sma", "ema", "rsi", "macd", "bollinger_bands"
    ])
    moving_averages: List[int] = Field(default=[20, 50, 200])
    cache_dir: str = Field(default="./.cache/stock_data")
    cache_expiry: int = Field(default=86400)  # 24시간
    
    # API 키
    polygon_api_key: str = Field(default="")
    alpha_vantage_api_key: str = Field(default="")
    finnhub_api_key: str = Field(default="")
    
    @field_validator("cache_dir")
    def validate_cache_dir(cls, v):
        """캐시 디렉토리 유효성 검사"""
        if v:
            # 디렉토리 생성
            path = Path(v)
            path.mkdir(parents=True, exist_ok=True)
        return v


class SecuritySettings(PydanticBaseSettings):
    """
    보안 설정
    """
    jwt_secret_key: str = Field(default="change_this_secret_key")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)
    password_min_length: int = Field(default=8)
    password_require_uppercase: bool = Field(default=True)
    password_require_lowercase: bool = Field(default=True)
    password_require_digit: bool = Field(default=True)
    password_require_special: bool = Field(default=True)
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests: int = Field(default=100)
    rate_limit_period_seconds: int = Field(default=60)


class BaseSettings(PydanticBaseSettings):
    """
    기본 설정 클래스
    
    모든 환경별 설정 클래스의 기본이 되는 클래스입니다.
    """
    # 애플리케이션 기본 설정
    app_name: str = Field(default="JaePa")
    app_description: str = Field(default="해외 금융 뉴스 크롤링과 감성 분석을 통한 투자 의사결정 도구")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
    environment: str = Field(default="development")
    
    # 하위 설정
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)
    crawling: CrawlingSettings = Field(default_factory=CrawlingSettings)
    sentiment: SentimentSettings = Field(default_factory=SentimentSettings)
    stock: StockSettings = Field(default_factory=StockSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        
    @model_validator(mode="after")
    def load_api_keys(self):
        """환경 변수에서 API 키 로드"""
        # Polygon API 키
        if not self.stock.polygon_api_key:
            self.stock.polygon_api_key = os.getenv("POLYGON_API_KEY", "")
        
        # Alpha Vantage API 키
        if not self.stock.alpha_vantage_api_key:
            self.stock.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
        
        # Finnhub API 키
        if not self.stock.finnhub_api_key:
            self.stock.finnhub_api_key = os.getenv("FINNHUB_API_KEY", "")
        
        return self
