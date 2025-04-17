"""
JaePa 백엔드 애플리케이션 메인 모듈

FastAPI 애플리케이션 초기화 및 API 라우트 설정을 담당합니다.
"""
import os
import sys
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dependency_injector.wiring import inject, Provide

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 설정 및 의존성 주입 컨테이너 가져오기
from config import settings
from core import container
from bootstrap import bootstrap_app

# 애플리케이션 부트스트랩
bootstrap_app()

# 로깅 설정
logging.basicConfig(level=getattr(logging, settings.logging.level))
logger = logging.getLogger(__name__)

from .api import auth_routes, user_routes, news_routes, sentiment_analysis_routes

# MongoDB 클라이언트 가져오기
mongo_client = container.mongodb_client()
db = mongo_client.get_database(settings.db.mongo_db_name)

# 애플리케이션 시작/종료 이벤트
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명 주기 관리"""
    # 시작 이벤트
    logger.info("JaePa API 서버 시작됨")

    yield

    # 종료 이벤트
    if mongo_client:
        mongo_client.close()
    logger.info("JaePa API 서버 종료됨")

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="JaePa API",
    description="금융 뉴스 크롤링 및 감성 분석 API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 실제 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우트 등록
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(news_routes.router)
app.include_router(sentiment_analysis_routes.router)

# 기본 라우트
@app.get("/")
async def root():
    return {
        "service": "JaePa API",
        "version": "0.1.0",
        "status": "online"
    }

# 상태 체크 라우트
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if mongo_client else "disconnected"
    }





if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
