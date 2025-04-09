#!/usr/bin/env python3
"""
금융 분석 데모 스크립트

이 스크립트는 FinBERT 모델과 Polygon API를 사용한 금융 분석 기능을 데모합니다.
"""
import argparse
import logging
import sys
import json
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 모듈 가져오기
try:
    from analysis.finbert_sentiment import FinBERTSentiment
    from data.polygon_client import PolygonClient
    from data.stock_data_store import StockDataStore
    from analysis.sentiment_price_analyzer import SentimentPriceAnalyzer
except ImportError as e:
    logger.error(f"모듈 가져오기 실패: {e}")
    logger.error("필요한 모듈이 설치되었는지 확인하세요.")
    sys.exit(1)

def analyze_text(args):
    """
    텍스트 감성 분석
    
    Args:
        args: 명령줄 인수
    """
    # FinBERT 감성 분석기 초기화
    finbert = FinBERTSentiment()
    
    # 텍스트 분석
    sentiment = finbert.analyze(args.text)
    
    # 결과 출력
    print("\n=== 텍스트 감성 분석 결과 ===")
    print(f"텍스트: {args.text}")
    print(f"감성: {sentiment['label']} (점수: {sentiment['score']:.4f})")
    print(f"세부 점수:")
    for label, score in sentiment['scores'].items():
        print(f"  {label}: {score:.4f}")

def analyze_news(args):
    """
    뉴스 감성 분석
    
    Args:
        args: 명령줄 인수
    """
    # 주식 데이터 저장소 초기화
    store = StockDataStore()
    
    # FinBERT 감성 분석기 초기화
    finbert = FinBERTSentiment()
    
    # 뉴스 가져오기
    news_items = store.get_stock_news(args.symbol, limit=args.limit)
    
    # 뉴스가 없는 경우
    if not news_items:
        print(f"\n{args.symbol}에 대한 뉴스가 없습니다.")
        store.close()
        return
    
    # 뉴스 감성 분석
    print(f"\n=== {args.symbol} 뉴스 감성 분석 결과 ===")
    for i, news in enumerate(news_items, 1):
        # 뉴스 감성 분석
        news_with_sentiment = finbert.analyze_news({
            "title": news.get("title", ""),
            "content": news.get("description", ""),
            "url": news.get("article_url", ""),
            "published_date": news.get("published_utc", "")
        })
        
        print(f"\n뉴스 {i}:")
        print(f"제목: {news_with_sentiment['title']}")
        print(f"감성: {news_with_sentiment['sentiment']['label']} (점수: {news_with_sentiment['sentiment']['score']:.4f})")
        
        # 세부 정보 출력 (--verbose 옵션)
        if args.verbose:
            print(f"세부 점수:")
            for label, score in news_with_sentiment['sentiment']['scores'].items():
                print(f"  {label}: {score:.4f}")
            print(f"URL: {news_with_sentiment.get('url', '')}")
            print(f"날짜: {news_with_sentiment.get('published_date', '')}")
    
    # 연결 종료
    store.close()

def analyze_correlation(args):
    """
    감성-가격 상관관계 분석
    
    Args:
        args: 명령줄 인수
    """
    # 감성-가격 분석기 초기화
    analyzer = SentimentPriceAnalyzer()
    
    # 감성-가격 상관관계 분석
    result = analyzer.analyze_sentiment_price_correlation(args.symbol, days=args.days)
    
    # 결과 출력
    print(f"\n=== {args.symbol} 감성-가격 상관관계 분석 결과 ===")
    print(f"기간: {result['period']}")
    print(f"상관관계: {result['correlation']}")
    print(f"감성 추세: {result['sentiment_trend']}")
    print(f"가격 추세: {result['price_trend']}")
    print(f"\n분석:")
    print(result['analysis'])
    
    # 데이터 출력 (--verbose 옵션)
    if args.verbose and result.get('data'):
        print("\n데이터 샘플:")
        for i, record in enumerate(result['data'][:5], 1):
            print(f"  {i}. 날짜: {record.get('date')}, 종가: {record.get('close')}, 감성 점수: {record.get('sentiment_score')}")
    
    # JSON 출력 (--json 옵션)
    if args.json:
        json_result = {
            "symbol": result['symbol'],
            "period": result['period'],
            "correlation": result['correlation'],
            "sentiment_trend": result['sentiment_trend'],
            "price_trend": result['price_trend'],
            "analysis": result['analysis']
        }
        
        # 데이터 포함 (--verbose 옵션)
        if args.verbose and result.get('data'):
            json_result['data'] = result['data']
            
        print("\nJSON 출력:")
        print(json.dumps(json_result, indent=2))
    
    # 리소스 정리
    analyzer.close()

def get_sentiment_summary(args):
    """
    감성 요약
    
    Args:
        args: 명령줄 인수
    """
    # 감성-가격 분석기 초기화
    analyzer = SentimentPriceAnalyzer()
    
    # 감성 요약
    result = analyzer.get_sentiment_summary(args.symbol, days=args.days)
    
    # 결과 출력
    print(f"\n=== {args.symbol} 감성 요약 ===")
    print(f"기간: {result['period']}")
    print(f"감성: {result['sentiment']}")
    print(f"긍정: {result['positive_count']}, 부정: {result['negative_count']}, 중립: {result['neutral_count']}")
    print(f"\n요약:")
    print(result['summary'])
    
    # 뉴스 출력 (--verbose 옵션)
    if args.verbose and result.get('news'):
        print("\n뉴스 샘플:")
        for i, news in enumerate(result['news'][:5], 1):
            print(f"  {i}. 제목: {news.get('title')}")
            print(f"     감성: {news.get('sentiment', {}).get('label')} (점수: {news.get('sentiment', {}).get('score', 0):.4f})")
    
    # JSON 출력 (--json 옵션)
    if args.json:
        json_result = {
            "symbol": result['symbol'],
            "period": result['period'],
            "sentiment": result['sentiment'],
            "positive_count": result['positive_count'],
            "negative_count": result['negative_count'],
            "neutral_count": result['neutral_count'],
            "total_count": result['total_count'],
            "summary": result['summary']
        }
        
        # 뉴스 포함 (--verbose 옵션)
        if args.verbose and result.get('news'):
            json_result['news'] = [
                {
                    "title": news.get('title'),
                    "sentiment": news.get('sentiment', {}).get('label'),
                    "score": news.get('sentiment', {}).get('score', 0)
                }
                for news in result['news'][:5]
            ]
            
        print("\nJSON 출력:")
        print(json.dumps(json_result, indent=2))
    
    # 리소스 정리
    analyzer.close()

def main():
    """메인 함수"""
    # 명령줄 인수 파서 생성
    parser = argparse.ArgumentParser(description="FinBERT 금융 텍스트 감성 분석")
    subparsers = parser.add_subparsers(dest="command", help="명령")
    
    # 텍스트 분석 명령
    text_parser = subparsers.add_parser("text", help="텍스트 감성 분석")
    text_parser.add_argument("text", help="분석할 텍스트")
    
    # 뉴스 분석 명령
    news_parser = subparsers.add_parser("news", help="뉴스 감성 분석")
    news_parser.add_argument("symbol", help="주식 심볼 (예: AAPL, MSFT)")
    news_parser.add_argument("--limit", type=int, default=5, help="분석할 뉴스 수 (기본값: 5)")
    news_parser.add_argument("--verbose", action="store_true", help="상세 정보 출력")
    
    # 상관관계 분석 명령
    correlation_parser = subparsers.add_parser("correlation", help="감성-가격 상관관계 분석")
    correlation_parser.add_argument("symbol", help="주식 심볼 (예: AAPL, MSFT)")
    correlation_parser.add_argument("--days", type=int, default=30, help="분석할 일수 (기본값: 30)")
    correlation_parser.add_argument("--verbose", action="store_true", help="상세 정보 출력")
    correlation_parser.add_argument("--json", action="store_true", help="JSON 형식으로 출력")
    
    # 감성 요약 명령
    summary_parser = subparsers.add_parser("summary", help="감성 요약")
    summary_parser.add_argument("symbol", help="주식 심볼 (예: AAPL, MSFT)")
    summary_parser.add_argument("--days", type=int, default=7, help="분석할 일수 (기본값: 7)")
    summary_parser.add_argument("--verbose", action="store_true", help="상세 정보 출력")
    summary_parser.add_argument("--json", action="store_true", help="JSON 형식으로 출력")
    
    # 명령줄 인수 파싱
    args = parser.parse_args()
    
    # 명령 실행
    if args.command == "text":
        analyze_text(args)
    elif args.command == "news":
        analyze_news(args)
    elif args.command == "correlation":
        analyze_correlation(args)
    elif args.command == "summary":
        get_sentiment_summary(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
