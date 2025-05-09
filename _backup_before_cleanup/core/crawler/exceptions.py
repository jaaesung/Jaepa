"""
뉴스 크롤링 모듈 예외 클래스

뉴스 크롤링 과정에서 발생할 수 있는 다양한 예외를 정의합니다.
"""
from typing import Optional, Dict, Any


class CrawlerException(Exception):
    """크롤링 관련 기본 예외 클래스"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class HttpClientException(CrawlerException):
    """HTTP 요청 관련 예외"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 url: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.status_code = status_code
        self.url = url
        super().__init__(message, details)


class RateLimitException(HttpClientException):
    """API 요청 제한 관련 예외"""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, 
                 url: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.retry_after = retry_after
        super().__init__(message, 429, url, details)


class TimeoutException(HttpClientException):
    """요청 타임아웃 예외"""
    
    def __init__(self, message: str, url: Optional[str] = None, 
                 timeout: Optional[float] = None, details: Optional[Dict[str, Any]] = None):
        self.timeout = timeout
        super().__init__(message, None, url, details)


class ConnectionException(HttpClientException):
    """연결 관련 예외"""
    
    def __init__(self, message: str, url: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, None, url, details)


class ParsingException(CrawlerException):
    """데이터 파싱 관련 예외"""
    
    def __init__(self, message: str, source: Optional[str] = None, 
                 data: Optional[Any] = None, details: Optional[Dict[str, Any]] = None):
        self.source = source
        self.data = data
        super().__init__(message, details)


class SourceException(CrawlerException):
    """뉴스 소스 관련 예외"""
    
    def __init__(self, message: str, source_id: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        self.source_id = source_id
        super().__init__(message, details)


class StorageException(CrawlerException):
    """데이터 저장 관련 예외"""
    
    def __init__(self, message: str, operation: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        self.operation = operation
        super().__init__(message, details)


class ConfigurationException(CrawlerException):
    """설정 관련 예외"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        self.config_key = config_key
        super().__init__(message, details)


class AuthenticationException(CrawlerException):
    """인증 관련 예외"""
    
    def __init__(self, message: str, service: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        self.service = service
        super().__init__(message, details)
