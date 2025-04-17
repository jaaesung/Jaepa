"""
사용자 도메인 모델 모듈

사용자 관련 도메인 모델을 제공합니다.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime


@dataclass
class User:
    """
    사용자 모델
    
    사용자 정보를 나타냅니다.
    """
    
    username: str
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    roles: List[str] = field(default_factory=list)
    permissions: Set[str] = field(default_factory=set)
    id: Optional[str] = None
    
    def __post_init__(self):
        """
        초기화 후처리
        """
        # 문자열 날짜를 datetime으로 변환
        for date_field in ['created_at', 'updated_at', 'last_login']:
            value = getattr(self, date_field)
            if isinstance(value, str):
                try:
                    # ISO 형식 (예: "2023-01-01T12:00:00Z")
                    setattr(self, date_field, datetime.fromisoformat(value.replace('Z', '+00:00')))
                except (ValueError, TypeError):
                    # None 유지
                    pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        딕셔너리로 변환
        
        Returns:
            Dict[str, Any]: 딕셔너리 표현
        """
        result = {
            "username": self.username,
            "email": self.email,
            "hashed_password": self.hashed_password,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
            "preferences": self.preferences,
            "roles": self.roles,
            "permissions": list(self.permissions)
        }
        
        # 선택적 필드 추가
        if self.full_name:
            result["full_name"] = self.full_name
            
        if self.updated_at:
            result["updated_at"] = self.updated_at.isoformat()
            
        if self.last_login:
            result["last_login"] = self.last_login.isoformat()
            
        if self.id:
            result["id"] = self.id
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        딕셔너리에서 생성
        
        Args:
            data: 딕셔너리 데이터
            
        Returns:
            User: 생성된 사용자 객체
        """
        # 필수 필드 확인
        required_fields = ["username", "email", "hashed_password"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"필수 필드 누락: {field}")
        
        # ID 처리
        id_value = data.get("id") or data.get("_id")
        
        # 권한 처리
        permissions = data.get("permissions", [])
        if isinstance(permissions, list):
            permissions = set(permissions)
        
        # 객체 생성
        return cls(
            username=data["username"],
            email=data["email"],
            hashed_password=data["hashed_password"],
            full_name=data.get("full_name"),
            is_active=data.get("is_active", True),
            is_admin=data.get("is_admin", False),
            created_at=data.get("created_at", datetime.now()),
            updated_at=data.get("updated_at"),
            last_login=data.get("last_login"),
            preferences=data.get("preferences", {}),
            roles=data.get("roles", []),
            permissions=permissions,
            id=id_value
        )
    
    def has_permission(self, permission: str) -> bool:
        """
        권한 확인
        
        Args:
            permission: 확인할 권한
            
        Returns:
            bool: 권한 보유 여부
        """
        # 관리자는 모든 권한 보유
        if self.is_admin:
            return True
        
        # 권한 확인
        return permission in self.permissions
    
    def has_role(self, role: str) -> bool:
        """
        역할 확인
        
        Args:
            role: 확인할 역할
            
        Returns:
            bool: 역할 보유 여부
        """
        # 관리자는 모든 역할 보유
        if self.is_admin:
            return True
        
        # 역할 확인
        return role in self.roles
