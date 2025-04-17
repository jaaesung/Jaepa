"""
API 예외 처리 모듈 테스트
"""
import pytest
from fastapi import HTTPException, status

from api.exceptions import (
    APIError, BadRequestError, UnauthorizedError,
    ForbiddenError, NotFoundError, ConflictError,
    InternalServerError, ServiceUnavailableError
)


class TestAPIError:
    """API 오류 테스트"""
    
    def test_api_error_base(self):
        """기본 API 오류 테스트"""
        # 오류 생성
        error = APIError(
            message="Test error",
            status_code=400
        )
        
        # 오류 확인
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.details is None
    
    def test_api_error_with_details(self):
        """세부 정보가 있는 API 오류 테스트"""
        # 오류 생성
        error = APIError(
            message="Test error with details",
            status_code=400,
            details={"field": "error description"}
        )
        
        # 오류 확인
        assert error.message == "Test error with details"
        assert error.status_code == 400
        assert error.details == {"field": "error description"}
    
    def test_api_error_to_http_exception(self):
        """HTTP 예외 변환 테스트"""
        # 오류 생성
        error = APIError(
            message="Test error",
            status_code=400
        )
        
        # HTTP 예외 변환
        http_exception = error.to_http_exception()
        
        # 변환 결과 확인
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == 400
        assert http_exception.detail == "Test error"


class TestBadRequestError:
    """잘못된 요청 오류 테스트"""
    
    def test_bad_request_error(self):
        """기본 잘못된 요청 오류 테스트"""
        # 오류 생성
        error = BadRequestError(
            message="Bad request"
        )
        
        # 오류 확인
        assert error.message == "Bad request"
        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert error.details is None
    
    def test_bad_request_error_with_details(self):
        """세부 정보가 있는 잘못된 요청 오류 테스트"""
        # 오류 생성
        error = BadRequestError(
            message="Bad request with details",
            details={"field": "error description"}
        )
        
        # 오류 확인
        assert error.message == "Bad request with details"
        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert error.details == {"field": "error description"}


class TestUnauthorizedError:
    """인증되지 않은 오류 테스트"""
    
    def test_unauthorized_error(self):
        """기본 인증되지 않은 오류 테스트"""
        # 오류 생성
        error = UnauthorizedError(
            message="Unauthorized"
        )
        
        # 오류 확인
        assert error.message == "Unauthorized"
        assert error.status_code == status.HTTP_401_UNAUTHORIZED
        assert error.details is None


class TestForbiddenError:
    """금지된 오류 테스트"""
    
    def test_forbidden_error(self):
        """기본 금지된 오류 테스트"""
        # 오류 생성
        error = ForbiddenError(
            message="Forbidden"
        )
        
        # 오류 확인
        assert error.message == "Forbidden"
        assert error.status_code == status.HTTP_403_FORBIDDEN
        assert error.details is None


class TestNotFoundError:
    """찾을 수 없음 오류 테스트"""
    
    def test_not_found_error(self):
        """기본 찾을 수 없음 오류 테스트"""
        # 오류 생성
        error = NotFoundError(
            message="Not found"
        )
        
        # 오류 확인
        assert error.message == "Not found"
        assert error.status_code == status.HTTP_404_NOT_FOUND
        assert error.details is None
    
    def test_not_found_error_with_resource(self):
        """리소스가 있는 찾을 수 없음 오류 테스트"""
        # 오류 생성
        error = NotFoundError.with_resource("User", "123")
        
        # 오류 확인
        assert error.message == "User with ID 123 not found"
        assert error.status_code == status.HTTP_404_NOT_FOUND
        assert error.details is None


class TestConflictError:
    """충돌 오류 테스트"""
    
    def test_conflict_error(self):
        """기본 충돌 오류 테스트"""
        # 오류 생성
        error = ConflictError(
            message="Conflict"
        )
        
        # 오류 확인
        assert error.message == "Conflict"
        assert error.status_code == status.HTTP_409_CONFLICT
        assert error.details is None
    
    def test_conflict_error_with_resource(self):
        """리소스가 있는 충돌 오류 테스트"""
        # 오류 생성
        error = ConflictError.with_resource("User", "email", "test@example.com")
        
        # 오류 확인
        assert error.message == "User with email test@example.com already exists"
        assert error.status_code == status.HTTP_409_CONFLICT
        assert error.details is None


class TestInternalServerError:
    """내부 서버 오류 테스트"""
    
    def test_internal_server_error(self):
        """기본 내부 서버 오류 테스트"""
        # 오류 생성
        error = InternalServerError(
            message="Internal server error"
        )
        
        # 오류 확인
        assert error.message == "Internal server error"
        assert error.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert error.details is None


class TestServiceUnavailableError:
    """서비스 사용 불가 오류 테스트"""
    
    def test_service_unavailable_error(self):
        """기본 서비스 사용 불가 오류 테스트"""
        # 오류 생성
        error = ServiceUnavailableError(
            message="Service unavailable"
        )
        
        # 오류 확인
        assert error.message == "Service unavailable"
        assert error.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert error.details is None
