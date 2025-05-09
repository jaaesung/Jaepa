"""
크롤링 스케줄러 모듈

정기적인 데이터 수집 작업을 스케줄링합니다.
"""

import schedule
import time
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# 로깅 설정
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(log_dir, f"crawling_{datetime.now().strftime('%Y%m%d')}.log")),
    ],
)
logger = logging.getLogger(__name__)

# 프로젝트 루트 디렉토리를 모듈 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 수집기 및 처리기 가져오기
from crawling.collectors.news_collector import NewsCrawler
from crawling.collectors.stock_collector import StockDataCrawler
from crawling.processors.sentiment_analyzer import FinancialSentimentAnalyzer

class CrawlingScheduler:
    """크롤링 스케줄러 클래스"""

    def __init__(self):
        """초기화"""
        self.news_collector = NewsCrawler()
        self.stock_collector = StockDataCrawler()
        self.sentiment_analyzer = FinancialSentimentAnalyzer()

        # 수집 설정
        self.news_collection_interval = int(os.getenv("NEWS_COLLECTION_INTERVAL_MINUTES", "60"))
        self.stock_collection_interval = int(os.getenv("STOCK_COLLECTION_INTERVAL_MINUTES", "30"))

        # 수집 결과 저장 경로
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(self.data_dir, exist_ok=True)

    def collect_news(self):
        """뉴스 수집 작업"""
        try:
            logger.info("뉴스 수집 시작")

            # 뉴스 수집
            news_items = self.news_collector.get_news_from_rss(count=10)
            logger.info(f"뉴스 {len(news_items)}개 수집 완료")

            # 뉴스 내용 및 감성 분석
            for item in news_items:
                try:
                    # 뉴스 내용이 이미 있는지 확인
                    if "content" in item and item["content"]:
                        # 감성 분석
                        sentiment_result = self.sentiment_analyzer.analyze(item["content"])
                        if sentiment_result:
                            item["sentiment"] = sentiment_result["sentiment"]
                            item["sentiment_scores"] = sentiment_result["scores"]
                except Exception as e:
                    logger.error(f"뉴스 처리 실패: {e}")

            # 결과 저장
            self._save_data(
                news_items,
                f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            logger.info("뉴스 수집 및 처리 완료")

        except Exception as e:
            logger.error(f"뉴스 수집 작업 실패: {e}")

    def collect_stocks(self):
        """주식 데이터 수집 작업"""
        try:
            logger.info("주식 데이터 수집 시작")

            # 인기 주식 목록 가져오기
            popular_stocks = [
                "AAPL", "MSFT", "GOOGL", "AMZN", "META",
                "TSLA", "NVDA", "JPM", "V", "WMT"
            ]

            stock_data = []

            # 주식 데이터 수집
            for symbol in popular_stocks:
                try:
                    # 주식 정보 가져오기
                    info = self.stock_collector.get_stock_info_polygon(symbol)
                    if info and 'error' not in info:
                        # 주식 가격 데이터 가져오기
                        price_data = self.stock_collector.get_stock_data(symbol, period='1mo')
                        if not price_data.empty:
                            # 데이터프레임을 디셔너리로 변환
                            latest_price = price_data.iloc[-1].to_dict()
                            info['price'] = latest_price.get('close')
                            info['change'] = latest_price.get('close') - latest_price.get('open')
                            info['change_percent'] = (info['change'] / latest_price.get('open')) * 100 if latest_price.get('open') else 0
                            info['volume'] = latest_price.get('volume')
                            info['high'] = latest_price.get('high')
                            info['low'] = latest_price.get('low')
                            info['date'] = latest_price.get('date')

                        stock_data.append(info)
                except Exception as e:
                    logger.error(f"{symbol} 주식 데이터 수집 실패: {e}")

            # 결과 저장
            self._save_data(
                stock_data,
                f"stocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            logger.info(f"주식 데이터 {len(stock_data)}개 수집 완료")

        except Exception as e:
            logger.error(f"주식 데이터 수집 작업 실패: {e}")

    def _save_data(self, data: List[Dict[str, Any]], filename: str):
        """데이터 저장"""
        import json

        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"데이터 저장 완료: {filepath}")

        except Exception as e:
            logger.error(f"데이터 저장 실패: {e}")

    def schedule_jobs(self):
        """작업 스케줄링"""
        # 뉴스 수집 스케줄링
        schedule.every(self.news_collection_interval).minutes.do(self.collect_news)

        # 주식 데이터 수집 스케줄링
        schedule.every(self.stock_collection_interval).minutes.do(self.collect_stocks)

        # 초기 실행
        self.collect_news()
        self.collect_stocks()

        logger.info("크롤링 작업 스케줄링 완료")

        # 스케줄 실행
        while True:
            schedule.run_pending()
            time.sleep(1)

# 메인 실행
if __name__ == "__main__":
    try:
        logger.info("크롤링 스케줄러 시작")
        scheduler = CrawlingScheduler()
        scheduler.schedule_jobs()
    except KeyboardInterrupt:
        logger.info("크롤링 스케줄러 종료")
    except Exception as e:
        logger.error(f"크롤링 스케줄러 오류: {e}")
        sys.exit(1)
