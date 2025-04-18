"""
사용자 모델 모듈

사용자 데이터 모델을 정의합니다.
"""

from sqlalchemy import Boolean, Column, String, DateTime
from sqlalchemy.sql import func
from ..connection import Base

class User(Base):
    """사용자 모델"""
    
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
