"""
API 서버 모듈

FastAPI를 사용한 API 서버 설정 및 라우트 등록을 담당합니다.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="JaePa API",
    description="주식 뉴스 및 감성 분석을 위한 API",
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

# 상태 확인 엔드포인트
@app.get("/health")
async def health_check():
    """API 서버 상태 확인"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }

# 라우트 등록
from backend.api.routes import auth, news, stock, analysis
app.include_router(auth.router, prefix="/auth", tags=["인증"])
app.include_router(news.router, prefix="/news", tags=["뉴스"])
app.include_router(stock.router, prefix="/stocks", tags=["주식"])
app.include_router(analysis.router, prefix="/analysis", tags=["분석"])

# 전역 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "내부 서버 오류가 발생했습니다."},
    )

# 서버 실행 (직접 실행 시)
if __name__ == "__main__":
    logger.info("Starting API server...")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
