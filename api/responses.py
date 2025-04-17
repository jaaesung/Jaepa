"""
표준 API 응답 모듈

API 응답의 일관된 형식을 제공합니다.
"""
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field

T = TypeVar('T')


class ResponseStatus:
    """응답 상태 코드 상수"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ErrorDetail(BaseModel):
    """오류 상세 정보"""
    code: str = Field(..., description="오류 코드")
    message: str = Field(..., description="오류 메시지")
    field: Optional[str] = Field(None, description="오류가 발생한 필드 (해당되는 경우)")
    details: Optional[Dict[str, Any]] = Field(None, description="추가 오류 세부 정보")


class PaginationInfo(BaseModel):
    """페이지네이션 정보"""
    page: int = Field(..., description="현재 페이지 번호")
    limit: int = Field(..., description="페이지당 항목 수")
    total: int = Field(..., description="전체 항목 수")
    total_pages: int = Field(..., description="전체 페이지 수")
    has_next: bool = Field(..., description="다음 페이지 존재 여부")
    has_prev: bool = Field(..., description="이전 페이지 존재 여부")


class MetaInfo(BaseModel):
    """메타 정보"""
    timestamp: str = Field(..., description="응답 생성 시간 (ISO 형식)")
    request_id: Optional[str] = Field(None, description="요청 ID")
    version: str = Field("1.0", description="API 버전")
    pagination: Optional[PaginationInfo] = Field(None, description="페이지네이션 정보")
    processing_time: Optional[float] = Field(None, description="처리 시간 (밀리초)")


class ApiResponse(BaseModel, Generic[T]):
    """표준 API 응답"""
    status: str = Field(..., description="응답 상태 (success, error, warning, info)")
    message: str = Field(..., description="응답 메시지")
    data: Optional[T] = Field(None, description="응답 데이터")
    errors: Optional[List[ErrorDetail]] = Field(None, description="오류 목록")
    meta: MetaInfo = Field(..., description="메타 정보")


class PaginatedResponse(ApiResponse, Generic[T]):
    """페이지네이션된 API 응답"""
    data: List[T] = Field(..., description="응답 데이터 목록")


def create_response(
    data: Any = None,
    message: str = "요청이 성공적으로 처리되었습니다.",
    status: str = ResponseStatus.SUCCESS,
    errors: Optional[List[ErrorDetail]] = None,
    meta_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    표준 API 응답 생성
    
    Args:
        data: 응답 데이터
        message: 응답 메시지
        status: 응답 상태
        errors: 오류 목록
        meta_info: 메타 정보
        
    Returns:
        Dict[str, Any]: 표준 API 응답
    """
    from datetime import datetime
    import uuid
    
    # 기본 메타 정보
    meta = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": str(uuid.uuid4()),
        "version": "1.0"
    }
    
    # 추가 메타 정보 병합
    if meta_info:
        meta.update(meta_info)
    
    # 응답 생성
    response = {
        "status": status,
        "message": message,
        "meta": meta
    }
    
    # 데이터 추가
    if data is not None:
        response["data"] = data
    
    # 오류 추가
    if errors:
        response["errors"] = errors
    
    return response


def create_paginated_response(
    items: List[Any],
    total: int,
    page: int,
    limit: int,
    message: str = "요청이 성공적으로 처리되었습니다.",
    status: str = ResponseStatus.SUCCESS,
    meta_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    페이지네이션된 API 응답 생성
    
    Args:
        items: 항목 목록
        total: 전체 항목 수
        page: 현재 페이지 번호
        limit: 페이지당 항목 수
        message: 응답 메시지
        status: 응답 상태
        meta_info: 추가 메타 정보
        
    Returns:
        Dict[str, Any]: 페이지네이션된 API 응답
    """
    # 페이지네이션 정보 계산
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    has_next = page < total_pages
    has_prev = page > 1
    
    # 메타 정보에 페이지네이션 추가
    meta_info = meta_info or {}
    meta_info["pagination"] = {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev
    }
    
    # 응답 생성
    return create_response(
        data=items,
        message=message,
        status=status,
        meta_info=meta_info
    )


def create_error_response(
    message: str = "요청 처리 중 오류가 발생했습니다.",
    errors: Optional[List[ErrorDetail]] = None,
    status: str = ResponseStatus.ERROR,
    meta_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    오류 응답 생성
    
    Args:
        message: 오류 메시지
        errors: 오류 목록
        status: 응답 상태
        meta_info: 메타 정보
        
    Returns:
        Dict[str, Any]: 오류 응답
    """
    return create_response(
        message=message,
        status=status,
        errors=errors,
        meta_info=meta_info
    )
