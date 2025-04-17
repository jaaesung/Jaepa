"""
MongoDB 모듈 테스트
"""
import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List, Optional

from infrastructure.database.mongodb import (
    MongoDBClient, AsyncMongoDBClient,
    BaseMongoRepository, AsyncBaseMongoRepository
)
from infrastructure.database.interface import (
    DatabaseClientInterface, RepositoryInterface,
    AsyncDatabaseClientInterface, AsyncRepositoryInterface
)


class TestMongoDBClient:
    """MongoDB 클라이언트 테스트"""
    
    def test_implements_interface(self):
        """인터페이스 구현 여부 테스트"""
        assert issubclass(MongoDBClient, DatabaseClientInterface)
    
    @patch('infrastructure.database.mongodb.pymongo.MongoClient')
    def test_connect(self, mock_mongo_client):
        """연결 테스트"""
        # 모의 객체 설정
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        
        # 클라이언트 생성 및 연결
        client = MongoDBClient(uri="mongodb://localhost:27017")
        client.connect()
        
        # 연결 확인
        mock_mongo_client.assert_called_once_with(
            "mongodb://localhost:27017",
            connect=True,
            connectTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=30000,
            retryWrites=True,
            retryReads=True,
            serverSelectionTimeoutMS=5000,
            socketTimeoutMS=10000,
            heartbeatFrequencyMS=10000,
            appname="JaePa"
        )
        assert client.client == mock_client
        assert client._connected is True
    
    @patch('infrastructure.database.mongodb.pymongo.MongoClient')
    def test_close(self, mock_mongo_client):
        """연결 종료 테스트"""
        # 모의 객체 설정
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        
        # 클라이언트 생성 및 연결
        client = MongoDBClient(uri="mongodb://localhost:27017")
        client.connect()
        
        # 연결 종료
        client.close()
        
        # 연결 종료 확인
        mock_client.close.assert_called_once()
        assert client._connected is False
    
    @patch('infrastructure.database.mongodb.pymongo.MongoClient')
    def test_is_connected(self, mock_mongo_client):
        """연결 상태 확인 테스트"""
        # 모의 객체 설정
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        
        # 클라이언트 생성
        client = MongoDBClient(uri="mongodb://localhost:27017")
        
        # 연결 전 상태 확인
        assert client.is_connected() is False
        
        # 연결
        client.connect()
        
        # 연결 후 상태 확인
        assert client.is_connected() is True
        
        # 연결 종료
        client.close()
        
        # 연결 종료 후 상태 확인
        assert client.is_connected() is False
    
    @patch('infrastructure.database.mongodb.pymongo.MongoClient')
    def test_get_database(self, mock_mongo_client):
        """데이터베이스 가져오기 테스트"""
        # 모의 객체 설정
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        # 클라이언트 생성 및 연결
        client = MongoDBClient(uri="mongodb://localhost:27017", default_db_name="test_db")
        client.connect()
        
        # 기본 데이터베이스 가져오기
        db = client.get_database()
        
        # 데이터베이스 확인
        assert db == mock_db
        mock_client.__getitem__.assert_called_once_with("test_db")
        
        # 특정 데이터베이스 가져오기
        db = client.get_database("other_db")
        
        # 데이터베이스 확인
        assert db == mock_db
        mock_client.__getitem__.assert_called_with("other_db")
    
    @patch('infrastructure.database.mongodb.pymongo.MongoClient')
    def test_get_collection(self, mock_mongo_client):
        """컬렉션 가져오기 테스트"""
        # 모의 객체 설정
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_mongo_client.return_value = mock_client
        
        # 클라이언트 생성 및 연결
        client = MongoDBClient(uri="mongodb://localhost:27017", default_db_name="test_db")
        client.connect()
        
        # 기본 데이터베이스의 컬렉션 가져오기
        collection = client.get_collection("test_collection")
        
        # 컬렉션 확인
        assert collection == mock_collection
        mock_client.__getitem__.assert_called_with("test_db")
        mock_db.__getitem__.assert_called_once_with("test_collection")
        
        # 특정 데이터베이스의 컬렉션 가져오기
        collection = client.get_collection("test_collection", "other_db")
        
        # 컬렉션 확인
        assert collection == mock_collection
        mock_client.__getitem__.assert_called_with("other_db")
        mock_db.__getitem__.assert_called_with("test_collection")
    
    @patch('infrastructure.database.mongodb.pymongo.MongoClient')
    def test_health_check(self, mock_mongo_client):
        """상태 확인 테스트"""
        # 모의 객체 설정
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {"ok": 1, "version": "4.4.0"}
        mock_mongo_client.return_value = mock_client
        
        # 클라이언트 생성 및 연결
        client = MongoDBClient(uri="mongodb://localhost:27017")
        client.connect()
        
        # 상태 확인
        health = client.health_check()
        
        # 상태 확인 결과 확인
        assert health["status"] == "connected"
        assert "details" in health
        assert "response_time_ms" in health["details"]
        assert health["details"]["version"] == "4.4.0"
        mock_client.admin.command.assert_called_once_with("ping")


class TestAsyncMongoDBClient:
    """비동기 MongoDB 클라이언트 테스트"""
    
    def test_implements_interface(self):
        """인터페이스 구현 여부 테스트"""
        assert issubclass(AsyncMongoDBClient, AsyncDatabaseClientInterface)
    
    @pytest.mark.asyncio
    @patch('infrastructure.database.mongodb.motor.motor_asyncio.AsyncIOMotorClient')
    async def test_connect(self, mock_motor_client):
        """연결 테스트"""
        # 모의 객체 설정
        mock_client = MagicMock()
        mock_motor_client.return_value = mock_client
        
        # 클라이언트 생성 및 연결
        client = AsyncMongoDBClient(uri="mongodb://localhost:27017")
        await client.connect()
        
        # 연결 확인
        mock_motor_client.assert_called_once_with(
            "mongodb://localhost:27017",
            connectTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=30000,
            retryWrites=True,
            retryReads=True,
            serverSelectionTimeoutMS=5000,
            socketTimeoutMS=10000,
            heartbeatFrequencyMS=10000,
            appname="JaePa"
        )
        assert client.client == mock_client
        assert client._connected is True


class TestBaseMongoRepository:
    """기본 MongoDB 저장소 테스트"""
    
    def test_implements_interface(self):
        """인터페이스 구현 여부 테스트"""
        assert issubclass(BaseMongoRepository, RepositoryInterface)
    
    def test_init(self):
        """초기화 테스트"""
        # 모의 객체 설정
        mock_client = MagicMock(spec=MongoDBClient)
        mock_model_class = MagicMock()
        
        # 저장소 생성
        repo = BaseMongoRepository(
            client=mock_client,
            collection_name="test_collection",
            model_class=mock_model_class
        )
        
        # 초기화 확인
        assert repo.client == mock_client
        assert repo.collection_name == "test_collection"
        assert repo.model_class == mock_model_class
    
    def test_get_collection(self):
        """컬렉션 가져오기 테스트"""
        # 모의 객체 설정
        mock_client = MagicMock(spec=MongoDBClient)
        mock_collection = MagicMock()
        mock_client.get_collection.return_value = mock_collection
        mock_model_class = MagicMock()
        
        # 저장소 생성
        repo = BaseMongoRepository(
            client=mock_client,
            collection_name="test_collection",
            model_class=mock_model_class
        )
        
        # 컬렉션 가져오기
        collection = repo._get_collection()
        
        # 컬렉션 확인
        assert collection == mock_collection
        mock_client.get_collection.assert_called_once_with("test_collection")
    
    def test_to_model(self):
        """모델 변환 테스트"""
        # 모의 객체 설정
        mock_client = MagicMock(spec=MongoDBClient)
        
        # 모의 모델 클래스 생성
        class MockModel:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        # 저장소 생성
        repo = BaseMongoRepository(
            client=mock_client,
            collection_name="test_collection",
            model_class=MockModel
        )
        
        # 데이터 변환
        data = {"id": "123", "name": "Test"}
        model = repo._to_model(data)
        
        # 변환 결과 확인
        assert isinstance(model, MockModel)
        assert model.id == "123"
        assert model.name == "Test"
        
        # None 변환
        assert repo._to_model(None) is None
    
    def test_to_document(self):
        """문서 변환 테스트"""
        # 모의 객체 설정
        mock_client = MagicMock(spec=MongoDBClient)
        
        # 모의 모델 생성
        class MockModel:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
            
            def model_dump(self, **kwargs):
                return {"id": getattr(self, "id", None), "name": getattr(self, "name", None)}
        
        # 저장소 생성
        repo = BaseMongoRepository(
            client=mock_client,
            collection_name="test_collection",
            model_class=MockModel
        )
        
        # 모델 생성
        model = MockModel(id="123", name="Test")
        
        # 문서 변환
        document = repo._to_document(model)
        
        # 변환 결과 확인
        assert document == {"id": "123", "name": "Test"}


class TestAsyncBaseMongoRepository:
    """비동기 기본 MongoDB 저장소 테스트"""
    
    def test_implements_interface(self):
        """인터페이스 구현 여부 테스트"""
        assert issubclass(AsyncBaseMongoRepository, AsyncRepositoryInterface)
    
    def test_init(self):
        """초기화 테스트"""
        # 모의 객체 설정
        mock_client = MagicMock(spec=AsyncMongoDBClient)
        mock_model_class = MagicMock()
        
        # 저장소 생성
        repo = AsyncBaseMongoRepository(
            client=mock_client,
            collection_name="test_collection",
            model_class=mock_model_class
        )
        
        # 초기화 확인
        assert repo.client == mock_client
        assert repo.collection_name == "test_collection"
        assert repo.model_class == mock_model_class
    
    @pytest.mark.asyncio
    async def test_get_collection(self):
        """컬렉션 가져오기 테스트"""
        # 모의 객체 설정
        mock_client = MagicMock(spec=AsyncMongoDBClient)
        mock_collection = MagicMock()
        mock_client.get_collection.return_value = mock_collection
        mock_model_class = MagicMock()
        
        # 저장소 생성
        repo = AsyncBaseMongoRepository(
            client=mock_client,
            collection_name="test_collection",
            model_class=mock_model_class
        )
        
        # 컬렉션 가져오기
        collection = await repo._get_collection()
        
        # 컬렉션 확인
        assert collection == mock_collection
        mock_client.get_collection.assert_called_once_with("test_collection")
