"""
백엔드 메인 모듈

백엔드 애플리케이션의 진입점입니다.
"""

import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 현재 디렉토리를 모듈 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 설정 가져오기
from config import settings

# API 서버 가져오기
from backend.api.server import app as api_app

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG if settings.environment == "development" else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 메인 앱 생성
app = FastAPI(
    title="JaePa Backend",
    description="주식 뉴스 및 감성 분석 백엔드",
    version="1.0.0",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 앱 마운트
app.mount("/api", api_app)

# 루트 엔드포인트
@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "name": "JaePa Backend",
        "version": "1.0.0",
        "environment": settings.environment,
    }

# 상태 확인 엔드포인트
@app.get("/health")
async def health_check():
    """상태 확인 엔드포인트"""
    return {
        "status": "healthy",
        "environment": settings.environment,
    }

# 서버 실행 (직접 실행 시)
if __name__ == "__main__":
    import uvicorn

    logger.info(f"백엔드 서버 시작 (환경: {settings.environment})")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
