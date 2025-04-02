#!/usr/bin/env python3
"""
JaePa 프로젝트 메인 모듈

이 모듈은 CLI 인터페이스를 제공하는 메인 진입점입니다.
"""
import argparse
import datetime
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('jaepa.log')
    ]
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# 현재 디렉토리를 PYTHONPATH에 추가하여 모듈 가져오기 편리하게 함
sys.path.append(str(Path(__file__).parent))

# 모듈 가져오기
try:
    from crawling.news_crawler import NewsCrawler, SentimentAnalyzer
    from crawling.stock_data_crawler import StockDataCrawler
except ImportError as e:
    logger.error(f"모듈 가져오기 실패: {e}")
    logger.error("필요한 모듈이 설치되었는지 확인하세요.")
    sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    """
    명령행 인자 파싱

    Returns:
        argparse.Namespace: 파싱된 인자
    """
    parser = argparse.ArgumentParser(description='JaePa - 금융 뉴스 감성 분석 도구')
    subparsers = parser.add_subparsers(dest='command', help='수행할 명령')

    # 뉴스 명령
    news_parser = subparsers.add_parser('news', help='뉴스 관련 명령')
    news_subparsers = news_parser.add_subparsers(dest='news_command', help='뉴스 명령 유형')
    
    # 뉴스 검색
    search_parser = news_subparsers.add_parser('search', help='키워드로 뉴스 검색')
    search_parser.add_argument('keyword', help='검색 키워드')
    search_parser.add_argument('--days', type=int, default=7, help='검색할 기간(일), 기본값: 7')
    search_parser.add_argument('--sources', nargs='+', help='뉴스 소스 (공백으로 구분)')
    
    # 최신 뉴스 가져오기
    latest_parser = news_subparsers.add_parser('latest', help='최신 뉴스 가져오기')
    latest_parser.add_argument('--count', type=int, default=5, help='각 소스별 가져올 뉴스 수, 기본값: 5')
    latest_parser.add_argument('--sources', nargs='+', help='뉴스 소스 (공백으로 구분)')
    
    # 감성 분석
    sentiment_parser = news_subparsers.add_parser('sentiment', help='뉴스 감성 분석')
    sentiment_parser.add_argument('--days', type=int, default=7, help='분석할 기간(일), 기본값: 7')
    sentiment_parser.add_argument('--symbol', help='관련 주식 심볼 (예: AAPL)')
    
    # 주식 명령
    stock_parser = subparsers.add_parser('stock', help='주식 관련 명령')
    stock_subparsers = stock_parser.add_subparsers(dest='stock_command', help='주식 명령 유형')
    
    # 주식 데이터 가져오기
    data_parser = stock_subparsers.add_parser('data', help='주식 데이터 가져오기')
    data_parser.add_argument('symbol', help='주식 심볼 (예: AAPL)')
    data_parser.add_argument('--period', default='1mo', help='기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max), 기본값: 1mo')
    data_parser.add_argument('--interval', default='1d', help='간격 (1d, 1wk, 1mo), 기본값: 1d')
    
    # 암호화폐 데이터 가져오기
    crypto_parser = stock_subparsers.add_parser('crypto', help='암호화폐 데이터 가져오기')
    crypto_parser.add_argument('symbol', help='암호화폐 ID (예: bitcoin)')
    crypto_parser.add_argument('--days', type=int, default=30, help='가져올 기간(일), 기본값: 30')
    
    # 분석 명령
    analysis_parser = subparsers.add_parser('analysis', help='분석 관련 명령')
    analysis_subparsers = analysis_parser.add_subparsers(dest='analysis_command', help='분석 명령 유형')
    
    # 상관관계 분석
    correlation_parser = analysis_subparsers.add_parser('correlation', help='감성-가격 상관관계 분석')
    correlation_parser.add_argument('symbol', help='주식 심볼 (예: AAPL)')
    correlation_parser.add_argument('--days', type=int, default=30, help='분석할 기간(일), 기본값: 30')
    
    # 트렌드 분석
    trend_parser = analysis_subparsers.add_parser('trend', help='감성 트렌드 분석')
    trend_parser.add_argument('--symbol', help='주식 심볼 (선택 사항)')
    trend_parser.add_argument('--days', type=int, default=30, help='분석할 기간(일), 기본값: 30')
    
    # 스케줄링 명령
    schedule_parser = subparsers.add_parser('schedule', help='작업 스케줄링')
    schedule_subparsers = schedule_parser.add_subparsers(dest='schedule_command', help='스케줄링 명령 유형')
    
    # 작업 추가
    add_parser = schedule_subparsers.add_parser('add', help='스케줄링 작업 추가')
    add_parser.add_argument('job_type', choices=['news', 'stock', 'analysis'], help='작업 유형')
    add_parser.add_argument('--interval', type=int, default=24, help='실행 간격(시간), 기본값: 24')
    add_parser.add_argument('--args', help='작업 인수 (JSON 형식)')
    
    # 작업 목록
    list_parser = schedule_subparsers.add_parser('list', help='스케줄링된 작업 목록 보기')
    
    # 작업 삭제
    remove_parser = schedule_subparsers.add_parser('remove', help='스케줄링된 작업 삭제')
    remove_parser.add_argument('job_id', help='삭제할 작업 ID')
    
    return parser.parse_args()


def handle_news_command(args: argparse.Namespace) -> None:
    """
    뉴스 관련 명령 처리

    Args:
        args: 파싱된 명령행 인자
    """
    if not args.news_command:
        logger.error("뉴스 명령이 지정되지 않았습니다. 'search', 'latest', 'sentiment' 중 하나를 사용하세요.")
        return
        
    # 뉴스 크롤러 초기화
    crawler = NewsCrawler()
    
    if args.news_command == 'search':
        logger.info(f"키워드 '{args.keyword}'로 뉴스 검색 중...")
        articles = crawler.search_news(
            keyword=args.keyword,
            days=args.days,
            sources=args.sources
        )
        
        if articles:
            print(f"\n{len(articles)}개의 뉴스 기사를 찾았습니다:\n")
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article['title']}")
                print(f"   출처: {article['source']} | 날짜: {article['published_date']}")
                print(f"   URL: {article['url']}")
                
                if 'sentiment' in article and article['sentiment']:
                    pos = article['sentiment']['positive']
                    neu = article['sentiment']['neutral']
                    neg = article['sentiment']['negative']
                    print(f"   감성: 긍정 {pos:.2f}, 중립 {neu:.2f}, 부정 {neg:.2f}")
                
                print(f"   키워드: {', '.join(article['keywords'])}")
                print()
        else:
            print(f"키워드 '{args.keyword}'에 대한 뉴스를 찾지 못했습니다.")
    
    elif args.news_command == 'latest':
        logger.info("최신 뉴스 가져오는 중...")
        articles = crawler.get_latest_news(
            sources=args.sources,
            count=args.count
        )
        
        if articles:
            print(f"\n{len(articles)}개의 최신 뉴스 기사를 가져왔습니다:\n")
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article['title']}")
                print(f"   출처: {article['source']} | 날짜: {article['published_date']}")
                print(f"   URL: {article['url']}")
                
                if 'sentiment' in article and article['sentiment']:
                    pos = article['sentiment']['positive']
                    neu = article['sentiment']['neutral']
                    neg = article['sentiment']['negative']
                    print(f"   감성: 긍정 {pos:.2f}, 중립 {neu:.2f}, 부정 {neg:.2f}")
                    
                print(f"   키워드: {', '.join(article['keywords'])}")
                print()
        else:
            print("최신 뉴스를 가져오지 못했습니다.")
    
    elif args.news_command == 'sentiment':
        logger.info("뉴스 감성 분석 중...")
        
        if not hasattr(crawler, 'sentiment_analyzer') or not crawler.sentiment_analyzer:
            crawler.initialize_sentiment_analyzer()
            
        # 일단 더미 데이터 반환 (실제로는 MongoDB에서 데이터 가져와야 함)
        # 향후 구현 예정
        print("\n뉴스 감성 분석 결과 (최근 7일):\n")
        print("날짜\t\t긍정\t중립\t부정\t기사 수")
        print("-" * 50)
        
        # 더미 데이터
        today = datetime.datetime.now()
        for i in range(args.days):
            date = (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            pos = 0.6 + (i % 3) * 0.1
            neu = 0.3 - (i % 2) * 0.05
            neg = 1 - pos - neu
            count = 10 + i
            
            print(f"{date}\t{pos:.2f}\t{neu:.2f}\t{neg:.2f}\t{count}")
    
    # 크롤러 정리
    crawler.close()


def handle_stock_command(args: argparse.Namespace) -> None:
    """
    주식 관련 명령 처리

    Args:
        args: 파싱된 명령행 인자
    """
    if not args.stock_command:
        logger.error("주식 명령이 지정되지 않았습니다. 'data' 또는 'crypto'를 사용하세요.")
        return
        
    # 주식 데이터 크롤러 초기화
    crawler = StockDataCrawler()
    
    if args.stock_command == 'data':
        logger.info(f"{args.symbol} 주식 데이터 가져오는 중...")
        data = crawler.get_stock_data(
            symbol=args.symbol,
            period=args.period,
            interval=args.interval
        )
        
        if not data.empty:
            # 기술적 지표 계산
            data_with_indicators = crawler.calculate_indicators(data)
            
            print(f"\n{args.symbol} 주식 데이터 ({len(data)} 레코드):\n")
            print(data_with_indicators.head(10).to_string())
            
            print("\n기술적 지표 요약:")
            last_row = data_with_indicators.iloc[-1]
            
            # SMA
            sma_cols = [col for col in data_with_indicators.columns if col.startswith('sma_')]
            if sma_cols:
                print("\n단순 이동평균선 (SMA):")
                for col in sma_cols:
                    period = col.split('_')[1]
                    value = last_row[col]
                    print(f"  {period}일 SMA: {value:.2f}")
            
            # RSI
            if 'rsi_14' in data_with_indicators.columns:
                rsi = last_row['rsi_14']
                print(f"\nRSI (14일): {rsi:.2f}")
                
                if rsi < 30:
                    print("  상태: 과매도 (Oversold)")
                elif rsi > 70:
                    print("  상태: 과매수 (Overbought)")
                else:
                    print("  상태: 중립 (Neutral)")
            
            # MACD
            if 'macd' in data_with_indicators.columns and 'macd_signal' in data_with_indicators.columns:
                macd = last_row['macd']
                macd_signal = last_row['macd_signal']
                
                print(f"\nMACD: {macd:.4f}")
                print(f"MACD 시그널: {macd_signal:.4f}")
                
                if macd > macd_signal:
                    print("  시그널: 매수 (MACD > 시그널 라인)")
                else:
                    print("  시그널: 매도 (MACD < 시그널 라인)")
        else:
            print(f"{args.symbol} 주식 데이터를 가져오지 못했습니다.")
    
    elif args.stock_command == 'crypto':
        logger.info(f"{args.symbol} 암호화폐 데이터 가져오는 중...")
        data = crawler.get_crypto_data(
            symbol=args.symbol,
            days=args.days
        )
        
        if not data.empty:
            print(f"\n{args.symbol} 암호화폐 데이터 ({len(data)} 레코드):\n")
            print(data.head(10).to_string())
            
            # 간단한 통계
            first_price = data.iloc[0]['price']
            last_price = data.iloc[-1]['price']
            price_change = last_price - first_price
            price_change_pct = (price_change / first_price) * 100
            
            print(f"\n기간: {data.iloc[-1]['date']} ~ {data.iloc[0]['date']}")
            print(f"시작 가격: ${first_price:.2f}")
            print(f"현재 가격: ${last_price:.2f}")
            print(f"가격 변화: ${price_change:.2f} ({price_change_pct:.2f}%)")
            print(f"최고 가격: ${data['price'].max():.2f}")
            print(f"최저 가격: ${data['price'].min():.2f}")
            print(f"평균 가격: ${data['price'].mean():.2f}")
            print(f"거래량 (24h): ${data.iloc[0]['volume']:.2f}")
        else:
            print(f"{args.symbol} 암호화폐 데이터를 가져오지 못했습니다.")
    
    # 크롤러 정리
    crawler.close()


def handle_analysis_command(args: argparse.Namespace) -> None:
    """
    분석 관련 명령 처리

    Args:
        args: 파싱된 명령행 인자
    """
    if not args.analysis_command:
        logger.error("분석 명령이 지정되지 않았습니다. 'correlation' 또는 'trend'를 사용하세요.")
        return
        
    if args.analysis_command == 'correlation':
        logger.info(f"{args.symbol} 감성-가격 상관관계 분석 중...")
        
        # 향후 구현 예정 - 현재는 더미 데이터 반환
        print(f"\n{args.symbol} 감성-가격 상관관계 분석 결과 (최근 {args.days}일):\n")
        
        print("상관계수:")
        print(f"  긍정 감성 - 가격: 0.68")
        print(f"  부정 감성 - 가격: -0.57")
        print(f"  감성 점수 - 가격 변화: 0.72")
        
        print("\n시차 분석 (일):")
        print("  지연\t상관계수")
        print("  -----\t-------")
        print("  0\t0.72")
        print("  1\t0.65")
        print("  2\t0.42")
        print("  3\t0.18")
        
        print("\n결론:")
        print("  - 감성 점수와 주가 사이에 중간~강한 상관관계가 있습니다.")
        print("  - 감성 효과는 당일에 가장 강하며 시간이 지날수록 감소합니다.")
        print("  - 긍정적인 뉴스는 주가 상승과 관련이 있으며, 부정적인 뉴스는 주가 하락과 관련이 있습니다.")
    
    elif args.analysis_command == 'trend':
        symbol_str = f"{args.symbol} " if args.symbol else ""
        logger.info(f"{symbol_str}감성 트렌드 분석 중...")
        
        # 향후 구현 예정 - 현재는 더미 데이터 반환
        print(f"\n{symbol_str}감성 트렌드 분석 결과 (최근 {args.days}일):\n")
        
        print("날짜\t\t감성 점수\t기사 수\t가격 변화(%)")
        print("-" * 60)
        
        # 더미 데이터
        today = datetime.datetime.now()
        for i in range(7):  # 일주일 데이터만 표시
            date = (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            sentiment = 0.6 + (i % 3) * 0.1 - (i % 2) * 0.2
            count = 10 + i
            price_change = 1.2 - i * 0.4
            
            print(f"{date}\t{sentiment:.2f}\t\t{count}\t{price_change:.2f}")
        
        print("\n주요 키워드 (빈도 및 평균 감성):")
        print("  키워드\t\t빈도\t평균 감성")
        print("  --------\t----\t--------")
        print("  earnings\t47\t0.72")
        print("  innovation\t35\t0.81")
        print("  competition\t28\t0.45")
        
        print("\n감성 트렌드:")
        print("  - 전반적인 감성은 약간 긍정적 (평균 0.62)")
        print("  - 지난 주 대비 감성 점수 11% 상승")
        print("  - 기사 수는 일정하게 유지됨")


def handle_schedule_command(args: argparse.Namespace) -> None:
    """
    스케줄링 관련 명령 처리

    Args:
        args: 파싱된 명령행 인자
    """
    if not args.schedule_command:
        logger.error("스케줄링 명령이 지정되지 않았습니다. 'add', 'list', 'remove' 중 하나를 사용하세요.")
        return
    
    schedule_file = Path(__file__).parent / 'schedule.json'
    
    # 스케줄 파일 로드
    jobs = []
    if schedule_file.exists():
        try:
            with open(schedule_file, 'r') as f:
                jobs = json.load(f)
        except Exception as e:
            logger.error(f"스케줄 파일 로드 실패: {e}")
    
    if args.schedule_command == 'add':
        logger.info(f"{args.job_type} 유형의 스케줄링 작업 추가 중...")
        
        # 작업 인수 파싱
        job_args = {}
        if args.args:
            try:
                job_args = json.loads(args.args)
            except json.JSONDecodeError:
                logger.error("잘못된 JSON 형식의 작업 인수입니다.")
                return
        
        # 새 작업 생성
        job = {
            "id": f"job_{len(jobs) + 1}",
            "type": args.job_type,
            "interval": args.interval,
            "args": job_args,
            "created_at": datetime.datetime.now().isoformat(),
            "next_run": (datetime.datetime.now() + datetime.timedelta(hours=args.interval)).isoformat()
        }
        
        jobs.append(job)
        
        # 스케줄 파일 저장
        try:
            with open(schedule_file, 'w') as f:
                json.dump(jobs, f, indent=2)
            print(f"작업이 성공적으로 추가되었습니다 (ID: {job['id']}).")
        except Exception as e:
            logger.error(f"스케줄 파일 저장 실패: {e}")
    
    elif args.schedule_command == 'list':
        if not jobs:
            print("스케줄링된 작업이 없습니다.")
            return
            
        print("\n스케줄링된 작업 목록:\n")
        print("ID\t유형\t간격(시간)\t다음 실행\t\t\t인수")
        print("-" * 80)
        
        for job in jobs:
            next_run = datetime.datetime.fromisoformat(job['next_run']).strftime('%Y-%m-%d %H:%M')
            args_str = json.dumps(job['args'])
            print(f"{job['id']}\t{job['type']}\t{job['interval']}\t\t{next_run}\t{args_str}")
    
    elif args.schedule_command == 'remove':
        job_id = args.job_id
        
        # 작업 찾기
        for i, job in enumerate(jobs):
            if job['id'] == job_id:
                del jobs[i]
                
                # 스케줄 파일 저장
                try:
                    with open(schedule_file, 'w') as f:
                        json.dump(jobs, f, indent=2)
                    print(f"작업 {job_id}이(가) 성공적으로 삭제되었습니다.")
                except Exception as e:
                    logger.error(f"스케줄 파일 저장 실패: {e}")
                return
        
        print(f"작업 ID {job_id}을(를) 찾을 수 없습니다.")


def main() -> None:
    """
    메인 함수
    """
    # 시작 로그
    logger.info("JaePa 애플리케이션 시작")
    
    # 인자 파싱
    args = parse_arguments()
    
    # 명령어 없이 실행된 경우 도움말 표시
    if not args.command:
        print("JaePa - 금융 뉴스 감성 분석 도구")
        print("\n사용 가능한 명령:")
        print("  news      - 뉴스 관련 명령 (search, latest, sentiment)")
        print("  stock     - 주식 관련 명령 (data, crypto)")
        print("  analysis  - 분석 관련 명령 (correlation, trend)")
        print("  schedule  - 작업 스케줄링 (add, list, remove)")
        print("\n자세한 사용법: python main.py <command> --help")
        return
    
    # 명령 처리
    try:
        if args.command == 'news':
            handle_news_command(args)
        elif args.command == 'stock':
            handle_stock_command(args)
        elif args.command == 'analysis':
            handle_analysis_command(args)
        elif args.command == 'schedule':
            handle_schedule_command(args)
    except Exception as e:
        logger.error(f"명령 실행 중 오류 발생: {e}")
    
    # 종료 로그
    logger.info("JaePa 애플리케이션 종료")


if __name__ == "__main__":
    main()
