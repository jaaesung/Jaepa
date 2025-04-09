"""
pytest 설정 파일

이 파일은 pytest 설정 및 공통 fixture를 정의합니다.
"""
import sys
import os
import json
import pytest
import logging
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# .env 파일 로드
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
    print(f"\n경고: .env 파일을 찾을 수 없습니다: {dotenv_path}")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            "published_date": "2023-04-01 10:00:00",
            "source": "테스트 소스 1",
            "source_type": "rss",
            "keywords": ["테스트", "뉴스", "키워드1"]
        },
        {
            "title": "테스트 뉴스 2",
            "content": "테스트 뉴스 2의 내용입니다.",
            "url": "https://example.com/news2",
            "published_date": "2023-04-02 11:00:00",
            "source": "테스트 소스 2",
            "source_type": "api",
            "keywords": ["테스트", "뉴스", "키워드2"]
        },
        {
            "title": "테스트 뉴스 3",
            "content": "테스트 뉴스 3의 내용입니다.",
            "url": "https://example.com/news3",
            "published_date": "2023-04-03 12:00:00",
            "source": "테스트 소스 3",
            "source_type": "finnhub",
            "keywords": ["테스트", "뉴스", "키워드3"]
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
            "date": "2023-04-01",
            "open": 150.0,
            "high": 155.0,
            "low": 149.0,
            "close": 153.0,
            "volume": 1000000
        },
        {
            "ticker": "AAPL",
            "date": "2023-04-02",
            "open": 153.0,
            "high": 158.0,
            "low": 152.0,
            "close": 157.0,
            "volume": 1200000
        },
        {
            "ticker": "AAPL",
            "date": "2023-04-03",
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
