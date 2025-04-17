"""
API 상태 확인 통합 테스트
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_api_root(test_client):
    """API 루트 엔드포인트 테스트"""
    # 요청
    response = test_client.get("/api")
    
    # 응답 확인
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "message" in response.json()
    assert "version" in response.json()
    assert "endpoints" in response.json()


@pytest.mark.integration
def test_api_health(test_client):
    """API 상태 확인 엔드포인트 테스트"""
    # 요청
    response = test_client.get("/api/v1/health")
    
    # 응답 확인
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "data" in response.json()
    assert "uptime" in response.json()["data"]
    assert "version" in response.json()["data"]
    assert "environment" in response.json()["data"]


@pytest.mark.integration
def test_api_docs(test_client):
    """API 문서 엔드포인트 테스트"""
    # 요청
    response = test_client.get("/api/docs")
    
    # 응답 확인
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Swagger UI" in response.text


@pytest.mark.integration
def test_api_redoc(test_client):
    """API ReDoc 엔드포인트 테스트"""
    # 요청
    response = test_client.get("/api/redoc")
    
    # 응답 확인
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "ReDoc" in response.text


@pytest.mark.integration
def test_api_openapi(test_client):
    """API OpenAPI 스키마 엔드포인트 테스트"""
    # 요청
    response = test_client.get("/api/openapi.json")
    
    # 응답 확인
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "openapi" in response.json()
    assert "info" in response.json()
    assert "paths" in response.json()
    assert "components" in response.json()
