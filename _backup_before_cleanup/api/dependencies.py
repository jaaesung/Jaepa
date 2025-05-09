"""
API 의존성 모듈

API 엔드포인트에서 사용할 의존성 함수를 제공합니다.
"""
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta

from fastapi import Depends, Request, Query, Path, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from database import get_db
import models
import schemas
from api.exceptions import (
    AuthenticationException, PermissionDeniedException, ResourceNotFoundException,
    ErrorCode
)
from auth import get_current_active_user

# 로깅 설정
logger = logging.getLogger(__name__)

# OAuth2 스키마 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


async def get_current_user_with_permissions(
    request: Request,
    token: str = Depends(oauth2_scheme),
    required_permissions: Optional[List[str]] = None,
    db: Session = Depends(get_db)
) -> models.User:
    """
    현재 사용자 가져오기 (권한 확인)
    
    Args:
        request: HTTP 요청
        token: 액세스 토큰
        required_permissions: 필요한 권한 목록
        db: 데이터베이스 세션
        
    Returns:
        models.User: 현재 사용자
        
    Raises:
        AuthenticationException: 인증 실패 시
        PermissionDeniedException: 권한 부족 시
    """
    # 현재 사용자 가져오기
    current_user = await get_current_active_user(token, db)
    
    # 권한 확인
    if required_permissions:
        # 사용자 권한 가져오기 (예시)
        user_permissions = []  # 실제로는 사용자 권한을 가져오는 로직 필요
        
        # 필요한 모든 권한이 있는지 확인
        if not all(perm in user_permissions for perm in required_permissions):
            logger.warning(
                f"Permission denied for user {current_user.username}: "
                f"Required {required_permissions}, has {user_permissions}"
            )
            raise PermissionDeniedException(
                message="이 작업을 수행할 권한이 없습니다.",
                details={
                    "required_permissions": required_permissions,
                    "user_permissions": user_permissions
                }
            )
    
    return current_user


def get_pagination_params(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수")
) -> Dict[str, int]:
    """
    페이지네이션 파라미터 가져오기
    
    Args:
        page: 페이지 번호
        limit: 페이지당 항목 수
        
    Returns:
        Dict[str, int]: 페이지네이션 파라미터
    """
    return {"page": page, "limit": limit, "skip": (page - 1) * limit}


def get_date_range_params(
    start_date: Optional[datetime] = Query(None, description="시작 날짜 (ISO 형식)"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜 (ISO 형식)"),
    days: Optional[int] = Query(None, ge=1, le=365, description="최근 일수")
) -> Dict[str, datetime]:
    """
    날짜 범위 파라미터 가져오기
    
    Args:
        start_date: 시작 날짜
        end_date: 종료 날짜
        days: 최근 일수
        
    Returns:
        Dict[str, datetime]: 날짜 범위 파라미터
    """
    # 종료 날짜 기본값: 현재 시간
    if end_date is None:
        end_date = datetime.utcnow()
    
    # 시작 날짜 계산
    if start_date is None and days is not None:
        start_date = end_date - timedelta(days=days)
    elif start_date is None:
        # 기본값: 30일 전
        start_date = end_date - timedelta(days=30)
    
    return {"start_date": start_date, "end_date": end_date}


def get_sort_params(
    sort_by: Optional[str] = Query(None, description="정렬 기준 필드"),
    sort_order: Optional[str] = Query("desc", description="정렬 순서 (asc 또는 desc)")
) -> Dict[str, str]:
    """
    정렬 파라미터 가져오기
    
    Args:
        sort_by: 정렬 기준 필드
        sort_order: 정렬 순서
        
    Returns:
        Dict[str, str]: 정렬 파라미터
    """
    # 정렬 순서 검증
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"
    
    return {"sort_by": sort_by, "sort_order": sort_order}


def get_filter_params(
    keyword: Optional[str] = Query(None, description="검색 키워드"),
    category: Optional[str] = Query(None, description="카테고리"),
    status: Optional[str] = Query(None, description="상태"),
    tags: Optional[List[str]] = Query(None, description="태그 목록")
) -> Dict[str, Any]:
    """
    필터 파라미터 가져오기
    
    Args:
        keyword: 검색 키워드
        category: 카테고리
        status: 상태
        tags: 태그 목록
        
    Returns:
        Dict[str, Any]: 필터 파라미터
    """
    filters = {}
    
    if keyword:
        filters["keyword"] = keyword
    
    if category:
        filters["category"] = category
    
    if status:
        filters["status"] = status
    
    if tags:
        filters["tags"] = tags
    
    return filters


def get_request_id(
    request: Request,
    x_request_id: Optional[str] = Header(None, description="요청 ID")
) -> str:
    """
    요청 ID 가져오기
    
    Args:
        request: HTTP 요청
        x_request_id: X-Request-ID 헤더
        
    Returns:
        str: 요청 ID
    """
    # 헤더에서 요청 ID 가져오기
    if x_request_id:
        return x_request_id
    
    # 요청 상태에서 요청 ID 가져오기
    if hasattr(request.state, "request_id"):
        return request.state.request_id
    
    # 기본값: 없음
    return "unknown"


def get_finbert_sentiment_analyzer():
    """
    FinBERT 감성 분석기 가져오기
    
    Returns:
        FinBERTSentiment: FinBERT 감성 분석기
    """
    from analysis.finbert_sentiment import FinBERTSentiment
    
    try:
        # 감성 분석기 생성
        analyzer = FinBERTSentiment()
        return analyzer
    except Exception as e:
        logger.error(f"FinBERT 감성 분석기 초기화 실패: {str(e)}")
        raise


def get_stock_data_store():
    """
    주식 데이터 저장소 가져오기
    
    Returns:
        StockDataStore: 주식 데이터 저장소
    """
    from data.stock_data_store import StockDataStore
    
    try:
        # 주식 데이터 저장소 생성
        store = StockDataStore()
        return store
    except Exception as e:
        logger.error(f"주식 데이터 저장소 초기화 실패: {str(e)}")
        raise


def get_sentiment_price_analyzer():
    """
    감성-가격 분석기 가져오기
    
    Returns:
        SentimentPriceAnalyzer: 감성-가격 분석기
    """
    from analysis.sentiment_price_analyzer import SentimentPriceAnalyzer
    
    try:
        # 감성-가격 분석기 생성
        analyzer = SentimentPriceAnalyzer()
        return analyzer
    except Exception as e:
        logger.error(f"감성-가격 분석기 초기화 실패: {str(e)}")
        raise
