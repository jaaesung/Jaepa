"""
주식 모델 모듈

주식 데이터 모델을 정의합니다.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from ..connection import Base

class Stock(Base):
    """주식 기본 정보 모델"""
    
    __tablename__ = "stocks"
    
    symbol = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    exchange = Column(String, index=True)
    sector = Column(String, index=True, nullable=True)
    industry = Column(String, index=True, nullable=True)
    description = Column(Text, nullable=True)
    website = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class StockPrice(Base):
    """주식 가격 모델"""
    
    __tablename__ = "stock_prices"
    
    id = Column(String, primary_key=True, index=True)
    symbol = Column(String, ForeignKey("stocks.symbol"), index=True)
    date = Column(DateTime(timezone=True), index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Watchlist(Base):
    """관심 주식 목록 모델"""
    
    __tablename__ = "watchlists"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    symbol = Column(String, ForeignKey("stocks.symbol"), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
