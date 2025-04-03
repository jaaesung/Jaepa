"""
인증 미들웨어 모듈

FastAPI/Flask 라우트에 인증을 적용하는 미들웨어를 제공합니다.
"""
import os
from functools import wraps
from typing import Dict, Optional, Callable, Any

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from flask import request, jsonify, g

from .jwt_handler import JWTHandler
from ..models.user import User


# FastAPI 인증 핸들러
security = HTTPBearer()


def get_current_user_fastapi(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    FastAPI 현재 사용자 가져오기 의존성
    
    Args:
        credentials: HTTP 인증 정보
        
    Returns:
        Dict[str, Any]: 현재 사용자 정보
        
    Raises:
        HTTPException: 인증 실패 시
    """
    token = credentials.credentials
    payload = JWTHandler.verify_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 정보",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # DB에서 사용자 조회 (DB 연결 필요)
    # user = User(db).get_user_by_id(payload.get("sub"))
    
    # 여기에서는 간단히 페이로드만 반환
    return payload


def require_auth_fastapi(roles: Optional[list] = None):
    """
    FastAPI 역할 기반 인증 의존성 생성
    
    Args:
        roles: 허용된 역할 목록 (None인 경우 모든 인증된 사용자 허용)
        
    Returns:
        Callable: 역할 확인 의존성 함수
    """
    def role_checker(user_data: Dict[str, Any] = Depends(get_current_user_fastapi)):
        if roles and user_data.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 부족합니다",
            )
        return user_data
    return role_checker


# Flask 인증 데코레이터
def require_auth_flask(f=None, roles=None):
    """
    Flask 라우트에 인증 적용 데코레이터
    
    Args:
        f: 래핑할 함수
        roles: 허용된 역할 목록 (None인 경우 모든 인증된 사용자 허용)
        
    Returns:
        Callable: 래핑된 함수
    """
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({"error": "인증 토큰이 필요합니다"}), 401
                
            token = auth_header.split(' ')[1]
            payload = JWTHandler.verify_access_token(token)
            
            if not payload:
                return jsonify({"error": "유효하지 않은 인증 토큰입니다"}), 401
                
            # 역할 확인
            if roles and payload.get("role") not in roles:
                return jsonify({"error": "권한이 부족합니다"}), 403
                
            # 현재 사용자 정보를 g 객체에 저장
            g.user = payload
            
            return func(*args, **kwargs)
        return decorated_function
        
    if f:
        return decorator(f)
    return decorator
