#!/usr/bin/env python3
"""
통합 뉴스 수집기 테스트 스크립트

GDELT와 기존 크롤링 시스템을 통합한 뉴스 수집기를 테스트합니다.
"""
import os
import sys
import logging
import json
from datetime import datetime, timedelta
from pprint import pprint

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from crawling.integrated_news_collector import IntegratedNewsCollector

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_collect_news_from_all_sources():
    """모든 소스에서 뉴스 수집 테스트"""
    collector = IntegratedNewsCollector()
    
    try:
        results = collector.collect_news_from_all_sources(
            keywords=["finance", "stock market"],
            symbols=["AAPL", "MSFT"],
            days=1,
            limit=2
        )
        
        print("\n=== 모든 소스에서 뉴스 수집 결과 ===")
        pprint(results)
        
        return results
    finally:
        collector.close()

def test_collect_news_by_symbol():
    """특정 심볼에 대한 뉴스 수집 테스트"""
    collector = IntegratedNewsCollector()
    
    try:
        results = collector.collect_news_by_symbol(
            symbol="AAPL",
            days=1,
            limit=2
        )
        
        print("\n=== 애플 관련 뉴스 수집 결과 ===")
        pprint(results)
        
        return results
    finally:
        collector.close()

def test_get_news_by_symbol():
    """특정 심볼에 대한 뉴스 조회 테스트"""
    collector = IntegratedNewsCollector()
    
    try:
        news = collector.get_news_by_symbol(
            symbol="AAPL",
            days=7,
            limit=3
        )
        
        print("\n=== 애플 관련 뉴스 조회 결과 ===")
        print(f"총 {len(news)}개 뉴스 조회됨")
        
        for i, article in enumerate(news[:2], 1):  # 처음 2개만 출력
            print(f"\n기사 {i}:")
            print(f"제목: {article.get('title', 'N/A')}")
            print(f"출처: {article.get('source', 'N/A')} ({article.get('source_type', 'N/A')})")
            print(f"날짜: {article.get('published_date', 'N/A')}")
            print(f"URL: {article.get('url', 'N/A')}")
            
            # 감성 정보 출력
            sentiment = article.get('sentiment', {})
            if sentiment:
                print(f"감성 점수: {sentiment.get('score', 'N/A')}")
                print(f"긍정: {sentiment.get('positive', 'N/A'):.2f}, " +
                      f"부정: {sentiment.get('negative', 'N/A'):.2f}, " +
                      f"중립: {sentiment.get('neutral', 'N/A'):.2f}")
        
        return news
    finally:
        collector.close()

def test_search_news():
    """키워드로 뉴스 검색 테스트"""
    collector = IntegratedNewsCollector()
    
    try:
        news = collector.search_news(
            query="artificial intelligence",
            days=30,
            limit=3
        )
        
        print("\n=== 'artificial intelligence' 검색 결과 ===")
        print(f"총 {len(news)}개 뉴스 조회됨")
        
        for i, article in enumerate(news[:2], 1):  # 처음 2개만 출력
            print(f"\n기사 {i}:")
            print(f"제목: {article.get('title', 'N/A')}")
            print(f"출처: {article.get('source', 'N/A')} ({article.get('source_type', 'N/A')})")
            print(f"날짜: {article.get('published_date', 'N/A')}")
            print(f"URL: {article.get('url', 'N/A')}")
            
            # 감성 정보 출력
            sentiment = article.get('sentiment', {})
            if sentiment:
                print(f"감성 점수: {sentiment.get('score', 'N/A')}")
        
        return news
    finally:
        collector.close()

def test_gdelt_client_directly():
    """GDELT 클라이언트 직접 테스트"""
    from crawling.gdelt_client import GDELTClient
    
    client = GDELTClient()
    
    # 애플 관련 뉴스 검색
    apple_news = client.get_news_by_symbol("AAPL", days=1, max_records=2)
    
    print("\n=== GDELT에서 애플 관련 뉴스 검색 결과 ===")
    print(f"총 {len(apple_news)}개 뉴스 검색됨")
    
    for i, news in enumerate(apple_news[:2], 1):  # 처음 2개만 출력
        print(f"\n기사 {i}:")
        print(f"제목: {news.get('title', 'N/A')}")
        print(f"날짜: {news.get('published_date', 'N/A')}")
        print(f"출처: {news.get('source', 'N/A')}")
        print(f"URL: {news.get('url', 'N/A')}")
        
        # 감성 정보 출력
        sentiment = news.get('sentiment', {})
        if sentiment:
            print(f"감성 점수: {sentiment.get('score', 'N/A')}")
    
    # 시장 감성 지표
    market_sentiment = client.get_market_sentiment(days=1)
    
    print("\n=== GDELT 시장 감성 지표 ===")
    print(f"날짜: {market_sentiment.get('date', 'N/A')}")
    print(f"기사 수: {market_sentiment.get('article_count', 'N/A')}")
    
    sentiment = market_sentiment.get('sentiment', {})
    if sentiment:
        print(f"평균 감성 점수: {sentiment.get('average_score', 'N/A')}")
        print(f"긍정: {sentiment.get('positive', 'N/A'):.2f}, " +
              f"부정: {sentiment.get('negative', 'N/A'):.2f}, " +
              f"중립: {sentiment.get('neutral', 'N/A'):.2f}")
    
    return {
        "apple_news": apple_news,
        "market_sentiment": market_sentiment
    }

if __name__ == "__main__":
    print("\n===== 통합 뉴스 수집기 테스트 =====\n")
    
    # 테스트 실행
    try:
        # GDELT 클라이언트 직접 테스트
        test_gdelt_client_directly()
        
        # 통합 뉴스 수집기 테스트
        test_collect_news_from_all_sources()
        test_collect_news_by_symbol()
        test_get_news_by_symbol()
        test_search_news()
        
        print("\n모든 테스트가 완료되었습니다.")
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {str(e)}")
        raise
