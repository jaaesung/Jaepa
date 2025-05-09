"""
뉴스 API 라우터

뉴스 조회, 검색, 감성 분석 등 뉴스 관련 API 엔드포인트를 제공합니다.
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, Path, Request

from api.responses import create_response, create_paginated_response, ResponseStatus
from api.exceptions import (
    ResourceNotFoundException, ExternalServiceException, ValidationException,
    ErrorCode
)
from api.dependencies import (
    get_current_user_with_permissions, get_pagination_params, get_date_range_params,
    get_sort_params, get_filter_params, get_request_id, get_finbert_sentiment_analyzer,
    get_stock_data_store
)

# 로깅 설정
logger = logging.getLogger(__name__)

# 라우터 설정
router = APIRouter(
    prefix="/news",
    tags=["뉴스"],
    responses={
        401: {"description": "인증되지 않음"},
        403: {"description": "권한 없음"},
        404: {"description": "찾을 수 없음"},
        422: {"description": "유효하지 않은 요청"},
        500: {"description": "서버 오류"}
    }
)


@router.get("/")
async def get_news(
    request: Request,
    pagination: Dict[str, int] = Depends(get_pagination_params),
    date_range: Dict[str, datetime] = Depends(get_date_range_params),
    sort: Dict[str, str] = Depends(get_sort_params),
    filters: Dict[str, Any] = Depends(get_filter_params),
    request_id: str = Depends(get_request_id),
    stock_data_store = Depends(get_stock_data_store)
):
    """
    뉴스 목록 조회
    
    필터링, 정렬, 페이지네이션을 지원하는 뉴스 목록을 조회합니다.
    """
    try:
        # 뉴스 조회 파라미터 설정
        params = {
            "skip": pagination["skip"],
            "limit": pagination["limit"],
            "start_date": date_range["start_date"],
            "end_date": date_range["end_date"],
            "sort_by": sort["sort_by"] or "published_date",
            "sort_order": sort["sort_order"]
        }
        
        # 필터 추가
        if "keyword" in filters:
            params["keyword"] = filters["keyword"]
        
        if "category" in filters:
            params["category"] = filters["category"]
        
        if "tags" in filters:
            params["tags"] = filters["tags"]
        
        # 뉴스 조회
        news_items, total = stock_data_store.get_news_with_count(**params)
        
        logger.info(
            f"뉴스 목록 조회: {len(news_items)}개 항목 반환 (총 {total}개 중) "
            f"(요청 ID: {request_id})"
        )
        
        # 응답 생성
        return create_paginated_response(
            items=news_items,
            total=total,
            page=pagination["page"],
            limit=pagination["limit"],
            message="뉴스 목록 조회 성공",
            meta_info={"request_id": request_id}
        )
    except Exception as e:
        logger.error(
            f"뉴스 목록 조회 오류: {str(e)} "
            f"(요청 ID: {request_id})"
        )
        raise


@router.get("/{news_id}")
async def get_news_by_id(
    news_id: str = Path(..., description="뉴스 ID"),
    request_id: str = Depends(get_request_id),
    stock_data_store = Depends(get_stock_data_store)
):
    """
    뉴스 상세 조회
    
    특정 뉴스의 상세 정보를 조회합니다.
    """
    try:
        # 뉴스 조회
        news = stock_data_store.get_news_by_id(news_id)
        
        # 뉴스가 없는 경우
        if not news:
            logger.warning(
                f"뉴스 상세 조회 실패: 뉴스 ID '{news_id}'를 찾을 수 없음 "
                f"(요청 ID: {request_id})"
            )
            raise ResourceNotFoundException(
                resource_type="News",
                resource_id=news_id
            )
        
        logger.info(
            f"뉴스 상세 조회: 뉴스 ID '{news_id}' 조회 성공 "
            f"(요청 ID: {request_id})"
        )
        
        # 응답 생성
        return create_response(
            data=news,
            message="뉴스 상세 조회 성공",
            meta_info={"request_id": request_id}
        )
    except ResourceNotFoundException:
        raise
    except Exception as e:
        logger.error(
            f"뉴스 상세 조회 오류: {str(e)} "
            f"(요청 ID: {request_id})"
        )
        raise


@router.get("/search")
async def search_news(
    query: str = Query(..., description="검색 쿼리"),
    symbol: Optional[str] = Query(None, description="주식 심볼"),
    pagination: Dict[str, int] = Depends(get_pagination_params),
    date_range: Dict[str, datetime] = Depends(get_date_range_params),
    request_id: str = Depends(get_request_id),
    stock_data_store = Depends(get_stock_data_store)
):
    """
    뉴스 검색
    
    키워드로 뉴스를 검색합니다.
    """
    try:
        # 검색 파라미터 설정
        params = {
            "keyword": query,
            "skip": pagination["skip"],
            "limit": pagination["limit"],
            "start_date": date_range["start_date"],
            "end_date": date_range["end_date"]
        }
        
        # 심볼 추가
        if symbol:
            params["symbol"] = symbol
        
        # 뉴스 검색
        news_items, total = stock_data_store.search_news_with_count(**params)
        
        logger.info(
            f"뉴스 검색: 쿼리 '{query}'로 {len(news_items)}개 항목 반환 (총 {total}개 중) "
            f"(요청 ID: {request_id})"
        )
        
        # 응답 생성
        return create_paginated_response(
            items=news_items,
            total=total,
            page=pagination["page"],
            limit=pagination["limit"],
            message="뉴스 검색 성공",
            meta_info={"request_id": request_id}
        )
    except Exception as e:
        logger.error(
            f"뉴스 검색 오류: {str(e)} "
            f"(요청 ID: {request_id})"
        )
        raise


@router.get("/symbol/{symbol}")
async def get_news_by_symbol(
    symbol: str = Path(..., description="주식 심볼"),
    pagination: Dict[str, int] = Depends(get_pagination_params),
    date_range: Dict[str, datetime] = Depends(get_date_range_params),
    request_id: str = Depends(get_request_id),
    stock_data_store = Depends(get_stock_data_store)
):
    """
    심볼별 뉴스 조회
    
    특정 주식 심볼에 관련된 뉴스를 조회합니다.
    """
    try:
        # 뉴스 조회 파라미터 설정
        params = {
            "symbol": symbol,
            "skip": pagination["skip"],
            "limit": pagination["limit"],
            "start_date": date_range["start_date"],
            "end_date": date_range["end_date"]
        }
        
        # 뉴스 조회
        news_items = stock_data_store.get_stock_news(**params)
        
        # 총 개수 계산 (실제로는 별도의 카운트 쿼리가 필요할 수 있음)
        total = len(news_items)
        
        logger.info(
            f"심볼별 뉴스 조회: 심볼 '{symbol}'로 {len(news_items)}개 항목 반환 "
            f"(요청 ID: {request_id})"
        )
        
        # 응답 생성
        return create_paginated_response(
            items=news_items,
            total=total,
            page=pagination["page"],
            limit=pagination["limit"],
            message=f"{symbol} 관련 뉴스 조회 성공",
            meta_info={"request_id": request_id}
        )
    except Exception as e:
        logger.error(
            f"심볼별 뉴스 조회 오류: {str(e)} "
            f"(요청 ID: {request_id})"
        )
        raise


@router.get("/{news_id}/sentiment")
async def get_news_sentiment(
    news_id: str = Path(..., description="뉴스 ID"),
    request_id: str = Depends(get_request_id),
    stock_data_store = Depends(get_stock_data_store),
    finbert = Depends(get_finbert_sentiment_analyzer)
):
    """
    뉴스 감성 분석
    
    특정 뉴스의 감성 분석 결과를 조회합니다.
    """
    try:
        # 뉴스 조회
        news = stock_data_store.get_news_by_id(news_id)
        
        # 뉴스가 없는 경우
        if not news:
            logger.warning(
                f"뉴스 감성 분석 실패: 뉴스 ID '{news_id}'를 찾을 수 없음 "
                f"(요청 ID: {request_id})"
            )
            raise ResourceNotFoundException(
                resource_type="News",
                resource_id=news_id
            )
        
        # 이미 감성 분석 결과가 있는 경우
        if "sentiment" in news:
            logger.info(
                f"뉴스 감성 분석: 뉴스 ID '{news_id}'의 기존 감성 분석 결과 반환 "
                f"(요청 ID: {request_id})"
            )
            return create_response(
                data=news["sentiment"],
                message="뉴스 감성 분석 성공",
                meta_info={"request_id": request_id}
            )
        
        # 감성 분석 수행
        analyzed_news = finbert.analyze_news({
            "title": news.get("title", ""),
            "content": news.get("description", ""),
            "url": news.get("article_url", ""),
            "published_date": news.get("published_utc", "")
        })
        
        # 감성 분석 결과 저장
        sentiment = analyzed_news["sentiment"]
        stock_data_store.update_news_sentiment(news_id, sentiment)
        
        logger.info(
            f"뉴스 감성 분석: 뉴스 ID '{news_id}'의 감성 분석 완료 (감성: {sentiment['label']}) "
            f"(요청 ID: {request_id})"
        )
        
        # 응답 생성
        return create_response(
            data=sentiment,
            message="뉴스 감성 분석 성공",
            meta_info={"request_id": request_id}
        )
    except ResourceNotFoundException:
        raise
    except Exception as e:
        logger.error(
            f"뉴스 감성 분석 오류: {str(e)} "
            f"(요청 ID: {request_id})"
        )
        raise
