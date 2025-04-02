"""
애플리케이션 설정 모듈
"""
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 환경 변수 로드
env_path = Path(__file__).parents[2] / '.env'
load_dotenv(dotenv_path=env_path)


class DatabaseSettings(BaseModel):
    """
    데이터베이스 설정
    """
    mongo_uri: str = Field(default=os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    mongo_db_name: str = Field(default=os.getenv("MONGO_DB_NAME", "jaepa"))
    mongo_user: Optional[str] = Field(default=os.getenv("MONGO_USER"))
    mongo_password: Optional[str] = Field(default=os.getenv("MONGO_PASSWORD"))


class APISettings(BaseModel):
    """
    API 관련 설정
    """
    host: str = Field(default=os.getenv("API_HOST", "0.0.0.0"))
    port: int = Field(default=int(os.getenv("API_PORT", "5000")))
    secret_key: str = Field(default=os.getenv("SECRET_KEY", "development_secret_key"))
    jwt_secret_key: str = Field(default=os.getenv("JWT_SECRET_KEY", "development_jwt_secret"))
    access_token_expire_minutes: int = Field(
        default=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    )


class NewsAPISettings(BaseModel):
    """
    뉴스 API 설정
    """
    newsapi_key: Optional[str] = Field(default=os.getenv("NEWSAPI_KEY"))


class FinanceAPISettings(BaseModel):
    """
    금융 데이터 API 설정
    """
    alphavantage_api_key: Optional[str] = Field(default=os.getenv("ALPHAVANTAGE_API_KEY"))
    finnhub_api_key: Optional[str] = Field(default=os.getenv("FINNHUB_API_KEY"))
    coingecko_api_key: Optional[str] = Field(default=os.getenv("COINGECKO_API_KEY"))


class ModelSettings(BaseModel):
    """
    모델 설정
    """
    finbert_model_path: str = Field(
        default=os.getenv("FINBERT_MODEL_PATH", "models/finbert")
    )


class Settings(BaseModel):
    """
    애플리케이션 전체 설정
    """
    debug: bool = Field(default=os.getenv("DEBUG", "True").lower() == "true")
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api: APISettings = Field(default_factory=APISettings)
    news_api: NewsAPISettings = Field(default_factory=NewsAPISettings)
    finance_api: FinanceAPISettings = Field(default_factory=FinanceAPISettings)
    model: ModelSettings = Field(default_factory=ModelSettings)


# 애플리케이션 설정 인스턴스
settings = Settings()
