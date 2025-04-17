"""
분석 API 라우터

감성 분석, 상관관계 분석 등 분석 관련 API 엔드포인트를 제공합니다.
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, Path, Request, Body
from pydantic import BaseModel

from api.responses import create_response, ResponseStatus
from api.exceptions import (
    ResourceNotFoundException, ExternalServiceException, ValidationException,
    ErrorCode
)
from api.dependencies import (
    get_current_user_with_permissions, get_date_range_params,
    get_request_id, get_finbert_sentiment_analyzer,
    get_sentiment_price_analyzer
)

# 로깅 설정
logger = logging.getLogger(__name__)

# 라우터 설정
router = APIRouter(
    prefix="/analysis",
    tags=["분석"],
    responses={
        401: {"description": "인증되지 않음"},
        403: {"description": "권한 없음"},
        404: {"description": "찾을 수 없음"},
        422: {"description": "유효하지 않은 요청"},
        500: {"description": "서버 오류"}
    }
)


# 요청 모델
class TextAnalysisRequest(BaseModel):
    """텍스트 분석 요청"""
    text: str


class NewsAnalysisRequest(BaseModel):
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


@router.post("/text")
async def analyze_text(
    request: TextAnalysisRequest,
    request_id: str = Depends(get_request_id),
    finbert = Depends(get_finbert_sentiment_analyzer)
):
    """
    텍스트 감성 분석
    
    입력된 텍스트의 감성을 분석합니다.
    """
    try:
        # 텍스트 유효성 검사
        if not request.text.strip():
            logger.warning(
                f"텍스트 감성 분석 실패: 빈 텍스트 "
                f"(요청 ID: {request_id})"
            )
            raise ValidationException(
                message="분석할 텍스트를 입력해주세요.",
                field="text"
            )
        
        # 감성 분석 수행
        sentiment = finbert.analyze(request.text)
        
        logger.info(
            f"텍스트 감성 분석: 텍스트 분석 완료 (감성: {sentiment['label']}) "
            f"(요청 ID: {request_id})"
        )
        
        # 응답 생성
        return create_response(
            data={
                "text": request.text,
                "sentiment": sentiment["label"],
                "score": sentiment["score"],
                "scores": sentiment["scores"]
            },
            message="텍스트 감성 분석 성공",
            meta_info={"request_id": request_id}
        )
    except ValidationException:
        raise
    except Exception as e:
        logger.error(
            f"텍스트 감성 분석 오류: {str(e)} "
            f"(요청 ID: {request_id})"
        )
        raise


@router.post("/news")
async def analyze_news(
    request: NewsAnalysisRequest,
    request_id: str = Depends(get_request_id),
    finbert = Depends(get_finbert_sentiment_analyzer),
    stock_data_store = Depends(get_sentiment_price_analyzer)
):
    """
    뉴스 감성 분석
    
    특정 주식 심볼에 관련된 뉴스의 감성을 분석합니다.
    """
    try:
        # 뉴스 가져오기
        news_items = stock_data_store.get_stock_news(request.symbol, limit=request.limit)
        
        # 뉴스가 없는 경우
        if not news_items:
            logger.info(
                f"뉴스 감성 분석: 심볼 '{request.symbol}'에 대한 뉴스가 없음 "
                f"(요청 ID: {request_id})"
            )
            return create_response(
                data={
                    "symbol": request.symbol,
                    "count": 0,
                    "news": []
                },
                message=f"{request.symbol}에 대한 뉴스가 없습니다.",
                meta_info={"request_id": request_id}
            )
        
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
        
        logger.info(
            f"뉴스 감성 분석: 심볼 '{request.symbol}'에 대한 {len(news_with_sentiment)}개 뉴스 분석 완료 "
            f"(요청 ID: {request_id})"
        )
        
        # 응답 생성
        return create_response(
            data={
                "symbol": request.symbol,
                "count": len(news_with_sentiment),
                "news": news_with_sentiment
            },
            message=f"{request.symbol} 관련 뉴스 감성 분석 성공",
            meta_info={"request_id": request_id}
        )
    except Exception as e:
        logger.error(
            f"뉴스 감성 분석 오류: {str(e)} "
            f"(요청 ID: {request_id})"
        )
        raise


@router.post("/correlation")
async def analyze_correlation(
    request: CorrelationRequest,
    request_id: str = Depends(get_request_id),
    sentiment_price_analyzer = Depends(get_sentiment_price_analyzer)
):
    """
    감성-가격 상관관계 분석
    
    뉴스 감성과 주가 변동의 상관관계를 분석합니다.
    """
    try:
        # 상관관계 분석
        result = sentiment_price_analyzer.analyze_sentiment_price_correlation(
            request.symbol,
            days=request.days
        )
        
        # 데이터 필드 제거 (너무 큼)
        if "data" in result:
            del result["data"]
        
        logger.info(
            f"상관관계 분석: 심볼 '{request.symbol}'의 {request.days}일 상관관계 분석 완료 "
            f"(요청 ID: {request_id})"
        )
        
        # 응답 생성
        return create_response(
            data=result,
            message=f"{request.symbol}의 감성-가격 상관관계 분석 성공",
            meta_info={"request_id": request_id}
        )
    except Exception as e:
        logger.error(
            f"상관관계 분석 오류: {str(e)} "
            f"(요청 ID: {request_id})"
        )
        raise


@router.post("/summary")
async def get_sentiment_summary(
    request: SummaryRequest,
    request_id: str = Depends(get_request_id),
    sentiment_price_analyzer = Depends(get_sentiment_price_analyzer)
):
    """
    감성 요약
    
    특정 주식 심볼에 관련된 뉴스의 감성 요약을 제공합니다.
    """
    try:
        # 감성 요약
        result = sentiment_price_analyzer.get_sentiment_summary(
            request.symbol,
            days=request.days
        )
        
        # 뉴스 필드 제거 (너무 큼)
        if "news" in result:
            del result["news"]
        
        logger.info(
            f"감성 요약: 심볼 '{request.symbol}'의 {request.days}일 감성 요약 완료 "
            f"(요청 ID: {request_id})"
        )
        
        # 응답 생성
        return create_response(
            data=result,
            message=f"{request.symbol}의 감성 요약 성공",
            meta_info={"request_id": request_id}
        )
    except Exception as e:
        logger.error(
            f"감성 요약 오류: {str(e)} "
            f"(요청 ID: {request_id})"
        )
        raise
