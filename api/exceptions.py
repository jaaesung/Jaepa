"""
사용자 정의 예외 모듈

API에서 사용할 사용자 정의 예외 클래스를 제공합니다.
"""
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, status


class ErrorCode:
    """오류 코드 상수"""
    # 인증 관련 오류
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    
    # 리소스 관련 오류
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    
    # 유효성 검사 오류
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    
    # 비즈니스 로직 오류
    BUSINESS_LOGIC_ERROR = "BUSINESS_LOGIC_ERROR"
    OPERATION_FAILED = "OPERATION_FAILED"
    
    # 외부 서비스 오류
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    API_RATE_LIMIT = "API_RATE_LIMIT"
    NETWORK_ERROR = "NETWORK_ERROR"
    
    # 서버 오류
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


class ApiException(HTTPException):
    """
    API 예외 기본 클래스
    
    모든 API 예외의 기본 클래스입니다.
    """
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        """
        ApiException 초기화
        
        Args:
            status_code: HTTP 상태 코드
            error_code: 오류 코드
            message: 오류 메시지
            field: 오류가 발생한 필드 (해당되는 경우)
            details: 추가 오류 세부 정보
            headers: 응답 헤더
        """
        self.error_code = error_code
        self.field = field
        self.details = details
        
        # 오류 상세 정보 생성
        error_detail = {
            "code": error_code,
            "message": message
        }
        
        if field:
            error_detail["field"] = field
            
        if details:
            error_detail["details"] = details
        
        super().__init__(status_code=status_code, detail=error_detail, headers=headers)


class AuthenticationException(ApiException):
    """인증 예외"""
    
    def __init__(
        self,
        message: str = "인증에 실패했습니다.",
        error_code: str = ErrorCode.AUTHENTICATION_FAILED,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code,
            message=message,
            details=details,
            headers={"WWW-Authenticate": "Bearer"}
        )


class PermissionDeniedException(ApiException):
    """권한 거부 예외"""
    
    def __init__(
        self,
        message: str = "이 작업을 수행할 권한이 없습니다.",
        error_code: str = ErrorCode.PERMISSION_DENIED,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code,
            message=message,
            details=details
        )


class ResourceNotFoundException(ApiException):
    """리소스 찾을 수 없음 예외"""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: Union[str, int],
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"{resource_type} (ID: {resource_id})를 찾을 수 없습니다."
            
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            message=message,
            details=details or {"resource_type": resource_type, "resource_id": resource_id}
        )


class ResourceAlreadyExistsException(ApiException):
    """리소스 이미 존재 예외"""
    
    def __init__(
        self,
        resource_type: str,
        identifier: Dict[str, Any],
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"{resource_type}가 이미 존재합니다."
            
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code=ErrorCode.RESOURCE_ALREADY_EXISTS,
            message=message,
            details=details or {"resource_type": resource_type, "identifier": identifier}
        )


class ValidationException(ApiException):
    """유효성 검사 예외"""
    
    def __init__(
        self,
        message: str = "입력 데이터가 유효하지 않습니다.",
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code=ErrorCode.VALIDATION_ERROR,
            message=message,
            field=field,
            details=details
        )


class BusinessLogicException(ApiException):
    """비즈니스 로직 예외"""
    
    def __init__(
        self,
        message: str,
        error_code: str = ErrorCode.BUSINESS_LOGIC_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code,
            message=message,
            details=details
        )


class ExternalServiceException(ApiException):
    """외부 서비스 예외"""
    
    def __init__(
        self,
        service_name: str,
        message: Optional[str] = None,
        error_code: str = ErrorCode.EXTERNAL_SERVICE_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"외부 서비스 {service_name}에 접근하는 중 오류가 발생했습니다."
            
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code=error_code,
            message=message,
            details=details or {"service_name": service_name}
        )


class RateLimitException(ApiException):
    """속도 제한 예외"""
    
    def __init__(
        self,
        message: str = "요청 속도 제한을 초과했습니다. 잠시 후 다시 시도해주세요.",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
            
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=ErrorCode.API_RATE_LIMIT,
            message=message,
            details=details,
            headers=headers
        )


class DatabaseException(ApiException):
    """데이터베이스 예외"""
    
    def __init__(
        self,
        message: str = "데이터베이스 작업 중 오류가 발생했습니다.",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.DATABASE_ERROR,
            message=message,
            details=details
        )


class InternalServerException(ApiException):
    """내부 서버 예외"""
    
    def __init__(
        self,
        message: str = "서버 내부 오류가 발생했습니다.",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=message,
            details=details
        )


class NotImplementedException(ApiException):
    """구현되지 않음 예외"""
    
    def __init__(
        self,
        message: str = "이 기능은 아직 구현되지 않았습니다.",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            error_code=ErrorCode.NOT_IMPLEMENTED,
            message=message,
            details=details
        )
