"""
설정 모듈

애플리케이션 설정을 관리합니다.
"""

import os
from typing import Optional, Dict, Any, List
from pydantic import BaseSettings, validator
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings(BaseSettings):
    # 애플리케이션 설정
    APP_NAME: str = "JaePa"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "주식 뉴스 및 감성 분석 애플리케이션"
    
    # API 설정
    API_PREFIX: str = "/api"
    API_DEBUG: bool = os.getenv("API_DEBUG", "False").lower() == "true"
    
    # 보안 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    ALGORITHM: str = "HS256"
    
    # 데이터베이스 설정
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./jaepa.db")
    
    # CORS 설정
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://jaepa.example.com",
    ]
    
    # 외부 API 설정
    POLYGON_API_KEY: Optional[str] = os.getenv("POLYGON_API_KEY")
    FINNHUB_API_KEY: Optional[str] = os.getenv("FINNHUB_API_KEY")
    
    # 크롤링 설정
    CRAWLING_INTERVAL_MINUTES: int = int(os.getenv("CRAWLING_INTERVAL_MINUTES", "60"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# 설정 인스턴스 생성
settings = Settings()

# 환경별 설정 로드
def get_settings():
    return settings
