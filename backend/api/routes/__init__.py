"""
API 라우트 패키지

모든 API 라우트를 통합하고 내보냅니다.
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .news import router as news_router
from .stock import router as stock_router
from .analysis import router as analysis_router

# 메인 라우터 생성
api_router = APIRouter()

# 각 라우트 등록
api_router.include_router(auth_router, prefix="/auth", tags=["인증"])
api_router.include_router(news_router, prefix="/news", tags=["뉴스"])
api_router.include_router(stock_router, prefix="/stocks", tags=["주식"])
api_router.include_router(analysis_router, prefix="/analysis", tags=["분석"])
