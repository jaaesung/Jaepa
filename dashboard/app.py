"""
JaePa 뉴스 대시보드 웹 앱

FastAPI를 사용하여 수집된 뉴스와 감성 분석 결과를 시각화하는 대시보드를 제공합니다.
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# 상위 디렉토리를 import 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, Query, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv
import pandas as pd
import json

# 환경 변수 로드
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="JaePa 뉴스 대시보드",
    description="금융 뉴스 수집 및 감성 분석 결과를 시각화하는 대시보드",
    version="0.1.0"
)

# 템플릿 및 정적 파일 설정
templates_path = Path(__file__).parent / "templates"
static_path = Path(__file__).parent / "static"

# 디렉토리가 없으면 생성
templates_path.mkdir(exist_ok=True)
static_path.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(templates_path))
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# MongoDB 연결 클래스
class Database:
    """MongoDB 연결 및 데이터 접근 클래스"""
    
    def __init__(self):
        """Database 클래스 초기화"""
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.mongo_db_name = os.getenv("MONGO_DB_NAME", "jaepa")
        self.client = None
        self.db = None
        
        # 컬렉션 이름
        self.news_collection_name = "financial_news"
        self.sentiment_collection_name = "news_sentiment_trends"
        self.stock_data_collection_name = "stock_data"
        
    def connect(self):
        """MongoDB 연결"""
        if not self.client:
            try:
                self.client = MongoClient(self.mongo_uri)
                self.db = self.client[self.mongo_db_name]
                logger.info(f"MongoDB 연결 성공: {self.mongo_uri}, DB: {self.mongo_db_name}")
            except Exception as e:
                logger.error(f"MongoDB 연결 실패: {str(e)}")
                raise HTTPException(status_code=500, detail="데이터베이스 연결 실패")
        return self.db
    
    def close(self):
        """MongoDB 연결 종료"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB 연결 종료")


# 데이터베이스 객체 생성
db = Database()


# 의존성 주입: 데이터베이스 연결
def get_db():
    """
    FastAPI 의존성으로 사용하기 위한 데이터베이스 객체 반환
    """
    try:
        db.connect()
        yield db
    finally:
        pass  # 연결은 유지


# 메인 페이지 (대시보드)
@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request, db: Database = Depends(get_db)):
    """
    대시보드 메인 페이지
    """
    # 최근 7일간 수집된 뉴스 기사 수
    news_count = await get_news_count(db, days=7)
    
    # 감성 분석 평균 (최근 7일)
    sentiment_avg = await get_sentiment_average(db, days=7)
    
    # 소스별 뉴스 수
    sources_count = await get_sources_count(db, days=7)
    
    # 서로 다른 감성으로 분류된 관련 심볼 상위 5개
    symbols = await get_top_symbols_by_sentiment(db, limit=5, days=7)
    
    return templates.TemplateResponse(
        "dashboard.html", 
        {
            "request": request,
            "news_count": news_count,
            "sentiment_avg": sentiment_avg,
            "sources_count": sources_count,
            "symbols": symbols
        }
    )


# API: 최근 뉴스 목록
@app.get("/api/news", response_class=JSONResponse)
async def get_recent_news(
    db: Database = Depends(get_db),
    days: int = Query(7, description="가져올 뉴스의 기간(일)"),
    limit: int = Query(20, description="가져올 뉴스의 최대 개수"),
    source_type: Optional[str] = Query(None, description="뉴스 소스 유형(rss, finnhub, newsdata)"),
    source: Optional[str] = Query(None, description="뉴스 출처"),
    symbol: Optional[str] = Query(None, description="관련 심볼")
):
    """
    최근 수집된 뉴스 목록을 JSON 형식으로 반환
    """
    # 쿼리 필터 구성
    date_limit = datetime.now() - timedelta(days=days)
    date_limit_str = date_limit.isoformat()
    
    query_filter = {"published_date": {"$gte": date_limit_str}}
    
    if source_type:
        query_filter["source_type"] = source_type
        
    if source:
        query_filter["source"] = source
        
    if symbol:
        query_filter["related_symbols"] = symbol
    
    # 뉴스 조회
    news_collection = db.db[db.news_collection_name]
    
    cursor = news_collection.find(
        query_filter,
        {
            "_id": 0,
            "url": 1, 
            "title": 1, 
            "content": {"$substr": ["$content", 0, 200]},  # 내용은 200자로 제한
            "published_date": 1,
            "source": 1,
            "source_type": 1,
            "sentiment": 1,
            "related_symbols": 1
        }
    ).sort("published_date", DESCENDING).limit(limit)
    
    news_list = []
    async for news in cursor:
        # 감성 점수 소수점 2자리로 반올림
        if news.get("sentiment"):
            for k, v in news["sentiment"].items():
                news["sentiment"][k] = round(v, 2)
        news_list.append(news)
    
    return {"news": news_list, "count": len(news_list)}


# API: 뉴스 수집 통계
@app.get("/api/stats/news", response_class=JSONResponse)
async def get_news_stats(
    db: Database = Depends(get_db),
    days: int = Query(30, description="통계 기간(일)")
):
    """
    뉴스 수집 통계 (일별, 소스별)
    """
    # 쿼리 필터
    date_limit = datetime.now() - timedelta(days=days)
    date_limit_str = date_limit.isoformat()
    
    # 집계 파이프라인
    pipeline = [
        # 날짜 필터링
        {"$match": {"published_date": {"$gte": date_limit_str}}},
        
        # 날짜 추출 (YYYY-MM-DD 형식)
        {"$addFields": {"date_str": {"$substr": ["$published_date", 0, 10]}}},
        
        # 날짜 및 소스별 그룹화
        {"$group": {
            "_id": {"date": "$date_str", "source_type": "$source_type"},
            "count": {"$sum": 1}
        }},
        
        # 결과 정형화
        {"$project": {
            "_id": 0,
            "date": "$_id.date",
            "source_type": "$_id.source_type",
            "count": 1
        }},
        
        # 날짜별 정렬
        {"$sort": {"date": 1}}
    ]
    
    # 집계 실행
    news_collection = db.db[db.news_collection_name]
    results = await news_collection.aggregate(pipeline).to_list(length=None)
    
    # 결과 변환 (날짜별 그룹화)
    date_groups = {}
    for r in results:
        date = r["date"]
        source_type = r.get("source_type", "unknown")
        count = r["count"]
        
        if date not in date_groups:
            date_groups[date] = {"date": date, "total": 0}
            
        date_groups[date][source_type] = count
        date_groups[date]["total"] += count
    
    # 날짜별 정렬
    stats = sorted(date_groups.values(), key=lambda x: x["date"])
    
    return {"stats": stats}


# API: 감성 분석 통계
@app.get("/api/stats/sentiment", response_class=JSONResponse)
async def get_sentiment_stats(
    db: Database = Depends(get_db),
    days: int = Query(30, description="통계 기간(일)"),
    symbol: Optional[str] = Query(None, description="특정 심볼에 대한 통계")
):
    """
    감성 분석 통계 (일별, 심볼별)
    """
    # 감성 트렌드 컬렉션에서 데이터 조회
    sentiment_collection = db.db[db.sentiment_collection_name]
    
    # 날짜 제한
    date_limit = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # 쿼리 필터
    query_filter = {"date": {"$gte": date_limit}}
    if symbol:
        query_filter["symbol"] = symbol
    
    # 데이터 조회
    cursor = sentiment_collection.find(
        query_filter,
        {
            "_id": 0,
            "date": 1,
            "symbol": 1,
            "daily_sentiment": 1
        }
    ).sort("date", 1)
    
    stats = []
    async for item in cursor:
        if "daily_sentiment" in item:
            stats.append({
                "date": item["date"],
                "symbol": item["symbol"],
                "positive": round(item["daily_sentiment"]["positive"], 2),
                "neutral": round(item["daily_sentiment"]["neutral"], 2),
                "negative": round(item["daily_sentiment"]["negative"], 2),
                "volume": item["daily_sentiment"]["volume"]
            })
    
    return {"stats": stats}


# 유틸리티 함수: 최근 뉴스 개수 계산
async def get_news_count(db: Database, days: int = 7) -> int:
    """
    최근 수집된 뉴스 기사 수 계산
    """
    date_limit = datetime.now() - timedelta(days=days)
    date_limit_str = date_limit.isoformat()
    
    news_collection = db.db[db.news_collection_name]
    count = await news_collection.count_documents({"published_date": {"$gte": date_limit_str}})
    
    return count


# 유틸리티 함수: 평균 감성 점수 계산
async def get_sentiment_average(db: Database, days: int = 7) -> Dict[str, float]:
    """
    최근 수집된 뉴스의 평균 감성 점수 계산
    """
    date_limit = datetime.now() - timedelta(days=days)
    date_limit_str = date_limit.isoformat()
    
    pipeline = [
        {"$match": {
            "published_date": {"$gte": date_limit_str},
            "sentiment": {"$ne": None}
        }},
        {"$group": {
            "_id": None,
            "avg_positive": {"$avg": "$sentiment.positive"},
            "avg_neutral": {"$avg": "$sentiment.neutral"},
            "avg_negative": {"$avg": "$sentiment.negative"},
            "count": {"$sum": 1}
        }}
    ]
    
    news_collection = db.db[db.news_collection_name]
    results = await news_collection.aggregate(pipeline).to_list(length=1)
    
    if results and len(results) > 0:
        result = results[0]
        return {
            "positive": round(result["avg_positive"], 2),
            "neutral": round(result["avg_neutral"], 2),
            "negative": round(result["avg_negative"], 2),
            "count": result["count"]
        }
    else:
        return {
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "count": 0
        }


# 유틸리티 함수: 소스별 뉴스 개수 계산
async def get_sources_count(db: Database, days: int = 7) -> List[Dict[str, Any]]:
    """
    소스별 뉴스 개수 계산
    """
    date_limit = datetime.now() - timedelta(days=days)
    date_limit_str = date_limit.isoformat()
    
    pipeline = [
        {"$match": {"published_date": {"$gte": date_limit_str}}},
        {"$group": {
            "_id": {"source_type": "$source_type", "source": "$source"},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "source_type": "$_id.source_type",
            "source": "$_id.source",
            "count": 1
        }},
        {"$sort": {"count": -1}}
    ]
    
    news_collection = db.db[db.news_collection_name]
    results = await news_collection.aggregate(pipeline).to_list(length=None)
    
    # 소스 유형별로 그룹화
    source_types = {}
    for r in results:
        source_type = r.get("source_type", "unknown")
        if source_type not in source_types:
            source_types[source_type] = {"source_type": source_type, "total": 0, "sources": []}
            
        source_types[source_type]["sources"].append({
            "source": r["source"],
            "count": r["count"]
        })
        source_types[source_type]["total"] += r["count"]
    
    # 총 개수로 정렬
    return sorted(source_types.values(), key=lambda x: x["total"], reverse=True)


# 유틸리티 함수: 감성별 상위 심볼 가져오기
async def get_top_symbols_by_sentiment(db: Database, limit: int = 5, days: int = 7) -> Dict[str, List[Dict[str, Any]]]:
    """
    감성별 상위 심볼 가져오기
    """
    date_limit = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    sentiment_collection = db.db[db.sentiment_collection_name]
    
    # 긍정적 감성 상위 심볼
    positive_symbols = await sentiment_collection.find(
        {
            "date": {"$gte": date_limit},
            "symbol": {"$ne": "GENERAL"},
            "daily_sentiment.volume": {"$gte": 3}  # 최소 기사 수
        },
        {
            "_id": 0,
            "symbol": 1,
            "daily_sentiment.positive": 1,
            "daily_sentiment.volume": 1
        }
    ).sort("daily_sentiment.positive", -1).limit(limit).to_list(length=limit)
    
    # 부정적 감성 상위 심볼
    negative_symbols = await sentiment_collection.find(
        {
            "date": {"$gte": date_limit},
            "symbol": {"$ne": "GENERAL"},
            "daily_sentiment.volume": {"$gte": 3}  # 최소 기사 수
        },
        {
            "_id": 0,
            "symbol": 1,
            "daily_sentiment.negative": 1,
            "daily_sentiment.volume": 1
        }
    ).sort("daily_sentiment.negative", -1).limit(limit).to_list(length=limit)
    
    # 결과 정형화
    return {
        "positive": [
            {
                "symbol": item["symbol"],
                "score": round(item["daily_sentiment"]["positive"], 2),
                "volume": item["daily_sentiment"]["volume"]
            } for item in positive_symbols
        ],
        "negative": [
            {
                "symbol": item["symbol"],
                "score": round(item["daily_sentiment"]["negative"], 2),
                "volume": item["daily_sentiment"]["volume"]
            } for item in negative_symbols
        ]
    }


# 서버 종료 시 MongoDB 연결 종료
@app.on_event("shutdown")
def shutdown_event():
    """서버 종료 시 실행될 함수"""
    db.close()


# 직접 실행 시 개발 서버 시작
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
