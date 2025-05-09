"""
사용자 모델 모듈

사용자 정보를 관리하는 모델입니다.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from bson import ObjectId
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash


class User:
    """
    사용자 모델 클래스

    사용자 정보와 인증을 관리합니다.
    """

    def __init__(self, db):
        """
        User 클래스 초기화

        Args:
            db: MongoDB 데이터베이스 연결
        """
        self.db = db
        self.collection = db.users

        # 인덱스 생성
        self.collection.create_index("username", unique=True)
        self.collection.create_index("email", unique=True)

    def create_user(self, username: str, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        새 사용자 생성

        Args:
            username: 사용자 이름
            email: 이메일 주소
            password: 비밀번호

        Returns:
            Optional[Dict[str, Any]]: 생성된 사용자 정보 또는 None (실패 시)
        """
        # 이미 존재하는 사용자인지 확인
        if self.collection.find_one({"username": username}):
            return None

        if self.collection.find_one({"email": email}):
            return None

        # 비밀번호 해시화
        password_hash = generate_password_hash(password)

        user_data = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.now(),
            "last_login": None,
            "role": "user",  # 기본 역할: user
            "is_active": True,
            "preferences": {}
        }

        try:
            result = self.collection.insert_one(user_data)
            user_data["_id"] = result.inserted_id
            return user_data
        except Exception as e:
            print(f"사용자 생성 중 오류: {str(e)}")
            return None

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        사용자 인증

        Args:
            username: 사용자 이름
            password: 비밀번호

        Returns:
            Optional[Dict[str, Any]]: 인증된 사용자 정보 또는 None (실패 시)
        """
        user = self.collection.find_one({"username": username})

        if not user:
            return None

        # 비밀번호 확인
        if not check_password_hash(user["password_hash"], password):
            return None

        # 마지막 로그인 시간 업데이트
        self.collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.now()}}
        )

        return user

    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        이메일로 사용자 찾기

        Args:
            email: 이메일 주소

        Returns:
            Optional[Dict[str, Any]]: 사용자 정보 또는 None (존재하지 않는 경우)
        """
        return self.collection.find_one({"email": email})

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        비밀번호 확인

        Args:
            password: 입력된 비밀번호
            password_hash: 저장된 비밀번호 해시

        Returns:
            bool: 비밀번호 일치 여부
        """
        return check_password_hash(password_hash, password)

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        ID로 사용자 조회

        Args:
            user_id: 사용자 ID

        Returns:
            Optional[Dict[str, Any]]: 사용자 정보 또는 None (존재하지 않는 경우)
        """
        try:
            return self.collection.find_one({"_id": ObjectId(user_id)})
        except:
            return None

    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """
        사용자 정보 업데이트

        Args:
            user_id: 사용자 ID
            update_data: 업데이트할 데이터

        Returns:
            bool: 업데이트 성공 여부
        """
        # 보안상 중요한 필드는 업데이트에서 제외
        if "password_hash" in update_data:
            del update_data["password_hash"]
        if "_id" in update_data:
            del update_data["_id"]

        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"사용자 업데이트 중 오류: {str(e)}")
            return False

    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        사용자 비밀번호 변경

        Args:
            user_id: 사용자 ID
            current_password: 현재 비밀번호
            new_password: 새 비밀번호

        Returns:
            bool: 비밀번호 변경 성공 여부
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        # 현재 비밀번호 확인
        if not check_password_hash(user["password_hash"], current_password):
            return False

        # 새 비밀번호 해시화
        password_hash = generate_password_hash(new_password)

        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"password_hash": password_hash}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"비밀번호 변경 중 오류: {str(e)}")
            return False

    def delete_user(self, user_id: str) -> bool:
        """
        사용자 삭제

        Args:
            user_id: 사용자 ID

        Returns:
            bool: 삭제 성공 여부
        """
        try:
            result = self.collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"사용자 삭제 중 오류: {str(e)}")
            return False
