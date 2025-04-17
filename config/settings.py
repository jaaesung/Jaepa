"""
JaePa 프로젝트 설정 모듈

환경 변수, JSON 파일, 기본값 순으로 설정을 로드하는 중앙화된 설정 시스템입니다.
"""

import os
import json
import logging
from typing import Any, Dict, List, Union
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

# 로깅 설정
logger = logging.getLogger(__name__)


class DatabaseSettings(BaseSettings):
    """
    데이터베이스 관련 설정
    """
    # MongoDB 설정
    mongo_username: str = Field("jaepa_user", env="MONGO_USERNAME")
    mongo_password: str = Field("change_this_password", env="MONGO_PASSWORD")
    mongo_uri: str = Field("mongodb://localhost:27017/", env="MONGO_URI")
    mongo_db_name: str = Field("jaepa", env="MONGO_DB_NAME")

    # 컬렉션 이름
    news_collection: str = "financial_news"
    sentiment_collection: str = "news_sentiment"
    stock_data_collection: str = "stock_data"
    crypto_data_collection: str = "crypto_data"
    user_collection: str = "users"
    symbol_news_relation_collection: str = "symbol_news_relation"
    news_sentiment_trends_collection: str = "news_sentiment_trends"
    sentiment_stock_correlation_collection: str = "sentiment_stock_correlation"

    @field_validator("mongo_uri", mode="before")
    def validate_mongo_uri(cls, v: str, info) -> str:
        """MongoDB URI 검증 및 생성"""
        if "{" in v and "}" in v:  # 템플릿 문자열인 경우
            values = info.data
            username = values.get("mongo_username", "")
            password = values.get("mongo_password", "")
            return v.format(username=username, password=password)
        return v

    model_config = {
        "env_prefix": "",
        "case_sensitive": False
    }


class APISettings(BaseSettings):
    """
    API 관련 설정
    """
    # API 서버 설정
    host: str = Field("0.0.0.0", env="API_HOST")
    port: int = Field(8000, env="API_PORT")
    debug: bool = Field(False, env="API_DEBUG")
    api_prefix: str = Field("/api", env="API_PREFIX")
    api_version: str = Field("v1", env="API_VERSION")

    # CORS 설정
    cors_origins: List[str] = Field(["http://localhost:80", "http://frontend"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(["*"], env="CORS_ALLOW_HEADERS")

    @field_validator("cors_origins", mode="before")
    def validate_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """CORS 원본 검증 및 변환"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = {
        "env_prefix": "",
        "case_sensitive": False
    }


class CrawlingSettings(BaseSettings):
    """
    크롤링 관련 설정
    """
    # 요청 설정
    timeout: int = Field(30, env="CRAWLING_TIMEOUT")
    retries: int = Field(3, env="CRAWLING_RETRIES")
    retry_delay: int = Field(2, env="CRAWLING_RETRY_DELAY")
    user_agent: str = Field(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        env="CRAWLING_USER_AGENT"
    )

    # 속도 제한
    requests_per_minute: int = Field(10, env="CRAWLING_REQUESTS_PER_MINUTE")
    pause_between_requests: int = Field(6, env="CRAWLING_PAUSE_BETWEEN_REQUESTS")

    # RSS 피드 설정
    rss_feeds: Dict[str, Dict[str, str]] = {
        "nasdaq": {
            "name": "Nasdaq",
            "url": "https://www.nasdaq.com/feed/rssoutbound?category=Markets",
            "fallback_url": "https://www.nasdaq.com/feed/rssoutbound"
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
        },
        "yahoo_finance": {
            "name": "Yahoo Finance",
            "url": "https://finance.yahoo.com/news/rssindex",
            "fallback_url": "https://finance.yahoo.com/rss/topstories"
        }
    }

    # 뉴스 소스 설정
    news_sources: Dict[str, Dict[str, str]] = {
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
    }

    # API 소스 설정
    api_sources: Dict[str, Dict[str, Any]] = {
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
    }

    # 데이터 정규화 설정
    data_normalization: Dict[str, Any] = {
        "title_similarity_threshold": 85,
        "time_difference_seconds": 300,
        "field_mapping": {
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
        }
    }

    # 스케줄러 설정
    scheduler: Dict[str, str] = {
        "news_update_interval": "6h",
        "stock_data_update_interval": "24h",
        "sentiment_analysis_interval": "6h"
    }

    model_config = {
        "env_prefix": "CRAWLING_",
        "case_sensitive": False
    }


class SentimentAnalysisSettings(BaseSettings):
    """
    감성 분석 관련 설정
    """
    # 모델 설정
    model: str = Field("finbert", env="SENTIMENT_MODEL")
    model_path: str = Field("models/finbert", env="SENTIMENT_MODEL_PATH")
    batch_size: int = Field(16, env="SENTIMENT_BATCH_SIZE")

    # 임계값 설정
    positive_threshold: float = Field(0.6, env="SENTIMENT_POSITIVE_THRESHOLD")
    negative_threshold: float = Field(0.6, env="SENTIMENT_NEGATIVE_THRESHOLD")

    # 다국어 지원 설정
    multilingual: bool = Field(False, env="SENTIMENT_MULTILINGUAL")
    languages: List[str] = Field(["en"], env="SENTIMENT_LANGUAGES")

    @field_validator("languages", mode="before")
    def validate_languages(cls, v: Union[str, List[str]]) -> List[str]:
        """언어 목록 검증 및 변환"""
        if isinstance(v, str):
            return [lang.strip() for lang in v.split(",")]
        return v

    model_config = {
        "env_prefix": "SENTIMENT_",
        "case_sensitive": False
    }


class LoggingSettings(BaseSettings):
    """
    로깅 관련 설정
    """
    # 로그 레벨
    level: str = Field("INFO", env="LOG_LEVEL")

    # 로그 파일 설정
    file_enabled: bool = Field(False, env="LOG_FILE_ENABLED")
    file_path: str = Field("logs/jaepa.log", env="LOG_FILE_PATH")

    # 로그 포맷
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )

    # 로그 회전 설정
    rotation: str = Field("1 day", env="LOG_ROTATION")
    retention: str = Field("30 days", env="LOG_RETENTION")

    # 민감 정보 마스킹
    mask_sensitive_data: bool = Field(True, env="LOG_MASK_SENSITIVE_DATA")
    sensitive_fields: List[str] = Field(
        ["password", "secret", "token", "key", "auth", "credential"],
        env="LOG_SENSITIVE_FIELDS"
    )

    @field_validator("level")
    def validate_level(cls, v: str) -> str:
        """로그 레벨 검증"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v

    @field_validator("sensitive_fields", mode="before")
    def validate_sensitive_fields(cls, v: Union[str, List[str]]) -> List[str]:
        """민감 필드 목록 검증 및 변환"""
        if isinstance(v, str):
            return [field.strip() for field in v.split(",")]
        return v

    model_config = {
        "env_prefix": "LOG_",
        "case_sensitive": False
    }


class SecuritySettings(BaseSettings):
    """
    보안 관련 설정
    """
    # JWT 설정
    jwt_secret_key: str = Field("change_this_secret_key", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # 비밀번호 설정
    password_min_length: int = Field(8, env="PASSWORD_MIN_LENGTH")
    password_require_uppercase: bool = Field(True, env="PASSWORD_REQUIRE_UPPERCASE")
    password_require_lowercase: bool = Field(True, env="PASSWORD_REQUIRE_LOWERCASE")
    password_require_digit: bool = Field(True, env="PASSWORD_REQUIRE_DIGIT")
    password_require_special: bool = Field(True, env="PASSWORD_REQUIRE_SPECIAL")

    # 속도 제한 설정
    rate_limit_enabled: bool = Field(True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(100, env="RATE_LIMIT_REQUESTS")
    rate_limit_period_seconds: int = Field(60, env="RATE_LIMIT_PERIOD_SECONDS")

    @field_validator("jwt_algorithm")
    def validate_jwt_algorithm(cls, v: str) -> str:
        """JWT 알고리즘 검증"""
        valid_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
        if v not in valid_algorithms:
            raise ValueError(f"Invalid JWT algorithm: {v}. Must be one of {valid_algorithms}")
        return v

    model_config = {
        "env_prefix": "",
        "case_sensitive": False
    }


class StockDataSettings(BaseSettings):
    """
    주식 데이터 관련 설정
    """
    # 기본 설정
    default_period: str = Field("1y", env="STOCK_DEFAULT_PERIOD")
    default_interval: str = Field("1d", env="STOCK_DEFAULT_INTERVAL")

    # 기술적 지표
    technical_indicators: List[str] = Field(
        ["sma", "ema", "rsi", "macd", "bollinger_bands"],
        env="STOCK_TECHNICAL_INDICATORS"
    )

    # 이동 평균
    moving_averages: List[int] = Field([20, 50, 200], env="STOCK_MOVING_AVERAGES")

    # API 키
    polygon_api_key: str = Field("", env="POLYGON_API_KEY")
    alpha_vantage_api_key: str = Field("", env="ALPHA_VANTAGE_API_KEY")
    finnhub_api_key: str = Field("", env="FINNHUB_API_KEY")

    @field_validator("technical_indicators", mode="before")
    def validate_technical_indicators(cls, v: Union[str, List[str]]) -> List[str]:
        """기술적 지표 목록 검증 및 변환"""
        if isinstance(v, str):
            return [indicator.strip() for indicator in v.split(",")]
        return v

    @field_validator("moving_averages", mode="before")
    def validate_moving_averages(cls, v: Union[str, List[int]]) -> List[int]:
        """이동 평균 목록 검증 및 변환"""
        if isinstance(v, str):
            return [int(ma.strip()) for ma in v.split(",")]
        return v

    model_config = {
        "env_prefix": "STOCK_",
        "case_sensitive": False
    }


class GDELTSettings(BaseSettings):
    """
    GDELT 관련 설정
    """
    # API 설정
    api_base_url: str = Field("https://api.gdeltproject.org/api/v2/", env="GDELT_API_BASE_URL")
    doc_api_url: str = Field("doc/doc", env="GDELT_DOC_API_URL")
    gkg_api_url: str = Field("gkg/gkg", env="GDELT_GKG_API_URL")
    events_api_url: str = Field("events/events", env="GDELT_EVENTS_API_URL")

    # 요청 설정
    request_interval: float = Field(1.0, env="GDELT_REQUEST_INTERVAL")
    max_records: int = Field(250, env="GDELT_MAX_RECORDS")

    # 회사 정보
    company_mapping_file: str = Field("data/company_mapping.json", env="GDELT_COMPANY_MAPPING_FILE")

    model_config = {
        "env_prefix": "GDELT_",
        "case_sensitive": False
    }


class Settings(BaseSettings):
    """
    JaePa 프로젝트 전체 설정

    환경 변수, JSON 파일, 기본값 순으로 설정을 로드합니다.
    """
    # 프로젝트 기본 설정
    project_name: str = Field("JaePa", env="PROJECT_NAME")
    project_description: str = Field(
        "해외 금융 뉴스 크롤링과 감성 분석을 통한 투자 의사결정 도구",
        env="PROJECT_DESCRIPTION"
    )
    version: str = Field("0.1.0", env="VERSION")
    debug: bool = Field(False, env="DEBUG")

    # 환경 설정
    environment: str = Field("development", env="ENVIRONMENT")
    config_file: str = Field("config/config.json", env="CONFIG_FILE")

    # 하위 설정
    db: DatabaseSettings = DatabaseSettings()
    api: APISettings = APISettings()
    crawling: CrawlingSettings = CrawlingSettings()
    sentiment: SentimentAnalysisSettings = SentimentAnalysisSettings()
    logging: LoggingSettings = LoggingSettings()
    security: SecuritySettings = SecuritySettings()
    stock: StockDataSettings = StockDataSettings()
    gdelt: GDELTSettings = GDELTSettings()

    @field_validator("environment")
    def validate_environment(cls, v: str) -> str:
        """환경 설정 검증"""
        valid_environments = ["development", "testing", "staging", "production"]
        v = v.lower()
        if v not in valid_environments:
            raise ValueError(f"Invalid environment: {v}. Must be one of {valid_environments}")
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_nested_delimiter": "__",
        "case_sensitive": False,
        "extra": "ignore"
    }

    @classmethod
    def settings_customise_sources(cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings):
        """설정 소스 우선순위 커스터마이징"""
        return (
            env_settings,  # 1. 환경 변수 (최우선)
            init_settings,  # 2. 초기화 인자
            json_config_settings,  # 3. JSON 설정 파일
            dotenv_settings,  # 4. .env 파일
            file_secret_settings,  # 5. 시크릿 파일
        )


def json_config_settings(settings=None) -> Dict[str, Any]:
    """JSON 설정 파일에서 설정 로드"""
    # 설정 파일 경로 결정
    config_file = os.getenv("CONFIG_FILE", "config/config.json")

    # 설정 파일이 존재하지 않으면 크롤링 설정 파일 사용
    if not os.path.exists(config_file):
        config_file = "crawling/config.json"

    # 설정 파일이 존재하지 않으면 빈 딕셔너리 반환
    if not os.path.exists(config_file):
        logger.warning(f"설정 파일을 찾을 수 없습니다: {config_file}")
        return {}

    # 설정 파일 로드
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"설정 파일 로드 중 오류 발생: {e}")
        return {}


@lru_cache()
def get_settings() -> Settings:
    """
    설정 인스턴스 반환 (캐싱)

    설정 값을 캐싱하여 성능을 최적화합니다.
    """
    return Settings()


# 전역 설정 인스턴스
settings = get_settings()


if __name__ == "__main__":
    """설정 모듈 테스트"""
    import sys

    # 로깅 설정
    logging.basicConfig(
        level=getattr(logging, settings.logging.level),
        format=settings.logging.format,
        stream=sys.stdout,
    )

    # 설정 출력
    logger.info(f"프로젝트 이름: {settings.project_name}")
    logger.info(f"환경: {settings.environment}")
    logger.info(f"디버그 모드: {settings.debug}")
    logger.info(f"MongoDB URI: {settings.db.mongo_uri.replace(settings.db.mongo_password, '********')}")
    logger.info(f"JWT 알고리즘: {settings.security.jwt_algorithm}")
    logger.info(f"감성 분석 모델: {settings.sentiment.model}")
    logger.info(f"로그 레벨: {settings.logging.level}")
    logger.info(f"크롤링 타임아웃: {settings.crawling.timeout}")
    logger.info(f"API 호스트: {settings.api.host}")
    logger.info(f"API 포트: {settings.api.port}")
    logger.info(f"CORS 원본: {settings.api.cors_origins}")
    logger.info(f"주식 데이터 기본 기간: {settings.stock.default_period}")
    logger.info(f"GDELT API 기본 URL: {settings.gdelt.api_base_url}")
