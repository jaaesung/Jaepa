"""
주식 라우트 모듈

주식 데이터 관련 API 엔드포인트를 정의합니다.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date

# 컨트롤러 가져오기 (추후 구현)
# from ..controllers.stock_controller import StockController

router = APIRouter()
# stock_controller = StockController()

@router.get("/search")
async def search_stocks(query: str):
    """주식 검색"""
    # return await stock_controller.search_stocks(query)
    return [
        {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
    ]

@router.get("/{symbol}")
async def get_stock_details(symbol: str):
    """주식 상세 정보 가져오기"""
    # return await stock_controller.get_stock_details(symbol)
    return {
        "symbol": symbol,
        "name": "샘플 주식",
        "exchange": "NASDAQ",
        "sector": "기술",
        "industry": "소프트웨어",
        "description": "샘플 주식 설명입니다.",
        "website": "https://example.com",
        "market_cap": 1000000000,
        "pe_ratio": 20.5,
        "dividend_yield": 1.5,
    }

@router.get("/{symbol}/quote")
async def get_stock_quote(symbol: str):
    """주식 실시간 데이터 가져오기"""
    # return await stock_controller.get_stock_quote(symbol)
    return {
        "symbol": symbol,
        "price": 150.0,
        "change": 1.5,
        "change_percent": 1.0,
        "volume": 1000000,
        "prev_close": 148.5,
        "open": 149.0,
        "high": 151.0,
        "low": 148.0,
    }

@router.get("/{symbol}/historical")
async def get_stock_historical(
    symbol: str,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    interval: str = Query("day", regex="^(day|week|month)$"),
):
    """주식 히스토리 데이터 가져오기"""
    # return await stock_controller.get_stock_historical(symbol, from_date, to_date, interval)
    return [
        {
            "date": "2023-01-01",
            "open": 150.0,
            "high": 155.0,
            "low": 148.0,
            "close": 153.0,
            "volume": 1000000,
        },
        {
            "date": "2023-01-02",
            "open": 153.0,
            "high": 158.0,
            "low": 152.0,
            "close": 157.0,
            "volume": 1200000,
        },
    ]

@router.get("/{symbol}/news")
async def get_stock_news(
    symbol: str,
    limit: int = Query(10, ge=1, le=100),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
):
    """주식 관련 뉴스 가져오기"""
    # return await stock_controller.get_stock_news(symbol, limit, from_date, to_date)
    return [
        {
            "id": "1",
            "title": f"{symbol} 관련 샘플 뉴스",
            "summary": "샘플 뉴스 요약입니다.",
            "source": "샘플 소스",
            "url": "https://example.com/news/1",
            "published_at": "2023-01-01T00:00:00Z",
            "sentiment": "positive",
        }
    ]

@router.get("/{symbol}/financials")
async def get_stock_financials(symbol: str):
    """주식 재무 정보 가져오기"""
    # return await stock_controller.get_stock_financials(symbol)
    return {
        "income_statement": {
            "revenue": 100000000,
            "gross_profit": 50000000,
            "operating_income": 30000000,
            "net_income": 20000000,
        },
        "balance_sheet": {
            "total_assets": 200000000,
            "total_liabilities": 100000000,
            "total_equity": 100000000,
        },
        "cash_flow": {
            "operating_cash_flow": 25000000,
            "investing_cash_flow": -10000000,
            "financing_cash_flow": -5000000,
        },
    }

@router.get("/popular")
async def get_popular_stocks(limit: int = Query(10, ge=1, le=100)):
    """인기 주식 목록 가져오기"""
    # return await stock_controller.get_popular_stocks(limit)
    return [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 150.0,
            "change_percent": 1.0,
        },
        {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "price": 300.0,
            "change_percent": 0.5,
        },
    ]

@router.get("/sector-performance")
async def get_sector_performance():
    """섹터별 성과 가져오기"""
    # return await stock_controller.get_sector_performance()
    return [
        {"sector": "기술", "performance": 5.2},
        {"sector": "금융", "performance": 3.1},
        {"sector": "헬스케어", "performance": 2.5},
        {"sector": "에너지", "performance": -1.2},
        {"sector": "소비재", "performance": 1.8},
    ]
