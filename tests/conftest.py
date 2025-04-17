"""
pytest 설정 파일

이 파일은 pytest 설정 및 공통 fixture를 정의합니다.
"""
import sys
import os
import json
import pytest
import logging
import asyncio
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator, AsyncGenerator
from unittest.mock import MagicMock, patch

import motor.motor_asyncio
import pymongo
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# .env.test 파일 로드 (테스트용 환경 변수)
dotenv_path = project_root / '.env.test'
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
    print(f"\n.env.test 파일이 로드되었습니다: {dotenv_path}")
else:
    # 기본 .env 파일 로드
    dotenv_path = project_root / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
        print(f"\n.env 파일이 로드되었습니다: {dotenv_path}")
        print(f"POLYGON_API_KEY 설정 여부: {'POLYGON_API_KEY' in os.environ}")
        if 'POLYGON_API_KEY' in os.environ:
            key = os.environ['POLYGON_API_KEY']
            masked_key = key[:4] + '*' * (len(key) - 4) if len(key) > 4 else '****'
            print(f"POLYGON_API_KEY: {masked_key}")
    else:
        print(f"\n경고: 환경 변수 파일을 찾을 수 없습니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 테스트 환경 설정
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("TEST_MODE", "True")

# MongoDB 테스트 설정
MONGODB_TEST_URI = os.environ.get("MONGODB_TEST_URI", "mongodb://localhost:27017/")
MONGODB_TEST_DB = os.environ.get("MONGODB_TEST_DB", "jaepa_test")


# ===== 데이터베이스 관련 Fixture =====

@pytest.fixture(scope="session")
def event_loop():
    """
    pytest-asyncio용 이벤트 루프 fixture

    Returns:
        asyncio.AbstractEventLoop: 이벤트 루프
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def mongo_client():
    """
    MongoDB 클라이언트 fixture

    Returns:
        pymongo.MongoClient: MongoDB 클라이언트
    """
    client = pymongo.MongoClient(MONGODB_TEST_URI)
    yield client
    client.drop_database(MONGODB_TEST_DB)
    client.close()


@pytest.fixture(scope="session")
def mongo_db(mongo_client):
    """
    MongoDB 데이터베이스 fixture

    Args:
        mongo_client: MongoDB 클라이언트

    Returns:
        pymongo.database.Database: MongoDB 데이터베이스
    """
    db = mongo_client[MONGODB_TEST_DB]
    yield db
    # 테스트 후 모든 컬렉션 삭제
    for collection_name in db.list_collection_names():
        db.drop_collection(collection_name)


@pytest.fixture
async def async_mongo_client():
    """
    비동기 MongoDB 클라이언트 fixture

    Returns:
        motor.motor_asyncio.AsyncIOMotorClient: 비동기 MongoDB 클라이언트
    """
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_TEST_URI)
    yield client
    await client.drop_database(MONGODB_TEST_DB)
    client.close()


@pytest.fixture
async def async_mongo_db(async_mongo_client):
    """
    비동기 MongoDB 데이터베이스 fixture

    Args:
        async_mongo_client: 비동기 MongoDB 클라이언트

    Returns:
        motor.motor_asyncio.AsyncIOMotorDatabase: 비동기 MongoDB 데이터베이스
    """
    db = async_mongo_client[MONGODB_TEST_DB]
    yield db
    # 테스트 후 모든 컬렉션 삭제
    collections = await db.list_collection_names()
    for collection_name in collections:
        await db.drop_collection(collection_name)


# ===== API 관련 Fixture =====

@pytest.fixture
def api_client():
    """
    FastAPI 테스트 클라이언트 fixture

    Returns:
        TestClient: FastAPI 테스트 클라이언트
    """
    # 순환 임포트 방지를 위해 여기서 임포트
    try:
        from backend.app.main import app

        with TestClient(app) as client:
            yield client
    except ImportError:
        pytest.skip("FastAPI 앱을 임포트할 수 없습니다.")


@pytest.fixture
def auth_headers():
    """
    인증 헤더 fixture

    Returns:
        Dict[str, str]: 인증 헤더
    """
    # 테스트용 토큰 생성
    try:
        from backend.app.auth import create_access_token

        access_token = create_access_token(
            data={"sub": "test_user"},
            expires_delta=timedelta(minutes=30)
        )

        return {"Authorization": f"Bearer {access_token}"}
    except ImportError:
        pytest.skip("인증 모듈을 임포트할 수 없습니다.")
        return {}


# ===== 모의 데이터 Fixture =====

@pytest.fixture
def mock_news_data() -> List[Dict[str, Any]]:
    """
    모의 뉴스 데이터를 제공하는 fixture

    Returns:
        List[Dict]: 모의 뉴스 데이터 목록
    """
    return [
        {
            "title": "테스트 뉴스 1",
            "content": "테스트 뉴스 1의 내용입니다.",
            "url": "https://example.com/news1",
            "published_date": datetime.now() - timedelta(days=1),
            "source": "테스트 소스 1",
            "source_type": "rss",
            "keywords": ["테스트", "뉴스", "키워드1"],
            "symbols": ["AAPL"]
        },
        {
            "title": "테스트 뉴스 2",
            "content": "테스트 뉴스 2의 내용입니다.",
            "url": "https://example.com/news2",
            "published_date": datetime.now() - timedelta(days=2),
            "source": "테스트 소스 2",
            "source_type": "api",
            "keywords": ["테스트", "뉴스", "키워드2"],
            "symbols": ["GOOGL"]
        },
        {
            "title": "테스트 뉴스 3",
            "content": "테스트 뉴스 3의 내용입니다.",
            "url": "https://example.com/news3",
            "published_date": datetime.now() - timedelta(days=3),
            "source": "테스트 소스 3",
            "source_type": "finnhub",
            "keywords": ["테스트", "뉴스", "키워드3"],
            "symbols": ["MSFT", "AAPL"]
        }
    ]

@pytest.fixture
def mock_stock_data() -> List[Dict[str, Any]]:
    """
    모의 주식 데이터를 제공하는 fixture

    Returns:
        List[Dict]: 모의 주식 데이터 목록
    """
    return [
        {
            "ticker": "AAPL",
            "date": datetime.now().date() - timedelta(days=1),
            "open": 150.0,
            "high": 155.0,
            "low": 149.0,
            "close": 153.0,
            "volume": 1000000
        },
        {
            "ticker": "AAPL",
            "date": datetime.now().date() - timedelta(days=2),
            "open": 153.0,
            "high": 158.0,
            "low": 152.0,
            "close": 157.0,
            "volume": 1200000
        },
        {
            "ticker": "AAPL",
            "date": datetime.now().date() - timedelta(days=3),
            "open": 157.0,
            "high": 160.0,
            "low": 156.0,
            "close": 159.0,
            "volume": 1100000
        }
    ]

@pytest.fixture
def mock_sentiment_data() -> List[Dict[str, Any]]:
    """
    모의 감성 분석 데이터를 제공하는 fixture

    Returns:
        List[Dict]: 모의 감성 분석 데이터 목록
    """
    return [
        {
            "text": "이 회사의 실적이 매우 좋습니다.",
            "label": "positive",
            "score": 0.85,
            "scores": {"positive": 0.85, "neutral": 0.10, "negative": 0.05}
        },
        {
            "text": "이 회사의 실적은 보통입니다.",
            "label": "neutral",
            "score": 0.75,
            "scores": {"positive": 0.15, "neutral": 0.75, "negative": 0.10}
        },
        {
            "text": "이 회사의 실적이 매우 나쁩니다.",
            "label": "negative",
            "score": 0.80,
            "scores": {"positive": 0.05, "neutral": 0.15, "negative": 0.80}
        }
    ]

@pytest.fixture
def mock_mongodb_client(monkeypatch):
    """
    MongoDB 클라이언트를 모킹하는 fixture

    Args:
        monkeypatch: pytest monkeypatch 객체

    Returns:
        MagicMock: 모의 MongoDB 클라이언트
    """
    from unittest.mock import MagicMock

    # 모의 컬렉션 생성
    mock_collection = MagicMock()
    mock_collection.find.return_value = []
    mock_collection.find_one.return_value = None
    mock_collection.insert_one.return_value = MagicMock()
    mock_collection.insert_many.return_value = MagicMock()

    # 모의 데이터베이스 생성
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection

    # 모의 클라이언트 생성
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db

    return mock_client


@pytest.fixture
def load_fixture():
    """
    테스트 픽스처 로드 헬퍼

    Returns:
        function: 픽스처 파일을 로드하는 함수
    """
    def _load_fixture(filename):
        fixture_path = Path(__file__).parent / "fixtures" / filename
        if not fixture_path.exists():
            pytest.fail(f"픽스처 파일을 찾을 수 없습니다: {fixture_path}")
        with open(fixture_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return _load_fixture


@pytest.fixture
def mock_polygon_ticker_details(load_fixture):
    """
    Polygon 티커 세부 정보 모킹

    Args:
        load_fixture: 픽스처 로드 헬퍼

    Returns:
        dict: 모의 티커 세부 정보
    """
    return load_fixture("polygon_ticker_details.json")


@pytest.fixture
def mock_polygon_daily_bars(load_fixture):
    """
    Polygon 일별 가격 바 모킹

    Args:
        load_fixture: 픽스처 로드 헬퍼

    Returns:
        dict: 모의 일별 가격 바
    """
    return load_fixture("polygon_daily_bars.json")


@pytest.fixture
def mock_polygon_news(load_fixture):
    """
    Polygon 뉴스 모킹

    Args:
        load_fixture: 픽스처 로드 헬퍼

    Returns:
        dict: 모의 뉴스
    """
    return load_fixture("polygon_news.json")


@pytest.fixture
def mock_finbert_sentiment(load_fixture):
    """
    FinBERT 감성 분석 결과 모킹

    Args:
        load_fixture: 픽스처 로드 헬퍼

    Returns:
        dict: 모의 감성 분석 결과
    """
    return load_fixture("finbert_sentiment.json")


@pytest.fixture
def mock_user_data() -> List[Dict[str, Any]]:
    """
    모의 사용자 데이터를 제공하는 fixture

    Returns:
        List[Dict[str, Any]]: 모의 사용자 데이터 목록
    """
    return [
        {
            "username": "test_user1",
            "email": "test1@example.com",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # 'password'
            "full_name": "Test User 1",
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now() - timedelta(days=10)
        },
        {
            "username": "test_user2",
            "email": "test2@example.com",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # 'password'
            "full_name": "Test User 2",
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now() - timedelta(days=5)
        },
        {
            "username": "admin_user",
            "email": "admin@example.com",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # 'password'
            "full_name": "Admin User",
            "is_active": True,
            "is_admin": True,
            "created_at": datetime.now() - timedelta(days=20)
        }
    ]


# ===== 유틸리티 Fixture =====

@pytest.fixture
def temp_dir():
    """
    임시 디렉토리 fixture

    Returns:
        Path: 임시 디렉토리 경로
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_response():
    """
    모의 HTTP 응답 생성 헬퍼

    Returns:
        function: 모의 HTTP 응답을 생성하는 함수
    """
    def _create_mock_response(data, status_code=200, headers=None):
        mock_resp = MagicMock()
        mock_resp.json.return_value = data
        mock_resp.status_code = status_code
        mock_resp.headers = headers or {}
        mock_resp.text = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
        mock_resp.content = mock_resp.text.encode('utf-8')
        mock_resp.raise_for_status.return_value = None
        return mock_resp
    return _create_mock_response


# ===== 모의 외부 서비스 Fixture =====

@pytest.fixture
def mock_polygon_api():
    """
    Polygon API 모킹 fixture

    Returns:
        MagicMock: 모의 Polygon API 클라이언트
    """
    with patch('polygon.RESTClient') as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_finnhub_api():
    """
    Finnhub API 모킹 fixture

    Returns:
        MagicMock: 모의 Finnhub API 클라이언트
    """
    with patch('finnhub.Client') as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_finbert():
    """
    FinBERT 모델 모킹 fixture

    Returns:
        MagicMock: 모의 FinBERT 모델
    """
    with patch('transformers.AutoModelForSequenceClassification.from_pretrained') as mock_model, \
         patch('transformers.AutoTokenizer.from_pretrained') as mock_tokenizer:

        mock_model_instance = MagicMock()
        mock_tokenizer_instance = MagicMock()

        mock_model.return_value = mock_model_instance
        mock_tokenizer.return_value = mock_tokenizer_instance

        # 모의 예측 결과 설정
        mock_output = MagicMock()
        mock_output.logits = MagicMock()
        mock_model_instance.return_value = mock_output

        yield {
            "model": mock_model_instance,
            "tokenizer": mock_tokenizer_instance
        }
