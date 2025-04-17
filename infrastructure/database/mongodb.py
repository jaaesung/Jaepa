"""
MongoDB 데이터베이스 모듈

MongoDB 데이터베이스 접근을 위한 클라이언트 및 저장소 구현체를 제공합니다.
"""
import time
import logging
from typing import Dict, Any, List, Optional, Union, TypeVar, Generic, Type, cast
from datetime import datetime
from bson import ObjectId

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from motor.motor_asyncio import AsyncIOMotorCollection

from pydantic import BaseModel

from .interface import (
    DatabaseClientInterface, RepositoryInterface,
    AsyncDatabaseClientInterface, AsyncRepositoryInterface
)

# 로깅 설정
logger = logging.getLogger(__name__)

# 타입 변수
T = TypeVar('T', bound=BaseModel)


class MongoDBClient(DatabaseClientInterface):
    """
    MongoDB 클라이언트 구현체
    """
    
    def __init__(
        self,
        uri: str,
        default_db_name: str,
        connect_timeout: int = 5000,
        max_pool_size: int = 10,
        min_pool_size: int = 1,
        max_idle_time_ms: int = 10000,
        retry_writes: bool = True,
        retry_reads: bool = True,
        server_selection_timeout_ms: int = 5000,
        socket_timeout_ms: int = 5000,
        heartbeat_frequency_ms: int = 5000,
        app_name: str = "JaePa"
    ):
        """
        초기화
        
        Args:
            uri: MongoDB URI
            default_db_name: 기본 데이터베이스 이름
            connect_timeout: 연결 타임아웃 (ms)
            max_pool_size: 최대 연결 풀 크기
            min_pool_size: 최소 연결 풀 크기
            max_idle_time_ms: 최대 유휴 시간 (ms)
            retry_writes: 쓰기 재시도 여부
            retry_reads: 읽기 재시도 여부
            server_selection_timeout_ms: 서버 선택 타임아웃 (ms)
            socket_timeout_ms: 소켓 타임아웃 (ms)
            heartbeat_frequency_ms: 하트비트 주기 (ms)
            app_name: 애플리케이션 이름
        """
        self.uri = uri
        self.default_db_name = default_db_name
        self.client_options = {
            "connectTimeoutMS": connect_timeout,
            "maxPoolSize": max_pool_size,
            "minPoolSize": min_pool_size,
            "maxIdleTimeMS": max_idle_time_ms,
            "retryWrites": retry_writes,
            "retryReads": retry_reads,
            "serverSelectionTimeoutMS": server_selection_timeout_ms,
            "socketTimeoutMS": socket_timeout_ms,
            "heartbeatFrequencyMS": heartbeat_frequency_ms,
            "appName": app_name
        }
        self.client = None
        self._connected = False
        self._last_connection_check = 0
        
        logger.debug(f"MongoDB client initialized with URI: {uri}, DB: {default_db_name}")
    
    def connect(self) -> None:
        """
        데이터베이스에 연결
        """
        try:
            if not self.client:
                logger.debug("Creating new MongoDB client")
                self.client = MongoClient(self.uri, **self.client_options)
            
            # 연결 테스트
            self.client.admin.command('ping')
            self._connected = True
            logger.info(f"Connected to MongoDB at {self.uri}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self._connected = False
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def close(self) -> None:
        """
        데이터베이스 연결 종료
        """
        if self.client:
            logger.debug("Closing MongoDB client")
            self.client.close()
            self.client = None
            self._connected = False
            logger.info("MongoDB connection closed")
    
    def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            bool: 연결 상태
        """
        # 캐싱된 상태가 있고 최근에 확인한 경우 (10초 이내)
        current_time = time.time()
        if self._connected and (current_time - self._last_connection_check) < 10:
            return self._connected
        
        # 연결 상태 확인
        if not self.client:
            self._connected = False
            return False
        
        try:
            self.client.admin.command('ping')
            self._connected = True
        except (ConnectionFailure, ServerSelectionTimeoutError):
            self._connected = False
        
        # 마지막 확인 시간 업데이트
        self._last_connection_check = current_time
        return self._connected
    
    def get_database(self, db_name: Optional[str] = None) -> Database:
        """
        데이터베이스 객체 반환
        
        Args:
            db_name: 데이터베이스 이름 (기본값: None)
            
        Returns:
            Database: 데이터베이스 객체
        """
        if not self.is_connected():
            self.connect()
        
        db_name = db_name or self.default_db_name
        return self.client[db_name]
    
    def get_collection(self, collection_name: str, db_name: Optional[str] = None) -> Collection:
        """
        컬렉션 객체 반환
        
        Args:
            collection_name: 컬렉션 이름
            db_name: 데이터베이스 이름 (기본값: None)
            
        Returns:
            Collection: 컬렉션 객체
        """
        db = self.get_database(db_name)
        return db[collection_name]
    
    def health_check(self) -> Dict[str, Any]:
        """
        상태 확인
        
        Returns:
            Dict[str, Any]: 상태 정보
        """
        result = {
            "status": "disconnected",
            "details": {}
        }
        
        if not self.client:
            return result
        
        try:
            # 응답 시간 측정
            start_time = time.time()
            server_info = self.client.admin.command('serverStatus')
            end_time = time.time()
            
            # 상태 정보 구성
            result["status"] = "connected"
            result["details"] = {
                "response_time_ms": round((end_time - start_time) * 1000, 2),
                "version": server_info.get("version", "unknown"),
                "connections": server_info.get("connections", {}),
                "uptime_seconds": server_info.get("uptime", 0)
            }
        except Exception as e:
            result["status"] = "error"
            result["details"] = {
                "error": str(e)
            }
        
        return result


class AsyncMongoDBClient(AsyncDatabaseClientInterface):
    """
    비동기 MongoDB 클라이언트 구현체
    """
    
    def __init__(
        self,
        uri: str,
        default_db_name: str,
        connect_timeout: int = 5000,
        max_pool_size: int = 10,
        min_pool_size: int = 1,
        max_idle_time_ms: int = 10000,
        retry_writes: bool = True,
        retry_reads: bool = True,
        server_selection_timeout_ms: int = 5000,
        socket_timeout_ms: int = 5000,
        heartbeat_frequency_ms: int = 5000,
        app_name: str = "JaePa"
    ):
        """
        초기화
        
        Args:
            uri: MongoDB URI
            default_db_name: 기본 데이터베이스 이름
            connect_timeout: 연결 타임아웃 (ms)
            max_pool_size: 최대 연결 풀 크기
            min_pool_size: 최소 연결 풀 크기
            max_idle_time_ms: 최대 유휴 시간 (ms)
            retry_writes: 쓰기 재시도 여부
            retry_reads: 읽기 재시도 여부
            server_selection_timeout_ms: 서버 선택 타임아웃 (ms)
            socket_timeout_ms: 소켓 타임아웃 (ms)
            heartbeat_frequency_ms: 하트비트 주기 (ms)
            app_name: 애플리케이션 이름
        """
        self.uri = uri
        self.default_db_name = default_db_name
        self.client_options = {
            "connectTimeoutMS": connect_timeout,
            "maxPoolSize": max_pool_size,
            "minPoolSize": min_pool_size,
            "maxIdleTimeMS": max_idle_time_ms,
            "retryWrites": retry_writes,
            "retryReads": retry_reads,
            "serverSelectionTimeoutMS": server_selection_timeout_ms,
            "socketTimeoutMS": socket_timeout_ms,
            "heartbeatFrequencyMS": heartbeat_frequency_ms,
            "appName": app_name
        }
        self.client = None
        self._connected = False
        self._last_connection_check = 0
        
        logger.debug(f"Async MongoDB client initialized with URI: {uri}, DB: {default_db_name}")
    
    async def connect(self) -> None:
        """
        데이터베이스에 연결
        """
        try:
            if not self.client:
                logger.debug("Creating new async MongoDB client")
                self.client = AsyncIOMotorClient(self.uri, **self.client_options)
            
            # 연결 테스트
            await self.client.admin.command('ping')
            self._connected = True
            logger.info(f"Connected to MongoDB at {self.uri}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self._connected = False
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def close(self) -> None:
        """
        데이터베이스 연결 종료
        """
        if self.client:
            logger.debug("Closing async MongoDB client")
            await self.client.close()
            self.client = None
            self._connected = False
            logger.info("MongoDB connection closed")
    
    async def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            bool: 연결 상태
        """
        # 캐싱된 상태가 있고 최근에 확인한 경우 (10초 이내)
        current_time = time.time()
        if self._connected and (current_time - self._last_connection_check) < 10:
            return self._connected
        
        # 연결 상태 확인
        if not self.client:
            self._connected = False
            return False
        
        try:
            await self.client.admin.command('ping')
            self._connected = True
        except (ConnectionFailure, ServerSelectionTimeoutError):
            self._connected = False
        
        # 마지막 확인 시간 업데이트
        self._last_connection_check = current_time
        return self._connected
    
    async def get_database(self, db_name: Optional[str] = None) -> AsyncIOMotorDatabase:
        """
        데이터베이스 객체 반환
        
        Args:
            db_name: 데이터베이스 이름 (기본값: None)
            
        Returns:
            AsyncIOMotorDatabase: 데이터베이스 객체
        """
        if not await self.is_connected():
            await self.connect()
        
        db_name = db_name or self.default_db_name
        return self.client[db_name]
    
    async def get_collection(self, collection_name: str, db_name: Optional[str] = None) -> AsyncIOMotorCollection:
        """
        컬렉션 객체 반환
        
        Args:
            collection_name: 컬렉션 이름
            db_name: 데이터베이스 이름 (기본값: None)
            
        Returns:
            AsyncIOMotorCollection: 컬렉션 객체
        """
        db = await self.get_database(db_name)
        return db[collection_name]
    
    async def health_check(self) -> Dict[str, Any]:
        """
        상태 확인
        
        Returns:
            Dict[str, Any]: 상태 정보
        """
        result = {
            "status": "disconnected",
            "details": {}
        }
        
        if not self.client:
            return result
        
        try:
            # 응답 시간 측정
            start_time = time.time()
            server_info = await self.client.admin.command('serverStatus')
            end_time = time.time()
            
            # 상태 정보 구성
            result["status"] = "connected"
            result["details"] = {
                "response_time_ms": round((end_time - start_time) * 1000, 2),
                "version": server_info.get("version", "unknown"),
                "connections": server_info.get("connections", {}),
                "uptime_seconds": server_info.get("uptime", 0)
            }
        except Exception as e:
            result["status"] = "error"
            result["details"] = {
                "error": str(e)
            }
        
        return result


class BaseMongoRepository(RepositoryInterface[T]):
    """
    기본 MongoDB 저장소 구현체
    """
    
    def __init__(self, client: MongoDBClient, collection_name: str, model_class: Type[T]):
        """
        초기화
        
        Args:
            client: MongoDB 클라이언트
            collection_name: 컬렉션 이름
            model_class: 모델 클래스
        """
        self.client = client
        self.collection_name = collection_name
        self.model_class = model_class
        
        logger.debug(f"MongoDB repository initialized for collection: {collection_name}")
    
    def _get_collection(self) -> Collection:
        """
        컬렉션 객체 반환
        
        Returns:
            Collection: 컬렉션 객체
        """
        return self.client.get_collection(self.collection_name)
    
    def _to_model(self, data: Dict[str, Any]) -> Optional[T]:
        """
        데이터를 모델로 변환
        
        Args:
            data: 데이터
            
        Returns:
            Optional[T]: 모델 또는 None
        """
        if not data:
            return None
        
        # ObjectId를 문자열로 변환
        if '_id' in data:
            data['id'] = str(data.pop('_id'))
        
        return self.model_class(**data)
    
    def _to_document(self, item: T) -> Dict[str, Any]:
        """
        모델을 문서로 변환
        
        Args:
            item: 모델
            
        Returns:
            Dict[str, Any]: 문서
        """
        # 모델을 딕셔너리로 변환
        data = item.model_dump(exclude_unset=True)
        
        # id를 _id로 변환
        if 'id' in data:
            data['_id'] = ObjectId(data.pop('id'))
        
        return data
    
    def find_by_id(self, id: str) -> Optional[T]:
        """
        ID로 항목 조회
        
        Args:
            id: 항목 ID
            
        Returns:
            Optional[T]: 항목 또는 None
        """
        collection = self._get_collection()
        data = collection.find_one({"_id": ObjectId(id)})
        return self._to_model(data)
    
    def find_one(self, filter: Dict[str, Any]) -> Optional[T]:
        """
        필터로 단일 항목 조회
        
        Args:
            filter: 필터
            
        Returns:
            Optional[T]: 항목 또는 None
        """
        collection = self._get_collection()
        data = collection.find_one(filter)
        return self._to_model(data)
    
    def find_many(self, filter: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[T]:
        """
        필터로 여러 항목 조회
        
        Args:
            filter: 필터
            skip: 건너뛸 항목 수 (기본값: 0)
            limit: 최대 항목 수 (기본값: 100)
            
        Returns:
            List[T]: 항목 목록
        """
        collection = self._get_collection()
        cursor = collection.find(filter).skip(skip).limit(limit)
        return [self._to_model(data) for data in cursor]
    
    def create(self, item: T) -> T:
        """
        항목 생성
        
        Args:
            item: 생성할 항목
            
        Returns:
            T: 생성된 항목
        """
        collection = self._get_collection()
        document = self._to_document(item)
        
        # _id가 없으면 자동 생성
        if '_id' not in document:
            document['_id'] = ObjectId()
        
        # 생성 시간 추가
        if 'created_at' not in document:
            document['created_at'] = datetime.utcnow()
        
        # 업데이트 시간 추가
        document['updated_at'] = datetime.utcnow()
        
        result = collection.insert_one(document)
        
        # 생성된 항목 반환
        return self.find_by_id(str(result.inserted_id))
    
    def update(self, id: str, item: T) -> Optional[T]:
        """
        항목 업데이트
        
        Args:
            id: 항목 ID
            item: 업데이트할 항목
            
        Returns:
            Optional[T]: 업데이트된 항목 또는 None
        """
        collection = self._get_collection()
        document = self._to_document(item)
        
        # _id 제거 (변경 불가)
        if '_id' in document:
            del document['_id']
        
        # 업데이트 시간 추가
        document['updated_at'] = datetime.utcnow()
        
        result = collection.update_one({"_id": ObjectId(id)}, {"$set": document})
        
        if result.matched_count == 0:
            return None
        
        # 업데이트된 항목 반환
        return self.find_by_id(id)
    
    def delete(self, id: str) -> bool:
        """
        항목 삭제
        
        Args:
            id: 항목 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        collection = self._get_collection()
        result = collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
    def count(self, filter: Dict[str, Any]) -> int:
        """
        항목 수 조회
        
        Args:
            filter: 필터
            
        Returns:
            int: 항목 수
        """
        collection = self._get_collection()
        return collection.count_documents(filter)


class AsyncBaseMongoRepository(AsyncRepositoryInterface[T]):
    """
    비동기 기본 MongoDB 저장소 구현체
    """
    
    def __init__(self, client: AsyncMongoDBClient, collection_name: str, model_class: Type[T]):
        """
        초기화
        
        Args:
            client: 비동기 MongoDB 클라이언트
            collection_name: 컬렉션 이름
            model_class: 모델 클래스
        """
        self.client = client
        self.collection_name = collection_name
        self.model_class = model_class
        
        logger.debug(f"Async MongoDB repository initialized for collection: {collection_name}")
    
    async def _get_collection(self) -> AsyncIOMotorCollection:
        """
        컬렉션 객체 반환
        
        Returns:
            AsyncIOMotorCollection: 컬렉션 객체
        """
        return await self.client.get_collection(self.collection_name)
    
    def _to_model(self, data: Dict[str, Any]) -> Optional[T]:
        """
        데이터를 모델로 변환
        
        Args:
            data: 데이터
            
        Returns:
            Optional[T]: 모델 또는 None
        """
        if not data:
            return None
        
        # ObjectId를 문자열로 변환
        if '_id' in data:
            data['id'] = str(data.pop('_id'))
        
        return self.model_class(**data)
    
    def _to_document(self, item: T) -> Dict[str, Any]:
        """
        모델을 문서로 변환
        
        Args:
            item: 모델
            
        Returns:
            Dict[str, Any]: 문서
        """
        # 모델을 딕셔너리로 변환
        data = item.model_dump(exclude_unset=True)
        
        # id를 _id로 변환
        if 'id' in data:
            data['_id'] = ObjectId(data.pop('id'))
        
        return data
    
    async def find_by_id(self, id: str) -> Optional[T]:
        """
        ID로 항목 조회
        
        Args:
            id: 항목 ID
            
        Returns:
            Optional[T]: 항목 또는 None
        """
        collection = await self._get_collection()
        data = await collection.find_one({"_id": ObjectId(id)})
        return self._to_model(data)
    
    async def find_one(self, filter: Dict[str, Any]) -> Optional[T]:
        """
        필터로 단일 항목 조회
        
        Args:
            filter: 필터
            
        Returns:
            Optional[T]: 항목 또는 None
        """
        collection = await self._get_collection()
        data = await collection.find_one(filter)
        return self._to_model(data)
    
    async def find_many(self, filter: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[T]:
        """
        필터로 여러 항목 조회
        
        Args:
            filter: 필터
            skip: 건너뛸 항목 수 (기본값: 0)
            limit: 최대 항목 수 (기본값: 100)
            
        Returns:
            List[T]: 항목 목록
        """
        collection = await self._get_collection()
        cursor = collection.find(filter).skip(skip).limit(limit)
        result = []
        async for data in cursor:
            result.append(self._to_model(data))
        return result
    
    async def create(self, item: T) -> T:
        """
        항목 생성
        
        Args:
            item: 생성할 항목
            
        Returns:
            T: 생성된 항목
        """
        collection = await self._get_collection()
        document = self._to_document(item)
        
        # _id가 없으면 자동 생성
        if '_id' not in document:
            document['_id'] = ObjectId()
        
        # 생성 시간 추가
        if 'created_at' not in document:
            document['created_at'] = datetime.utcnow()
        
        # 업데이트 시간 추가
        document['updated_at'] = datetime.utcnow()
        
        result = await collection.insert_one(document)
        
        # 생성된 항목 반환
        return await self.find_by_id(str(result.inserted_id))
    
    async def update(self, id: str, item: T) -> Optional[T]:
        """
        항목 업데이트
        
        Args:
            id: 항목 ID
            item: 업데이트할 항목
            
        Returns:
            Optional[T]: 업데이트된 항목 또는 None
        """
        collection = await self._get_collection()
        document = self._to_document(item)
        
        # _id 제거 (변경 불가)
        if '_id' in document:
            del document['_id']
        
        # 업데이트 시간 추가
        document['updated_at'] = datetime.utcnow()
        
        result = await collection.update_one({"_id": ObjectId(id)}, {"$set": document})
        
        if result.matched_count == 0:
            return None
        
        # 업데이트된 항목 반환
        return await self.find_by_id(id)
    
    async def delete(self, id: str) -> bool:
        """
        항목 삭제
        
        Args:
            id: 항목 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        collection = await self._get_collection()
        result = await collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
    async def count(self, filter: Dict[str, Any]) -> int:
        """
        항목 수 조회
        
        Args:
            filter: 필터
            
        Returns:
            int: 항목 수
        """
        collection = await self._get_collection()
        return await collection.count_documents(filter)
