"""
사용자 저장소 모듈

사용자 데이터 저장소를 제공합니다.
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from bson import ObjectId

from infrastructure.database.database_client import DatabaseClientInterface
from infrastructure.repository.repository import BaseMongoRepository
from domain.models.user import User

# 로깅 설정
logger = logging.getLogger(__name__)


class UserRepository(BaseMongoRepository[User, str]):
    """
    사용자 저장소
    
    사용자 데이터 저장소를 구현합니다.
    """
    
    def __init__(self, client: DatabaseClientInterface, db_name: str, collection_name: str = "users"):
        """
        UserRepository 초기화
        
        Args:
            client: 데이터베이스 클라이언트
            db_name: 데이터베이스 이름
            collection_name: 컬렉션 이름
        """
        super().__init__(client, db_name, collection_name)
    
    def _define_indexes(self) -> List[Dict[str, Any]]:
        """
        인덱스 정의
        
        Returns:
            List[Dict[str, Any]]: 인덱스 정의 목록
        """
        return [
            # 사용자명 고유 인덱스
            {
                "keys": [("username", 1)],
                "name": "username_unique_idx",
                "unique": True
            },
            # 이메일 고유 인덱스
            {
                "keys": [("email", 1)],
                "name": "email_unique_idx",
                "unique": True
            },
            # 역할 인덱스
            {
                "keys": [("roles", 1)],
                "name": "roles_idx"
            },
            # 생성일 인덱스
            {
                "keys": [("created_at", -1)],
                "name": "created_at_idx"
            }
        ]
    
    def _convert_id(self, id: str) -> Any:
        """
        ID 변환
        
        Args:
            id: 엔티티 ID
            
        Returns:
            Any: 변환된 ID
        """
        try:
            return ObjectId(id)
        except Exception:
            return id
    
    def _to_entity(self, document: Dict[str, Any]) -> User:
        """
        문서를 엔티티로 변환
        
        Args:
            document: MongoDB 문서
            
        Returns:
            User: 변환된 사용자 엔티티
        """
        # ID 변환
        if "_id" in document:
            document["id"] = str(document["_id"])
            del document["_id"]
        
        # 엔티티 생성
        return User.from_dict(document)
    
    def _to_document(self, entity: User) -> Dict[str, Any]:
        """
        엔티티를 문서로 변환
        
        Args:
            entity: 사용자 엔티티
            
        Returns:
            Dict[str, Any]: 변환된 문서
        """
        # 딕셔너리 변환
        document = entity.to_dict()
        
        # ID 처리
        if "id" in document:
            try:
                document["_id"] = ObjectId(document["id"])
            except Exception:
                document["_id"] = document["id"]
            del document["id"]
        
        # 권한 처리
        if "permissions" in document and isinstance(document["permissions"], set):
            document["permissions"] = list(document["permissions"])
        
        return document
    
    async def find_by_username(self, username: str) -> Optional[User]:
        """
        사용자명으로 사용자 조회
        
        Args:
            username: 사용자명
            
        Returns:
            Optional[User]: 조회된 사용자 또는 None
        """
        return await self.find_one_by_query({"username": username})
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """
        이메일로 사용자 조회
        
        Args:
            email: 이메일
            
        Returns:
            Optional[User]: 조회된 사용자 또는 None
        """
        return await self.find_one_by_query({"email": email})
    
    async def find_by_role(self, role: str, limit: int = 20, skip: int = 0) -> List[User]:
        """
        역할로 사용자 조회
        
        Args:
            role: 역할
            limit: 최대 개수
            skip: 건너뛸 개수
            
        Returns:
            List[User]: 조회된 사용자 목록
        """
        return await self.find_by_query(
            {"roles": role},
            skip=skip,
            limit=limit
        )
    
    async def update_last_login(self, user_id: str) -> bool:
        """
        마지막 로그인 시간 업데이트
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            # ID 변환
            object_id = self._convert_id(user_id)
            
            # 업데이트
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$set": {"last_login": datetime.now(), "updated_at": datetime.now()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"마지막 로그인 시간 업데이트 실패: {str(e)}")
            return False
    
    async def update_password(self, user_id: str, hashed_password: str) -> bool:
        """
        비밀번호 업데이트
        
        Args:
            user_id: 사용자 ID
            hashed_password: 해시된 비밀번호
            
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            # ID 변환
            object_id = self._convert_id(user_id)
            
            # 업데이트
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$set": {"hashed_password": hashed_password, "updated_at": datetime.now()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"비밀번호 업데이트 실패: {str(e)}")
            return False
    
    async def update_roles(self, user_id: str, roles: List[str]) -> bool:
        """
        역할 업데이트
        
        Args:
            user_id: 사용자 ID
            roles: 역할 목록
            
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            # ID 변환
            object_id = self._convert_id(user_id)
            
            # 업데이트
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$set": {"roles": roles, "updated_at": datetime.now()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"역할 업데이트 실패: {str(e)}")
            return False
    
    async def update_permissions(self, user_id: str, permissions: List[str]) -> bool:
        """
        권한 업데이트
        
        Args:
            user_id: 사용자 ID
            permissions: 권한 목록
            
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            # ID 변환
            object_id = self._convert_id(user_id)
            
            # 업데이트
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$set": {"permissions": permissions, "updated_at": datetime.now()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"권한 업데이트 실패: {str(e)}")
            return False
    
    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        환경설정 업데이트
        
        Args:
            user_id: 사용자 ID
            preferences: 환경설정
            
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            # ID 변환
            object_id = self._convert_id(user_id)
            
            # 업데이트
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$set": {"preferences": preferences, "updated_at": datetime.now()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"환경설정 업데이트 실패: {str(e)}")
            return False
    
    async def deactivate(self, user_id: str) -> bool:
        """
        사용자 비활성화
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            bool: 비활성화 성공 여부
        """
        try:
            # ID 변환
            object_id = self._convert_id(user_id)
            
            # 업데이트
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$set": {"is_active": False, "updated_at": datetime.now()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"사용자 비활성화 실패: {str(e)}")
            return False
    
    async def activate(self, user_id: str) -> bool:
        """
        사용자 활성화
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            bool: 활성화 성공 여부
        """
        try:
            # ID 변환
            object_id = self._convert_id(user_id)
            
            # 업데이트
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$set": {"is_active": True, "updated_at": datetime.now()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"사용자 활성화 실패: {str(e)}")
            return False
