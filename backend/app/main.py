"""
JaePa 백엔드 애플리케이션 메인 모듈

FastAPI 애플리케이션 초기화 및 API 라우트 설정을 담당합니다.
"""
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pymongo import MongoClient

from .api import auth_routes, user_routes

# 환경 변수 로드
load_dotenv()

# MongoDB 연결
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "jaepa")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB_NAME]

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="JaePa API",
    description="금융 뉴스 크롤링 및 감성 분석 API",
    version="0.1.0"
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


# 애플리케이션 시작/종료 이벤트
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행되는 코드"""
    print("JaePa API 서버 시작됨")


@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 실행되는 코드"""
    if mongo_client:
        mongo_client.close()
    print("JaePa API 서버 종료됨")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
