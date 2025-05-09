"""
뉴스 모델 모듈

뉴스 데이터 모델을 정의합니다.
"""

from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from ..connection import Base

class News(Base):
    """뉴스 모델"""
    
    __tablename__ = "news"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    summary = Column(Text, nullable=True)
    source = Column(String, index=True)
    url = Column(String, unique=True)
    image_url = Column(String, nullable=True)
    category = Column(String, index=True, nullable=True)
    published_at = Column(DateTime(timezone=True), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class NewsSentiment(Base):
    """뉴스 감성 분석 결과 모델"""
    
    __tablename__ = "news_sentiments"
    
    id = Column(String, primary_key=True, index=True)
    news_id = Column(String, ForeignKey("news.id"), index=True)
    model = Column(String, index=True)
    positive = Column(Float)
    neutral = Column(Float)
    negative = Column(Float)
    sentiment = Column(String, index=True)  # positive, neutral, negative
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SavedNews(Base):
    """저장된 뉴스 모델"""
    
    __tablename__ = "saved_news"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    news_id = Column(String, ForeignKey("news.id"), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
