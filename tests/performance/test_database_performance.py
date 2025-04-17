"""
데이터베이스 성능 테스트
"""
import pytest
import os
import time
import random
import string
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
    tags: List[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


def generate_random_string(length: int = 10) -> str:
    """랜덤 문자열 생성"""
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


def generate_test_item() -> TestItem:
    """테스트 아이템 생성"""
    return TestItem(
        name=generate_random_string(),
        value=random.randint(1, 1000),
        tags=[generate_random_string(5) for _ in range(random.randint(1, 5))]
    )


@pytest.mark.performance
@pytest.mark.skipif(not os.environ.get("MONGODB_TEST_URI"), reason="MongoDB 테스트 URI가 설정되지 않았습니다.")
class TestMongoDBPerformance:
    """MongoDB 성능 테스트"""
    
    @pytest.fixture(scope="class")
    def mongo_repo(self):
        """MongoDB 저장소 fixture"""
        # 클라이언트 생성
        client = DatabaseFactory.create_client(
            engine="mongodb",
            uri=os.environ.get("MONGODB_TEST_URI"),
            default_db_name=os.environ.get("MONGODB_TEST_DB", "jaepa_test")
        )
        
        # 연결
        client.connect()
        
        # 저장소 생성
        repo = BaseMongoRepository(
            client=client,
            collection_name="perf_test_items",
            model_class=TestItem
        )
        
        # 컬렉션 초기화
        collection = repo._get_collection()
        collection.delete_many({})
        
        yield repo
        
        # 정리
        collection.delete_many({})
        client.close()
    
    def test_bulk_insert_performance(self, mongo_repo, benchmark):
        """대량 삽입 성능 테스트"""
        def _bulk_insert():
            items = [generate_test_item() for _ in range(100)]
            created_items = []
            for item in items:
                created_item = mongo_repo.create(item)
                created_items.append(created_item)
            return created_items
        
        # 벤치마크 실행
        result = benchmark(_bulk_insert)
        
        # 결과 확인
        assert len(result) == 100
    
    def test_bulk_find_performance(self, mongo_repo, benchmark):
        """대량 조회 성능 테스트"""
        # 테스트 데이터 생성
        items = [generate_test_item() for _ in range(100)]
        for item in items:
            mongo_repo.create(item)
        
        def _bulk_find():
            return mongo_repo.find_many({}, skip=0, limit=100)
        
        # 벤치마크 실행
        result = benchmark(_bulk_find)
        
        # 결과 확인
        assert len(result) == 100
    
    def test_find_by_tag_performance(self, mongo_repo, benchmark):
        """태그 조회 성능 테스트"""
        # 테스트 데이터 생성
        common_tag = "performance_test"
        items = []
        for _ in range(100):
            item = generate_test_item()
            item.tags.append(common_tag)
            created_item = mongo_repo.create(item)
            items.append(created_item)
        
        def _find_by_tag():
            # MongoDB 쿼리 사용
            collection = mongo_repo._get_collection()
            cursor = collection.find({"tags": common_tag})
            return list(cursor)
        
        # 벤치마크 실행
        result = benchmark(_find_by_tag)
        
        # 결과 확인
        assert len(result) == 100
    
    def test_update_performance(self, mongo_repo, benchmark):
        """업데이트 성능 테스트"""
        # 테스트 데이터 생성
        items = []
        for _ in range(100):
            created_item = mongo_repo.create(generate_test_item())
            items.append(created_item)
        
        def _update_items():
            updated_items = []
            for item in items:
                item.value = random.randint(1000, 2000)
                updated_item = mongo_repo.update(item.id, item)
                updated_items.append(updated_item)
            return updated_items
        
        # 벤치마크 실행
        result = benchmark(_update_items)
        
        # 결과 확인
        assert len(result) == 100
        for item in result:
            assert item.value >= 1000
            assert item.value <= 2000


@pytest.mark.performance
@pytest.mark.asyncio
@pytest.mark.skipif(not os.environ.get("MONGODB_TEST_URI"), reason="MongoDB 테스트 URI가 설정되지 않았습니다.")
class TestAsyncMongoDBPerformance:
    """비동기 MongoDB 성능 테스트"""
    
    @pytest.fixture(scope="class")
    async def async_mongo_repo(self):
        """비동기 MongoDB 저장소 fixture"""
        # 클라이언트 생성
        client = DatabaseFactory.create_async_client(
            engine="mongodb",
            uri=os.environ.get("MONGODB_TEST_URI"),
            default_db_name=os.environ.get("MONGODB_TEST_DB", "jaepa_test")
        )
        
        # 연결
        await client.connect()
        
        # 저장소 생성
        repo = AsyncBaseMongoRepository(
            client=client,
            collection_name="perf_test_items_async",
            model_class=TestItem
        )
        
        # 컬렉션 초기화
        collection = await repo._get_collection()
        await collection.delete_many({})
        
        yield repo
        
        # 정리
        await collection.delete_many({})
        await client.close()
    
    @pytest.mark.benchmark(group="async")
    async def test_async_bulk_insert_performance(self, async_mongo_repo, benchmark):
        """비동기 대량 삽입 성능 테스트"""
        async def _async_bulk_insert():
            items = [generate_test_item() for _ in range(100)]
            created_items = []
            for item in items:
                created_item = await async_mongo_repo.create(item)
                created_items.append(created_item)
            return created_items
        
        # 벤치마크 실행
        result = await benchmark(_async_bulk_insert)
        
        # 결과 확인
        assert len(result) == 100
    
    @pytest.mark.benchmark(group="async")
    async def test_async_bulk_find_performance(self, async_mongo_repo, benchmark):
        """비동기 대량 조회 성능 테스트"""
        # 테스트 데이터 생성
        items = [generate_test_item() for _ in range(100)]
        for item in items:
            await async_mongo_repo.create(item)
        
        async def _async_bulk_find():
            return await async_mongo_repo.find_many({}, skip=0, limit=100)
        
        # 벤치마크 실행
        result = await benchmark(_async_bulk_find)
        
        # 결과 확인
        assert len(result) == 100
    
    @pytest.mark.benchmark(group="async")
    async def test_async_find_by_tag_performance(self, async_mongo_repo, benchmark):
        """비동기 태그 조회 성능 테스트"""
        # 테스트 데이터 생성
        common_tag = "async_performance_test"
        items = []
        for _ in range(100):
            item = generate_test_item()
            item.tags.append(common_tag)
            created_item = await async_mongo_repo.create(item)
            items.append(created_item)
        
        async def _async_find_by_tag():
            # MongoDB 쿼리 사용
            collection = await async_mongo_repo._get_collection()
            cursor = collection.find({"tags": common_tag})
            return [doc async for doc in cursor]
        
        # 벤치마크 실행
        result = await benchmark(_async_find_by_tag)
        
        # 결과 확인
        assert len(result) == 100
