"""
테스트 유틸리티 모듈

이 모듈은 테스트에 필요한 공통 유틸리티 함수를 제공합니다.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_mock_data(filename: str) -> Union[Dict, List]:
    """
    모의 데이터 파일을 로드합니다.
    
    Args:
        filename: 데이터 파일 이름 (tests/data 디렉토리 내의 파일)
        
    Returns:
        Dict 또는 List: 로드된 JSON 데이터
    """
    data_path = Path(__file__).parent / "data" / filename
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"파일을 찾을 수 없습니다: {data_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"JSON 파싱 오류: {data_path}")
        return {}

def setup_test_environment() -> None:
    """
    테스트 환경을 설정합니다.
    
    - 필요한 환경 변수 설정
    - 테스트 디렉토리 경로 추가
    """
    # 프로젝트 루트 경로
    project_root = Path(__file__).parent.parent
    
    # 환경 변수 설정 (필요한 경우)
    os.environ.setdefault("TEST_MODE", "True")
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger.info(f"테스트 환경이 설정되었습니다. 프로젝트 루트: {project_root}")

def get_test_data_path() -> Path:
    """
    테스트 데이터 디렉토리 경로를 반환합니다.
    
    Returns:
        Path: 테스트 데이터 디렉토리 경로
    """
    return Path(__file__).parent / "data"

def create_mock_datetime(days_ago: int = 0, hours_ago: int = 0) -> datetime:
    """
    테스트용 날짜/시간 객체를 생성합니다.
    
    Args:
        days_ago: 현재로부터 뒤로 갈 일수
        hours_ago: 현재로부터 뒤로 갈 시간
        
    Returns:
        datetime: 생성된 날짜/시간 객체
    """
    return datetime.now() - timedelta(days=days_ago, hours=hours_ago)

def create_mock_news_data(count: int = 5) -> List[Dict[str, Any]]:
    """
    모의 뉴스 데이터를 생성합니다.
    
    Args:
        count: 생성할 뉴스 항목 수
        
    Returns:
        List[Dict]: 모의 뉴스 데이터 목록
    """
    news_data = []
    for i in range(count):
        news_data.append({
            "title": f"테스트 뉴스 {i+1}",
            "content": f"테스트 뉴스 {i+1}의 내용입니다.",
            "url": f"https://example.com/news{i+1}",
            "published_date": create_mock_datetime(days_ago=i).strftime("%Y-%m-%d %H:%M:%S"),
            "source": "테스트 소스",
            "source_type": "test",
            "keywords": ["테스트", "뉴스", f"키워드{i+1}"]
        })
    return news_data
