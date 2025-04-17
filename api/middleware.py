"""
API 미들웨어 모듈

API 요청 처리를 위한 미들웨어를 제공합니다.
"""
import time
import uuid
import logging
from typing import Callable, Dict, Optional, Set

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from api.exceptions import RateLimitException

# 로깅 설정
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    요청 로깅 미들웨어
    
    모든 API 요청과 응답을 로깅합니다.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[Set[str]] = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
    ):
        """
        RequestLoggingMiddleware 초기화
        
        Args:
            app: ASGI 애플리케이션
            exclude_paths: 로깅에서 제외할 경로 집합
            log_request_body: 요청 본문 로깅 여부
            log_response_body: 응답 본문 로깅 여부
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or set()
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        요청 처리 및 로깅
        
        Args:
            request: HTTP 요청
            call_next: 다음 미들웨어 호출 함수
            
        Returns:
            Response: HTTP 응답
        """
        # 제외 경로 확인
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # 요청 ID 생성
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 시작 시간 기록
        start_time = time.time()
        
        # 요청 정보 로깅
        client_host = request.client.host if request.client else "unknown"
        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"from {client_host} (ID: {request_id})"
        )
        
        # 요청 헤더 로깅
        logger.debug(f"Request headers: {dict(request.headers)}")
        
        # 요청 본문 로깅 (설정된 경우)
        if self.log_request_body:
            try:
                body = await request.body()
                if body:
                    logger.debug(f"Request body: {body.decode('utf-8')}")
            except Exception as e:
                logger.warning(f"Failed to log request body: {str(e)}")
        
        # 다음 미들웨어 호출
        try:
            response = await call_next(request)
            
            # 처리 시간 계산
            process_time = time.time() - start_time
            
            # 응답 정보 로깅
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Time: {process_time:.4f}s (ID: {request_id})"
            )
            
            # 응답 헤더에 요청 ID 추가
            response.headers["X-Request-ID"] = request_id
            
            # 응답 헤더에 처리 시간 추가
            response.headers["X-Process-Time"] = str(process_time)
            
            # 응답 본문 로깅 (설정된 경우)
            if self.log_response_body:
                # 응답 본문은 이미 소비되었을 수 있으므로 로깅하지 않음
                pass
            
            return response
            
        except Exception as e:
            # 오류 로깅
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"- Error: {str(e)} (ID: {request_id})"
            )
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    속도 제한 미들웨어
    
    API 요청 속도를 제한합니다.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        rate_limit: int = 100,  # 기본값: 분당 100개 요청
        window_size: int = 60,  # 기본값: 60초 (1분)
        exclude_paths: Optional[Set[str]] = None,
    ):
        """
        RateLimitMiddleware 초기화
        
        Args:
            app: ASGI 애플리케이션
            rate_limit: 시간 창 내 최대 요청 수
            window_size: 시간 창 크기 (초)
            exclude_paths: 속도 제한에서 제외할 경로 집합
        """
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window_size = window_size
        self.exclude_paths = exclude_paths or set()
        self.requests = {}  # {client_ip: [(timestamp, count), ...]}
    
    def _clean_old_requests(self, client_ip: str, current_time: float) -> None:
        """
        오래된 요청 정보 정리
        
        Args:
            client_ip: 클라이언트 IP
            current_time: 현재 시간
        """
        if client_ip in self.requests:
            # 시간 창 내의 요청만 유지
            self.requests[client_ip] = [
                (ts, count) for ts, count in self.requests[client_ip]
                if current_time - ts < self.window_size
            ]
    
    def _get_request_count(self, client_ip: str, current_time: float) -> int:
        """
        시간 창 내 요청 수 계산
        
        Args:
            client_ip: 클라이언트 IP
            current_time: 현재 시간
            
        Returns:
            int: 시간 창 내 요청 수
        """
        self._clean_old_requests(client_ip, current_time)
        
        # 요청 수 합산
        return sum(count for _, count in self.requests.get(client_ip, []))
    
    def _add_request(self, client_ip: str, current_time: float) -> None:
        """
        요청 추가
        
        Args:
            client_ip: 클라이언트 IP
            current_time: 현재 시간
        """
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # 새 요청 추가
        self.requests[client_ip].append((current_time, 1))
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        요청 처리 및 속도 제한 적용
        
        Args:
            request: HTTP 요청
            call_next: 다음 미들웨어 호출 함수
            
        Returns:
            Response: HTTP 응답
            
        Raises:
            RateLimitException: 속도 제한 초과 시
        """
        # 제외 경로 확인
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # 클라이언트 IP 가져오기
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # 요청 수 확인
        request_count = self._get_request_count(client_ip, current_time)
        
        # 속도 제한 확인
        if request_count >= self.rate_limit:
            # 다음 요청 가능 시간 계산
            oldest_timestamp = min(
                [ts for ts, _ in self.requests.get(client_ip, [(current_time, 0)])]
            )
            retry_after = int(self.window_size - (current_time - oldest_timestamp))
            
            logger.warning(
                f"Rate limit exceeded for {client_ip}: "
                f"{request_count} requests in {self.window_size}s"
            )
            
            # 속도 제한 예외 발생
            raise RateLimitException(
                retry_after=max(1, retry_after),
                details={
                    "limit": self.rate_limit,
                    "window_size": self.window_size,
                    "current_count": request_count
                }
            )
        
        # 요청 추가
        self._add_request(client_ip, current_time)
        
        # 다음 미들웨어 호출
        return await call_next(request)


class ResponseTimeMiddleware(BaseHTTPMiddleware):
    """
    응답 시간 미들웨어
    
    API 요청 처리 시간을 측정하고 로깅합니다.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        slow_response_threshold: float = 1.0,  # 기본값: 1초
    ):
        """
        ResponseTimeMiddleware 초기화
        
        Args:
            app: ASGI 애플리케이션
            slow_response_threshold: 느린 응답 임계값 (초)
        """
        super().__init__(app)
        self.slow_response_threshold = slow_response_threshold
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        요청 처리 및 응답 시간 측정
        
        Args:
            request: HTTP 요청
            call_next: 다음 미들웨어 호출 함수
            
        Returns:
            Response: HTTP 응답
        """
        # 시작 시간 기록
        start_time = time.time()
        
        # 다음 미들웨어 호출
        response = await call_next(request)
        
        # 처리 시간 계산
        process_time = time.time() - start_time
        
        # 응답 헤더에 처리 시간 추가
        response.headers["X-Process-Time"] = str(process_time)
        
        # 느린 응답 로깅
        if process_time > self.slow_response_threshold:
            logger.warning(
                f"Slow response detected: {request.method} {request.url.path} "
                f"- Time: {process_time:.4f}s"
            )
        
        return response


def setup_middleware(app: FastAPI, config: Dict) -> None:
    """
    미들웨어 설정
    
    Args:
        app: FastAPI 애플리케이션
        config: 설정 정보
    """
    # CORS 미들웨어 추가
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.get("cors_origins", ["*"]),
        allow_credentials=config.get("cors_allow_credentials", True),
        allow_methods=config.get("cors_allow_methods", ["*"]),
        allow_headers=config.get("cors_allow_headers", ["*"]),
    )
    
    # 요청 로깅 미들웨어 추가
    app.add_middleware(
        RequestLoggingMiddleware,
        exclude_paths=set(config.get("logging_exclude_paths", ["/health", "/metrics"])),
        log_request_body=config.get("log_request_body", False),
        log_response_body=config.get("log_response_body", False),
    )
    
    # 속도 제한 미들웨어 추가
    app.add_middleware(
        RateLimitMiddleware,
        rate_limit=config.get("rate_limit", 100),
        window_size=config.get("rate_limit_window", 60),
        exclude_paths=set(config.get("rate_limit_exclude_paths", ["/health", "/metrics"])),
    )
    
    # 응답 시간 미들웨어 추가
    app.add_middleware(
        ResponseTimeMiddleware,
        slow_response_threshold=config.get("slow_response_threshold", 1.0),
    )
