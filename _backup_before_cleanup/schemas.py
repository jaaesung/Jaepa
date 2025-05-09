from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 사용자 기본 스키마
class UserBase(BaseModel):
    email: str
    username: str

# 사용자 생성 스키마
class UserCreate(UserBase):
    password: str

# 토큰 스키마
class Token(BaseModel):
    access_token: str
    token_type: str

# 토큰 데이터 스키마
class TokenData(BaseModel):
    username: Optional[str] = None

# 사용자 응답 스키마
class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 로그인 스키마
class Login(BaseModel):
    username: str
    password: str
