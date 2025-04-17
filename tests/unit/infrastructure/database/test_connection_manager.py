"""
연결 관리자 단위 테스트

이 모듈은 데이터베이스 연결 관리자 클래스를 테스트합니다.
"""
import pytest
import unittest
import time
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from infrastructure.database.connection_manager import ConnectionManager, AsyncConnectionManager


class TestConnectionManager(unittest.TestCase):
    """
    연결 관리자 테스트 클래스
    """
    
    def setUp(self):
        """
        테스트 설정
        """
        # 모의 클라이언트 생성
        self.mock_client = MagicMock()
        self.mock_client.connect.return_value = True
        self.mock_client.is_connected.return_value = True
        self.mock_client.health_check.return_value = {"status": "connected"}
        
        # 연결 관리자 생성
        self.manager = ConnectionManager(
            client=self.mock_client,
            health_check_interval=1,
            reconnect_interval=0.1,
            max_reconnect_attempts=3
        )
    
    def tearDown(self):
        """
        테스트 종료 처리
        """
        # 연결 관리자 중지
        self.manager.stop()
    
    def test_init(self):
        """
        초기화 테스트
        """
        # 초기화 확인
        self.assertEqual(self.manager.client, self.mock_client)
        self.assertEqual(self.manager.health_check_interval, 1)
        self.assertEqual(self.manager.reconnect_interval, 0.1)
        self.assertEqual(self.manager.max_reconnect_attempts, 3)
        
        # 내부 상태 확인
        self.assertIsNotNone(self.manager._lock)
        self.assertIsNone(self.manager._health_check_thread)
        self.assertFalse(self.manager._stop_health_check.is_set())
        self.assertIsInstance(self.manager._last_health_check, datetime)
        self.assertEqual(self.manager._health_status, {"status": "unknown"})
        self.assertEqual(self.manager._reconnect_attempts, 0)
    
    def test_start_success(self):
        """
        시작 성공 테스트
        """
        # 시작 테스트
        result = self.manager.start()
        
        # 검증
        self.assertTrue(result)
        self.assertIsNotNone(self.manager._health_check_thread)
        self.assertTrue(self.manager._health_check_thread.is_alive())
        self.assertFalse(self.manager._stop_health_check.is_set())
        
        # 호출 검증
        self.mock_client.connect.assert_called_once()
    
    def test_start_already_running(self):
        """
        이미 실행 중인 상태에서 시작 테스트
        """
        # 첫 번째 시작
        self.manager.start()
        
        # 두 번째 시작
        result = self.manager.start()
        
        # 검증
        self.assertTrue(result)
        
        # 호출 검증 (한 번만 호출되어야 함)
        self.mock_client.connect.assert_called_once()
    
    def test_start_failure(self):
        """
        시작 실패 테스트
        """
        # 모의 객체 설정
        self.mock_client.connect.return_value = False
        
        # 시작 테스트
        result = self.manager.start()
        
        # 검증
        self.assertFalse(result)
        self.assertIsNone(self.manager._health_check_thread)
        
        # 호출 검증
        self.mock_client.connect.assert_called_once()
    
    def test_stop(self):
        """
        중지 테스트
        """
        # 시작 후 중지 테스트
        self.manager.start()
        self.manager.stop()
        
        # 검증
        self.assertTrue(self.manager._stop_health_check.is_set())
        
        # 스레드가 종료될 때까지 대기
        if self.manager._health_check_thread:
            self.manager._health_check_thread.join(timeout=1.0)
        
        self.assertIsNone(self.manager._health_check_thread)
        
        # 호출 검증
        self.mock_client.close.assert_called_once()
    
    def test_get_client(self):
        """
        클라이언트 가져오기 테스트
        """
        # 시작
        self.manager.start()
        
        # 클라이언트 가져오기
        client = self.manager.get_client()
        
        # 검증
        self.assertEqual(client, self.mock_client)
        
        # 연결 끊김 상태에서 클라이언트 가져오기
        self.mock_client.is_connected.return_value = False
        self.mock_client.connect.return_value = True
        
        client = self.manager.get_client()
        
        # 검증
        self.assertEqual(client, self.mock_client)
        
        # 재연결 실패 시 예외 발생
        self.mock_client.connect.return_value = False
        
        with self.assertRaises(ConnectionError):
            self.manager.get_client()
    
    def test_get_health_status(self):
        """
        상태 정보 가져오기 테스트
        """
        # 시작
        self.manager.start()
        
        # 상태 정보 가져오기
        status = self.manager.get_health_status()
        
        # 검증
        self.assertEqual(status, {"status": "connected"})
        
        # 호출 검증
        self.mock_client.health_check.assert_called_once()
    
    def test_check_health(self):
        """
        상태 확인 테스트
        """
        # 시작
        self.manager.start()
        
        # 상태 확인
        self.manager._check_health()
        
        # 검증
        self.assertEqual(self.manager._health_status, {"status": "connected"})
        
        # 호출 검증
        self.mock_client.health_check.assert_called_once()
        
        # 오류 발생 시 상태 확인
        self.mock_client.health_check.side_effect = Exception("상태 확인 오류")
        
        self.manager._check_health()
        
        # 검증
        self.assertEqual(self.manager._health_status["status"], "error")
        self.assertIn("details", self.manager._health_status)
        self.assertIn("error", self.manager._health_status["details"])
    
    def test_reconnect(self):
        """
        재연결 테스트
        """
        # 시작
        self.manager.start()
        
        # 재연결 성공
        self.mock_client.connect.return_value = True
        
        result = self.manager._reconnect()
        
        # 검증
        self.assertTrue(result)
        self.assertEqual(self.manager._reconnect_attempts, 0)
        
        # 호출 검증
        self.mock_client.close.assert_called_once()
        self.assertEqual(self.mock_client.connect.call_count, 2)  # 초기 연결 + 재연결
        
        # 재연결 실패
        self.mock_client.connect.return_value = False
        
        result = self.manager._reconnect()
        
        # 검증
        self.assertFalse(result)
        self.assertEqual(self.manager._reconnect_attempts, 1)
        
        # 최대 재연결 시도 횟수 초과
        self.manager._reconnect_attempts = 3
        
        result = self.manager._reconnect()
        
        # 검증
        self.assertFalse(result)


@pytest.mark.asyncio
class TestAsyncConnectionManager:
    """
    비동기 연결 관리자 테스트 클래스
    """
    
    @pytest.fixture(autouse=True)
    async def setup_manager(self):
        """
        테스트 설정
        """
        # 모의 클라이언트 팩토리 생성
        self.mock_client = AsyncMock()
        self.mock_client.connect.return_value = True
        self.mock_client.is_connected.return_value = True
        self.mock_client.health_check.return_value = {"status": "connected"}
        
        def mock_factory():
            return self.mock_client
        
        # 연결 관리자 생성
        self.manager = AsyncConnectionManager(
            client_factory=mock_factory,
            health_check_interval=1,
            reconnect_interval=0.1,
            max_reconnect_attempts=3
        )
        
        yield
        
        # 연결 관리자 중지
        await self.manager.stop()
    
    async def test_init(self):
        """
        초기화 테스트
        """
        # 초기화 확인
        assert self.manager.client_factory() == self.mock_client
        assert self.manager.health_check_interval == 1
        assert self.manager.reconnect_interval == 0.1
        assert self.manager.max_reconnect_attempts == 3
        
        # 내부 상태 확인
        assert self.manager._client is None
        assert self.manager._lock is not None
        assert isinstance(self.manager._last_health_check, datetime)
        assert self.manager._health_status == {"status": "unknown"}
        assert self.manager._reconnect_attempts == 0
        assert self.manager._health_check_task is None
    
    async def test_start_success(self):
        """
        시작 성공 테스트
        """
        # 시작 테스트
        result = await self.manager.start()
        
        # 검증
        assert result is True
        assert self.manager._client is not None
        assert self.manager._health_check_task is not None
        
        # 호출 검증
        self.mock_client.connect.assert_called_once()
    
    async def test_start_failure(self):
        """
        시작 실패 테스트
        """
        # 모의 객체 설정
        self.mock_client.connect.return_value = False
        
        # 시작 테스트
        result = await self.manager.start()
        
        # 검증
        assert result is False
        assert self.manager._health_check_task is None
        
        # 호출 검증
        self.mock_client.connect.assert_called_once()
    
    async def test_stop(self):
        """
        중지 테스트
        """
        # 시작 후 중지 테스트
        await self.manager.start()
        await self.manager.stop()
        
        # 검증
        assert self.manager._client is None
        assert self.manager._health_check_task is None
        
        # 호출 검증
        self.mock_client.close.assert_called_once()
    
    async def test_get_client(self):
        """
        클라이언트 가져오기 테스트
        """
        # 시작
        await self.manager.start()
        
        # 클라이언트 가져오기
        client = await self.manager.get_client()
        
        # 검증
        assert client == self.mock_client
        
        # 연결 끊김 상태에서 클라이언트 가져오기
        self.mock_client.is_connected.return_value = False
        self.mock_client.connect.return_value = True
        
        client = await self.manager.get_client()
        
        # 검증
        assert client == self.mock_client
        
        # 재연결 실패 시 예외 발생
        self.mock_client.connect.return_value = False
        
        with pytest.raises(ConnectionError):
            await self.manager.get_client()
    
    async def test_get_health_status(self):
        """
        상태 정보 가져오기 테스트
        """
        # 시작
        await self.manager.start()
        
        # 상태 정보 가져오기
        status = await self.manager.get_health_status()
        
        # 검증
        assert status == {"status": "connected"}
        
        # 호출 검증
        self.mock_client.health_check.assert_called_once()
    
    async def test_check_health(self):
        """
        상태 확인 테스트
        """
        # 시작
        await self.manager.start()
        
        # 상태 확인
        await self.manager._check_health()
        
        # 검증
        assert self.manager._health_status == {"status": "connected"}
        
        # 호출 검증
        self.mock_client.health_check.assert_called()
        
        # 오류 발생 시 상태 확인
        self.mock_client.health_check.side_effect = Exception("상태 확인 오류")
        
        await self.manager._check_health()
        
        # 검증
        assert self.manager._health_status["status"] == "error"
        assert "details" in self.manager._health_status
        assert "error" in self.manager._health_status["details"]
    
    async def test_reconnect(self):
        """
        재연결 테스트
        """
        # 시작
        await self.manager.start()
        
        # 재연결 성공
        self.mock_client.connect.return_value = True
        
        result = await self.manager._reconnect()
        
        # 검증
        assert result is True
        assert self.manager._reconnect_attempts == 0
        
        # 호출 검증
        self.mock_client.close.assert_called()
        assert self.mock_client.connect.call_count >= 2  # 초기 연결 + 재연결
        
        # 재연결 실패
        self.mock_client.connect.return_value = False
        
        result = await self.manager._reconnect()
        
        # 검증
        assert result is False
        assert self.manager._reconnect_attempts == 1
        
        # 최대 재연결 시도 횟수 초과
        self.manager._reconnect_attempts = 3
        
        result = await self.manager._reconnect()
        
        # 검증
        assert result is False
