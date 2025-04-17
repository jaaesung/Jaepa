"""
API 응답 모듈 테스트
"""
import pytest
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import status
from pydantic import BaseModel

from api.responses import (
    ResponseModel, SuccessResponse, ErrorResponse,
    PaginatedResponse, DataResponse
)


class TestResponseModel:
    """응답 모델 테스트"""
    
    def test_response_model_base(self):
        """기본 응답 모델 테스트"""
        # 응답 생성
        response = ResponseModel(
            status="success",
            message="Test message"
        )
        
        # 응답 확인
        assert response.status == "success"
        assert response.message == "Test message"
        assert response.timestamp is not None
        assert isinstance(response.timestamp, datetime)
    
    def test_response_model_dict(self):
        """응답 모델 딕셔너리 변환 테스트"""
        # 응답 생성
        response = ResponseModel(
            status="success",
            message="Test message"
        )
        
        # 딕셔너리 변환
        response_dict = response.model_dump()
        
        # 변환 결과 확인
        assert response_dict["status"] == "success"
        assert response_dict["message"] == "Test message"
        assert "timestamp" in response_dict


class TestSuccessResponse:
    """성공 응답 테스트"""
    
    def test_success_response(self):
        """기본 성공 응답 테스트"""
        # 응답 생성
        response = SuccessResponse(
            message="Success message"
        )
        
        # 응답 확인
        assert response.status == "success"
        assert response.message == "Success message"
        assert response.status_code == status.HTTP_200_OK
    
    def test_success_response_with_data(self):
        """데이터가 있는 성공 응답 테스트"""
        # 응답 생성
        response = SuccessResponse(
            message="Success with data",
            data={"key": "value"}
        )
        
        # 응답 확인
        assert response.status == "success"
        assert response.message == "Success with data"
        assert response.data == {"key": "value"}
        assert response.status_code == status.HTTP_200_OK
    
    def test_success_response_with_custom_status_code(self):
        """사용자 정의 상태 코드가 있는 성공 응답 테스트"""
        # 응답 생성
        response = SuccessResponse(
            message="Created",
            status_code=status.HTTP_201_CREATED
        )
        
        # 응답 확인
        assert response.status == "success"
        assert response.message == "Created"
        assert response.status_code == status.HTTP_201_CREATED


class TestErrorResponse:
    """오류 응답 테스트"""
    
    def test_error_response(self):
        """기본 오류 응답 테스트"""
        # 응답 생성
        response = ErrorResponse(
            message="Error message"
        )
        
        # 응답 확인
        assert response.status == "error"
        assert response.message == "Error message"
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_error_response_with_details(self):
        """세부 정보가 있는 오류 응답 테스트"""
        # 응답 생성
        response = ErrorResponse(
            message="Error with details",
            details={"field": "error description"}
        )
        
        # 응답 확인
        assert response.status == "error"
        assert response.message == "Error with details"
        assert response.details == {"field": "error description"}
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_error_response_with_custom_status_code(self):
        """사용자 정의 상태 코드가 있는 오류 응답 테스트"""
        # 응답 생성
        response = ErrorResponse(
            message="Not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
        
        # 응답 확인
        assert response.status == "error"
        assert response.message == "Not found"
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPaginatedResponse:
    """페이지네이션 응답 테스트"""
    
    def test_paginated_response(self):
        """기본 페이지네이션 응답 테스트"""
        # 응답 생성
        response = PaginatedResponse(
            data=[1, 2, 3],
            total=10,
            page=1,
            size=3
        )
        
        # 응답 확인
        assert response.status == "success"
        assert response.data == [1, 2, 3]
        assert response.total == 10
        assert response.page == 1
        assert response.size == 3
        assert response.pages == 4
        assert response.status_code == status.HTTP_200_OK
    
    def test_paginated_response_with_custom_message(self):
        """사용자 정의 메시지가 있는 페이지네이션 응답 테스트"""
        # 응답 생성
        response = PaginatedResponse(
            data=[1, 2, 3],
            total=10,
            page=1,
            size=3,
            message="Custom pagination message"
        )
        
        # 응답 확인
        assert response.status == "success"
        assert response.message == "Custom pagination message"
        assert response.data == [1, 2, 3]
        assert response.total == 10
        assert response.page == 1
        assert response.size == 3
        assert response.pages == 4
        assert response.status_code == status.HTTP_200_OK


class TestDataResponse:
    """데이터 응답 테스트"""
    
    def test_data_response_with_list(self):
        """리스트 데이터 응답 테스트"""
        # 응답 생성
        response = DataResponse(
            data=[1, 2, 3]
        )
        
        # 응답 확인
        assert response.status == "success"
        assert response.data == [1, 2, 3]
        assert response.status_code == status.HTTP_200_OK
    
    def test_data_response_with_dict(self):
        """딕셔너리 데이터 응답 테스트"""
        # 응답 생성
        response = DataResponse(
            data={"key": "value"}
        )
        
        # 응답 확인
        assert response.status == "success"
        assert response.data == {"key": "value"}
        assert response.status_code == status.HTTP_200_OK
    
    def test_data_response_with_pydantic_model(self):
        """Pydantic 모델 데이터 응답 테스트"""
        # 모델 정의
        class TestModel(BaseModel):
            id: int
            name: str
        
        # 모델 인스턴스 생성
        model = TestModel(id=1, name="Test")
        
        # 응답 생성
        response = DataResponse(
            data=model
        )
        
        # 응답 확인
        assert response.status == "success"
        assert response.data == model
        assert response.status_code == status.HTTP_200_OK
    
    def test_data_response_with_custom_message(self):
        """사용자 정의 메시지가 있는 데이터 응답 테스트"""
        # 응답 생성
        response = DataResponse(
            data={"key": "value"},
            message="Custom data message"
        )
        
        # 응답 확인
        assert response.status == "success"
        assert response.message == "Custom data message"
        assert response.data == {"key": "value"}
        assert response.status_code == status.HTTP_200_OK
