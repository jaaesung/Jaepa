"""
HTTP 클라이언트 인터페이스 모듈

HTTP 요청 및 응답 처리를 위한 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class HttpClient(ABC):
    """
    HTTP 클라이언트 인터페이스
    
    HTTP 요청 및 응답 처리를 위한 공통 인터페이스를 정의합니다.
    """
    
    @abstractmethod
    def get(self, url: str, params: Optional[Dict[str, Any]] = None, 
           headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        GET 요청 수행
        
        Args:
            url: 요청 URL
            params: 쿼리 파라미터
            headers: 요청 헤더
            timeout: 타임아웃 (초)
            
        Returns:
            Dict[str, Any]: 응답 데이터
            
        Raises:
            HttpClientError: HTTP 요청 실패 시
        """
        pass
    
    @abstractmethod
    def post(self, url: str, data: Optional[Dict[str, Any]] = None, 
            json_data: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None, 
            timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        POST 요청 수행
        
        Args:
            url: 요청 URL
            data: 폼 데이터
            json_data: JSON 데이터
            headers: 요청 헤더
            timeout: 타임아웃 (초)
            
        Returns:
            Dict[str, Any]: 응답 데이터
            
        Raises:
            HttpClientError: HTTP 요청 실패 시
        """
        pass
    
    @abstractmethod
    def put(self, url: str, data: Optional[Dict[str, Any]] = None, 
           json_data: Optional[Dict[str, Any]] = None, 
           headers: Optional[Dict[str, str]] = None, 
           timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        PUT 요청 수행
        
        Args:
            url: 요청 URL
            data: 폼 데이터
            json_data: JSON 데이터
            headers: 요청 헤더
            timeout: 타임아웃 (초)
            
        Returns:
            Dict[str, Any]: 응답 데이터
            
        Raises:
            HttpClientError: HTTP 요청 실패 시
        """
        pass
    
    @abstractmethod
    def delete(self, url: str, params: Optional[Dict[str, Any]] = None, 
              headers: Optional[Dict[str, str]] = None, 
              timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        DELETE 요청 수행
        
        Args:
            url: 요청 URL
            params: 쿼리 파라미터
            headers: 요청 헤더
            timeout: 타임아웃 (초)
            
        Returns:
            Dict[str, Any]: 응답 데이터
            
        Raises:
            HttpClientError: HTTP 요청 실패 시
        """
        pass
    
    @abstractmethod
    def get_text(self, url: str, params: Optional[Dict[str, Any]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                timeout: Optional[int] = None) -> str:
        """
        GET 요청 수행 후 텍스트 응답 반환
        
        Args:
            url: 요청 URL
            params: 쿼리 파라미터
            headers: 요청 헤더
            timeout: 타임아웃 (초)
            
        Returns:
            str: 응답 텍스트
            
        Raises:
            HttpClientError: HTTP 요청 실패 시
        """
        pass
    
    @abstractmethod
    def get_binary(self, url: str, params: Optional[Dict[str, Any]] = None, 
                  headers: Optional[Dict[str, str]] = None, 
                  timeout: Optional[int] = None) -> bytes:
        """
        GET 요청 수행 후 바이너리 응답 반환
        
        Args:
            url: 요청 URL
            params: 쿼리 파라미터
            headers: 요청 헤더
            timeout: 타임아웃 (초)
            
        Returns:
            bytes: 응답 바이너리 데이터
            
        Raises:
            HttpClientError: HTTP 요청 실패 시
        """
        pass
    
    @abstractmethod
    def set_default_headers(self, headers: Dict[str, str]) -> None:
        """
        기본 요청 헤더 설정
        
        Args:
            headers: 기본 요청 헤더
        """
        pass
    
    @abstractmethod
    def set_base_url(self, base_url: str) -> None:
        """
        기본 URL 설정
        
        Args:
            base_url: 기본 URL
        """
        pass
    
    @abstractmethod
    def set_timeout(self, timeout: int) -> None:
        """
        기본 타임아웃 설정
        
        Args:
            timeout: 타임아웃 (초)
        """
        pass
    
    @abstractmethod
    def set_retry_policy(self, max_retries: int, retry_delay: int) -> None:
        """
        재시도 정책 설정
        
        Args:
            max_retries: 최대 재시도 횟수
            retry_delay: 재시도 간격 (초)
        """
        pass


class HttpClientError(Exception):
    """
    HTTP 클라이언트 오류
    
    HTTP 요청 실패 시 발생하는 예외입니다.
    """
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                response_text: Optional[str] = None, url: Optional[str] = None):
        """
        HttpClientError 초기화
        
        Args:
            message: 오류 메시지
            status_code: HTTP 상태 코드
            response_text: 응답 텍스트
            url: 요청 URL
        """
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        self.url = url
        super().__init__(self.message)
