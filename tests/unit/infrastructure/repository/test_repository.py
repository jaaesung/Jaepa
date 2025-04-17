"""
저장소 단위 테스트

이 모듈은 저장소 클래스를 테스트합니다.
"""
import pytest
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
from bson import ObjectId

from infrastructure.repository.repository import BaseMongoRepository


class TestEntity:
    """
    테스트용 엔티티 클래스
    """
    
    def __init__(self, name, value, id=None):
        self.name = name
        self.value = value
        self.id = id
    
    def __eq__(self, other):
        if not isinstance(other, TestEntity):
            return False
        return (
            self.name == other.name and
            self.value == other.value and
            self.id == other.id
        )


class TestMongoRepository(BaseMongoRepository[TestEntity, str]):
    """
    테스트용 MongoDB 저장소 클래스
    """
    
    def __init__(self, client, db_name="test_db", collection_name="test_collection"):
        super().__init__(client, db_name, collection_name)
    
    def _convert_id(self, id):
        try:
            return ObjectId(id)
        except:
            return id
    
    def _to_entity(self, document):
        if document is None:
            return None
        
        id = str(document["_id"]) if "_id" in document else None
        return TestEntity(
            name=document.get("name"),
            value=document.get("value"),
            id=id
        )
    
    def _to_document(self, entity):
        document = {
            "name": entity.name,
            "value": entity.value
        }
        
        if entity.id:
            try:
                document["_id"] = ObjectId(entity.id)
            except:
                document["_id"] = entity.id
        
        return document
    
    def _define_indexes(self):
        return [
            {
                "keys": [("name", 1)],
                "name": "name_idx"
            },
            {
                "keys": [("value", -1)],
                "name": "value_idx"
            }
        ]


@pytest.mark.asyncio
class TestBaseMongoRepository:
    """
    기본 MongoDB 저장소 테스트 클래스
    """
    
    @pytest.fixture(autouse=True)
    async def setup_repository(self):
        """
        테스트 설정
        """
        # 모의 클라이언트 생성
        self.mock_client = AsyncMock()
        self.mock_db = AsyncMock()
        self.mock_collection = AsyncMock()
        
        self.mock_client.get_collection.return_value = self.mock_collection
        
        # 저장소 생성
        self.repository = TestMongoRepository(self.mock_client)
        
        yield
    
    async def test_find_by_id(self):
        """
        ID로 엔티티 조회 테스트
        """
        # 모의 응답 설정
        test_id = "507f1f77bcf86cd799439011"
        mock_document = {
            "_id": ObjectId(test_id),
            "name": "test_name",
            "value": 123
        }
        self.mock_collection.find_one.return_value = mock_document
        
        # 조회 테스트
        entity = await self.repository.find_by_id(test_id)
        
        # 검증
        assert entity is not None
        assert entity.id == test_id
        assert entity.name == "test_name"
        assert entity.value == 123
        
        # 호출 검증
        self.mock_collection.find_one.assert_called_once_with({"_id": ObjectId(test_id)})
        
        # 존재하지 않는 ID 조회
        self.mock_collection.find_one.return_value = None
        
        entity = await self.repository.find_by_id("invalid_id")
        
        # 검증
        assert entity is None
    
    async def test_find_all(self):
        """
        모든 엔티티 조회 테스트
        """
        # 모의 응답 설정
        mock_documents = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "name": "test1",
                "value": 100
            },
            {
                "_id": ObjectId("507f1f77bcf86cd799439022"),
                "name": "test2",
                "value": 200
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = mock_documents
        self.mock_collection.find.return_value = mock_cursor
        
        # 조회 테스트
        entities = await self.repository.find_all(skip=10, limit=20)
        
        # 검증
        assert len(entities) == 2
        assert entities[0].name == "test1"
        assert entities[0].value == 100
        assert entities[1].name == "test2"
        assert entities[1].value == 200
        
        # 호출 검증
        self.mock_collection.find.assert_called_once()
        mock_cursor.skip.assert_called_once_with(10)
        mock_cursor.limit.assert_called_once_with(20)
        mock_cursor.to_list.assert_called_once_with(length=20)
    
    async def test_save(self):
        """
        엔티티 저장 테스트
        """
        # 새 엔티티 저장
        entity = TestEntity(name="new_entity", value=300)
        
        # 모의 응답 설정
        mock_result = AsyncMock()
        mock_result.inserted_id = ObjectId("507f1f77bcf86cd799439033")
        self.mock_collection.insert_one.return_value = mock_result
        
        # 저장 테스트
        saved_entity = await self.repository.save(entity)
        
        # 검증
        assert saved_entity is not None
        assert saved_entity.name == "new_entity"
        assert saved_entity.value == 300
        assert saved_entity.id == "507f1f77bcf86cd799439033"
        
        # 호출 검증
        self.mock_collection.insert_one.assert_called_once()
        
        # 기존 엔티티 업데이트
        entity = TestEntity(name="updated_entity", value=400, id="507f1f77bcf86cd799439044")
        
        # 모의 응답 설정
        mock_result = AsyncMock()
        mock_result.modified_count = 1
        self.mock_collection.replace_one.return_value = mock_result
        
        # 저장 테스트
        saved_entity = await self.repository.save(entity)
        
        # 검증
        assert saved_entity is not None
        assert saved_entity.name == "updated_entity"
        assert saved_entity.value == 400
        assert saved_entity.id == "507f1f77bcf86cd799439044"
        
        # 호출 검증
        self.mock_collection.replace_one.assert_called_once()
    
    async def test_save_many(self):
        """
        여러 엔티티 저장 테스트
        """
        # 새 엔티티 목록
        entities = [
            TestEntity(name="entity1", value=100),
            TestEntity(name="entity2", value=200)
        ]
        
        # 모의 응답 설정
        mock_result = AsyncMock()
        mock_result.inserted_ids = [
            ObjectId("507f1f77bcf86cd799439055"),
            ObjectId("507f1f77bcf86cd799439066")
        ]
        self.mock_collection.insert_many.return_value = mock_result
        
        # 저장 테스트
        saved_entities = await self.repository.save_many(entities)
        
        # 검증
        assert len(saved_entities) == 2
        assert saved_entities[0].name == "entity1"
        assert saved_entities[0].value == 100
        assert saved_entities[0].id == "507f1f77bcf86cd799439055"
        assert saved_entities[1].name == "entity2"
        assert saved_entities[1].value == 200
        assert saved_entities[1].id == "507f1f77bcf86cd799439066"
        
        # 호출 검증
        self.mock_collection.insert_many.assert_called_once()
        
        # 기존 엔티티와 새 엔티티 혼합
        entities = [
            TestEntity(name="entity3", value=300, id="507f1f77bcf86cd799439077"),
            TestEntity(name="entity4", value=400)
        ]
        
        # 모의 응답 설정
        mock_replace_result = AsyncMock()
        mock_replace_result.modified_count = 1
        self.mock_collection.replace_one.return_value = mock_replace_result
        
        mock_insert_result = AsyncMock()
        mock_insert_result.inserted_ids = [ObjectId("507f1f77bcf86cd799439088")]
        self.mock_collection.insert_many.return_value = mock_insert_result
        
        # 저장 테스트
        saved_entities = await self.repository.save_many(entities)
        
        # 검증
        assert len(saved_entities) == 2
    
    async def test_update(self):
        """
        엔티티 업데이트 테스트
        """
        # 업데이트할 엔티티
        entity = TestEntity(name="updated_name", value=500)
        test_id = "507f1f77bcf86cd799439099"
        
        # 모의 응답 설정
        mock_result = AsyncMock()
        mock_result.modified_count = 1
        self.mock_collection.replace_one.return_value = mock_result
        
        # 업데이트 테스트
        updated_entity = await self.repository.update(test_id, entity)
        
        # 검증
        assert updated_entity is not None
        assert updated_entity.name == "updated_name"
        assert updated_entity.value == 500
        assert updated_entity.id == test_id
        
        # 호출 검증
        self.mock_collection.replace_one.assert_called_once_with(
            {"_id": ObjectId(test_id)},
            {"name": "updated_name", "value": 500, "_id": ObjectId(test_id)}
        )
        
        # 업데이트 실패
        mock_result.modified_count = 0
        
        updated_entity = await self.repository.update("invalid_id", entity)
        
        # 검증
        assert updated_entity is None
    
    async def test_delete(self):
        """
        엔티티 삭제 테스트
        """
        # 삭제할 ID
        test_id = "507f1f77bcf86cd799439100"
        
        # 모의 응답 설정
        mock_result = AsyncMock()
        mock_result.deleted_count = 1
        self.mock_collection.delete_one.return_value = mock_result
        
        # 삭제 테스트
        result = await self.repository.delete(test_id)
        
        # 검증
        assert result is True
        
        # 호출 검증
        self.mock_collection.delete_one.assert_called_once_with({"_id": ObjectId(test_id)})
        
        # 삭제 실패
        mock_result.deleted_count = 0
        
        result = await self.repository.delete("invalid_id")
        
        # 검증
        assert result is False
    
    async def test_count(self):
        """
        엔티티 개수 조회 테스트
        """
        # 모의 응답 설정
        self.mock_collection.count_documents.return_value = 42
        
        # 개수 조회 테스트
        count = await self.repository.count()
        
        # 검증
        assert count == 42
        
        # 호출 검증
        self.mock_collection.count_documents.assert_called_once_with({})
    
    async def test_exists(self):
        """
        엔티티 존재 여부 확인 테스트
        """
        # 존재하는 ID
        test_id = "507f1f77bcf86cd799439101"
        
        # 모의 응답 설정
        self.mock_collection.count_documents.return_value = 1
        
        # 존재 여부 확인 테스트
        exists = await self.repository.exists(test_id)
        
        # 검증
        assert exists is True
        
        # 호출 검증
        self.mock_collection.count_documents.assert_called_once_with(
            {"_id": ObjectId(test_id)},
            limit=1
        )
        
        # 존재하지 않는 ID
        self.mock_collection.count_documents.return_value = 0
        
        exists = await self.repository.exists("invalid_id")
        
        # 검증
        assert exists is False
    
    async def test_find_by_query(self):
        """
        쿼리로 엔티티 조회 테스트
        """
        # 모의 응답 설정
        mock_documents = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439102"),
                "name": "query_test1",
                "value": 600
            },
            {
                "_id": ObjectId("507f1f77bcf86cd799439103"),
                "name": "query_test2",
                "value": 700
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = mock_documents
        self.mock_collection.find.return_value = mock_cursor
        
        # 쿼리 조회 테스트
        query = {"name": {"$regex": "query_"}}
        entities = await self.repository.find_by_query(query, skip=5, limit=10)
        
        # 검증
        assert len(entities) == 2
        assert entities[0].name == "query_test1"
        assert entities[0].value == 600
        assert entities[1].name == "query_test2"
        assert entities[1].value == 700
        
        # 호출 검증
        self.mock_collection.find.assert_called_once_with(query)
        mock_cursor.skip.assert_called_once_with(5)
        mock_cursor.limit.assert_called_once_with(10)
        mock_cursor.to_list.assert_called_once_with(length=10)
    
    async def test_find_one_by_query(self):
        """
        쿼리로 단일 엔티티 조회 테스트
        """
        # 모의 응답 설정
        mock_document = {
            "_id": ObjectId("507f1f77bcf86cd799439104"),
            "name": "single_query_test",
            "value": 800
        }
        self.mock_collection.find_one.return_value = mock_document
        
        # 쿼리 조회 테스트
        query = {"name": "single_query_test"}
        entity = await self.repository.find_one_by_query(query)
        
        # 검증
        assert entity is not None
        assert entity.name == "single_query_test"
        assert entity.value == 800
        
        # 호출 검증
        self.mock_collection.find_one.assert_called_once_with(query)
        
        # 결과 없음
        self.mock_collection.find_one.return_value = None
        
        entity = await self.repository.find_one_by_query({"name": "non_existent"})
        
        # 검증
        assert entity is None
    
    async def test_count_by_query(self):
        """
        쿼리로 엔티티 개수 조회 테스트
        """
        # 모의 응답 설정
        self.mock_collection.count_documents.return_value = 5
        
        # 쿼리 개수 조회 테스트
        query = {"value": {"$gt": 500}}
        count = await self.repository.count_by_query(query)
        
        # 검증
        assert count == 5
        
        # 호출 검증
        self.mock_collection.count_documents.assert_called_once_with(query)
    
    async def test_update_by_query(self):
        """
        쿼리로 엔티티 업데이트 테스트
        """
        # 모의 응답 설정
        mock_result = AsyncMock()
        mock_result.modified_count = 3
        self.mock_collection.update_many.return_value = mock_result
        
        # 쿼리 업데이트 테스트
        query = {"value": {"$lt": 300}}
        update = {"$set": {"status": "low_value"}}
        count = await self.repository.update_by_query(query, update)
        
        # 검증
        assert count == 3
        
        # 호출 검증
        self.mock_collection.update_many.assert_called_once_with(query, update)
    
    async def test_delete_by_query(self):
        """
        쿼리로 엔티티 삭제 테스트
        """
        # 모의 응답 설정
        mock_result = AsyncMock()
        mock_result.deleted_count = 2
        self.mock_collection.delete_many.return_value = mock_result
        
        # 쿼리 삭제 테스트
        query = {"value": {"$lt": 0}}
        count = await self.repository.delete_by_query(query)
        
        # 검증
        assert count == 2
        
        # 호출 검증
        self.mock_collection.delete_many.assert_called_once_with(query)
    
    async def test_aggregate(self):
        """
        집계 파이프라인 실행 테스트
        """
        # 모의 응답 설정
        mock_results = [
            {"_id": "group1", "total": 1000},
            {"_id": "group2", "total": 2000}
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = mock_results
        self.mock_collection.aggregate.return_value = mock_cursor
        
        # 집계 테스트
        pipeline = [
            {"$group": {"_id": "$group", "total": {"$sum": "$value"}}}
        ]
        results = await self.repository.aggregate(pipeline)
        
        # 검증
        assert len(results) == 2
        assert results[0]["_id"] == "group1"
        assert results[0]["total"] == 1000
        assert results[1]["_id"] == "group2"
        assert results[1]["total"] == 2000
        
        # 호출 검증
        self.mock_collection.aggregate.assert_called_once_with(pipeline)
        mock_cursor.to_list.assert_called_once_with(length=None)
    
    async def test_create_indexes(self):
        """
        인덱스 생성 테스트
        """
        # 모의 응답 설정
        self.mock_collection.create_index.side_effect = ["name_idx", "value_idx"]
        
        # 인덱스 생성 테스트
        indexes = await self.repository.create_indexes()
        
        # 검증
        assert len(indexes) == 2
        assert "name_idx" in indexes
        assert "value_idx" in indexes
        
        # 호출 검증
        assert self.mock_collection.create_index.call_count == 2
