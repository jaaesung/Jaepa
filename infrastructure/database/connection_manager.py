"""
데이터베이스 연결 관리 모듈

데이터베이스 연결 관리 및 풀링을 담당하는 클래스를 제공합니다.
"""
import logging
import time
import threading
from typing import Any, Dict, List, Optional, Union, Set
from datetime import datetime, timedelta

from infrastructure.database.database_client import DatabaseClientInterface

# 로깅 설정
logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    데이터베이스 연결 관리 클래스
    
    데이터베이스 연결 관리 및 풀링을 담당합니다.
    """
    
    def __init__(
        self,
        client: DatabaseClientInterface,
        health_check_interval: int = 60,  # 초
        reconnect_interval: int = 5,  # 초
        max_reconnect_attempts: int = 5
    ):
        """
        ConnectionManager 초기화
        
        Args:
            client: 데이터베이스 클라이언트
            health_check_interval: 상태 확인 주기 (초)
            reconnect_interval: 재연결 시도 간격 (초)
            max_reconnect_attempts: 최대 재연결 시도 횟수
        """
        self.client = client
        self.health_check_interval = health_check_interval
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        
        self._lock = threading.RLock()
        self._health_check_thread = None
        self._stop_health_check = threading.Event()
        self._last_health_check = datetime.now()
        self._health_status = {"status": "unknown"}
        self._reconnect_attempts = 0
    
    def start(self) -> bool:
        """
        연결 관리 시작
        
        Returns:
            bool: 시작 성공 여부
        """
        with self._lock:
            # 이미 실행 중인 경우
            if self._health_check_thread and self._health_check_thread.is_alive():
                logger.warning("연결 관리가 이미 실행 중입니다.")
                return True
            
            # 연결 시도
            if not self.client.connect():
                logger.error("초기 데이터베이스 연결 실패")
                return False
            
            # 상태 확인 스레드 시작
            self._stop_health_check.clear()
            self._health_check_thread = threading.Thread(
                target=self._health_check_loop,
                daemon=True
            )
            self._health_check_thread.start()
            
            logger.info("연결 관리 시작됨")
            return True
    
    def stop(self) -> None:
        """
        연결 관리 중지
        """
        with self._lock:
            if self._health_check_thread and self._health_check_thread.is_alive():
                # 상태 확인 스레드 중지
                self._stop_health_check.set()
                self._health_check_thread.join(timeout=5.0)
                self._health_check_thread = None
            
            # 연결 종료
            self.client.close()
            
            logger.info("연결 관리 중지됨")
    
    def get_client(self) -> DatabaseClientInterface:
        """
        데이터베이스 클라이언트 가져오기
        
        Returns:
            DatabaseClientInterface: 데이터베이스 클라이언트
            
        Raises:
            ConnectionError: 연결 실패 시
        """
        with self._lock:
            # 연결 확인
            if not self.client.is_connected():
                # 재연결 시도
                if not self._reconnect():
                    raise ConnectionError("데이터베이스 연결 실패")
            
            return self.client
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        상태 정보 가져오기
        
        Returns:
            Dict[str, Any]: 상태 정보
        """
        with self._lock:
            # 마지막 상태 확인 후 일정 시간이 지난 경우 다시 확인
            if (datetime.now() - self._last_health_check).total_seconds() > self.health_check_interval:
                self._check_health()
            
            return self._health_status
    
    def _health_check_loop(self) -> None:
        """
        상태 확인 루프
        """
        while not self._stop_health_check.is_set():
            try:
                # 상태 확인
                self._check_health()
                
                # 연결이 끊어진 경우 재연결 시도
                if self._health_status.get("status") != "connected":
                    self._reconnect()
                else:
                    # 연결이 정상인 경우 재연결 시도 횟수 초기화
                    self._reconnect_attempts = 0
                
            except Exception as e:
                logger.error(f"상태 확인 중 오류: {str(e)}")
            
            # 다음 확인까지 대기
            self._stop_health_check.wait(self.health_check_interval)
    
    def _check_health(self) -> None:
        """
        상태 확인
        """
        try:
            # 클라이언트 상태 확인
            self._health_status = self.client.health_check()
            self._last_health_check = datetime.now()
            
            # 상태 로깅
            if self._health_status.get("status") == "connected":
                logger.debug("데이터베이스 연결 상태: 정상")
            else:
                logger.warning(f"데이터베이스 연결 상태: {self._health_status.get('status')}")
                
        except Exception as e:
            logger.error(f"상태 확인 중 오류: {str(e)}")
            self._health_status = {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "details": {"error": str(e)}
            }
    
    def _reconnect(self) -> bool:
        """
        재연결 시도
        
        Returns:
            bool: 재연결 성공 여부
        """
        # 최대 재연결 시도 횟수 초과 확인
        if self._reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"최대 재연결 시도 횟수({self.max_reconnect_attempts}회) 초과")
            return False
        
        try:
            # 연결 종료
            self.client.close()
            
            # 재연결 시도
            logger.info(f"데이터베이스 재연결 시도 ({self._reconnect_attempts + 1}/{self.max_reconnect_attempts})")
            if self.client.connect():
                logger.info("데이터베이스 재연결 성공")
                self._reconnect_attempts = 0
                return True
            
            # 재연결 실패
            self._reconnect_attempts += 1
            logger.warning(f"데이터베이스 재연결 실패 ({self._reconnect_attempts}/{self.max_reconnect_attempts})")
            
            # 다음 시도까지 대기
            time.sleep(self.reconnect_interval)
            
            return False
            
        except Exception as e:
            self._reconnect_attempts += 1
            logger.error(f"재연결 중 오류: {str(e)}")
            return False


class AsyncConnectionManager:
    """
    비동기 데이터베이스 연결 관리 클래스
    
    비동기 데이터베이스 연결 관리 및 풀링을 담당합니다.
    """
    
    def __init__(
        self,
        client_factory: callable,
        health_check_interval: int = 60,  # 초
        reconnect_interval: int = 5,  # 초
        max_reconnect_attempts: int = 5
    ):
        """
        AsyncConnectionManager 초기화
        
        Args:
            client_factory: 데이터베이스 클라이언트 팩토리 함수
            health_check_interval: 상태 확인 주기 (초)
            reconnect_interval: 재연결 시도 간격 (초)
            max_reconnect_attempts: 최대 재연결 시도 횟수
        """
        self.client_factory = client_factory
        self.health_check_interval = health_check_interval
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        
        self._client = None
        self._lock = threading.RLock()
        self._last_health_check = datetime.now()
        self._health_status = {"status": "unknown"}
        self._reconnect_attempts = 0
        self._health_check_task = None
    
    async def start(self) -> bool:
        """
        연결 관리 시작
        
        Returns:
            bool: 시작 성공 여부
        """
        with self._lock:
            # 클라이언트 생성
            if self._client is None:
                self._client = self.client_factory()
            
            # 연결 시도
            if not await self._client.connect():
                logger.error("초기 데이터베이스 연결 실패")
                return False
            
            # 상태 확인 태스크 시작
            if self._health_check_task is None:
                import asyncio
                self._health_check_task = asyncio.create_task(self._health_check_loop())
            
            logger.info("비동기 연결 관리 시작됨")
            return True
    
    async def stop(self) -> None:
        """
        연결 관리 중지
        """
        with self._lock:
            # 상태 확인 태스크 중지
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except:
                    pass
                self._health_check_task = None
            
            # 연결 종료
            if self._client:
                await self._client.close()
                self._client = None
            
            logger.info("비동기 연결 관리 중지됨")
    
    async def get_client(self) -> Any:
        """
        데이터베이스 클라이언트 가져오기
        
        Returns:
            Any: 데이터베이스 클라이언트
            
        Raises:
            ConnectionError: 연결 실패 시
        """
        with self._lock:
            # 클라이언트가 없는 경우 생성
            if self._client is None:
                self._client = self.client_factory()
            
            # 연결 확인
            if not await self._client.is_connected():
                # 재연결 시도
                if not await self._reconnect():
                    raise ConnectionError("데이터베이스 연결 실패")
            
            return self._client
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        상태 정보 가져오기
        
        Returns:
            Dict[str, Any]: 상태 정보
        """
        with self._lock:
            # 마지막 상태 확인 후 일정 시간이 지난 경우 다시 확인
            if (datetime.now() - self._last_health_check).total_seconds() > self.health_check_interval:
                await self._check_health()
            
            return self._health_status
    
    async def _health_check_loop(self) -> None:
        """
        상태 확인 루프
        """
        import asyncio
        
        while True:
            try:
                # 상태 확인
                await self._check_health()
                
                # 연결이 끊어진 경우 재연결 시도
                if self._health_status.get("status") != "connected":
                    await self._reconnect()
                else:
                    # 연결이 정상인 경우 재연결 시도 횟수 초기화
                    self._reconnect_attempts = 0
                
            except asyncio.CancelledError:
                logger.info("상태 확인 루프 취소됨")
                break
                
            except Exception as e:
                logger.error(f"상태 확인 중 오류: {str(e)}")
            
            # 다음 확인까지 대기
            await asyncio.sleep(self.health_check_interval)
    
    async def _check_health(self) -> None:
        """
        상태 확인
        """
        try:
            # 클라이언트가 없는 경우 생성
            if self._client is None:
                self._client = self.client_factory()
                if not await self._client.connect():
                    self._health_status = {
                        "status": "disconnected",
                        "timestamp": datetime.now().isoformat(),
                        "details": {"error": "연결 실패"}
                    }
                    return
            
            # 클라이언트 상태 확인
            self._health_status = await self._client.health_check()
            self._last_health_check = datetime.now()
            
            # 상태 로깅
            if self._health_status.get("status") == "connected":
                logger.debug("데이터베이스 연결 상태: 정상")
            else:
                logger.warning(f"데이터베이스 연결 상태: {self._health_status.get('status')}")
                
        except Exception as e:
            logger.error(f"상태 확인 중 오류: {str(e)}")
            self._health_status = {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "details": {"error": str(e)}
            }
    
    async def _reconnect(self) -> bool:
        """
        재연결 시도
        
        Returns:
            bool: 재연결 성공 여부
        """
        import asyncio
        
        # 최대 재연결 시도 횟수 초과 확인
        if self._reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"최대 재연결 시도 횟수({self.max_reconnect_attempts}회) 초과")
            return False
        
        try:
            # 연결 종료
            if self._client:
                await self._client.close()
            
            # 클라이언트 재생성
            self._client = self.client_factory()
            
            # 재연결 시도
            logger.info(f"데이터베이스 재연결 시도 ({self._reconnect_attempts + 1}/{self.max_reconnect_attempts})")
            if await self._client.connect():
                logger.info("데이터베이스 재연결 성공")
                self._reconnect_attempts = 0
                return True
            
            # 재연결 실패
            self._reconnect_attempts += 1
            logger.warning(f"데이터베이스 재연결 실패 ({self._reconnect_attempts}/{self.max_reconnect_attempts})")
            
            # 다음 시도까지 대기
            await asyncio.sleep(self.reconnect_interval)
            
            return False
            
        except Exception as e:
            self._reconnect_attempts += 1
            logger.error(f"재연결 중 오류: {str(e)}")
            return False
