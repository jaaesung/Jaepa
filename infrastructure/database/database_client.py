"""
데이터베이스 클라이언트 모듈

데이터베이스 연결 및 기본 작업을 위한 인터페이스와 구현체를 제공합니다.
"""
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple, Set, Callable
from datetime import datetime

import pymongo
from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING, TEXT
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import (
    ConnectionFailure, ServerSelectionTimeoutError,
    OperationFailure, DuplicateKeyError
)

# 로깅 설정
logger = logging.getLogger(__name__)


class DatabaseClientInterface(ABC):
    """
    데이터베이스 클라이언트 인터페이스

    데이터베이스 연결 및 기본 작업을 위한 인터페이스를 정의합니다.
    """

    @abstractmethod
    def connect(self) -> bool:
        """
        데이터베이스 연결

        Returns:
            bool: 연결 성공 여부
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        데이터베이스 연결 종료
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            bool: 연결 상태
        """
        pass

    @abstractmethod
    def get_database(self, db_name: Optional[str] = None) -> Any:
        """
        데이터베이스 객체 가져오기

        Args:
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            Any: 데이터베이스 객체
        """
        pass

    @abstractmethod
    def get_collection(self, collection_name: str, db_name: Optional[str] = None) -> Any:
        """
        컬렉션 객체 가져오기

        Args:
            collection_name: 컬렉션 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            Any: 컬렉션 객체
        """
        pass

    @abstractmethod
    def create_index(
        self,
        collection_name: str,
        keys: List[Tuple[str, int]],
        index_name: Optional[str] = None,
        unique: bool = False,
        db_name: Optional[str] = None
    ) -> str:
        """
        인덱스 생성

        Args:
            collection_name: 컬렉션 이름
            keys: 인덱스 키 목록 [(필드명, 방향), ...]
            index_name: 인덱스 이름 (None인 경우 자동 생성)
            unique: 고유 인덱스 여부
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            str: 생성된 인덱스 이름
        """
        pass

    @abstractmethod
    def create_text_index(
        self,
        collection_name: str,
        fields: List[str],
        weights: Optional[Dict[str, int]] = None,
        index_name: Optional[str] = None,
        db_name: Optional[str] = None
    ) -> str:
        """
        텍스트 인덱스 생성

        Args:
            collection_name: 컬렉션 이름
            fields: 인덱스 필드 목록
            weights: 필드별 가중치 (None인 경우 모두 1)
            index_name: 인덱스 이름 (None인 경우 자동 생성)
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            str: 생성된 인덱스 이름
        """
        pass

    @abstractmethod
    def list_indexes(self, collection_name: str, db_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        인덱스 목록 조회

        Args:
            collection_name: 컬렉션 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            List[Dict[str, Any]]: 인덱스 정보 목록
        """
        pass

    @abstractmethod
    def drop_index(self, collection_name: str, index_name: str, db_name: Optional[str] = None) -> bool:
        """
        인덱스 삭제

        Args:
            collection_name: 컬렉션 이름
            index_name: 인덱스 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            bool: 삭제 성공 여부
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        데이터베이스 상태 확인

        Returns:
            Dict[str, Any]: 상태 정보
        """
        pass

    @abstractmethod
    def create_index(
        self,
        collection_name: str,
        keys: List[Tuple[str, int]],
        index_name: Optional[str] = None,
        unique: bool = False,
        db_name: Optional[str] = None
    ) -> str:
        """
        인덱스 생성

        Args:
            collection_name: 컬렉션 이름
            keys: 인덱스 키 목록 [(필드명, 방향), ...]
            index_name: 인덱스 이름 (None인 경우 자동 생성)
            unique: 고유 인덱스 여부
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            str: 생성된 인덱스 이름
        """
        pass

    @abstractmethod
    def create_text_index(
        self,
        collection_name: str,
        fields: List[str],
        weights: Optional[Dict[str, int]] = None,
        index_name: Optional[str] = None,
        db_name: Optional[str] = None
    ) -> str:
        """
        텍스트 인덱스 생성

        Args:
            collection_name: 컬렉션 이름
            fields: 인덱스 필드 목록
            weights: 필드별 가중치 (None인 경우 모두 1)
            index_name: 인덱스 이름 (None인 경우 자동 생성)
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            str: 생성된 인덱스 이름
        """
        pass

    @abstractmethod
    def list_indexes(self, collection_name: str, db_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        인덱스 목록 조회

        Args:
            collection_name: 컬렉션 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            List[Dict[str, Any]]: 인덱스 정보 목록
        """
        pass

    @abstractmethod
    def drop_index(self, collection_name: str, index_name: str, db_name: Optional[str] = None) -> bool:
        """
        인덱스 삭제

        Args:
            collection_name: 컬렉션 이름
            index_name: 인덱스 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            bool: 삭제 성공 여부
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        데이터베이스 상태 확인

        Returns:
            Dict[str, Any]: 상태 정보
        """
        pass

    @abstractmethod
    def begin_transaction(self) -> Any:
        """
        트랜잭션 시작

        Returns:
            Any: 트랜잭션 세션
        """
        pass

    @abstractmethod
    def commit_transaction(self, session: Any) -> bool:
        """
        트랜잭션 커밋

        Args:
            session: 트랜잭션 세션

        Returns:
            bool: 커밋 성공 여부
        """
        pass

    @abstractmethod
    def abort_transaction(self, session: Any) -> bool:
        """
        트랜잭션 롤백

        Args:
            session: 트랜잭션 세션

        Returns:
            bool: 롤백 성공 여부
        """
        pass

    @abstractmethod
    def with_transaction(self, callback: Callable[[Any], Any]) -> Any:
        """
        트랜잭션 내에서 콜백 실행

        Args:
            callback: 트랜잭션 내에서 실행할 콜백 함수

        Returns:
            Any: 콜백 함수의 반환값
        """
        pass


class MongoDBClient(DatabaseClientInterface):
    """
    MongoDB 클라이언트 구현

    MongoDB 데이터베이스 연결 및 기본 작업을 구현합니다.
    """

    def __init__(
        self,
        uri: str,
        default_db_name: str,
        connect_timeout: int = 5000,
        max_pool_size: int = 10,
        min_pool_size: int = 1,
        max_idle_time_ms: int = 60000,
        retry_writes: bool = True,
        retry_reads: bool = True,
        server_selection_timeout_ms: int = 30000,
        socket_timeout_ms: int = 30000,
        heartbeat_frequency_ms: int = 10000,
        app_name: str = "JaePa"
    ):
        """
        MongoDBClient 초기화

        Args:
            uri: MongoDB 연결 URI
            default_db_name: 기본 데이터베이스 이름
            connect_timeout: 연결 타임아웃 (밀리초)
            max_pool_size: 최대 연결 풀 크기
            min_pool_size: 최소 연결 풀 크기
            max_idle_time_ms: 최대 유휴 시간 (밀리초)
            retry_writes: 쓰기 재시도 여부
            retry_reads: 읽기 재시도 여부
            server_selection_timeout_ms: 서버 선택 타임아웃 (밀리초)
            socket_timeout_ms: 소켓 타임아웃 (밀리초)
            heartbeat_frequency_ms: 하트비트 주기 (밀리초)
            app_name: 애플리케이션 이름
        """
        self.uri = uri
        self.default_db_name = default_db_name
        self.connect_timeout = connect_timeout
        self.max_pool_size = max_pool_size
        self.min_pool_size = min_pool_size
        self.max_idle_time_ms = max_idle_time_ms
        self.retry_writes = retry_writes
        self.retry_reads = retry_reads
        self.server_selection_timeout_ms = server_selection_timeout_ms
        self.socket_timeout_ms = socket_timeout_ms
        self.heartbeat_frequency_ms = heartbeat_frequency_ms
        self.app_name = app_name

        self.client = None
        self.db = None
        self._connected = False
        self._last_connection_check = 0
        self._connection_check_interval = 60  # 초

    def connect(self) -> bool:
        """
        MongoDB 연결

        Returns:
            bool: 연결 성공 여부
        """
        if self.client is not None:
            return True

        try:
            # 연결 옵션 설정
            options = {
                "connectTimeoutMS": self.connect_timeout,
                "maxPoolSize": self.max_pool_size,
                "minPoolSize": self.min_pool_size,
                "maxIdleTimeMS": self.max_idle_time_ms,
                "retryWrites": self.retry_writes,
                "retryReads": self.retry_reads,
                "serverSelectionTimeoutMS": self.server_selection_timeout_ms,
                "socketTimeoutMS": self.socket_timeout_ms,
                "heartbeatFrequencyMS": self.heartbeat_frequency_ms,
                "appName": self.app_name
            }

            # MongoDB 클라이언트 생성
            self.client = MongoClient(self.uri, **options)

            # 연결 테스트
            self.client.admin.command('ping')

            # 기본 데이터베이스 설정
            self.db = self.client[self.default_db_name]

            self._connected = True
            self._last_connection_check = time.time()

            logger.info(f"MongoDB 연결 성공: {self.uri}, DB: {self.default_db_name}")
            return True

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB 연결 실패: {str(e)}")
            self.client = None
            self.db = None
            self._connected = False
            return False

        except Exception as e:
            logger.error(f"MongoDB 연결 중 예외 발생: {str(e)}")
            self.client = None
            self.db = None
            self._connected = False
            return False

    def close(self) -> None:
        """
        MongoDB 연결 종료
        """
        if self.client:
            try:
                self.client.close()
                logger.info("MongoDB 연결 종료")
            except Exception as e:
                logger.error(f"MongoDB 연결 종료 중 오류: {str(e)}")
            finally:
                self.client = None
                self.db = None
                self._connected = False

    def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            bool: 연결 상태
        """
        # 연결 상태 캐싱 (빈번한 확인 방지)
        current_time = time.time()
        if current_time - self._last_connection_check < self._connection_check_interval:
            return self._connected

        if not self.client:
            self._connected = False
            return False

        try:
            # 연결 테스트
            self.client.admin.command('ping')
            self._connected = True
            self._last_connection_check = current_time
            return True
        except Exception:
            self._connected = False
            return False

    def get_database(self, db_name: Optional[str] = None) -> Database:
        """
        데이터베이스 객체 가져오기

        Args:
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            Database: 데이터베이스 객체

        Raises:
            ConnectionError: 연결 실패 시
        """
        if not self.client:
            if not self.connect():
                raise ConnectionError("MongoDB 연결 실패")

        db_name = db_name or self.default_db_name
        return self.client[db_name]

    def get_collection(self, collection_name: str, db_name: Optional[str] = None) -> Collection:
        """
        컬렉션 객체 가져오기

        Args:
            collection_name: 컬렉션 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            Collection: 컬렉션 객체

        Raises:
            ConnectionError: 연결 실패 시
        """
        db = self.get_database(db_name)
        return db[collection_name]

    def create_index(
        self,
        collection_name: str,
        keys: List[Tuple[str, int]],
        index_name: Optional[str] = None,
        unique: bool = False,
        db_name: Optional[str] = None
    ) -> str:
        """
        인덱스 생성

        Args:
            collection_name: 컬렉션 이름
            keys: 인덱스 키 목록 [(필드명, 방향), ...]
            index_name: 인덱스 이름 (None인 경우 자동 생성)
            unique: 고유 인덱스 여부
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            str: 생성된 인덱스 이름

        Raises:
            ConnectionError: 연결 실패 시
            OperationError: 인덱스 생성 실패 시
        """
        collection = self.get_collection(collection_name, db_name)

        try:
            # 인덱스 생성
            index_name = collection.create_index(
                keys,
                name=index_name,
                unique=unique,
                background=True  # 백그라운드에서 인덱스 생성
            )

            logger.info(f"인덱스 생성 성공: {collection_name}.{index_name}")
            return index_name

        except DuplicateKeyError:
            logger.warning(f"이미 존재하는 인덱스: {collection_name}.{index_name}")
            return index_name

        except OperationFailure as e:
            logger.error(f"인덱스 생성 실패: {str(e)}")
            raise

    def create_text_index(
        self,
        collection_name: str,
        fields: List[str],
        weights: Optional[Dict[str, int]] = None,
        index_name: Optional[str] = None,
        db_name: Optional[str] = None
    ) -> str:
        """
        텍스트 인덱스 생성

        Args:
            collection_name: 컬렉션 이름
            fields: 인덱스 필드 목록
            weights: 필드별 가중치 (None인 경우 모두 1)
            index_name: 인덱스 이름 (None인 경우 자동 생성)
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            str: 생성된 인덱스 이름

        Raises:
            ConnectionError: 연결 실패 시
            OperationError: 인덱스 생성 실패 시
        """
        collection = self.get_collection(collection_name, db_name)

        try:
            # 기존 텍스트 인덱스 확인 및 삭제
            existing_indexes = collection.index_information()
            for idx_name, idx_info in existing_indexes.items():
                if 'weights' in idx_info:  # 텍스트 인덱스 식별
                    try:
                        collection.drop_index(idx_name)
                        logger.info(f"기존 텍스트 인덱스 '{idx_name}' 삭제됨")
                    except Exception as e:
                        logger.warning(f"텍스트 인덱스 '{idx_name}' 삭제 중 오류: {str(e)}")

            # 텍스트 인덱스 생성
            index_keys = [(field, pymongo.TEXT) for field in fields]

            # 인덱스 생성
            index_name = collection.create_index(
                index_keys,
                name=index_name,
                weights=weights,
                background=True  # 백그라운드에서 인덱스 생성
            )

            logger.info(f"텍스트 인덱스 생성 성공: {collection_name}.{index_name}")
            return index_name

        except OperationFailure as e:
            logger.error(f"텍스트 인덱스 생성 실패: {str(e)}")
            raise

    def list_indexes(self, collection_name: str, db_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        인덱스 목록 조회

        Args:
            collection_name: 컬렉션 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            List[Dict[str, Any]]: 인덱스 정보 목록

        Raises:
            ConnectionError: 연결 실패 시
        """
        collection = self.get_collection(collection_name, db_name)

        try:
            # 인덱스 정보 조회
            indexes = collection.index_information()

            # 결과 변환
            result = []
            for name, info in indexes.items():
                result.append({
                    "name": name,
                    "keys": info.get("key", []),
                    "unique": info.get("unique", False),
                    "weights": info.get("weights", {})
                })

            return result

        except Exception as e:
            logger.error(f"인덱스 목록 조회 실패: {str(e)}")
            raise

    def drop_index(self, collection_name: str, index_name: str, db_name: Optional[str] = None) -> bool:
        """
        인덱스 삭제

        Args:
            collection_name: 컬렉션 이름
            index_name: 인덱스 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            bool: 삭제 성공 여부

        Raises:
            ConnectionError: 연결 실패 시
        """
        collection = self.get_collection(collection_name, db_name)

        try:
            # 인덱스 삭제
            collection.drop_index(index_name)
            logger.info(f"인덱스 삭제 성공: {collection_name}.{index_name}")
            return True

        except OperationFailure as e:
            logger.error(f"인덱스 삭제 실패: {str(e)}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        데이터베이스 상태 확인

        Returns:
            Dict[str, Any]: 상태 정보
        """
        result = {
            "status": "unknown",
            "timestamp": datetime.now().isoformat(),
            "details": {}
        }

        if not self.client:
            result["status"] = "disconnected"
            return result

        try:
            # 연결 테스트
            start_time = time.time()
            self.client.admin.command('ping')
            response_time = time.time() - start_time

            # 서버 상태 조회
            server_status = self.client.admin.command('serverStatus')

            # 결과 설정
            result["status"] = "connected"
            result["details"] = {
                "response_time_ms": round(response_time * 1000, 2),
                "connections": {
                    "current": server_status.get("connections", {}).get("current", 0),
                    "available": server_status.get("connections", {}).get("available", 0),
                    "total_created": server_status.get("connections", {}).get("totalCreated", 0)
                },
                "version": server_status.get("version", "unknown")
            }

            return result

        except Exception as e:
            result["status"] = "error"
            result["details"] = {"error": str(e)}
            return result

    def begin_transaction(self) -> Any:
        """
        트랜잭션 시작

        Returns:
            Any: 트랜잭션 세션

        Raises:
            ConnectionError: 연결 실패 시
        """
        if not self.is_connected() and not self.connect():
            raise ConnectionError("MongoDB 연결 실패")

        try:
            # 세션 시작
            session = self.client.start_session()

            # 트랜잭션 시작
            session.start_transaction()

            logger.debug("트랜잭션 시작")
            return session

        except Exception as e:
            logger.error(f"트랜잭션 시작 실패: {str(e)}")
            raise

    def commit_transaction(self, session: Any) -> bool:
        """
        트랜잭션 커밋

        Args:
            session: 트랜잭션 세션

        Returns:
            bool: 커밋 성공 여부
        """
        if not session:
            logger.error("세션이 없습니다.")
            return False

        try:
            # 트랜잭션 커밋
            session.commit_transaction()
            session.end_session()

            logger.debug("트랜잭션 커밋 성공")
            return True

        except Exception as e:
            logger.error(f"트랜잭션 커밋 실패: {str(e)}")
            try:
                session.abort_transaction()
                session.end_session()
            except Exception:
                pass
            return False

    def abort_transaction(self, session: Any) -> bool:
        """
        트랜잭션 롤백

        Args:
            session: 트랜잭션 세션

        Returns:
            bool: 롤백 성공 여부
        """
        if not session:
            logger.error("세션이 없습니다.")
            return False

        try:
            # 트랜잭션 롤백
            session.abort_transaction()
            session.end_session()

            logger.debug("트랜잭션 롤백 성공")
            return True

        except Exception as e:
            logger.error(f"트랜잭션 롤백 실패: {str(e)}")
            try:
                session.end_session()
            except Exception:
                pass
            return False

    def with_transaction(self, callback: Callable[[Any], Any]) -> Any:
        """
        트랜잭션 내에서 콜백 실행

        Args:
            callback: 트랜잭션 내에서 실행할 콜백 함수

        Returns:
            Any: 콜백 함수의 반환값

        Raises:
            ConnectionError: 연결 실패 시
        """
        if not self.is_connected() and not self.connect():
            raise ConnectionError("MongoDB 연결 실패")

        session = None
        try:
            # 세션 시작
            session = self.client.start_session()

            # 트랜잭션 내에서 콜백 실행
            result = session.with_transaction(lambda s: callback(s))

            return result

        except Exception as e:
            logger.error(f"트랜잭션 실행 실패: {str(e)}")
            raise

        finally:
            if session:
                session.end_session()

    def connect(self) -> bool:
        """
        MongoDB 연결

        Returns:
            bool: 연결 성공 여부
        """
        if self.client is not None:
            return True

        try:
            # 연결 옵션 설정
            options = {
                "connectTimeoutMS": self.connect_timeout,
                "maxPoolSize": self.max_pool_size,
                "minPoolSize": self.min_pool_size,
                "maxIdleTimeMS": self.max_idle_time_ms,
                "retryWrites": self.retry_writes,
                "retryReads": self.retry_reads,
                "serverSelectionTimeoutMS": self.server_selection_timeout_ms,
                "socketTimeoutMS": self.socket_timeout_ms,
                "heartbeatFrequencyMS": self.heartbeat_frequency_ms,
                "appName": self.app_name
            }

            # MongoDB 클라이언트 생성
            self.client = MongoClient(self.uri, **options)

            # 연결 테스트
            self.client.admin.command('ping')

            # 기본 데이터베이스 설정
            self.db = self.client[self.default_db_name]

            self._connected = True
            self._last_connection_check = time.time()

            logger.info(f"MongoDB 연결 성공: {self.uri}, DB: {self.default_db_name}")
            return True

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB 연결 실패: {str(e)}")
            self.client = None
            self.db = None
            self._connected = False
            return False

        except Exception as e:
            logger.error(f"MongoDB 연결 중 예외 발생: {str(e)}")
            self.client = None
            self.db = None
            self._connected = False
            return False

    def close(self) -> None:
        """
        MongoDB 연결 종료
        """
        if self.client:
            try:
                self.client.close()
                logger.info("MongoDB 연결 종료")
            except Exception as e:
                logger.error(f"MongoDB 연결 종료 중 오류: {str(e)}")
            finally:
                self.client = None
                self.db = None
                self._connected = False

    def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            bool: 연결 상태
        """
        # 연결 상태 캐싱 (빈번한 확인 방지)
        current_time = time.time()
        if current_time - self._last_connection_check < self._connection_check_interval:
            return self._connected

        if not self.client:
            self._connected = False
            return False

        try:
            # 연결 테스트
            self.client.admin.command('ping')
            self._connected = True
            self._last_connection_check = current_time
            return True
        except Exception:
            self._connected = False
            return False

    def get_database(self, db_name: Optional[str] = None) -> Database:
        """
        데이터베이스 객체 가져오기

        Args:
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            Database: 데이터베이스 객체

        Raises:
            ConnectionError: 연결 실패 시
        """
        if not self.client:
            if not self.connect():
                raise ConnectionError("MongoDB 연결 실패")

        db_name = db_name or self.default_db_name
        return self.client[db_name]

    def get_collection(self, collection_name: str, db_name: Optional[str] = None) -> Collection:
        """
        컬렉션 객체 가져오기

        Args:
            collection_name: 컬렉션 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            Collection: 컬렉션 객체

        Raises:
            ConnectionError: 연결 실패 시
        """
        db = self.get_database(db_name)
        return db[collection_name]

    def create_index(
        self,
        collection_name: str,
        keys: List[Tuple[str, int]],
        index_name: Optional[str] = None,
        unique: bool = False,
        db_name: Optional[str] = None
    ) -> str:
        """
        인덱스 생성

        Args:
            collection_name: 컬렉션 이름
            keys: 인덱스 키 목록 [(필드명, 방향), ...]
            index_name: 인덱스 이름 (None인 경우 자동 생성)
            unique: 고유 인덱스 여부
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            str: 생성된 인덱스 이름

        Raises:
            ConnectionError: 연결 실패 시
            OperationError: 인덱스 생성 실패 시
        """
        collection = self.get_collection(collection_name, db_name)

        try:
            # 인덱스 생성
            index_name = collection.create_index(
                keys,
                name=index_name,
                unique=unique,
                background=True  # 백그라운드에서 인덱스 생성
            )

            logger.info(f"인덱스 생성 성공: {collection_name}.{index_name}")
            return index_name

        except DuplicateKeyError:
            logger.warning(f"이미 존재하는 인덱스: {collection_name}.{index_name}")
            return index_name

        except OperationFailure as e:
            logger.error(f"인덱스 생성 실패: {str(e)}")
            raise

    def create_text_index(
        self,
        collection_name: str,
        fields: List[str],
        weights: Optional[Dict[str, int]] = None,
        index_name: Optional[str] = None,
        db_name: Optional[str] = None
    ) -> str:
        """
        텍스트 인덱스 생성

        Args:
            collection_name: 컬렉션 이름
            fields: 인덱스 필드 목록
            weights: 필드별 가중치 (None인 경우 모두 1)
            index_name: 인덱스 이름 (None인 경우 자동 생성)
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            str: 생성된 인덱스 이름

        Raises:
            ConnectionError: 연결 실패 시
            OperationError: 인덱스 생성 실패 시
        """
        collection = self.get_collection(collection_name, db_name)

        try:
            # 기존 텍스트 인덱스 확인 및 삭제
            existing_indexes = collection.index_information()
            for idx_name, idx_info in existing_indexes.items():
                if 'weights' in idx_info:  # 텍스트 인덱스 식별
                    try:
                        collection.drop_index(idx_name)
                        logger.info(f"기존 텍스트 인덱스 '{idx_name}' 삭제됨")
                    except Exception as e:
                        logger.warning(f"텍스트 인덱스 '{idx_name}' 삭제 중 오류: {str(e)}")

            # 텍스트 인덱스 생성
            index_keys = [(field, pymongo.TEXT) for field in fields]

            # 인덱스 생성
            index_name = collection.create_index(
                index_keys,
                name=index_name,
                weights=weights,
                background=True  # 백그라운드에서 인덱스 생성
            )

            logger.info(f"텍스트 인덱스 생성 성공: {collection_name}.{index_name}")
            return index_name

        except OperationFailure as e:
            logger.error(f"텍스트 인덱스 생성 실패: {str(e)}")
            raise

    def list_indexes(self, collection_name: str, db_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        인덱스 목록 조회

        Args:
            collection_name: 컬렉션 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            List[Dict[str, Any]]: 인덱스 정보 목록

        Raises:
            ConnectionError: 연결 실패 시
        """
        collection = self.get_collection(collection_name, db_name)

        try:
            # 인덱스 정보 조회
            indexes = collection.index_information()

            # 결과 변환
            result = []
            for name, info in indexes.items():
                result.append({
                    "name": name,
                    "keys": info.get("key", []),
                    "unique": info.get("unique", False),
                    "weights": info.get("weights", {})
                })

            return result

        except Exception as e:
            logger.error(f"인덱스 목록 조회 실패: {str(e)}")
            raise

    def drop_index(self, collection_name: str, index_name: str, db_name: Optional[str] = None) -> bool:
        """
        인덱스 삭제

        Args:
            collection_name: 컬렉션 이름
            index_name: 인덱스 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            bool: 삭제 성공 여부

        Raises:
            ConnectionError: 연결 실패 시
        """
        collection = self.get_collection(collection_name, db_name)

        try:
            # 인덱스 삭제
            collection.drop_index(index_name)
            logger.info(f"인덱스 삭제 성공: {collection_name}.{index_name}")
            return True

        except OperationFailure as e:
            logger.error(f"인덱스 삭제 실패: {str(e)}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        데이터베이스 상태 확인

        Returns:
            Dict[str, Any]: 상태 정보
        """
        result = {
            "status": "unknown",
            "timestamp": datetime.now().isoformat(),
            "details": {}
        }

        if not self.client:
            result["status"] = "disconnected"
            return result

        try:
            # 연결 테스트
            start_time = time.time()
            self.client.admin.command('ping')
            response_time = time.time() - start_time

            # 서버 상태 조회
            server_status = self.client.admin.command('serverStatus')

            # 결과 설정
            result["status"] = "connected"
            result["details"] = {
                "response_time_ms": round(response_time * 1000, 2),
                "connections": {
                    "current": server_status.get("connections", {}).get("current", 0),
                    "available": server_status.get("connections", {}).get("available", 0),
                    "total_created": server_status.get("connections", {}).get("totalCreated", 0)
                },
                "version": server_status.get("version", "unknown")
            }

            return result

        except Exception as e:
            result["status"] = "error"
            result["details"] = {"error": str(e)}
            return result

    def connect(self) -> bool:
        """
        MongoDB 연결

        Returns:
            bool: 연결 성공 여부
        """
        if self.client is not None:
            return True

        try:
            # 연결 옵션 설정
            options = {
                "connectTimeoutMS": self.connect_timeout,
                "maxPoolSize": self.max_pool_size,
                "minPoolSize": self.min_pool_size,
                "maxIdleTimeMS": self.max_idle_time_ms,
                "retryWrites": self.retry_writes,
                "retryReads": self.retry_reads,
                "serverSelectionTimeoutMS": self.server_selection_timeout_ms,
                "socketTimeoutMS": self.socket_timeout_ms,
                "heartbeatFrequencyMS": self.heartbeat_frequency_ms,
                "appName": self.app_name
            }

            # MongoDB 클라이언트 생성
            self.client = MongoClient(self.uri, **options)

            # 연결 테스트
            self.client.admin.command('ping')

            # 기본 데이터베이스 설정
            self.db = self.client[self.default_db_name]

            self._connected = True
            self._last_connection_check = time.time()

            logger.info(f"MongoDB 연결 성공: {self.uri}, DB: {self.default_db_name}")
            return True

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB 연결 실패: {str(e)}")
            self.client = None
            self.db = None
            self._connected = False
            return False

        except Exception as e:
            logger.error(f"MongoDB 연결 중 예외 발생: {str(e)}")
            self.client = None
            self.db = None
            self._connected = False
            return False

    def close(self) -> None:
        """
        MongoDB 연결 종료
        """
        if self.client:
            try:
                self.client.close()
                logger.info("MongoDB 연결 종료")
            except Exception as e:
                logger.error(f"MongoDB 연결 종료 중 오류: {str(e)}")
            finally:
                self.client = None
                self.db = None
                self._connected = False

    def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            bool: 연결 상태
        """
        # 연결 상태 캐싱 (빈번한 확인 방지)
        current_time = time.time()
        if current_time - self._last_connection_check < self._connection_check_interval:
            return self._connected

        if not self.client:
            self._connected = False
            return False

        try:
            # 연결 테스트
            self.client.admin.command('ping')
            self._connected = True
            self._last_connection_check = current_time
            return True
        except Exception:
            self._connected = False
            return False

    def get_database(self, db_name: Optional[str] = None) -> Database:
        """
        데이터베이스 객체 가져오기

        Args:
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            Database: 데이터베이스 객체

        Raises:
            ConnectionError: 연결 실패 시
        """
        if not self.is_connected() and not self.connect():
            raise ConnectionError("MongoDB 연결 실패")

        db_name = db_name or self.default_db_name
        return self.client[db_name]

    def get_collection(self, collection_name: str, db_name: Optional[str] = None) -> Collection:
        """
        컬렉션 객체 가져오기

        Args:
            collection_name: 컬렉션 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            Collection: 컬렉션 객체

        Raises:
            ConnectionError: 연결 실패 시
        """
        db = self.get_database(db_name)
        return db[collection_name]

    def create_index(
        self,
        collection_name: str,
        keys: List[Tuple[str, int]],
        index_name: Optional[str] = None,
        unique: bool = False,
        db_name: Optional[str] = None
    ) -> str:
        """
        인덱스 생성

        Args:
            collection_name: 컬렉션 이름
            keys: 인덱스 키 목록 [(필드명, 방향), ...]
            index_name: 인덱스 이름 (None인 경우 자동 생성)
            unique: 고유 인덱스 여부
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            str: 생성된 인덱스 이름

        Raises:
            ConnectionError: 연결 실패 시
            OperationError: 인덱스 생성 실패 시
        """
        collection = self.get_collection(collection_name, db_name)

        try:
            # 인덱스 생성
            index_name = collection.create_index(
                keys,
                name=index_name,
                unique=unique,
                background=True  # 백그라운드에서 인덱스 생성
            )

            logger.info(f"인덱스 생성 성공: {collection_name}.{index_name}")
            return index_name

        except DuplicateKeyError:
            logger.warning(f"이미 존재하는 인덱스: {collection_name}.{index_name}")
            return index_name

        except OperationFailure as e:
            logger.error(f"인덱스 생성 실패: {str(e)}")
            raise

    def create_text_index(
        self,
        collection_name: str,
        fields: List[str],
        weights: Optional[Dict[str, int]] = None,
        index_name: Optional[str] = None,
        db_name: Optional[str] = None
    ) -> str:
        """
        텍스트 인덱스 생성

        Args:
            collection_name: 컬렉션 이름
            fields: 인덱스 필드 목록
            weights: 필드별 가중치 (None인 경우 모두 1)
            index_name: 인덱스 이름 (None인 경우 자동 생성)
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            str: 생성된 인덱스 이름

        Raises:
            ConnectionError: 연결 실패 시
            OperationError: 인덱스 생성 실패 시
        """
        collection = self.get_collection(collection_name, db_name)

        try:
            # 기존 텍스트 인덱스 확인 및 삭제
            existing_indexes = collection.index_information()
            for idx_name, idx_info in existing_indexes.items():
                if 'weights' in idx_info:  # 텍스트 인덱스 식별
                    try:
                        collection.drop_index(idx_name)
                        logger.info(f"기존 텍스트 인덱스 '{idx_name}' 삭제됨")
                    except Exception as e:
                        logger.warning(f"텍스트 인덱스 '{idx_name}' 삭제 중 오류: {str(e)}")

            # 텍스트 인덱스 생성
            index_keys = [(field, TEXT) for field in fields]

            # 인덱스 생성
            index_name = collection.create_index(
                index_keys,
                name=index_name,
                weights=weights,
                background=True  # 백그라운드에서 인덱스 생성
            )

            logger.info(f"텍스트 인덱스 생성 성공: {collection_name}.{index_name}")
            return index_name

        except OperationFailure as e:
            logger.error(f"텍스트 인덱스 생성 실패: {str(e)}")
            raise

    def list_indexes(self, collection_name: str, db_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        인덱스 목록 조회

        Args:
            collection_name: 컬렉션 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            List[Dict[str, Any]]: 인덱스 정보 목록

        Raises:
            ConnectionError: 연결 실패 시
        """
        collection = self.get_collection(collection_name, db_name)

        try:
            # 인덱스 정보 조회
            indexes = collection.index_information()

            # 결과 변환
            result = []
            for name, info in indexes.items():
                result.append({
                    "name": name,
                    "keys": info.get("key", []),
                    "unique": info.get("unique", False),
                    "weights": info.get("weights", {})
                })

            return result

        except Exception as e:
            logger.error(f"인덱스 목록 조회 실패: {str(e)}")
            raise

    def drop_index(self, collection_name: str, index_name: str, db_name: Optional[str] = None) -> bool:
        """
        인덱스 삭제

        Args:
            collection_name: 컬렉션 이름
            index_name: 인덱스 이름
            db_name: 데이터베이스 이름 (None인 경우 기본 데이터베이스)

        Returns:
            bool: 삭제 성공 여부

        Raises:
            ConnectionError: 연결 실패 시
        """
        collection = self.get_collection(collection_name, db_name)

        try:
            # 인덱스 삭제
            collection.drop_index(index_name)
            logger.info(f"인덱스 삭제 성공: {collection_name}.{index_name}")
            return True

        except OperationFailure as e:
            logger.error(f"인덱스 삭제 실패: {str(e)}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        데이터베이스 상태 확인

        Returns:
            Dict[str, Any]: 상태 정보
        """
        result = {
            "status": "unknown",
            "timestamp": datetime.now().isoformat(),
            "details": {}
        }

        if not self.client:
            result["status"] = "disconnected"
            return result

        try:
            # 연결 테스트
            start_time = time.time()
            self.client.admin.command('ping')
            response_time = time.time() - start_time

            # 서버 상태 조회
            server_status = self.client.admin.command('serverStatus')

            # 결과 설정
            result["status"] = "connected"
            result["details"] = {
                "response_time_ms": round(response_time * 1000, 2),
                "connections": {
                    "current": server_status.get("connections", {}).get("current", 0),
                    "available": server_status.get("connections", {}).get("available", 0),
                    "total_created": server_status.get("connections", {}).get("totalCreated", 0)
                },
                "version": server_status.get("version", "unknown")
            }

            return result

        except Exception as e:
            result["status"] = "error"
            result["details"] = {"error": str(e)}
            return result

    def begin_transaction(self) -> Any:
        """
        트랜잭션 시작

        Returns:
            Any: 트랜잭션 세션

        Raises:
            ConnectionError: 연결 실패 시
        """
        if not self.is_connected() and not self.connect():
            raise ConnectionError("MongoDB 연결 실패")

        try:
            # 세션 시작
            session = self.client.start_session()

            # 트랜잭션 시작
            session.start_transaction()

            logger.debug("트랜잭션 시작")
            return session

        except Exception as e:
            logger.error(f"트랜잭션 시작 실패: {str(e)}")
            raise

    def commit_transaction(self, session: Any) -> bool:
        """
        트랜잭션 커밋

        Args:
            session: 트랜잭션 세션

        Returns:
            bool: 커밋 성공 여부
        """
        if not session:
            logger.error("세션이 없습니다.")
            return False

        try:
            # 트랜잭션 커밋
            session.commit_transaction()
            session.end_session()

            logger.debug("트랜잭션 커밋 성공")
            return True

        except Exception as e:
            logger.error(f"트랜잭션 커밋 실패: {str(e)}")
            try:
                session.abort_transaction()
                session.end_session()
            except Exception:
                pass
            return False

    def abort_transaction(self, session: Any) -> bool:
        """
        트랜잭션 롤백

        Args:
            session: 트랜잭션 세션

        Returns:
            bool: 롤백 성공 여부
        """
        if not session:
            logger.error("세션이 없습니다.")
            return False

        try:
            # 트랜잭션 롤백
            session.abort_transaction()
            session.end_session()

            logger.debug("트랜잭션 롤백 성공")
            return True

        except Exception as e:
            logger.error(f"트랜잭션 롤백 실패: {str(e)}")
            try:
                session.end_session()
            except Exception:
                pass
            return False

    def with_transaction(self, callback: Callable[[Any], Any]) -> Any:
        """
        트랜잭션 내에서 콜백 실행

        Args:
            callback: 트랜잭션 내에서 실행할 콜백 함수

        Returns:
            Any: 콜백 함수의 반환값

        Raises:
            ConnectionError: 연결 실패 시
        """
        if not self.is_connected() and not self.connect():
            raise ConnectionError("MongoDB 연결 실패")

        session = None
        try:
            # 세션 시작
            session = self.client.start_session()

            # 트랜잭션 내에서 콜백 실행
            result = session.with_transaction(lambda s: callback(s))

            return result

        except Exception as e:
            logger.error(f"트랜잭션 실행 실패: {str(e)}")
            raise

        finally:
            if session:
                session.end_session()
