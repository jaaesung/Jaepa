"""
HTTP 클라이언트 테스트 모듈

AsyncHttpClient 클래스에 대한 단위 테스트를 제공합니다.
"""
import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

import aiohttp
from aiohttp import ClientSession, ClientTimeout, ClientResponseError, ClientError

from core.crawler.http_client import AsyncHttpClient
from core.crawler.exceptions import (
    HttpClientException, RateLimitException, TimeoutException, ConnectionException
)


@pytest.fixture
def http_client():
    """HTTP 클라이언트 픽스처"""
    return AsyncHttpClient(timeout=5.0, max_retries=2, requests_per_minute=10)


class MockResponse:
    """모의 응답 클래스"""
    
    def __init__(self, status, text):
        self.status = status
        self._text = text
    
    async def text(self):
        return self._text
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_get_success(http_client):
    """GET 요청 성공 테스트"""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MockResponse(200, 'test content')
        mock_get.return_value = mock_response
        
        status_code, content = await http_client.get('https://example.com')
        
        assert status_code == 200
        assert content == 'test content'
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_get_timeout(http_client):
    """GET 요청 타임아웃 테스트"""
    with patch('aiohttp.ClientSession.get', side_effect=asyncio.TimeoutError):
        with pytest.raises(TimeoutException) as excinfo:
            await http_client.get('https://example.com')
        
        assert 'timed out' in str(excinfo.value)
        assert excinfo.value.url == 'https://example.com'


@pytest.mark.asyncio
async def test_get_rate_limit(http_client):
    """GET 요청 레이트 리밋 테스트"""
    headers = {'Retry-After': '30'}
    with patch('aiohttp.ClientSession.get', side_effect=ClientResponseError(
        request_info=MagicMock(),
        history=(),
        status=429,
        message='Too Many Requests',
        headers=headers
    )):
        with pytest.raises(RateLimitException) as excinfo:
            await http_client.get('https://example.com')
        
        assert 'Rate limit exceeded' in str(excinfo.value)
        assert excinfo.value.status_code == 429
        assert excinfo.value.url == 'https://example.com'


@pytest.mark.asyncio
async def test_get_connection_error(http_client):
    """GET 요청 연결 오류 테스트"""
    with patch('aiohttp.ClientSession.get', side_effect=ClientError('Connection error')):
        with pytest.raises(ConnectionException) as excinfo:
            await http_client.get('https://example.com')
        
        assert 'Connection error' in str(excinfo.value)
        assert excinfo.value.url == 'https://example.com'


@pytest.mark.asyncio
async def test_post_success(http_client):
    """POST 요청 성공 테스트"""
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = MockResponse(200, 'test content')
        mock_post.return_value = mock_response
        
        status_code, content = await http_client.post(
            'https://example.com',
            json_data={'key': 'value'}
        )
        
        assert status_code == 200
        assert content == 'test content'
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_get_with_retry_success(http_client):
    """재시도 로직 성공 테스트"""
    with patch('core.crawler.http_client.AsyncHttpClient.get') as mock_get:
        mock_get.side_effect = [
            (500, 'server error'),  # 첫 번째 시도: 서버 오류
            (200, 'success')        # 두 번째 시도: 성공
        ]
        
        status_code, content = await http_client.get_with_retry('https://example.com')
        
        assert status_code == 200
        assert content == 'success'
        assert mock_get.call_count == 2


@pytest.mark.asyncio
async def test_get_with_retry_max_retries_exceeded(http_client):
    """최대 재시도 횟수 초과 테스트"""
    with patch('core.crawler.http_client.AsyncHttpClient.get') as mock_get:
        mock_get.side_effect = [
            (500, 'server error'),  # 첫 번째 시도: 서버 오류
            (500, 'server error'),  # 두 번째 시도: 서버 오류
            (500, 'server error')   # 세 번째 시도: 서버 오류 (호출되지 않음)
        ]
        
        status_code, content = await http_client.get_with_retry('https://example.com')
        
        assert status_code == 500
        assert content == 'server error'
        assert mock_get.call_count == 2  # 최대 재시도 횟수 2


@pytest.mark.asyncio
async def test_get_with_retry_client_error(http_client):
    """클라이언트 오류 테스트"""
    with patch('core.crawler.http_client.AsyncHttpClient.get') as mock_get:
        mock_get.return_value = (404, 'not found')
        
        status_code, content = await http_client.get_with_retry('https://example.com')
        
        assert status_code == 404
        assert content == 'not found'
        assert mock_get.call_count == 1  # 클라이언트 오류는 재시도하지 않음


@pytest.mark.asyncio
async def test_rate_limit_check(http_client):
    """레이트 리밋 확인 테스트"""
    # 요청 속도 제한 설정
    http_client.set_rate_limit(2)  # 분당 2개 요청
    
    # 첫 번째 요청
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MockResponse(200, 'test content')
        mock_get.return_value = mock_response
        
        await http_client.get('https://example.com')
    
    # 두 번째 요청
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MockResponse(200, 'test content')
        mock_get.return_value = mock_response
        
        await http_client.get('https://example.com')
    
    # 세 번째 요청 (레이트 리밋 초과)
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MockResponse(200, 'test content')
        mock_get.return_value = mock_response
        
        with pytest.raises(RateLimitException) as excinfo:
            await http_client.get('https://example.com')
        
        assert 'Rate limit exceeded' in str(excinfo.value)
        assert excinfo.value.retry_after is not None
