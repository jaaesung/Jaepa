"""
뉴스 API 라우트 모듈

뉴스 데이터 관련 API 엔드포인트를 정의합니다.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..auth.auth_middleware import get_current_user
import sys
import os

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from crawling.integrated_news_collector import IntegratedNewsCollector

router = APIRouter(
    prefix="/api/news",
    tags=["news"],
    responses={404: {"description": "Not found"}},
)

# 뉴스 수집기 초기화
news_collector = IntegratedNewsCollector()

# 모델 정의
class NewsSearchParams(BaseModel):
    query: str
    days: Optional[int] = 30
    limit: Optional[int] = 50
    force_update: Optional[bool] = False

class SymbolNewsParams(BaseModel):
    symbol: str
    days: Optional[int] = 7
    limit: Optional[int] = 50
    force_update: Optional[bool] = False

class NewsCollectionParams(BaseModel):
    keywords: Optional[List[str]] = None
    symbols: Optional[List[str]] = None
    days: Optional[int] = 3
    limit: Optional[int] = 100

# API 엔드포인트
@router.get("/search")
async def search_news(
    query: str = Query(..., description="검색어"),
    days: int = Query(30, description="검색 기간 (일)"),
    limit: int = Query(50, description="최대 검색 결과 수"),
    force_update: bool = Query(False, description="강제 업데이트 여부"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    키워드로 뉴스 검색
    """
    try:
        results = news_collector.search_news(
            query=query,
            days=days,
            limit=limit,
            force_update=force_update
        )
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 검색 중 오류 발생: {str(e)}")

@router.get("/symbol/{symbol}")
async def get_news_by_symbol(
    symbol: str,
    days: int = Query(7, description="검색 기간 (일)"),
    limit: int = Query(50, description="최대 검색 결과 수"),
    force_update: bool = Query(False, description="강제 업데이트 여부"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    특정 주식 심볼에 대한 뉴스 조회
    """
    try:
        results = news_collector.get_news_by_symbol(
            symbol=symbol,
            days=days,
            limit=limit,
            force_update=force_update
        )
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 조회 중 오류 발생: {str(e)}")

@router.post("/collect")
async def collect_news(
    params: NewsCollectionParams,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    뉴스 수집 실행
    """
    # 관리자 권한 확인
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")

    try:
        results = news_collector.collect_news_from_all_sources(
            keywords=params.keywords,
            symbols=params.symbols,
            days=params.days,
            limit=params.limit
        )
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 수집 중 오류 발생: {str(e)}")

@router.post("/collect/symbol/{symbol}")
async def collect_news_by_symbol(
    symbol: str,
    days: int = Query(7, description="검색 기간 (일)"),
    limit: int = Query(50, description="최대 검색 결과 수"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    특정 주식 심볼에 대한 뉴스 수집
    """
    # 관리자 권한 확인
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")

    try:
        results = news_collector.collect_news_by_symbol(
            symbol=symbol,
            days=days,
            limit=limit
        )
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 수집 중 오류 발생: {str(e)}")

@router.get("/sources")
async def get_news_sources(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    뉴스 소스 목록 조회
    """
    sources = [
        {"id": "traditional", "name": "전통적 크롤링", "description": "직접 웹사이트에서 크롤링한 뉴스"},
        {"id": "enhanced", "name": "향상된 소스", "description": "RSS 피드 및 API를 통해 수집한 뉴스"},
        {"id": "gdelt", "name": "GDELT", "description": "GDELT 글로벌 뉴스 데이터베이스에서 수집한 뉴스"}
    ]
    return {"sources": sources}

# 서버 종료 시 연결 종료
@router.on_event("shutdown")
def shutdown_event():
    news_collector.close()
