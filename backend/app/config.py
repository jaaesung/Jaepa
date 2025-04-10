"""
JaePa 애플리케이션 설정 모듈

애플리케이션 설정 및 구성 옵션을 관리합니다.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseSettings

# 환경 변수 로드
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스
    """
    # 일반 설정
    APP_NAME: str = "JaePa"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

    # API 설정
    API_PREFIX: str = "/api"
    API_V1_STR: str = ""
    # 전체 API 경로는 /api로 통일하여 프론트엔드와 호환성 유지

    # MongoDB 설정
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "jaepa")

    # JWT 설정
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-jwt")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # CORS 설정
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080"
    ]

    # 뉴스 크롤링 설정
    NEWS_CRAWLER_RATE_LIMIT: int = int(os.getenv("NEWS_CRAWLER_RATE_LIMIT", "10"))

    class Config:
        """
        Pydantic 설정 내부 클래스
        """
        env_file = env_path
        case_sensitive = True


# 설정 인스턴스 생성
settings = Settings()
