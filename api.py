#!/usr/bin/env python3
"""
금융 분석 API

이 모듈은 FinBERT 모델과 Polygon API를 사용한 금융 분석 기능을 제공하는 웹 API를 구현합니다.
"""
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 모듈 가져오기
try:
    from analysis.finbert_sentiment import FinBERTSentiment
    from data.polygon_client import PolygonClient
    from data.stock_data_store import StockDataStore
    from analysis.sentiment_price_analyzer import SentimentPriceAnalyzer
except ImportError as e:
    logger.error(f"모듈 가져오기 실패: {e}")
    logger.error("필요한 모듈이 설치되었는지 확인하세요.")
    raise

# API 모델 정의
class TextRequest(BaseModel):
    """텍스트 분석 요청"""
    text: str

class NewsRequest(BaseModel):
    """뉴스 분석 요청"""
    symbol: str
    limit: int = 5

class CorrelationRequest(BaseModel):
    """상관관계 분석 요청"""
    symbol: str
    days: int = 30

class SummaryRequest(BaseModel):
    """감성 요약 요청"""
    symbol: str
    days: int = 7

# 생명 주기 관리자
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 이벤트 (이전의 startup)
    global finbert, stock_data_store, sentiment_price_analyzer

    logger.info("API 초기화 중...")

    # FinBERT 감성 분석기 초기화
    finbert = FinBERTSentiment()

    # 주식 데이터 저장소 초기화
    stock_data_store = StockDataStore()

    # 감성-가격 분석기 초기화
    sentiment_price_analyzer = SentimentPriceAnalyzer()

    logger.info("API 초기화 완료")

    yield  # 어플리케이션 실행 중

    # 종료 이벤트 (이전의 shutdown)
    logger.info("API 종료 중...")

    # 리소스 정리
    if stock_data_store:
        stock_data_store.close()

    if sentiment_price_analyzer:
        sentiment_price_analyzer.close()

    logger.info("API 종료 완료")

# FastAPI 앱 생성
app = FastAPI(
    title="금융 분석 API",
    description="FinBERT 모델과 Polygon API를 사용한 금융 분석 API",
    version="0.1.0",
    lifespan=lifespan
)

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 전역 객체
finbert = None
stock_data_store = None
sentiment_price_analyzer = None

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """루트 엔드포인트 - 대시보드 페이지 제공"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api")
async def api_root():
    """기본 API 엔드포인트"""
    return {
        "message": "금융 분석 API에 오신 것을 환영합니다.",
        "version": "0.1.0",
        "endpoints": [
            "/api/analyze/text",
            "/api/analyze/news",
            "/api/analyze/correlation",
            "/api/analyze/summary"
        ]
    }

@app.post("/api/analyze/text")
async def analyze_text(request: TextRequest):
    """
    텍스트 감성 분석

    Args:
        request: 텍스트 분석 요청

    Returns:
        Dict[str, Any]: 감성 분석 결과
    """
    global finbert

    if not finbert:
        raise HTTPException(status_code=500, detail="FinBERT 감성 분석기가 초기화되지 않았습니다.")

    try:
        # 텍스트 분석
        sentiment = finbert.analyze(request.text)

        return {
            "text": request.text,
            "sentiment": sentiment["label"],
            "score": sentiment["score"],
            "scores": sentiment["scores"]
        }
    except Exception as e:
        logger.error(f"텍스트 분석 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"텍스트 분석 중 오류 발생: {str(e)}")

@app.post("/api/analyze/news")
async def analyze_news(request: NewsRequest):
    """
    뉴스 감성 분석

    Args:
        request: 뉴스 분석 요청

    Returns:
        Dict[str, Any]: 뉴스 감성 분석 결과
    """
    global finbert, stock_data_store

    if not finbert or not stock_data_store:
        raise HTTPException(status_code=500, detail="필요한 구성 요소가 초기화되지 않았습니다.")

    try:
        # 뉴스 가져오기
        news_items = stock_data_store.get_stock_news(request.symbol, limit=request.limit)

        # 뉴스가 없는 경우
        if not news_items:
            return {
                "symbol": request.symbol,
                "message": f"{request.symbol}에 대한 뉴스가 없습니다.",
                "news": []
            }

        # 뉴스 감성 분석
        news_with_sentiment = []
        for news in news_items:
            # 뉴스 감성 분석
            analyzed_news = finbert.analyze_news({
                "title": news.get("title", ""),
                "content": news.get("description", ""),
                "url": news.get("article_url", ""),
                "published_date": news.get("published_utc", "")
            })

            news_with_sentiment.append({
                "title": analyzed_news["title"],
                "sentiment": analyzed_news["sentiment"]["label"],
                "score": analyzed_news["sentiment"]["score"],
                "scores": analyzed_news["sentiment"]["scores"],
                "url": analyzed_news.get("url", ""),
                "published_date": analyzed_news.get("published_date", "")
            })

        return {
            "symbol": request.symbol,
            "count": len(news_with_sentiment),
            "news": news_with_sentiment
        }
    except Exception as e:
        logger.error(f"뉴스 분석 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"뉴스 분석 중 오류 발생: {str(e)}")

@app.post("/api/analyze/correlation")
async def analyze_correlation(request: CorrelationRequest):
    """
    감성-가격 상관관계 분석

    Args:
        request: 상관관계 분석 요청

    Returns:
        Dict[str, Any]: 상관관계 분석 결과
    """
    global sentiment_price_analyzer

    if not sentiment_price_analyzer:
        raise HTTPException(status_code=500, detail="감성-가격 분석기가 초기화되지 않았습니다.")

    try:
        # 감성-가격 상관관계 분석
        result = sentiment_price_analyzer.analyze_sentiment_price_correlation(request.symbol, days=request.days)

        # 데이터 필드 제거 (너무 큼)
        if "data" in result:
            del result["data"]

        return result
    except Exception as e:
        logger.error(f"상관관계 분석 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상관관계 분석 중 오류 발생: {str(e)}")

@app.post("/api/analyze/summary")
async def get_sentiment_summary(request: SummaryRequest):
    """
    감성 요약

    Args:
        request: 감성 요약 요청

    Returns:
        Dict[str, Any]: 감성 요약
    """
    global sentiment_price_analyzer

    if not sentiment_price_analyzer:
        raise HTTPException(status_code=500, detail="감성-가격 분석기가 초기화되지 않았습니다.")

    try:
        # 감성 요약
        result = sentiment_price_analyzer.get_sentiment_summary(request.symbol, days=request.days)

        # 뉴스 필드 제거 (너무 큼)
        if "news" in result:
            del result["news"]

        return result
    except Exception as e:
        logger.error(f"감성 요약 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"감성 요약 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    # 서버 실행
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
