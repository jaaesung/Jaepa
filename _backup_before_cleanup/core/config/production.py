"""
프로덕션 환경 설정 모듈

프로덕션 환경에서 사용되는 설정을 정의합니다.
"""
from .base import BaseSettings, Field


class ProductionSettings(BaseSettings):
    """
    프로덕션 환경 설정 클래스
    """
    # 기본 설정 오버라이드
    debug: bool = Field(default=False)
    environment: str = Field(default="production")
    
    # 로깅 설정 오버라이드
    logging: dict = {
        "level": "INFO",
        "file_enabled": True,
        "file_path": "/var/log/jaepa/jaepa.log"
    }
    
    # API 설정 오버라이드
    api: dict = {
        "debug": False,
        "cors_origins": ["https://jaepa.example.com"]
    }
    
    # 데이터베이스 설정 오버라이드
    db: dict = {
        "mongo_max_pool_size": 20,
        "mongo_min_pool_size": 5
    }
    
    # 보안 설정 오버라이드
    security: dict = {
        "access_token_expire_minutes": 15,
        "rate_limit_enabled": True,
        "rate_limit_requests": 60
    }
    
    class Config:
        env_file = ".env.production"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
