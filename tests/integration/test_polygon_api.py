#!/usr/bin/env python3
"""
Polygon API 테스트 스크립트

이 스크립트는 Polygon API의 기본 기능을 테스트합니다.
"""
import os
import logging
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# Polygon 클라이언트 임포트
from data.polygon_client import PolygonClient

def test_get_stock_price():
    """
    주가 데이터 가져오기 테스트
    """
    # API 키 확인
    api_key = os.getenv("POLYGON_API_KEY")
    logger.info(f"Polygon API 키: {api_key[:5]}...{api_key[-5:]}")

    # Polygon 클라이언트 초기화
    polygon = PolygonClient()

    # 테스트할 심볼 목록
    symbols = ["AAPL", "MSFT", "GOOGL"]

    for symbol in symbols:
        logger.info(f"\n{'='*50}\n  {symbol} 주가 데이터 테스트\n{'='*50}")

        # 주가 데이터 가져오기 (30일)
        prices = polygon.get_stock_price(symbol, days=30)

        if prices:
            logger.info(f"{symbol} 주가 데이터 {len(prices)}개 가져옴")

            # 첫 번째 데이터 출력
            if len(prices) > 0:
                logger.info(f"첫 번째 데이터: {json.dumps(prices[0], indent=2)}")

            # 마지막 데이터 출력
            if len(prices) > 1:
                logger.info(f"마지막 데이터: {json.dumps(prices[-1], indent=2)}")
        else:
            logger.error(f"{symbol} 주가 데이터를 가져오지 못했습니다.")





if __name__ == "__main__":
    logger.info("Polygon API 테스트 시작")

    # 주가 데이터 테스트
    test_get_stock_price()

    # 뉴스 데이터 테스트 기능 제거

    # 회사 정보 테스트 기능 제거

    logger.info("Polygon API 테스트 완료")
