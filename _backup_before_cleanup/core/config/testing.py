"""
테스트 환경 설정 모듈

테스트 환경에서 사용되는 설정을 정의합니다.
"""
from .base import BaseSettings, Field


class TestingSettings(BaseSettings):
    """
    테스트 환경 설정 클래스
    """
    # 기본 설정 오버라이드
    debug: bool = Field(default=True)
    environment: str = Field(default="testing")
    
    # 로깅 설정 오버라이드
    logging: dict = {
        "level": "DEBUG",
        "file_enabled": False
    }
    
    # API 설정 오버라이드
    api: dict = {
        "debug": True,
        "port": 8001
    }
    
    # 데이터베이스 설정 오버라이드
    db: dict = {
        "mongo_uri": "mongodb://localhost:27017/",
        "mongo_db_name": "jaepa_test",
        "sqlite_url": "sqlite:///./jaepa_test.db"
    }
    
    # 크롤링 설정 오버라이드
    crawling: dict = {
        "timeout": 10,
        "retries": 1,
        "news_update_interval": "1h"
    }
    
    # 감성 분석 설정 오버라이드
    sentiment: dict = {
        "batch_size": 4
    }
    
    class Config:
        env_file = ".env.test"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
