"""
데이터베이스 연결 모듈

데이터베이스 연결 및 세션 관리를 담당합니다.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config.settings import settings

# 데이터베이스 URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델 기본 클래스
Base = declarative_base()

# 데이터베이스 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
