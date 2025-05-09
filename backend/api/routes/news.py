"""
뉴스 라우트 모듈

뉴스 관련 API 엔드포인트를 정의합니다.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date

# 컨트롤러 가져오기 (추후 구현)
# from ..controllers.news_controller import NewsController

router = APIRouter()
# news_controller = NewsController()

@router.get("/")
async def get_news(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    source: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    keyword: Optional[str] = None,
):
    """뉴스 목록 가져오기"""
    # return await news_controller.get_news(page, limit, category, source, start_date, end_date, keyword)
    return {
        "items": [
            {
                "id": "1",
                "title": "샘플 뉴스 제목",
                "content": "샘플 뉴스 내용입니다.",
                "source": "샘플 소스",
                "url": "https://example.com/news/1",
                "published_at": "2023-01-01T00:00:00Z",
                "category": "경제",
            }
        ],
        "total": 1,
        "page": page,
        "limit": limit,
    }

@router.get("/search")
async def search_news(
    query: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    """뉴스 검색"""
    # return await news_controller.search_news(query, page, limit)
    return {
        "items": [
            {
                "id": "1",
                "title": f"검색어 '{query}'에 대한 샘플 뉴스",
                "content": "샘플 뉴스 내용입니다.",
                "source": "샘플 소스",
                "url": "https://example.com/news/1",
                "published_at": "2023-01-01T00:00:00Z",
                "category": "경제",
            }
        ],
        "total": 1,
        "page": page,
        "limit": limit,
    }

@router.get("/categories")
async def get_categories():
    """뉴스 카테고리 목록 가져오기"""
    # return await news_controller.get_categories()
    return ["경제", "금융", "주식", "산업", "국제"]

@router.get("/sources")
async def get_sources():
    """뉴스 소스 목록 가져오기"""
    # return await news_controller.get_sources()
    return ["연합뉴스", "한국경제", "매일경제", "조선비즈", "블룸버그"]

@router.get("/{news_id}")
async def get_news_by_id(news_id: str):
    """특정 뉴스 상세 정보 가져오기"""
    # return await news_controller.get_news_by_id(news_id)
    return {
        "id": news_id,
        "title": "샘플 뉴스 제목",
        "content": "샘플 뉴스 상세 내용입니다.",
        "source": "샘플 소스",
        "url": f"https://example.com/news/{news_id}",
        "published_at": "2023-01-01T00:00:00Z",
        "category": "경제",
    }

@router.get("/{news_id}/sentiment")
async def get_news_sentiment(news_id: str):
    """특정 뉴스의 감성 분석 결과 가져오기"""
    # return await news_controller.get_news_sentiment(news_id)
    return {
        "positive": 0.6,
        "neutral": 0.3,
        "negative": 0.1,
    }

@router.get("/popular-keywords")
async def get_popular_keywords(
    limit: int = Query(10, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """인기 키워드 가져오기"""
    # return await news_controller.get_popular_keywords(limit, start_date, end_date)
    return [
        {"text": "주식", "value": 100, "sentiment": 0.2},
        {"text": "금리", "value": 80, "sentiment": -0.3},
        {"text": "인플레이션", "value": 60, "sentiment": -0.5},
        {"text": "성장", "value": 40, "sentiment": 0.7},
        {"text": "투자", "value": 30, "sentiment": 0.4},
    ]
