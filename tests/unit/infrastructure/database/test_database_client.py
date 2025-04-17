"""
데이터베이스 클라이언트 단위 테스트

이 모듈은 데이터베이스 클라이언트 클래스를 테스트합니다.
"""
import pytest
import pytest_asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from infrastructure.database.database_client import DatabaseClientInterface, MongoDBClient


class TestMongoDBClient(unittest.TestCase):
    """
    MongoDB 클라이언트 테스트 클래스
    """

    def setUp(self):
        """
        테스트 설정
        """
        # 테스트용 설정
        self.test_uri = "mongodb://localhost:27017/"
        self.test_db_name = "test_db"

        # 클라이언트 생성
        self.client = MongoDBClient(
            uri=self.test_uri,
            default_db_name=self.test_db_name,
            connect_timeout=1000,
            max_pool_size=5,
            min_pool_size=1,
            max_idle_time_ms=10000,
            retry_writes=True,
            retry_reads=True,
            server_selection_timeout_ms=5000,
            socket_timeout_ms=5000,
            heartbeat_frequency_ms=5000,
            app_name="test_app"
        )

    def tearDown(self):
        """
        테스트 종료 처리
        """
        # 클라이언트 연결 종료
        if self.client:
            self.client.close()

    def test_init(self):
        """
        초기화 테스트
        """
        # 초기화 확인
        self.assertEqual(self.client.uri, self.test_uri)
        self.assertEqual(self.client.default_db_name, self.test_db_name)
        self.assertEqual(self.client.connect_timeout, 1000)
        self.assertEqual(self.client.max_pool_size, 5)
        self.assertEqual(self.client.min_pool_size, 1)
        self.assertEqual(self.client.max_idle_time_ms, 10000)
        self.assertTrue(self.client.retry_writes)
        self.assertTrue(self.client.retry_reads)
        self.assertEqual(self.client.server_selection_timeout_ms, 5000)
        self.assertEqual(self.client.socket_timeout_ms, 5000)
        self.assertEqual(self.client.heartbeat_frequency_ms, 5000)
        self.assertEqual(self.client.app_name, "test_app")

        # 클라이언트 초기 상태 확인
        self.assertIsNone(self.client.client)
        self.assertIsNone(self.client.db)
        self.assertFalse(self.client._connected)

    @patch('infrastructure.database.database_client.MongoClient')
    def test_connect_success(self, mock_mongo_client):
        """
        연결 성공 테스트

        Args:
            mock_mongo_client: 모의 MongoDB 클라이언트
        """
        # 모의 객체 설정
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_admin = MagicMock()

        mock_client.__getitem__.return_value = mock_db
        mock_client.admin = mock_admin
        mock_mongo_client.return_value = mock_client

        # 연결 테스트
        result = self.client.connect()

        # 검증
        self.assertTrue(result)
        self.assertTrue(self.client._connected)
        self.assertIsNotNone(self.client.client)
        self.assertIsNotNone(self.client.db)

        # 호출 검증
        mock_mongo_client.assert_called_once()
        mock_admin.command.assert_called_once_with('ping')

    @patch('infrastructure.database.database_client.MongoClient')
    def test_connect_failure(self, mock_mongo_client):
        """
        연결 실패 테스트

        Args:
            mock_mongo_client: 모의 MongoDB 클라이언트
        """
        # 모의 객체 설정
        mock_mongo_client.side_effect = ConnectionFailure("연결 실패")

        # 연결 테스트
        result = self.client.connect()

        # 검증
        self.assertFalse(result)
        self.assertFalse(self.client._connected)
        self.assertIsNone(self.client.client)
        self.assertIsNone(self.client.db)

        # 호출 검증
        mock_mongo_client.assert_called_once()

    @patch('infrastructure.database.database_client.MongoClient')
    def test_close(self, mock_mongo_client):
        """
        연결 종료 테스트

        Args:
            mock_mongo_client: 모의 MongoDB 클라이언트
        """
        # 모의 객체 설정
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_admin = MagicMock()

        mock_client.__getitem__.return_value = mock_db
        mock_client.admin = mock_admin
        mock_mongo_client.return_value = mock_client

        # 연결 후 종료 테스트
        self.client.connect()
        self.client.close()

        # 검증
        self.assertFalse(self.client._connected)
        self.assertIsNone(self.client.client)
        self.assertIsNone(self.client.db)

        # 호출 검증
        mock_client.close.assert_called_once()

    @patch('infrastructure.database.database_client.MongoClient')
    def test_is_connected(self, mock_mongo_client):
        """
        연결 상태 확인 테스트

        Args:
            mock_mongo_client: 모의 MongoDB 클라이언트
        """
        # 모의 객체 설정
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_admin = MagicMock()

        mock_client.__getitem__.return_value = mock_db
        mock_client.admin = mock_admin
        mock_mongo_client.return_value = mock_client

        # 연결 전 상태 확인
        self.assertFalse(self.client.is_connected())

        # 연결 후 상태 확인
        self.client.connect()
        self.assertTrue(self.client.is_connected())

        # 연결 종료 후 상태 확인
        self.client.close()
        self.assertFalse(self.client.is_connected())

    @patch('infrastructure.database.database_client.MongoClient')
    def test_get_database(self, mock_mongo_client):
        """
        데이터베이스 가져오기 테스트

        Args:
            mock_mongo_client: 모의 MongoDB 클라이언트
        """
        # 모의 객체 설정
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_admin = MagicMock()

        mock_client.__getitem__.return_value = mock_db
        mock_client.admin = mock_admin
        mock_mongo_client.return_value = mock_client

        # 연결
        self.client.connect()

        # 기본 데이터베이스 가져오기
        db = self.client.get_database()
        self.assertEqual(db, mock_db)
        mock_client.__getitem__.assert_called_with(self.test_db_name)

        # 특정 데이터베이스 가져오기
        db = self.client.get_database("other_db")
        self.assertEqual(db, mock_db)
        mock_client.__getitem__.assert_called_with("other_db")

    @patch('infrastructure.database.database_client.MongoClient')
    def test_get_collection(self, mock_mongo_client):
        """
        컬렉션 가져오기 테스트

        Args:
            mock_mongo_client: 모의 MongoDB 클라이언트
        """
        # 모의 객체 설정
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_admin = MagicMock()

        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_client.admin = mock_admin
        mock_mongo_client.return_value = mock_client

        # 연결
        self.client.connect()

        # 기본 데이터베이스의 컬렉션 가져오기
        collection = self.client.get_collection("test_collection")
        self.assertEqual(collection, mock_collection)
        mock_client.__getitem__.assert_called_with(self.test_db_name)
        mock_db.__getitem__.assert_called_with("test_collection")

        # 특정 데이터베이스의 컬렉션 가져오기
        collection = self.client.get_collection("test_collection", "other_db")
        self.assertEqual(collection, mock_collection)
        mock_client.__getitem__.assert_called_with("other_db")
        mock_db.__getitem__.assert_called_with("test_collection")

    @patch('infrastructure.database.database_client.MongoClient')
    def test_health_check(self, mock_mongo_client):
        """
        상태 확인 테스트

        Args:
            mock_mongo_client: 모의 MongoDB 클라이언트
        """
        # 모의 객체 설정
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_admin = MagicMock()

        mock_client.__getitem__.return_value = mock_db
        mock_client.admin = mock_admin
        mock_mongo_client.return_value = mock_client

        # 연결 전 상태 확인
        health = self.client.health_check()
        self.assertEqual(health["status"], "disconnected")

        # 연결
        self.client.connect()

        # 연결 후 상태 확인
        mock_admin.command.return_value = {
            "version": "4.4.0",
            "uptime": 3600,
            "connections": {
                "current": 5,
                "available": 995,
                "totalCreated": 10
            }
        }

        health = self.client.health_check()
        self.assertEqual(health["status"], "connected")
        self.assertIn("details", health)
        self.assertIn("response_time_ms", health["details"])
        self.assertIn("connections", health["details"])
        self.assertIn("version", health["details"])

        # 연결 오류 시 상태 확인
        mock_admin.command.side_effect = ConnectionFailure("연결 실패")

        health = self.client.health_check()
        self.assertEqual(health["status"], "error")
        self.assertIn("details", health)
        self.assertIn("error", health["details"])


@pytest.mark.asyncio
class TestAsyncMongoDBClient:
    """
    비동기 MongoDB 클라이언트 테스트 클래스
    """

    @pytest_asyncio.fixture(autouse=True)
    async def setup_client(self):
        """
        테스트 설정
        """
        # 테스트용 설정
        self.test_uri = "mongodb://localhost:27017/"
        self.test_db_name = "test_db"

        # 모듈 패치
        with patch('infrastructure.database.async_database_client.AsyncIOMotorClient') as self.mock_motor_client:
            # 모의 객체 설정
            self.mock_client = AsyncMock()
            self.mock_db = AsyncMock()
            self.mock_admin = AsyncMock()

            self.mock_client.__getitem__.return_value = self.mock_db
            self.mock_client.admin = self.mock_admin
            self.mock_motor_client.return_value = self.mock_client

            # 클라이언트 생성
            from infrastructure.database.async_database_client import AsyncMongoDBClient

            self.client = AsyncMongoDBClient(
                uri=self.test_uri,
                default_db_name=self.test_db_name,
                connect_timeout=1000,
                max_pool_size=5,
                min_pool_size=1,
                max_idle_time_ms=10000,
                retry_writes=True,
                retry_reads=True,
                server_selection_timeout_ms=5000,
                socket_timeout_ms=5000,
                heartbeat_frequency_ms=5000,
                app_name="test_app"
            )

            # 테스트 실행
            yield

            # 클라이언트 연결 종료
            if self.client:
                await self.client.close()

    async def test_init(self):
        """
        초기화 테스트
        """
        # 초기화 확인
        assert self.client.uri == self.test_uri
        assert self.client.default_db_name == self.test_db_name
        assert self.client.connect_timeout == 1000
        assert self.client.max_pool_size == 5
        assert self.client.min_pool_size == 1
        assert self.client.max_idle_time_ms == 10000
        assert self.client.retry_writes is True
        assert self.client.retry_reads is True
        assert self.client.server_selection_timeout_ms == 5000
        assert self.client.socket_timeout_ms == 5000
        assert self.client.heartbeat_frequency_ms == 5000
        assert self.client.app_name == "test_app"

        # 클라이언트 초기 상태 확인
        assert self.client.client is None
        assert self.client.db is None
        assert self.client._connected is False

    async def test_connect_success(self):
        """
        연결 성공 테스트
        """
        # 연결 테스트
        result = await self.client.connect()

        # 검증
        assert result is True
        assert self.client._connected is True
        assert self.client.client is not None
        assert self.client.db is not None

        # 호출 검증
        self.mock_motor_client.assert_called_once()
        self.mock_admin.command.assert_called_once_with('ping')

    async def test_connect_failure(self):
        """
        연결 실패 테스트
        """
        # 모의 객체 설정
        self.mock_admin.command.side_effect = ConnectionFailure("연결 실패")

        # 연결 테스트
        result = await self.client.connect()

        # 검증
        assert result is False
        assert self.client._connected is False
        assert self.client.client is None
        assert self.client.db is None

    async def test_close(self):
        """
        연결 종료 테스트
        """
        # 연결 후 종료 테스트
        await self.client.connect()
        await self.client.close()

        # 검증
        assert self.client._connected is False
        assert self.client.client is None
        assert self.client.db is None

        # 호출 검증
        self.mock_client.close.assert_called_once()

    async def test_is_connected(self):
        """
        연결 상태 확인 테스트
        """
        # 연결 전 상태 확인
        self.client.client = None  # 명시적으로 클라이언트 설정
        self.client._connected = False  # 명시적으로 연결 상태 설정
        self.client._last_connection_check = 0  # 캐싱 초기화
        assert await self.client.is_connected() is False

        # 연결 후 상태 확인
        await self.client.connect()
        assert await self.client.is_connected() is True

        # 연결 오류 시 상태 확인
        self.mock_admin.command.side_effect = ConnectionFailure("연결 실패")
        self.client._last_connection_check = 0  # 캐싱 초기화
        assert await self.client.is_connected() is False

    async def test_get_database(self):
        """
        데이터베이스 가져오기 테스트
        """
        # 연결
        await self.client.connect()

        # 기본 데이터베이스 가져오기
        db = self.client.get_database()
        assert db == self.mock_db
        self.mock_client.__getitem__.assert_called_with(self.test_db_name)

        # 특정 데이터베이스 가져오기
        db = self.client.get_database("other_db")
        assert db == self.mock_db
        self.mock_client.__getitem__.assert_called_with("other_db")

    async def test_get_collection(self):
        """
        컬렉션 가져오기 테스트
        """
        # 모의 객체 설정
        mock_collection = AsyncMock()
        self.mock_db.__getitem__.return_value = mock_collection

        # 연결
        await self.client.connect()

        # 기본 데이터베이스의 컬렉션 가져오기
        collection = self.client.get_collection("test_collection")
        assert collection == mock_collection
        self.mock_client.__getitem__.assert_called_with(self.test_db_name)
        self.mock_db.__getitem__.assert_called_with("test_collection")

        # 특정 데이터베이스의 컬렉션 가져오기
        collection = self.client.get_collection("test_collection", "other_db")
        assert collection == mock_collection
        self.mock_client.__getitem__.assert_called_with("other_db")
        self.mock_db.__getitem__.assert_called_with("test_collection")

    async def test_health_check(self):
        """
        상태 확인 테스트
        """
        # 연결 전 상태 확인
        health = await self.client.health_check()
        assert health["status"] == "disconnected"

        # 연결
        await self.client.connect()

        # 연결 후 상태 확인
        self.mock_admin.command.return_value = {
            "version": "4.4.0",
            "uptime": 3600,
            "connections": {
                "current": 5,
                "available": 995,
                "totalCreated": 10
            }
        }

        health = await self.client.health_check()
        assert health["status"] == "connected"
        assert "details" in health
        assert "response_time_ms" in health["details"]
        assert "connections" in health["details"]
        assert "version" in health["details"]

        # 연결 오류 시 상태 확인
        self.mock_admin.command.side_effect = ConnectionFailure("연결 실패")

        health = await self.client.health_check()
        assert health["status"] == "error"
        assert "details" in health
        assert "error" in health["details"]
