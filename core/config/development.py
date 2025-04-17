"""
개발 환경 설정 모듈

개발 환경에서 사용되는 설정을 정의합니다.
"""
from .base import BaseSettings, Field


class DevelopmentSettings(BaseSettings):
    """
    개발 환경 설정 클래스
    """
    # 기본 설정 오버라이드
    debug: bool = Field(default=True)
    environment: str = Field(default="development")
    
    # 로깅 설정 오버라이드
    logging: dict = {
        "level": "DEBUG",
        "file_enabled": True,
        "file_path": "logs/jaepa_dev.log"
    }
    
    # API 설정 오버라이드
    api: dict = {
        "debug": True,
        "cors_origins": ["*"]
    }
    
    # 데이터베이스 설정 오버라이드
    db: dict = {
        "mongo_db_name": "jaepa_dev",
        "sqlite_url": "sqlite:///./jaepa_dev.db"
    }
    
    # 크롤링 설정 오버라이드
    crawling: dict = {
        "timeout": 60,
        "retries": 5,
        "news_update_interval": "1h"
    }
    
    class Config:
        env_file = ".env.development"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
