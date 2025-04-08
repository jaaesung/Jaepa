"""
JaePa 테스트 실행 스크립트

이 스크립트는 MongoDB 설정, 뉴스 수집, 감성 분석, 데이터 시각화 등 
JaePa의 핵심 기능을 손쉽게 테스트할 수 있도록 도와줍니다.
"""
import os
import sys
import logging
import argparse
from pathlib import Path
import subprocess
import webbrowser
import time
from typing import List, Dict, Any

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('jaepa_test.log')
    ]
)
logger = logging.getLogger(__name__)


def setup_mongodb():
    """MongoDB 설정 및 초기화"""
    logger.info("MongoDB 설정 및 초기화 중...")
    try:
        from backend.db.mongodb_setup import MongoDBSetup
        mongodb_setup = MongoDBSetup()
        
        # DB 연결 확인
        if not mongodb_setup.connect():
            logger.error("MongoDB 연결 실패")
            return False
            
        # 텍스트 인덱스 관련 문제를 피하기 위해 컴포넌트 별로 설정
        try:
            mongodb_setup.setup_sentiment_trends_collection()
            logger.info("감성 트렌드 컴포넌트 설정 완료")
        except Exception as e:
            logger.warning(f"감성 트렌드 컴포넌트 설정 오류: {str(e)}")
            
        try:
            mongodb_setup.setup_stock_data_collection()
            logger.info("주식 데이터 컴포넌트 설정 완료")
        except Exception as e:
            logger.warning(f"주식 데이터 컴포넌트 설정 오류: {str(e)}")
            
        try:
            mongodb_setup.setup_symbol_news_relation_collection()
            logger.info("심볼-뉴스 관계 컴포넌트 설정 완료")
        except Exception as e:
            logger.warning(f"심볼-뉴스 관계 컴포넌트 설정 오류: {str(e)}")
            
        try:
            mongodb_setup.setup_sentiment_stock_correlation_collection()
            logger.info("감성-주가 상관관계 컴포넌트 설정 완료")
        except Exception as e:
            logger.warning(f"감성-주가 상관관계 컴포넌트 설정 오류: {str(e)}")
            
        # 마지막으로 뉴스 컴포넌트 설정 (텍스트 인덱스 관련 문제 발생 가능)
        try:
            mongodb_setup.setup_news_collection()
            logger.info("뉴스 컴포넌트 설정 완료")
        except Exception as e:
            logger.warning(f"뉴스 컴포넌트 설정 오류: {str(e)}")
            
        # 자원 정리
        mongodb_setup.close()
        logger.info("MongoDB 설정 완료")
        return True
    except Exception as e:
        logger.error(f"MongoDB 설정 중 오류: {str(e)}")
        return False


def collect_news(sources: List[str] = None, days: int = 3, keywords: List[str] = None):
    """뉴스 수집 테스트"""
    logger.info(f"뉴스 수집 테스트를 시작합니다. 소스: {sources or '모두'}, 기간: {days}일, 키워드: {keywords or '없음'}")
    
    try:
        from crawling.news_integrator import NewsIntegrator
        
        # 통합 수집기 초기화
        integrator = NewsIntegrator()
        
        # 각 소스별로 수집
        if sources:
            for source in sources:
                if source == "rss":
                    logger.info("RSS 소스에서 뉴스 수집 중...")
                    if keywords:
                        for keyword in keywords:
                            logger.info(f"키워드 '{keyword}'로 RSS 검색 중...")
                            news = integrator.rss_crawler.search_news_from_rss(keyword=keyword, days=days)
                            logger.info(f"RSS 소스에서 키워드 '{keyword}'로 {len(news)}개 기사 수집됨")
                    else:
                        news = integrator.rss_crawler.get_news_from_rss()
                        logger.info(f"RSS 소스에서 {len(news)}개 기사 수집됨")
                
                elif source == "finnhub":
                    logger.info("Finnhub API에서 뉴스 수집 중...")
                    if keywords:
                        for keyword in keywords:
                            logger.info(f"키워드 '{keyword}'로 Finnhub 검색 중...")
                            news = integrator.api_handler.get_news_from_finnhub(symbol=keyword, days=days)
                            logger.info(f"Finnhub API에서 키워드 '{keyword}'로 {len(news)}개 기사 수집됨")
                    else:
                        news = integrator.api_handler.get_news_from_finnhub(days=days)
                        logger.info(f"Finnhub API에서 {len(news)}개 기사 수집됨")
                
                elif source == "newsdata":
                    logger.info("NewsData.io API에서 뉴스 수집 중...")
                    if keywords:
                        for keyword in keywords:
                            logger.info(f"키워드 '{keyword}'로 NewsData.io 검색 중...")
                            news = integrator.api_handler.get_news_from_newsdata(keyword=keyword, days=days)
                            logger.info(f"NewsData.io API에서 키워드 '{keyword}'로 {len(news)}개 기사 수집됨")
                    else:
                        news = integrator.api_handler.get_news_from_newsdata(days=days)
                        logger.info(f"NewsData.io API에서 {len(news)}개 기사 수집됨")
        
        # 통합 수집
        else:
            logger.info("모든 소스에서 통합 뉴스 수집 중...")
            if keywords:
                for keyword in keywords:
                    logger.info(f"키워드 '{keyword}'로 통합 검색 중...")
                    news = integrator.collect_news(keyword=keyword, days=days)
                    logger.info(f"통합 수집기에서 키워드 '{keyword}'로 {len(news)}개 기사 수집됨")
            else:
                news = integrator.collect_news(days=days)
                logger.info(f"통합 수집기에서 {len(news)}개 기사 수집됨")
        
        # 리소스 정리
        integrator.close()
        logger.info("뉴스 수집 테스트 완료")
        return True
        
    except Exception as e:
        logger.error(f"뉴스 수집 중 오류: {str(e)}")
        return False


def update_sentiment_trends():
    """감성 트렌드 업데이트 테스트"""
    logger.info("감성 트렌드 업데이트 테스트를 시작합니다.")
    
    try:
        from backend.db.mongodb_setup import MongoDBSetup
        mongodb_setup = MongoDBSetup()
        
        if mongodb_setup.update_sentiment_trends():
            logger.info("감성 트렌드 업데이트 완료")
            return True
        else:
            logger.error("감성 트렌드 업데이트 실패")
            return False
    except Exception as e:
        logger.error(f"감성 트렌드 업데이트 중 오류: {str(e)}")
        return False


def run_dashboard():
    """대시보드 실행"""
    logger.info("대시보드 서버를 시작합니다...")
    
    try:
        dashboard_path = Path(__file__).parent / "dashboard" / "app.py"
        
        # 서브프로세스로 FastAPI 서버 실행
        server_process = subprocess.Popen(
            [sys.executable, str(dashboard_path)], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 서버가 시작될 때까지 잠시 대기
        time.sleep(2)
        
        # 웹 브라우저에서 대시보드 열기
        webbrowser.open("http://localhost:8000")
        
        logger.info("대시보드가 시작되었습니다. 브라우저에서 http://localhost:8000 으로 접속하세요.")
        logger.info("종료하려면 Ctrl+C를 누르세요.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("사용자에 의해 대시보드가 종료되었습니다.")
            server_process.terminate()
            server_process.wait()
        
        return True
        
    except Exception as e:
        logger.error(f"대시보드 실행 중 오류: {str(e)}")
        return False


def run_test_suite():
    """전체 테스트 스위트 실행"""
    logger.info("전체 테스트 스위트를 실행합니다.")
    
    # MongoDB 설정
    if not setup_mongodb():
        logger.error("MongoDB 설정에 실패하여 테스트를 중단합니다.")
        return False
    
    # 뉴스 수집 테스트 (모든 소스, Bitcoin 및 Ethereum 키워드)
    if not collect_news(days=3, keywords=["BTC", "ETH", "AAPL"]):
        logger.error("뉴스 수집에 실패하여 테스트를 중단합니다.")
        return False
    
    # 감성 트렌드 업데이트
    if not update_sentiment_trends():
        logger.error("감성 트렌드 업데이트에 실패하여 테스트를 중단합니다.")
        return False
    
    # 대시보드 실행
    if not run_dashboard():
        logger.error("대시보드 실행에 실패하여 테스트를 중단합니다.")
        return False
    
    logger.info("모든 테스트가 성공적으로 완료되었습니다.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JaePa 테스트 스크립트")
    
    # 테스트 유형 선택
    parser.add_argument("--test", choices=["mongodb", "news", "sentiment", "dashboard", "all"], 
                        default="all", help="실행할 테스트 유형")
    
    # 뉴스 수집 관련 옵션
    parser.add_argument("--sources", nargs="+", choices=["rss", "finnhub", "newsdata"], 
                        help="뉴스 수집에 사용할 소스")
    parser.add_argument("--days", type=int, default=3, 
                        help="뉴스 수집 기간(일)")
    parser.add_argument("--keywords", nargs="+", 
                        help="뉴스 검색 키워드")
    
    args = parser.parse_args()
    
    if args.test == "mongodb":
        setup_mongodb()
    elif args.test == "news":
        collect_news(sources=args.sources, days=args.days, keywords=args.keywords)
    elif args.test == "sentiment":
        update_sentiment_trends()
    elif args.test == "dashboard":
        run_dashboard()
    elif args.test == "all":
        run_test_suite()
