#!/usr/bin/env python3
"""
GDELT API 테스트 스크립트

이 스크립트는 GDELT API의 기본 기능을 테스트합니다.
"""
import logging
import json
import time
from datetime import datetime, timedelta
import urllib.parse
import requests

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_random_user_agent():
    """랜덤 User-Agent 문자열 반환"""
    return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"

def make_gdelt_request(query, format_type="json", max_records=10):
    """
    GDELT API 요청 테스트

    Args:
        query: 검색어
        format_type: 응답 형식 (json, csv, html)
        max_records: 최대 검색 결과 수
    """
    # GDELT API 엔드포인트
    gdelt_v2_api = "https://api.gdeltproject.org/api/v2/doc/doc"

    # 쿼리 파라미터 구성 (timespan 없이)
    params = {
        "query": query,
        "format": format_type,
        "maxrecords": max_records,
        "sort": "DateDesc"
    }

    # URL 인코딩
    query_string = urllib.parse.urlencode(params)
    url = f"{gdelt_v2_api}?{query_string}"

    logger.info(f"GDELT API 요청: {url}")

    # 헤더 설정
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "application/json, text/html",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        # API 요청
        response = requests.get(url, headers=headers, timeout=15)

        logger.info(f"응답 상태 코드: {response.status_code}")
        logger.info(f"응답 헤더: {response.headers}")

        if response.status_code == 200:
            # 응답 내용 확인
            content_type = response.headers.get('Content-Type', '')
            logger.info(f"응답 Content-Type: {content_type}")

            # 응답 내용 출력 (처음 500자)
            response_text = response.text
            logger.info(f"응답 내용 (처음 500자): {response_text[:500]}")

            # JSON 파싱 시도
            if format_type == "json" and "application/json" in content_type:
                try:
                    response_json = json.loads(response_text)
                    articles = response_json.get("articles", [])
                    logger.info(f"파싱된 기사 수: {len(articles)}")

                    # 첫 번째 기사 출력
                    if articles:
                        logger.info(f"첫 번째 기사: {json.dumps(articles[0], indent=2)}")

                except json.JSONDecodeError as e:
                    logger.error(f"JSON 파싱 오류: {str(e)}")

            return response.status_code, response.text
        else:
            logger.error(f"API 요청 실패: {response.status_code}")
            return response.status_code, None

    except Exception as e:
        logger.error(f"요청 중 오류 발생: {str(e)}")
        return -1, None

def test_gdelt_api():
    """
    GDELT API 테스트
    """
    # 테스트 쿼리
    queries = [
        "Apple",
        "Microsoft",
        "Google",
        '"stock market"',
        '"financial news"'
    ]

    for query in queries:
        logger.info(f"\n{'='*50}\n  쿼리: {query}\n{'='*50}")

        # API 요청
        status_code, response_text = make_gdelt_request(query)

        # 결과 확인
        if status_code == 200 and response_text:
            logger.info(f"쿼리 '{query}' 성공")
        else:
            logger.error(f"쿼리 '{query}' 실패")

        # 요청 간격 조절
        time.sleep(2.0)

if __name__ == "__main__":
    test_gdelt_api()
