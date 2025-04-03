"""
사용자 관리 API 엔드포인트 모듈

사용자 정보 조회, 수정, 삭제 등 사용자 관리 API를 제공합니다.
"""
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from pymongo import MongoClient

from ..auth.auth_middleware import require_auth_fastapi
from ..models.user import User


# 요청/응답 모델 정의
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str
    last_login: Optional[str] = None
    preferences: Dict[str, Any] = {}


# 라우터 설정
router = APIRouter(prefix="/users", tags=["사용자"])


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


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(require_auth_fastapi(roles=["admin"])),
    db = Depends(get_db)
):
    """
    사용자 목록 조회 (관리자 전용)
    """
    users = list(db.users.find().skip(skip).limit(limit))
    
    # ObjectId를 문자열로 변환하고 비밀번호 해시 제거
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
        del user["password_hash"]
        
        # 날짜 포맷팅
        user["created_at"] = user["created_at"].isoformat() if user["created_at"] else None
        user["last_login"] = user["last_login"].isoformat() if user["last_login"] else None
    
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_auth_fastapi()),
    db = Depends(get_db)
):
    """
    사용자 정보 조회
    
    자신의 정보 또는 관리자는 모든 사용자 정보 조회 가능
    """
    # 권한 검사: 관리자이거나 자신의 정보만 조회 가능
    if current_user.get("role") != "admin" and current_user.get("sub") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 정보를 조회할 권한이 없습니다"
        )
    
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 사용자 ID 형식입니다"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    # 응답 데이터 포맷팅
    user["id"] = str(user["_id"])
    del user["_id"]
    del user["password_hash"]
    
    # 날짜 포맷팅
    user["created_at"] = user["created_at"].isoformat() if user["created_at"] else None
    user["last_login"] = user["last_login"].isoformat() if user["last_login"] else None
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: Dict[str, Any] = Depends(require_auth_fastapi()),
    db = Depends(get_db)
):
    """
    사용자 정보 업데이트
    
    자신의 정보 또는 관리자는 모든 사용자 정보 업데이트 가능
    """
    # 권한 검사: 관리자이거나 자신의 정보만 업데이트 가능
    if current_user.get("role") != "admin" and current_user.get("sub") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 정보를 업데이트할 권한이 없습니다"
        )
    
    user_model = User(db)
    
    # 업데이트할 필드만 추출
    update_data = user_data.dict(exclude_unset=True)
    
    # 업데이트 수행
    success = user_model.update_user(user_id, update_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없거나 업데이트에 실패했습니다"
        )
    
    # 업데이트된 사용자 정보 조회
    updated_user = user_model.get_user_by_id(user_id)
    
    # 응답 데이터 포맷팅
    updated_user["id"] = str(updated_user["_id"])
    del updated_user["_id"]
    del updated_user["password_hash"]
    
    # 날짜 포맷팅
    updated_user["created_at"] = updated_user["created_at"].isoformat() if updated_user["created_at"] else None
    updated_user["last_login"] = updated_user["last_login"].isoformat() if updated_user["last_login"] else None
    
    return updated_user


@router.post("/{user_id}/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user_id: str,
    password_data: PasswordChange,
    current_user: Dict[str, Any] = Depends(require_auth_fastapi()),
    db = Depends(get_db)
):
    """
    사용자 비밀번호 변경
    
    자신의 비밀번호만 변경 가능
    """
    # 권한 검사: 자신의 비밀번호만 변경 가능
    if current_user.get("sub") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 비밀번호를 변경할 수 없습니다"
        )
    
    user_model = User(db)
    
    # 비밀번호 변경 수행
    success = user_model.change_password(
        user_id,
        password_data.current_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 일치하지 않거나 변경에 실패했습니다"
        )
    
    return None


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_auth_fastapi()),
    db = Depends(get_db)
):
    """
    사용자 삭제
    
    자신의 계정 또는 관리자는 모든 사용자 삭제 가능
    """
    # 권한 검사: 관리자이거나 자신의 계정만 삭제 가능
    if current_user.get("role") != "admin" and current_user.get("sub") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자를 삭제할 권한이 없습니다"
        )
    
    user_model = User(db)
    
    # 사용자 삭제 수행
    success = user_model.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없거나 삭제에 실패했습니다"
        )
    
    return None
