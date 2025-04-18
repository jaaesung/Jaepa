"""
인증 API 엔드포인트 모듈

사용자 등록, 로그인, 토큰 갱신 등 인증 관련 API를 제공합니다.
"""
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from pymongo import MongoClient

from ..auth.jwt_handler import JWTHandler
from ..auth.auth_middleware import require_auth_fastapi
from ..models.user import User


# 요청/응답 모델 정의
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[Dict[str, Any]] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]


# 라우터 설정
router = APIRouter(prefix="/auth", tags=["인증"])


# 전역 MongoDB 연결 (실제 구현에서는 의존성 주입으로 처리)
def get_db():
    """
    MongoDB 연결 가져오기
    """
    client = MongoClient('mongodb://localhost:27017')
    db = client.jaepa
    try:
        yield db
    finally:
        client.close()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db = Depends(get_db)):
    """
    새 사용자 등록
    """
    user_model = User(db)

    # 사용자 생성
    user = user_model.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 사용자 이름 또는 이메일입니다"
        )

    # 사용자 ID를 문자열로 변환
    user["id"] = str(user["_id"])
    del user["_id"]
    del user["password_hash"]

    return user


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db = Depends(get_db)):
    """
    사용자 로그인 및 토큰 발급
    """
    user_model = User(db)

    # 이메일로 사용자 찾기
    user = user_model.find_by_email(login_data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="등록되지 않은 이메일입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 비밀번호 확인
    if not user_model.verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 비밀번호입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 사용자 ID
    user_id = str(user["_id"])

    # 토큰 생성
    access_token = JWTHandler.create_access_token(
        user_id,
        {"role": user["role"], "username": user["username"], "email": user["email"]}
    )
    refresh_token = JWTHandler.create_refresh_token(user_id)

    # 사용자 정보 준비
    user_info = {
        "id": user_id,
        "username": user["username"],
        "email": user["email"],
        "role": user["role"]
    }

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_info
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: RefreshTokenRequest):
    """
    리프레시 토큰으로 새 액세스 토큰 발급
    """
    # 리프레시 토큰 검증
    payload = JWTHandler.verify_refresh_token(token_data.refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 사용자 ID
    user_id = payload.get("sub")

    # 새 액세스 토큰 생성
    access_token = JWTHandler.create_access_token(user_id)

    return {
        "access_token": access_token,
        "refresh_token": token_data.refresh_token,  # 리프레시 토큰은 재사용
        "token_type": "bearer"
    }


@router.get("/me", response_model=Dict[str, Any])
async def get_current_user(user: Dict[str, Any] = Depends(require_auth_fastapi())):
    """
    현재 로그인한 사용자 정보 조회
    """
    return user


@router.post("/logout")
async def logout(user: Dict[str, Any] = Depends(require_auth_fastapi())):
    """
    로그아웃 (클라이언트 측에서 토큰 폐기)

    서버 측에서는 특별한 처리가 필요 없으며, 클라이언트가 토큰을 삭제합니다.
    필요에 따라 토큰 블랙리스트를 구현할 수 있습니다.
    """
    return {"message": "로그아웃 성공"}
