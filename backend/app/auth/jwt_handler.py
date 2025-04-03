"""
JWT 토큰 관리 모듈

JWT 토큰 생성, 검증 및 관리 기능을 제공합니다.
"""
import os
import jwt
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 환경 변수에서 시크릿 키 가져오기
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-for-jwt')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7'))


class JWTHandler:
    """
    JWT 토큰 관리 클래스
    
    JWT 토큰 생성, 검증, 갱신 등의 기능을 제공합니다.
    """
    
    @staticmethod
    def create_access_token(user_id: str, additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        액세스 토큰 생성
        
        Args:
            user_id: 사용자 ID
            additional_data: 토큰에 포함할 추가 데이터
            
        Returns:
            str: 생성된 JWT 액세스 토큰
        """
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # 기본 페이로드 설정
        payload = {
            "sub": str(user_id),  # subject (사용자 ID)
            "exp": expire.timestamp(),  # 만료 시간
            "iat": datetime.utcnow().timestamp(),  # 발급 시간
            "type": "access"  # 토큰 유형
        }
        
        # 추가 데이터 병합
        if additional_data:
            payload.update(additional_data)
            
        # 토큰 생성
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """
        리프레시 토큰 생성
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            str: 생성된 JWT 리프레시 토큰
        """
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "sub": str(user_id),
            "exp": expire.timestamp(),
            "iat": datetime.utcnow().timestamp(),
            "type": "refresh"
        }
            
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        토큰 디코딩 및 검증
        
        Args:
            token: JWT 토큰
            
        Returns:
            Optional[Dict[str, Any]]: 디코딩된 토큰 페이로드 또는 None (유효하지 않은 경우)
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            # 토큰 만료
            return None
        except jwt.InvalidTokenError:
            # 유효하지 않은 토큰
            return None
    
    @staticmethod
    def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
        """
        액세스 토큰 검증
        
        Args:
            token: JWT 액세스 토큰
            
        Returns:
            Optional[Dict[str, Any]]: 디코딩된 토큰 페이로드 또는 None (유효하지 않은 경우)
        """
        payload = JWTHandler.decode_token(token)
        
        if not payload:
            return None
            
        # 액세스 토큰 타입 확인
        if payload.get("type") != "access":
            return None
            
        return payload
    
    @staticmethod
    def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
        """
        리프레시 토큰 검증
        
        Args:
            token: JWT 리프레시 토큰
            
        Returns:
            Optional[Dict[str, Any]]: 디코딩된 토큰 페이로드 또는 None (유효하지 않은 경우)
        """
        payload = JWTHandler.decode_token(token)
        
        if not payload:
            return None
            
        # 리프레시 토큰 타입 확인
        if payload.get("type") != "refresh":
            return None
            
        return payload
    
    @staticmethod
    def refresh_access_token(refresh_token: str, additional_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        리프레시 토큰을 사용하여 새 액세스 토큰 발급
        
        Args:
            refresh_token: JWT 리프레시 토큰
            additional_data: 새 토큰에 포함할 추가 데이터
            
        Returns:
            Optional[str]: 새로운 액세스 토큰 또는 None (리프레시 토큰이 유효하지 않은 경우)
        """
        payload = JWTHandler.verify_refresh_token(refresh_token)
        
        if not payload:
            return None
            
        user_id = payload.get("sub")
        if not user_id:
            return None
            
        # 새 액세스 토큰 생성
        return JWTHandler.create_access_token(user_id, additional_data)
