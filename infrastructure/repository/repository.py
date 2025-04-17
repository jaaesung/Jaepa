"""
저장소 인터페이스 모듈

데이터 저장소의 기본 인터페이스를 제공합니다.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Generic, TypeVar, Set
from datetime import datetime

from infrastructure.database.database_client import DatabaseClientInterface

# 로깅 설정
logger = logging.getLogger(__name__)

# 제네릭 타입 변수
T = TypeVar('T')
ID = TypeVar('ID')


class RepositoryInterface(Generic[T, ID], ABC):
    """
    저장소 인터페이스
    
    데이터 저장소의 기본 인터페이스를 정의합니다.
    """
    
    @abstractmethod
    async def find_by_id(self, id: ID) -> Optional[T]:
        """
        ID로 엔티티 조회
        
        Args:
            id: 엔티티 ID
            
        Returns:
            Optional[T]: 조회된 엔티티 또는 None
        """
        pass
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        모든 엔티티 조회
        
        Args:
            skip: 건너뛸 개수
            limit: 최대 개수
            
        Returns:
            List[T]: 조회된 엔티티 목록
        """
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """
        엔티티 저장
        
        Args:
            entity: 저장할 엔티티
            
        Returns:
            T: 저장된 엔티티
        """
        pass
    
    @abstractmethod
    async def save_many(self, entities: List[T]) -> List[T]:
        """
        여러 엔티티 저장
        
        Args:
            entities: 저장할 엔티티 목록
            
        Returns:
            List[T]: 저장된 엔티티 목록
        """
        pass
    
    @abstractmethod
    async def update(self, id: ID, entity: T) -> Optional[T]:
        """
        엔티티 업데이트
        
        Args:
            id: 엔티티 ID
            entity: 업데이트할 엔티티
            
        Returns:
            Optional[T]: 업데이트된 엔티티 또는 None
        """
        pass
    
    @abstractmethod
    async def delete(self, id: ID) -> bool:
        """
        엔티티 삭제
        
        Args:
            id: 엔티티 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """
        엔티티 개수 조회
        
        Returns:
            int: 엔티티 개수
        """
        pass
    
    @abstractmethod
    async def exists(self, id: ID) -> bool:
        """
        엔티티 존재 여부 확인
        
        Args:
            id: 엔티티 ID
            
        Returns:
            bool: 존재 여부
        """
        pass


class MongoRepositoryInterface(RepositoryInterface[T, ID], ABC):
    """
    MongoDB 저장소 인터페이스
    
    MongoDB 기반 데이터 저장소의 기본 인터페이스를 정의합니다.
    """
    
    @abstractmethod
    async def find_by_query(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[T]:
        """
        쿼리로 엔티티 조회
        
        Args:
            query: MongoDB 쿼리
            skip: 건너뛸 개수
            limit: 최대 개수
            
        Returns:
            List[T]: 조회된 엔티티 목록
        """
        pass
    
    @abstractmethod
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[T]:
        """
        쿼리로 단일 엔티티 조회
        
        Args:
            query: MongoDB 쿼리
            
        Returns:
            Optional[T]: 조회된 엔티티 또는 None
        """
        pass
    
    @abstractmethod
    async def count_by_query(self, query: Dict[str, Any]) -> int:
        """
        쿼리로 엔티티 개수 조회
        
        Args:
            query: MongoDB 쿼리
            
        Returns:
            int: 엔티티 개수
        """
        pass
    
    @abstractmethod
    async def update_by_query(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """
        쿼리로 엔티티 업데이트
        
        Args:
            query: MongoDB 쿼리
            update: 업데이트 내용
            
        Returns:
            int: 업데이트된 엔티티 개수
        """
        pass
    
    @abstractmethod
    async def delete_by_query(self, query: Dict[str, Any]) -> int:
        """
        쿼리로 엔티티 삭제
        
        Args:
            query: MongoDB 쿼리
            
        Returns:
            int: 삭제된 엔티티 개수
        """
        pass
    
    @abstractmethod
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        집계 파이프라인 실행
        
        Args:
            pipeline: MongoDB 집계 파이프라인
            
        Returns:
            List[Dict[str, Any]]: 집계 결과
        """
        pass
    
    @abstractmethod
    async def create_indexes(self) -> List[str]:
        """
        인덱스 생성
        
        Returns:
            List[str]: 생성된 인덱스 이름 목록
        """
        pass


class BaseMongoRepository(MongoRepositoryInterface[T, ID], ABC):
    """
    MongoDB 저장소 기본 구현
    
    MongoDB 기반 데이터 저장소의 기본 구현을 제공합니다.
    """
    
    def __init__(self, client: DatabaseClientInterface, db_name: str, collection_name: str):
        """
        BaseMongoRepository 초기화
        
        Args:
            client: MongoDB 클라이언트
            db_name: 데이터베이스 이름
            collection_name: 컬렉션 이름
        """
        self.client = client
        self.db_name = db_name
        self.collection_name = collection_name
        self._collection = None
    
    @property
    def collection(self):
        """
        컬렉션 객체 가져오기
        
        Returns:
            Collection: MongoDB 컬렉션 객체
        """
        if self._collection is None:
            self._collection = self.client.get_collection(self.collection_name, self.db_name)
        return self._collection
    
    async def find_by_id(self, id: ID) -> Optional[T]:
        """
        ID로 엔티티 조회
        
        Args:
            id: 엔티티 ID
            
        Returns:
            Optional[T]: 조회된 엔티티 또는 None
        """
        try:
            # ID 변환
            object_id = self._convert_id(id)
            
            # 엔티티 조회
            document = await self.collection.find_one({"_id": object_id})
            
            if document:
                return self._to_entity(document)
            return None
            
        except Exception as e:
            logger.error(f"ID로 엔티티 조회 실패: {str(e)}")
            return None
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        모든 엔티티 조회
        
        Args:
            skip: 건너뛸 개수
            limit: 최대 개수
            
        Returns:
            List[T]: 조회된 엔티티 목록
        """
        try:
            # 엔티티 조회
            cursor = self.collection.find().skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # 엔티티 변환
            return [self._to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"모든 엔티티 조회 실패: {str(e)}")
            return []
    
    async def save(self, entity: T) -> T:
        """
        엔티티 저장
        
        Args:
            entity: 저장할 엔티티
            
        Returns:
            T: 저장된 엔티티
        """
        try:
            # 엔티티를 문서로 변환
            document = self._to_document(entity)
            
            # ID 확인
            if "_id" in document:
                # 업데이트
                result = await self.collection.replace_one(
                    {"_id": document["_id"]},
                    document,
                    upsert=True
                )
                
                if result.modified_count > 0 or result.upserted_id:
                    logger.debug(f"엔티티 업데이트 성공: {document.get('_id')}")
                else:
                    logger.warning(f"엔티티 업데이트 실패: {document.get('_id')}")
            else:
                # 삽입
                result = await self.collection.insert_one(document)
                
                if result.inserted_id:
                    logger.debug(f"엔티티 삽입 성공: {result.inserted_id}")
                    document["_id"] = result.inserted_id
                else:
                    logger.warning("엔티티 삽입 실패")
            
            # 저장된 엔티티 반환
            return self._to_entity(document)
            
        except Exception as e:
            logger.error(f"엔티티 저장 실패: {str(e)}")
            raise
    
    async def save_many(self, entities: List[T]) -> List[T]:
        """
        여러 엔티티 저장
        
        Args:
            entities: 저장할 엔티티 목록
            
        Returns:
            List[T]: 저장된 엔티티 목록
        """
        if not entities:
            return []
        
        try:
            # 엔티티를 문서로 변환
            documents = [self._to_document(entity) for entity in entities]
            
            # ID가 있는 문서와 없는 문서 분리
            documents_with_id = [doc for doc in documents if "_id" in doc]
            documents_without_id = [doc for doc in documents if "_id" not in doc]
            
            saved_documents = []
            
            # ID가 있는 문서 업데이트
            if documents_with_id:
                # 개별 업데이트 (bulk_write 대신 개별 처리)
                for doc in documents_with_id:
                    result = await self.collection.replace_one(
                        {"_id": doc["_id"]},
                        doc,
                        upsert=True
                    )
                    
                    if result.modified_count > 0 or result.upserted_id:
                        saved_documents.append(doc)
            
            # ID가 없는 문서 삽입
            if documents_without_id:
                result = await self.collection.insert_many(documents_without_id)
                
                if result.inserted_ids:
                    # 삽입된 ID 설정
                    for i, doc in enumerate(documents_without_id):
                        doc["_id"] = result.inserted_ids[i]
                        saved_documents.append(doc)
            
            # 저장된 엔티티 반환
            return [self._to_entity(doc) for doc in saved_documents]
            
        except Exception as e:
            logger.error(f"여러 엔티티 저장 실패: {str(e)}")
            raise
    
    async def update(self, id: ID, entity: T) -> Optional[T]:
        """
        엔티티 업데이트
        
        Args:
            id: 엔티티 ID
            entity: 업데이트할 엔티티
            
        Returns:
            Optional[T]: 업데이트된 엔티티 또는 None
        """
        try:
            # ID 변환
            object_id = self._convert_id(id)
            
            # 엔티티를 문서로 변환
            document = self._to_document(entity)
            
            # ID 설정
            document["_id"] = object_id
            
            # 업데이트
            result = await self.collection.replace_one(
                {"_id": object_id},
                document
            )
            
            if result.modified_count > 0:
                logger.debug(f"엔티티 업데이트 성공: {id}")
                return self._to_entity(document)
            
            logger.warning(f"엔티티 업데이트 실패: {id}")
            return None
            
        except Exception as e:
            logger.error(f"엔티티 업데이트 실패: {str(e)}")
            return None
    
    async def delete(self, id: ID) -> bool:
        """
        엔티티 삭제
        
        Args:
            id: 엔티티 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            # ID 변환
            object_id = self._convert_id(id)
            
            # 삭제
            result = await self.collection.delete_one({"_id": object_id})
            
            if result.deleted_count > 0:
                logger.debug(f"엔티티 삭제 성공: {id}")
                return True
            
            logger.warning(f"엔티티 삭제 실패: {id}")
            return False
            
        except Exception as e:
            logger.error(f"엔티티 삭제 실패: {str(e)}")
            return False
    
    async def count(self) -> int:
        """
        엔티티 개수 조회
        
        Returns:
            int: 엔티티 개수
        """
        try:
            # 개수 조회
            count = await self.collection.count_documents({})
            return count
            
        except Exception as e:
            logger.error(f"엔티티 개수 조회 실패: {str(e)}")
            return 0
    
    async def exists(self, id: ID) -> bool:
        """
        엔티티 존재 여부 확인
        
        Args:
            id: 엔티티 ID
            
        Returns:
            bool: 존재 여부
        """
        try:
            # ID 변환
            object_id = self._convert_id(id)
            
            # 존재 여부 확인
            count = await self.collection.count_documents({"_id": object_id}, limit=1)
            return count > 0
            
        except Exception as e:
            logger.error(f"엔티티 존재 여부 확인 실패: {str(e)}")
            return False
    
    async def find_by_query(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[T]:
        """
        쿼리로 엔티티 조회
        
        Args:
            query: MongoDB 쿼리
            skip: 건너뛸 개수
            limit: 최대 개수
            
        Returns:
            List[T]: 조회된 엔티티 목록
        """
        try:
            # 엔티티 조회
            cursor = self.collection.find(query).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # 엔티티 변환
            return [self._to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"쿼리로 엔티티 조회 실패: {str(e)}")
            return []
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[T]:
        """
        쿼리로 단일 엔티티 조회
        
        Args:
            query: MongoDB 쿼리
            
        Returns:
            Optional[T]: 조회된 엔티티 또는 None
        """
        try:
            # 엔티티 조회
            document = await self.collection.find_one(query)
            
            if document:
                return self._to_entity(document)
            return None
            
        except Exception as e:
            logger.error(f"쿼리로 단일 엔티티 조회 실패: {str(e)}")
            return None
    
    async def count_by_query(self, query: Dict[str, Any]) -> int:
        """
        쿼리로 엔티티 개수 조회
        
        Args:
            query: MongoDB 쿼리
            
        Returns:
            int: 엔티티 개수
        """
        try:
            # 개수 조회
            count = await self.collection.count_documents(query)
            return count
            
        except Exception as e:
            logger.error(f"쿼리로 엔티티 개수 조회 실패: {str(e)}")
            return 0
    
    async def update_by_query(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """
        쿼리로 엔티티 업데이트
        
        Args:
            query: MongoDB 쿼리
            update: 업데이트 내용
            
        Returns:
            int: 업데이트된 엔티티 개수
        """
        try:
            # 업데이트
            result = await self.collection.update_many(query, update)
            
            if result.modified_count > 0:
                logger.debug(f"쿼리로 엔티티 업데이트 성공: {result.modified_count}개")
            else:
                logger.warning("쿼리로 엔티티 업데이트 실패")
            
            return result.modified_count
            
        except Exception as e:
            logger.error(f"쿼리로 엔티티 업데이트 실패: {str(e)}")
            return 0
    
    async def delete_by_query(self, query: Dict[str, Any]) -> int:
        """
        쿼리로 엔티티 삭제
        
        Args:
            query: MongoDB 쿼리
            
        Returns:
            int: 삭제된 엔티티 개수
        """
        try:
            # 삭제
            result = await self.collection.delete_many(query)
            
            if result.deleted_count > 0:
                logger.debug(f"쿼리로 엔티티 삭제 성공: {result.deleted_count}개")
            else:
                logger.warning("쿼리로 엔티티 삭제 실패")
            
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"쿼리로 엔티티 삭제 실패: {str(e)}")
            return 0
    
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        집계 파이프라인 실행
        
        Args:
            pipeline: MongoDB 집계 파이프라인
            
        Returns:
            List[Dict[str, Any]]: 집계 결과
        """
        try:
            # 집계 실행
            cursor = self.collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            return results
            
        except Exception as e:
            logger.error(f"집계 파이프라인 실행 실패: {str(e)}")
            return []
    
    async def create_indexes(self) -> List[str]:
        """
        인덱스 생성
        
        Returns:
            List[str]: 생성된 인덱스 이름 목록
        """
        try:
            # 인덱스 정의
            indexes = self._define_indexes()
            
            if not indexes:
                return []
            
            # 인덱스 생성
            created_indexes = []
            for index in indexes:
                try:
                    index_name = await self.collection.create_index(**index)
                    created_indexes.append(index_name)
                    logger.info(f"인덱스 생성 성공: {self.collection_name}.{index_name}")
                except Exception as e:
                    logger.error(f"인덱스 생성 실패: {str(e)}")
            
            return created_indexes
            
        except Exception as e:
            logger.error(f"인덱스 생성 실패: {str(e)}")
            return []
    
    def _define_indexes(self) -> List[Dict[str, Any]]:
        """
        인덱스 정의
        
        Returns:
            List[Dict[str, Any]]: 인덱스 정의 목록
        """
        # 기본 구현은 빈 목록 반환
        # 하위 클래스에서 오버라이드하여 인덱스 정의
        return []
    
    def _convert_id(self, id: ID) -> Any:
        """
        ID 변환
        
        Args:
            id: 엔티티 ID
            
        Returns:
            Any: 변환된 ID
        """
        # 기본 구현은 ID를 그대로 반환
        # 하위 클래스에서 오버라이드하여 ID 변환 (예: 문자열 -> ObjectId)
        return id
    
    @abstractmethod
    def _to_entity(self, document: Dict[str, Any]) -> T:
        """
        문서를 엔티티로 변환
        
        Args:
            document: MongoDB 문서
            
        Returns:
            T: 변환된 엔티티
        """
        pass
    
    @abstractmethod
    def _to_document(self, entity: T) -> Dict[str, Any]:
        """
        엔티티를 문서로 변환
        
        Args:
            entity: 엔티티
            
        Returns:
            Dict[str, Any]: 변환된 문서
        """
        pass
