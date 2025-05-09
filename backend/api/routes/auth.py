"""
인증 라우트 모듈

사용자 인증 관련 API 엔드포인트를 정의합니다.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional

# 컨트롤러 가져오기 (추후 구현)
# from ..controllers.auth_controller import AuthController

router = APIRouter()
# auth_controller = AuthController()

# 토큰 가져오기 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register")
async def register(username: str, email: str, password: str):
    """새 사용자 등록"""
    # return await auth_controller.register(username, email, password)
    return {"message": "사용자 등록 기능 구현 예정"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """사용자 로그인 및 토큰 발급"""
    # return await auth_controller.login(form_data.username, form_data.password)
    return {"access_token": "dummy_token", "token_type": "bearer"}

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """현재 로그인한 사용자 정보 조회"""
    # return await auth_controller.get_current_user(token)
    return {"username": "test_user", "email": "test@example.com"}

@router.post("/forgot-password")
async def forgot_password(email: str):
    """비밀번호 재설정 요청"""
    # return await auth_controller.forgot_password(email)
    return {"message": "비밀번호 재설정 이메일 발송 기능 구현 예정"}

@router.post("/reset-password")
async def reset_password(token: str, new_password: str):
    """비밀번호 재설정"""
    # return await auth_controller.reset_password(token, new_password)
    return {"message": "비밀번호 재설정 기능 구현 예정"}
