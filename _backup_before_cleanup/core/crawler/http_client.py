"""
비동기 HTTP 클라이언트 모듈

aiohttp를 사용한 비동기 HTTP 요청 처리 기능을 제공합니다.
재시도 로직, 레이트 리밋 관리, 오류 처리 등을 포함합니다.
"""
import asyncio
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union

import aiohttp
from aiohttp import ClientSession, ClientTimeout, ClientError, ClientResponseError

from core.crawler.interfaces import HttpClientInterface
from core.crawler.exceptions import (
    HttpClientException, RateLimitException, TimeoutException, ConnectionException
)

# 로깅 설정
logger = logging.getLogger(__name__)


class AsyncHttpClient(HttpClientInterface):
    """
    비동기 HTTP 클라이언트
    
    aiohttp를 사용한 비동기 HTTP 요청 처리 기능을 제공합니다.
    """
    
    def __init__(self, timeout: float = 30.0, max_retries: int = 3, 
                 backoff_factor: float = 1.5, requests_per_minute: int = 60):
        """
        AsyncHttpClient 초기화
        
        Args:
            timeout: 기본 타임아웃 (초)
            max_retries: 기본 최대 재시도 횟수
            backoff_factor: 기본 백오프 계수
            requests_per_minute: 분당 최대 요청 수
        """
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor
        self._requests_per_minute = requests_per_minute
        self._default_headers = {
            "User-Agent": self._get_random_user_agent(),
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        # 레이트 리밋 관리
        self._last_request_time = None
        self._request_count = 0
        self._request_reset_time = None
    
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None, 
                 headers: Optional[Dict[str, str]] = None, 
                 timeout: Optional[float] = None) -> Tuple[int, str]:
        """
        GET 요청 수행
        
        Args:
            url: 요청 URL
            params: 쿼리 파라미터
            headers: 요청 헤더
            timeout: 타임아웃 (초)
            
        Returns:
            Tuple[int, str]: 상태 코드와 응답 내용
            
        Raises:
            HttpClientException: HTTP 요청 실패 시
        """
        # 레이트 리밋 확인
        await self._check_rate_limit()
        
        # 헤더 병합
        merged_headers = self._default_headers.copy()
        if headers:
            merged_headers.update(headers)
        
        # 타임아웃 설정
        timeout_value = timeout or self._timeout
        client_timeout = ClientTimeout(total=timeout_value)
        
        try:
            async with ClientSession(timeout=client_timeout) as session:
                async with session.get(url, params=params, headers=merged_headers) as response:
                    # 응답 처리
                    status_code = response.status
                    content = await response.text()
                    
                    # 요청 카운터 증가
                    self._increment_request_counter()
                    
                    return status_code, content
                    
        except asyncio.TimeoutError:
            raise TimeoutException(f"Request timed out after {timeout_value} seconds", url, timeout_value)
        except ClientResponseError as e:
            if e.status == 429:
                retry_after = int(e.headers.get("Retry-After", "60"))
                raise RateLimitException(f"Rate limit exceeded", retry_after, url)
            raise HttpClientException(f"HTTP error: {e.status}", e.status, url)
        except ClientError as e:
            raise ConnectionException(f"Connection error: {str(e)}", url)
        except Exception as e:
            raise HttpClientException(f"Request failed: {str(e)}", None, url)
    
    async def post(self, url: str, data: Optional[Dict[str, Any]] = None, 
                  json_data: Optional[Dict[str, Any]] = None, 
                  headers: Optional[Dict[str, str]] = None, 
                  timeout: Optional[float] = None) -> Tuple[int, str]:
        """
        POST 요청 수행
        
        Args:
            url: 요청 URL
            data: 폼 데이터
            json_data: JSON 데이터
            headers: 요청 헤더
            timeout: 타임아웃 (초)
            
        Returns:
            Tuple[int, str]: 상태 코드와 응답 내용
            
        Raises:
            HttpClientException: HTTP 요청 실패 시
        """
        # 레이트 리밋 확인
        await self._check_rate_limit()
        
        # 헤더 병합
        merged_headers = self._default_headers.copy()
        if headers:
            merged_headers.update(headers)
        
        # 타임아웃 설정
        timeout_value = timeout or self._timeout
        client_timeout = ClientTimeout(total=timeout_value)
        
        try:
            async with ClientSession(timeout=client_timeout) as session:
                async with session.post(url, data=data, json=json_data, headers=merged_headers) as response:
                    # 응답 처리
                    status_code = response.status
                    content = await response.text()
                    
                    # 요청 카운터 증가
                    self._increment_request_counter()
                    
                    return status_code, content
                    
        except asyncio.TimeoutError:
            raise TimeoutException(f"Request timed out after {timeout_value} seconds", url, timeout_value)
        except ClientResponseError as e:
            if e.status == 429:
                retry_after = int(e.headers.get("Retry-After", "60"))
                raise RateLimitException(f"Rate limit exceeded", retry_after, url)
            raise HttpClientException(f"HTTP error: {e.status}", e.status, url)
        except ClientError as e:
            raise ConnectionException(f"Connection error: {str(e)}", url)
        except Exception as e:
            raise HttpClientException(f"Request failed: {str(e)}", None, url)
    
    async def get_with_retry(self, url: str, params: Optional[Dict[str, Any]] = None, 
                            headers: Optional[Dict[str, str]] = None, 
                            max_retries: int = 3, backoff_factor: float = 1.5, 
                            timeout: Optional[float] = None) -> Tuple[int, str]:
        """
        재시도 로직이 포함된 GET 요청 수행
        
        Args:
            url: 요청 URL
            params: 쿼리 파라미터
            headers: 요청 헤더
            max_retries: 최대 재시도 횟수
            backoff_factor: 백오프 계수
            timeout: 타임아웃 (초)
            
        Returns:
            Tuple[int, str]: 상태 코드와 응답 내용
            
        Raises:
            HttpClientException: 모든 재시도 실패 시
        """
        retries = 0
        max_retry_count = max_retries or self._max_retries
        backoff = backoff_factor or self._backoff_factor
        last_exception = None
        
        while retries <= max_retry_count:
            try:
                # GET 요청 수행
                status_code, content = await self.get(url, params, headers, timeout)
                
                # 성공 응답인 경우 바로 반환
                if 200 <= status_code < 300:
                    return status_code, content
                
                # 서버 오류(5xx)인 경우 재시도
                if 500 <= status_code < 600 and retries < max_retry_count:
                    wait_time = backoff ** retries
                    logger.warning(f"Server error ({status_code}), retrying in {wait_time:.2f}s ({retries+1}/{max_retry_count})")
                    await asyncio.sleep(wait_time)
                    retries += 1
                    continue
                
                # 클라이언트 오류(4xx)인 경우 재시도하지 않음 (429 제외)
                if status_code == 429 and retries < max_retry_count:
                    wait_time = backoff ** retries
                    logger.warning(f"Rate limit exceeded, retrying in {wait_time:.2f}s ({retries+1}/{max_retry_count})")
                    await asyncio.sleep(wait_time)
                    retries += 1
                    continue
                
                # 그 외 상태 코드는 그대로 반환
                return status_code, content
                
            except RateLimitException as e:
                # 레이트 리밋 예외 처리
                if retries < max_retry_count:
                    wait_time = e.retry_after or (backoff ** retries)
                    logger.warning(f"Rate limit exceeded, retrying in {wait_time}s ({retries+1}/{max_retry_count})")
                    await asyncio.sleep(wait_time)
                    retries += 1
                    last_exception = e
                    continue
                raise
                
            except (TimeoutException, ConnectionException) as e:
                # 타임아웃 또는 연결 오류 처리
                if retries < max_retry_count:
                    wait_time = backoff ** retries
                    logger.warning(f"{e.__class__.__name__}: {e.message}, retrying in {wait_time:.2f}s ({retries+1}/{max_retry_count})")
                    await asyncio.sleep(wait_time)
                    retries += 1
                    last_exception = e
                    continue
                raise
                
            except HttpClientException as e:
                # 기타 HTTP 클라이언트 예외 처리
                if retries < max_retry_count:
                    wait_time = backoff ** retries
                    logger.warning(f"HTTP error: {e.message}, retrying in {wait_time:.2f}s ({retries+1}/{max_retry_count})")
                    await asyncio.sleep(wait_time)
                    retries += 1
                    last_exception = e
                    continue
                raise
                
            except Exception as e:
                # 예상치 못한 예외 처리
                if retries < max_retry_count:
                    wait_time = backoff ** retries
                    logger.warning(f"Unexpected error: {str(e)}, retrying in {wait_time:.2f}s ({retries+1}/{max_retry_count})")
                    await asyncio.sleep(wait_time)
                    retries += 1
                    last_exception = HttpClientException(f"Unexpected error: {str(e)}", None, url)
                    continue
                raise HttpClientException(f"Request failed after {max_retry_count} retries: {str(e)}", None, url)
        
        # 모든 재시도 실패
        if last_exception:
            raise last_exception
        raise HttpClientException(f"Request failed after {max_retry_count} retries", None, url)
    
    def set_default_headers(self, headers: Dict[str, str]) -> None:
        """
        기본 요청 헤더 설정
        
        Args:
            headers: 기본 요청 헤더
        """
        self._default_headers.update(headers)
    
    def set_rate_limit(self, requests_per_minute: int) -> None:
        """
        요청 속도 제한 설정
        
        Args:
            requests_per_minute: 분당 최대 요청 수
        """
        self._requests_per_minute = requests_per_minute
    
    async def _check_rate_limit(self) -> None:
        """
        레이트 리밋 확인
        
        Raises:
            RateLimitException: 레이트 리밋 초과 시
        """
        now = datetime.now()
        
        # 첫 요청이거나 리셋 시간이 지난 경우 카운터 초기화
        if self._request_reset_time is None or now >= self._request_reset_time:
            self._request_count = 0
            self._request_reset_time = now + timedelta(minutes=1)
        
        # 요청 수 제한 확인
        if self._request_count >= self._requests_per_minute:
            wait_seconds = (self._request_reset_time - now).total_seconds()
            raise RateLimitException(
                f"Rate limit exceeded: {self._requests_per_minute} requests per minute",
                int(wait_seconds)
            )
    
    def _increment_request_counter(self) -> None:
        """요청 카운터 증가"""
        now = datetime.now()
        
        # 첫 요청이거나 리셋 시간이 지난 경우 카운터 초기화
        if self._request_reset_time is None or now >= self._request_reset_time:
            self._request_count = 0
            self._request_reset_time = now + timedelta(minutes=1)
        
        # 요청 카운터 증가
        self._request_count += 1
        self._last_request_time = now
    
    def _get_random_user_agent(self) -> str:
        """
        랜덤 User-Agent 문자열 반환
        
        Returns:
            str: User-Agent 문자열
        """
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        ]
        return random.choice(user_agents)
