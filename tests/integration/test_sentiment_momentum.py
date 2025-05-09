#!/usr/bin/env python3
"""
감성 모멘텀 분석 테스트 스크립트

이 스크립트는 감성 모멘텀 분석기를 테스트합니다.
"""
import os
import logging
import json
from datetime import datetime, timedelta
import random
from typing import Dict, List, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# 감성 모멘텀 분석기 임포트
from analysis.sentiment_momentum_analyzer import SentimentMomentumAnalyzer
from data.polygon_client import PolygonClient
from crawling.mock_gdelt_client import MockGDELTClient

def generate_test_news_data(symbol: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    테스트용 뉴스 데이터 생성
    
    Args:
        symbol: 주식 심볼
        days: 생성할 일수
        
    Returns:
        List[Dict[str, Any]]: 테스트용 뉴스 데이터
    """
    news_data = []
    end_date = datetime.now()
    
    # 시드 설정 (재현 가능한 결과를 위해)
    random.seed(42)
    
    # 각 날짜별로 1-5개의 뉴스 생성
    for i in range(days):
        date = end_date - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        # 해당 날짜의 뉴스 수 (1-5개)
        news_count = random.randint(1, 5)
        
        # 특정 패턴 생성 (예: 처음 10일은 부정적, 다음 10일은 긍정적, 마지막 10일은 혼합)
        if i < 10:
            sentiment_base = -0.3  # 부정적 경향
        elif i < 20:
            sentiment_base = 0.3   # 긍정적 경향
        else:
            sentiment_base = 0.0   # 중립적 경향
        
        for j in range(news_count):
            # 감성 점수 생성 (기본 경향 + 랜덤 노이즈)
            sentiment_score = sentiment_base + random.uniform(-0.5, 0.5)
            sentiment_score = max(-1.0, min(1.0, sentiment_score))  # -1.0 ~ 1.0 범위로 제한
            
            # 감성 유형 결정
            if sentiment_score > 0.1:
                sentiment_type = "positive"
            elif sentiment_score < -0.1:
                sentiment_type = "negative"
            else:
                sentiment_type = "neutral"
            
            # 뉴스 데이터 생성
            news = {
                "title": f"{symbol} News {j+1} for {date_str}",
                "date": date_str,
                "sentiment_score": sentiment_score,
                "sentiment_type": sentiment_type,
                "url": f"https://example.com/news/{symbol}/{date_str}/{j+1}",
                "source": "Test Source"
            }
            
            news_data.append(news)
    
    return news_data

def test_sentiment_momentum_analyzer():
    """
    감성 모멘텀 분석기 테스트
    """
    # 테스트할 심볼
    symbols = ["AAPL", "MSFT", "GOOGL"]
    
    # 분석 기간 (일)
    days = 60
    
    # 감성 모멘텀 분석기 초기화
    analyzer = SentimentMomentumAnalyzer()
    
    # Polygon 클라이언트 초기화 (주가 데이터용)
    polygon = PolygonClient()
    
    # GDELT 클라이언트 초기화 (실제 뉴스 데이터용)
    gdelt = MockGDELTClient()
    
    for symbol in symbols:
        logger.info(f"\n{'='*50}\n  {symbol} 감성 모멘텀 분석 테스트\n{'='*50}")
        
        # 1. 테스트 데이터 생성
        logger.info(f"{symbol} 테스트 데이터 생성 중...")
        
        # 1.1 테스트용 뉴스 데이터 생성
        test_news_data = generate_test_news_data(symbol, days)
        logger.info(f"테스트용 뉴스 데이터 {len(test_news_data)}개 생성됨")
        
        # 1.2 실제 주가 데이터 가져오기
        stock_data = polygon.get_stock_price(symbol, days=days)
        logger.info(f"주가 데이터 {len(stock_data)}개 가져옴")
        
        # 2. 감성 모멘텀 분석 수행
        logger.info(f"{symbol} 감성 모멘텀 분석 수행 중...")
        result = analyzer.analyze_sentiment_momentum(
            news_data=test_news_data,
            stock_data=stock_data,
            short_window=5,
            long_window=10
        )
        
        if result["success"]:
            logger.info(f"감성 모멘텀 분석 성공: {len(result['daily_sentiment'])}개 데이터 포인트")
            
            # 3. 차트 생성
            logger.info(f"{symbol} 감성 모멘텀 차트 생성 중...")
            analyzer.generate_momentum_charts(symbol, result)
            
            # 4. 분석 요약 생성
            logger.info(f"{symbol} 감성 모멘텀 분석 요약 생성 중...")
            summary = analyzer.generate_momentum_summary(symbol, result)
            
            # 요약 출력
            print(f"\n{summary}\n")
            
            # 요약 저장
            summary_path = os.path.join(analyzer.results_dir, f"{symbol}_momentum_summary.md")
            with open(summary_path, "w") as f:
                f.write(summary)
            logger.info(f"분석 요약이 저장되었습니다: {summary_path}")
        else:
            logger.error(f"감성 모멘텀 분석 실패: {result.get('message', '알 수 없는 오류')}")

def test_with_real_data():
    """
    실제 데이터를 사용한 감성 모멘텀 분석 테스트
    """
    # 테스트할 심볼
    symbols = ["AAPL", "MSFT", "GOOGL"]
    
    # 분석 기간 (일)
    days = 60
    
    # 감성 모멘텀 분석기 초기화
    analyzer = SentimentMomentumAnalyzer()
    
    # Polygon 클라이언트 초기화 (주가 데이터용)
    polygon = PolygonClient()
    
    # GDELT 클라이언트 초기화 (실제 뉴스 데이터용)
    gdelt = MockGDELTClient()
    
    for symbol in symbols:
        logger.info(f"\n{'='*50}\n  {symbol} 실제 데이터 감성 모멘텀 분석\n{'='*50}")
        
        # 1. 실제 데이터 가져오기
        logger.info(f"{symbol} 실제 데이터 가져오는 중...")
        
        # 1.1 실제 뉴스 데이터 가져오기
        news_data = gdelt.get_historical_news_by_symbol(symbol, max_records=100)
        
        # 감성 점수 및 유형 추가
        for news in news_data:
            if "tone" in news:
                news["sentiment_score"] = float(news["tone"])
            else:
                news["sentiment_score"] = random.uniform(-0.5, 0.5)
                
            if news["sentiment_score"] > 0.1:
                news["sentiment_type"] = "positive"
            elif news["sentiment_score"] < -0.1:
                news["sentiment_type"] = "negative"
            else:
                news["sentiment_type"] = "neutral"
                
            # 날짜 형식 통일
            if "published_date" in news:
                news["date"] = news["published_date"]
            elif "published_utc" in news:
                news["date"] = news["published_utc"]
            elif "seendate" in news:
                news["date"] = datetime.fromtimestamp(news["seendate"]/1000.0).strftime("%Y-%m-%d")
        
        logger.info(f"뉴스 데이터 {len(news_data)}개 가져옴")
        
        # 1.2 실제 주가 데이터 가져오기
        stock_data = polygon.get_stock_price(symbol, days=days)
        logger.info(f"주가 데이터 {len(stock_data)}개 가져옴")
        
        # 2. 감성 모멘텀 분석 수행
        logger.info(f"{symbol} 감성 모멘텀 분석 수행 중...")
        result = analyzer.analyze_sentiment_momentum(
            news_data=news_data,
            stock_data=stock_data,
            short_window=3,
            long_window=7
        )
        
        if result["success"]:
            logger.info(f"감성 모멘텀 분석 성공: {len(result['daily_sentiment'])}개 데이터 포인트")
            
            # 3. 차트 생성
            logger.info(f"{symbol} 감성 모멘텀 차트 생성 중...")
            analyzer.generate_momentum_charts(symbol, result)
            
            # 4. 분석 요약 생성
            logger.info(f"{symbol} 감성 모멘텀 분석 요약 생성 중...")
            summary = analyzer.generate_momentum_summary(symbol, result)
            
            # 요약 출력
            print(f"\n{summary}\n")
            
            # 요약 저장
            summary_path = os.path.join(analyzer.results_dir, f"{symbol}_real_momentum_summary.md")
            with open(summary_path, "w") as f:
                f.write(summary)
            logger.info(f"분석 요약이 저장되었습니다: {summary_path}")
        else:
            logger.error(f"감성 모멘텀 분석 실패: {result.get('message', '알 수 없는 오류')}")

if __name__ == "__main__":
    print("감성 모멘텀 분석 테스트 시작")
    
    # 테스트 데이터로 테스트
    test_sentiment_momentum_analyzer()
    
    # 실제 데이터로 테스트
    test_with_real_data()
    
    print("감성 모멘텀 분석 테스트 완료")
