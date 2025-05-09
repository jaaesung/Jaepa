#!/usr/bin/env python3
"""
GDELT와 주가 상관관계 테스트 스크립트

이 스크립트는 GDELT 데이터와 주가 데이터 간의 상관관계를 테스트합니다.
"""
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# 모의 GDELT 클라이언트 사용
from crawling.mock_gdelt_client import MockGDELTClient as GDELTClient
use_mock = True
print("모의 GDELT 클라이언트를 사용합니다.")
from data.stock_data_store import StockDataStore

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

def test_gdelt_news_retrieval(symbol: str, days: int = 7):
    """
    GDELT 뉴스 검색 테스트

    Args:
        symbol: 주식 심볼 (예: AAPL)
        days: 검색 기간 (일)
    """
    logger.info(f"GDELT {symbol} 뉴스 검색 테스트 시작 (기간: {days}일)")

    # GDELT 클라이언트 초기화
    gdelt_client = GDELTClient()

    # 뉴스 검색 (모의 클라이언트는 days 파라미터를 사용하지 않음)
    news = gdelt_client.get_news_by_symbol(symbol, max_records=10)

    # 결과 출력
    logger.info(f"검색된 뉴스: {len(news)}개")

    if news:
        for i, article in enumerate(news[:5], 1):  # 최대 5개만 출력
            print(f"\n{i}. {article['title']}")
            print(f"   출처: {article['source']} | 날짜: {article['published_date']}")
            print(f"   URL: {article['url']}")
            print(f"   감성 점수: {article['sentiment']['score']:.4f}")
    else:
        print(f"{symbol}에 대한 뉴스를 찾지 못했습니다.")

def test_gdelt_sentiment_trends(symbol: str, days: int = 30):
    """
    GDELT 감성 트렌드 테스트

    Args:
        symbol: 주식 심볼 (예: AAPL)
        days: 분석 기간 (일)
    """
    logger.info(f"GDELT {symbol} 감성 트렌드 테스트 시작 (기간: {days}일)")

    # GDELT 클라이언트 초기화
    gdelt_client = GDELTClient()

    # 감성 트렌드 분석 (모의 클라이언트는 날짜 파라미터를 사용하지 않음)
    trends = gdelt_client.get_news_sentiment_trends(
        symbol=symbol,
        interval='day'
    )

    # 결과 출력
    logger.info(f"감성 트렌드 분석 결과: {len(trends['trends'])}개 기간")

    if trends['trends']:
        print(f"\n{symbol} 감성 트렌드 요약:")
        print(f"기간: {trends['period']}")
        print(f"평균 감성 점수: {trends['summary']['average_score']:.4f}")
        print(f"기사 수: {trends['summary']['article_count']}")

        print("\n날짜별 감성 점수:")
        for trend in trends['trends'][:10]:  # 최대 10개만 출력
            print(f"{trend['interval']}: {trend['sentiment']['score']:.4f} (기사 수: {trend['article_count']})")
    else:
        print(f"{symbol}에 대한 감성 트렌드를 분석하지 못했습니다.")

def test_gdelt_stock_correlation(symbol: str, days: int = 90):
    """
    GDELT 감성과 주가 상관관계 테스트

    Args:
        symbol: 주식 심볼 (예: AAPL)
        days: 분석 기간 (일)
    """
    logger.info(f"GDELT {symbol} 감성-주가 상관관계 테스트 시작 (기간: {days}일)")

    # GDELT 클라이언트 초기화
    gdelt_client = GDELTClient()

    # 주식 데이터 저장소 초기화
    stock_store = StockDataStore()

    # 주가 데이터 가져오기
    stock_data = stock_store.get_stock_price(symbol, days=days)

    # 주가 데이터 형식 변환
    stock_price_data = []
    for price in stock_data:
        stock_price_data.append({
            "date": price["date"],
            "close": price["close"],
            "change_pct": 0  # 변화율은 분석 함수 내에서 계산됨
        })

    # 감성-주가 상관관계 분석 (모의 클라이언트는 날짜 파라미터를 사용하지 않음)
    correlation = gdelt_client.analyze_sentiment_stock_correlation(
        symbol=symbol,
        stock_data=stock_price_data
    )

    # 결과 출력
    logger.info(f"감성-주가 상관관계 분석 결과: {correlation['data_points']}개 데이터 포인트")

    if correlation['data_points'] > 0:
        print(f"\n{symbol} 감성-주가 상관관계 분석:")
        print(f"기간: {correlation['period']}")
        print(f"데이터 포인트: {correlation['data_points']}")

        print("\n상관계수:")
        print(f"당일: {correlation['correlation']['same_day']:.4f}")
        print(f"다음날: {correlation['correlation']['next_day']:.4f}")
        print(f"3일 후: {correlation['correlation']['next_3_days']:.4f}")
        print(f"1주일 후: {correlation['correlation']['next_week']:.4f}")

        print("\n감성 그룹별 영향:")
        for impact in correlation['sentiment_impact']:
            print(f"\n{impact['sentiment_group']} (기사 수: {impact['count']})")
            print(f"  당일 가격 변화: {impact['avg_price_change']['same_day']:.4f}%")
            print(f"  다음날 가격 변화: {impact['avg_price_change']['next_day']:.4f}%")
            print(f"  3일 후 가격 변화: {impact['avg_price_change']['next_3_days']:.4f}%")
            print(f"  1주일 후 가격 변화: {impact['avg_price_change']['next_week']:.4f}%")
    else:
        print(f"{symbol}에 대한 감성-주가 상관관계를 분석하지 못했습니다.")

    # 리소스 정리
    stock_store.close()

def main():
    """
    메인 함수
    """
    # 테스트할 심볼
    symbols = ["AAPL", "MSFT", "GOOGL"]

    for symbol in symbols:
        print(f"\n{'='*50}")
        print(f"  {symbol} 테스트")
        print(f"{'='*50}")

        # GDELT 뉴스 검색 테스트
        test_gdelt_news_retrieval(symbol, days=7)

        # GDELT 감성 트렌드 테스트
        test_gdelt_sentiment_trends(symbol, days=30)

        # GDELT 감성-주가 상관관계 테스트
        test_gdelt_stock_correlation(symbol, days=90)

if __name__ == "__main__":
    main()
