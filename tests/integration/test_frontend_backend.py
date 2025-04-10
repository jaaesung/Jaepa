#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
프론트엔드와 백엔드 통합 테스트 스크립트
"""

import os
import sys
import pytest
import requests
import json
import time
import subprocess
from pathlib import Path

# 현재 스크립트의 디렉토리를 기준으로 프로젝트 루트 경로 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# 백엔드 API URL 및 테스트 계정
TEST_API_URL = os.environ.get("TEST_API_URL", "http://localhost:8000/api")
TEST_USERNAME = os.environ.get("TEST_USERNAME", "test@example.com")
TEST_PASSWORD = os.environ.get("TEST_PASSWORD", "testpassword")

@pytest.fixture(scope="module")
def api_token():
    """테스트에 사용할 API 토큰을 얻는 fixture"""
    try:
        response = requests.post(
            f"{TEST_API_URL}/auth/login",
            json={"email": TEST_USERNAME, "password": TEST_PASSWORD},
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("token")
    except requests.exceptions.RequestException as e:
        pytest.fail(f"API 서버에 연결할 수 없습니다: {e}")
        return None

def test_api_health():
    """API 서버 상태 확인"""
    try:
        response = requests.get(f"{TEST_API_URL}/health", timeout=5)
        assert response.status_code == 200
        assert response.json().get("status") == "ok"
    except requests.exceptions.RequestException as e:
        pytest.fail(f"API 서버에 연결할 수 없습니다: {e}")

def test_auth_endpoints(api_token):
    """인증 관련 엔드포인트 테스트"""
    # 사용자 정보 가져오기
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.get(f"{TEST_API_URL}/auth/user", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert "id" in user_data
    assert "email" in user_data

def test_news_endpoints(api_token):
    """뉴스 관련 엔드포인트 테스트"""
    headers = {"Authorization": f"Bearer {api_token}"}
    
    # 뉴스 목록 가져오기
    response = requests.get(f"{TEST_API_URL}/news", headers=headers)
    assert response.status_code == 200
    news_data = response.json()
    assert "items" in news_data
    assert "total" in news_data
    
    # 특정 뉴스 항목이 있으면 상세 정보 가져오기
    if news_data["items"]:
        news_id = news_data["items"][0]["id"]
        response = requests.get(f"{TEST_API_URL}/news/{news_id}", headers=headers)
        assert response.status_code == 200
        news_detail = response.json()
        assert "id" in news_detail
        assert "title" in news_detail
        assert "content" in news_detail

def test_stock_endpoints(api_token):
    """주식 관련 엔드포인트 테스트"""
    headers = {"Authorization": f"Bearer {api_token}"}
    
    # 주식 데이터 가져오기 (AAPL 예시)
    response = requests.get(
        f"{TEST_API_URL}/stocks/data/AAPL", 
        params={"period": "1w"},
        headers=headers
    )
    assert response.status_code == 200
    stock_data = response.json()
    assert "data" in stock_data
    
    # 주식 감성 상관관계 가져오기
    response = requests.get(
        f"{TEST_API_URL}/stocks/correlation/AAPL",
        headers=headers
    )
    assert response.status_code == 200
    correlation_data = response.json()
    assert "symbol" in correlation_data
    assert "correlation_data" in correlation_data

@pytest.fixture(scope="module")
def frontend_build():
    """프론트엔드 빌드하는 fixture"""
    # 현재 경로 저장
    original_dir = os.getcwd()
    
    try:
        # 프론트엔드 디렉토리로 이동
        os.chdir(PROJECT_ROOT / "frontend")
        
        # 의존성 설치 (필요한 경우)
        # subprocess.run(["npm", "install"], check=True)
        
        # 빌드 실행
        subprocess.run(["npm", "run", "build"], check=True)
        
        # 빌드 성공 확인
        build_dir = PROJECT_ROOT / "frontend" / "build"
        assert build_dir.exists(), "프론트엔드 빌드 디렉토리가 존재하지 않습니다."
        
        index_html = build_dir / "index.html"
        assert index_html.exists(), "index.html 파일이 존재하지 않습니다."
        
        yield build_dir
    
    except subprocess.CalledProcessError as e:
        pytest.fail(f"프론트엔드 빌드 실패: {e}")
    
    finally:
        # 원래 디렉토리로 복귀
        os.chdir(original_dir)

def test_frontend_build_files(frontend_build):
    """프론트엔드 빌드 파일 확인"""
    # 필수 빌드 파일 확인
    required_dirs = ["static"]
    for dirname in required_dirs:
        dir_path = frontend_build / dirname
        assert dir_path.exists(), f"{dirname} 디렉토리가 존재하지 않습니다."
    
    # CSS 및 JS 파일 존재 확인
    css_files = list(frontend_build.glob("static/css/*.css"))
    js_files = list(frontend_build.glob("static/js/*.js"))
    
    assert len(css_files) > 0, "CSS 파일이 존재하지 않습니다."
    assert len(js_files) > 0, "JS 파일이 존재하지 않습니다."

def test_frontend_env_variables():
    """프론트엔드 환경 변수 설정 확인"""
    env_file = PROJECT_ROOT / "frontend" / ".env"
    
    # .env 파일이 없다면 .env.example로 확인
    if not env_file.exists():
        env_file = PROJECT_ROOT / "frontend" / ".env.example"
    
    assert env_file.exists(), "프론트엔드 환경 변수 파일이 존재하지 않습니다."
    
    # 필수 환경 변수 확인
    required_vars = ["REACT_APP_API_URL"]
    
    with open(env_file, 'r') as f:
        env_content = f.read()
        
    for var in required_vars:
        assert var in env_content, f"필수 환경 변수 {var}가 .env 파일에 없습니다."

def test_api_cors_configuration():
    """API CORS 설정 확인"""
    try:
        # Options 요청으로 CORS 헤더 확인
        response = requests.options(
            f"{TEST_API_URL}/health",
            headers={"Origin": "http://localhost:3000"},
            timeout=5
        )
        
        # CORS 헤더 확인
        assert "Access-Control-Allow-Origin" in response.headers, "CORS 헤더가 설정되지 않았습니다."
        assert "Access-Control-Allow-Methods" in response.headers, "CORS 메소드 헤더가 설정되지 않았습니다."
        assert "Access-Control-Allow-Headers" in response.headers, "CORS 헤더 허용 목록이 설정되지 않았습니다."
    except requests.exceptions.RequestException as e:
        pytest.fail(f"API 서버에 연결할 수 없습니다: {e}")

if __name__ == "__main__":
    # 직접 실행 시 pytest 실행
    pytest.main(["-v", __file__])
