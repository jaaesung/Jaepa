"""
인증 API 라우터

사용자 등록, 로그인, 토큰 갱신 등 인증 관련 API 엔드포인트를 제공합니다.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models
import schemas
import crud
from database import get_db
from auth import authenticate_user, create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
from api.responses import create_response, ResponseStatus
from api.exceptions import (
    AuthenticationException, ValidationException, ResourceNotFoundException,
    ResourceAlreadyExistsException, ErrorCode
)
from api.dependencies import get_request_id

# 로깅 설정
logger = logging.getLogger(__name__)

# 라우터 설정
router = APIRouter(
    prefix="/auth",
    tags=["인증"],
    responses={
        401: {"description": "인증되지 않음"},
        403: {"description": "권한 없음"},
        404: {"description": "찾을 수 없음"},
        422: {"description": "유효하지 않은 요청"},
        500: {"description": "서버 오류"}
    }
)


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id)
):
    """
    액세스 토큰 발급
    
    사용자 인증 후 액세스 토큰을 발급합니다.
    """
    # 사용자 인증
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(
            f"로그인 실패: 사용자 '{form_data.username}'의 인증 실패 "
            f"(요청 ID: {request_id})"
        )
        raise AuthenticationException(
            message="잘못된 사용자 이름 또는 비밀번호입니다.",
            error_code=ErrorCode.INVALID_CREDENTIALS
        )
    
    # 액세스 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    logger.info(
        f"로그인 성공: 사용자 '{user.username}'에게 토큰 발급 "
        f"(요청 ID: {request_id})"
    )
    
    # 응답 생성
    return create_response(
        data={"access_token": access_token, "token_type": "bearer"},
        message="로그인 성공",
        meta_info={"request_id": request_id}
    )


@router.post("/register", response_model=schemas.User)
async def register_user(
    request: Request,
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id)
):
    """
    사용자 등록
    
    새 사용자를 등록합니다.
    """
    # 사용자 이름 중복 확인
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        logger.warning(
            f"사용자 등록 실패: 사용자 이름 '{user.username}'이 이미 존재함 "
            f"(요청 ID: {request_id})"
        )
        raise ResourceAlreadyExistsException(
            resource_type="User",
            identifier={"username": user.username},
            message="이미 사용 중인 사용자 이름입니다."
        )
    
    # 이메일 중복 확인
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        logger.warning(
            f"사용자 등록 실패: 이메일 '{user.email}'이 이미 존재함 "
            f"(요청 ID: {request_id})"
        )
        raise ResourceAlreadyExistsException(
            resource_type="User",
            identifier={"email": user.email},
            message="이미 사용 중인 이메일입니다."
        )
    
    try:
        # 사용자 생성
        new_user = crud.create_user(db=db, user=user)
        
        logger.info(
            f"사용자 등록 성공: 사용자 '{new_user.username}' 생성됨 "
            f"(요청 ID: {request_id})"
        )
        
        # 응답 생성
        return create_response(
            data=new_user,
            message="사용자 등록 성공",
            meta_info={"request_id": request_id}
        )
    except Exception as e:
        logger.error(
            f"사용자 등록 오류: {str(e)} "
            f"(요청 ID: {request_id})"
        )
        raise


@router.get("/me", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(get_current_active_user),
    request_id: str = Depends(get_request_id)
):
    """
    현재 사용자 정보 조회
    
    현재 인증된 사용자의 정보를 조회합니다.
    """
    logger.info(
        f"사용자 정보 조회: 사용자 '{current_user.username}'의 정보 요청 "
        f"(요청 ID: {request_id})"
    )
    
    # 응답 생성
    return create_response(
        data=current_user,
        message="사용자 정보 조회 성공",
        meta_info={"request_id": request_id}
    )


@router.post("/logout")
async def logout(
    response: Response,
    current_user: models.User = Depends(get_current_active_user),
    request_id: str = Depends(get_request_id)
):
    """
    로그아웃
    
    현재 사용자를 로그아웃합니다.
    """
    logger.info(
        f"로그아웃: 사용자 '{current_user.username}' 로그아웃 "
        f"(요청 ID: {request_id})"
    )
    
    # 쿠키 삭제 (클라이언트에서 토큰을 쿠키로 저장하는 경우)
    response.delete_cookie(key="access_token")
    
    # 응답 생성
    return create_response(
        message="로그아웃 성공",
        meta_info={"request_id": request_id}
    )
