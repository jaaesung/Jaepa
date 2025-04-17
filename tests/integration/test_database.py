"""
데이터베이스 통합 테스트
"""
import pytest
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from pydantic import BaseModel

from infrastructure.database import (
    DatabaseFactory, BaseMongoRepository, AsyncBaseMongoRepository
)


class TestItem(BaseModel):
    """테스트 아이템 모델"""
    id: Optional[str] = None
    name: str
    value: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@pytest.mark.integration
@pytest.mark.skipif(not os.environ.get("MONGODB_TEST_URI"), reason="MongoDB 테스트 URI가 설정되지 않았습니다.")
class TestMongoDBIntegration:
    """MongoDB 통합 테스트"""
    
    def test_mongodb_client_connection(self, mongo_client):
        """MongoDB 클라이언트 연결 테스트"""
        # 클라이언트 생성
        client = DatabaseFactory.create_client(
            engine="mongodb",
            uri=os.environ.get("MONGODB_TEST_URI"),
            default_db_name=os.environ.get("MONGODB_TEST_DB", "jaepa_test")
        )
        
        # 연결
        client.connect()
        
        try:
            # 연결 확인
            assert client.is_connected() is True
            
            # 상태 확인
            health = client.health_check()
            assert health["status"] == "connected"
            assert "details" in health
        finally:
            # 연결 종료
            client.close()
    
    def test_mongodb_repository_crud(self, mongo_client):
        """MongoDB 저장소 CRUD 테스트"""
        # 클라이언트 생성
        client = DatabaseFactory.create_client(
            engine="mongodb",
            uri=os.environ.get("MONGODB_TEST_URI"),
            default_db_name=os.environ.get("MONGODB_TEST_DB", "jaepa_test")
        )
        
        # 연결
        client.connect()
        
        try:
            # 저장소 생성
            repo = BaseMongoRepository(
                client=client,
                collection_name="test_items",
                model_class=TestItem
            )
            
            # 컬렉션 초기화
            collection = repo._get_collection()
            collection.delete_many({})
            
            # 아이템 생성
            item = TestItem(name="Test Item", value=42)
            created_item = repo.create(item)
            
            # 생성된 아이템 확인
            assert created_item.id is not None
            assert created_item.name == "Test Item"
            assert created_item.value == 42
            assert created_item.created_at is not None
            assert created_item.updated_at is not None
            
            # ID로 아이템 조회
            found_item = repo.find_by_id(created_item.id)
            assert found_item is not None
            assert found_item.id == created_item.id
            assert found_item.name == created_item.name
            assert found_item.value == created_item.value
            
            # 필터로 아이템 조회
            found_items = repo.find_many({"name": "Test Item"})
            assert len(found_items) == 1
            assert found_items[0].id == created_item.id
            
            # 아이템 업데이트
            updated_item = TestItem(
                id=created_item.id,
                name="Updated Item",
                value=100
            )
            result = repo.update(created_item.id, updated_item)
            assert result is not None
            assert result.id == created_item.id
            assert result.name == "Updated Item"
            assert result.value == 100
            assert result.updated_at is not None
            
            # 아이템 삭제
            deleted = repo.delete(created_item.id)
            assert deleted is True
            
            # 삭제 확인
            not_found = repo.find_by_id(created_item.id)
            assert not_found is None
        finally:
            # 연결 종료
            client.close()


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(not os.environ.get("MONGODB_TEST_URI"), reason="MongoDB 테스트 URI가 설정되지 않았습니다.")
class TestAsyncMongoDBIntegration:
    """비동기 MongoDB 통합 테스트"""
    
    async def test_async_mongodb_client_connection(self, async_mongo_client):
        """비동기 MongoDB 클라이언트 연결 테스트"""
        # 클라이언트 생성
        client = DatabaseFactory.create_async_client(
            engine="mongodb",
            uri=os.environ.get("MONGODB_TEST_URI"),
            default_db_name=os.environ.get("MONGODB_TEST_DB", "jaepa_test")
        )
        
        # 연결
        await client.connect()
        
        try:
            # 연결 확인
            assert await client.is_connected() is True
            
            # 상태 확인
            health = await client.health_check()
            assert health["status"] == "connected"
            assert "details" in health
        finally:
            # 연결 종료
            await client.close()
    
    async def test_async_mongodb_repository_crud(self, async_mongo_client):
        """비동기 MongoDB 저장소 CRUD 테스트"""
        # 클라이언트 생성
        client = DatabaseFactory.create_async_client(
            engine="mongodb",
            uri=os.environ.get("MONGODB_TEST_URI"),
            default_db_name=os.environ.get("MONGODB_TEST_DB", "jaepa_test")
        )
        
        # 연결
        await client.connect()
        
        try:
            # 저장소 생성
            repo = AsyncBaseMongoRepository(
                client=client,
                collection_name="test_items",
                model_class=TestItem
            )
            
            # 컬렉션 초기화
            collection = await repo._get_collection()
            await collection.delete_many({})
            
            # 아이템 생성
            item = TestItem(name="Test Item", value=42)
            created_item = await repo.create(item)
            
            # 생성된 아이템 확인
            assert created_item.id is not None
            assert created_item.name == "Test Item"
            assert created_item.value == 42
            assert created_item.created_at is not None
            assert created_item.updated_at is not None
            
            # ID로 아이템 조회
            found_item = await repo.find_by_id(created_item.id)
            assert found_item is not None
            assert found_item.id == created_item.id
            assert found_item.name == created_item.name
            assert found_item.value == created_item.value
            
            # 필터로 아이템 조회
            found_items = await repo.find_many({"name": "Test Item"})
            assert len(found_items) == 1
            assert found_items[0].id == created_item.id
            
            # 아이템 업데이트
            updated_item = TestItem(
                id=created_item.id,
                name="Updated Item",
                value=100
            )
            result = await repo.update(created_item.id, updated_item)
            assert result is not None
            assert result.id == created_item.id
            assert result.name == "Updated Item"
            assert result.value == 100
            assert result.updated_at is not None
            
            # 아이템 삭제
            deleted = await repo.delete(created_item.id)
            assert deleted is True
            
            # 삭제 확인
            not_found = await repo.find_by_id(created_item.id)
            assert not_found is None
        finally:
            # 연결 종료
            await client.close()
