"""
통합 뉴스 수집기 모듈

기존 크롤링 시스템과 GDELT를 통합하여 뉴스를 수집합니다.
"""
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv

from crawling.news_crawler import NewsCrawler
from crawling.news_sources_enhanced import NewsSourcesHandler
from crawling.gdelt_client import GDELTClient

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
env_path = Path(__file__).parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

# 설정 파일 로드
config_path = Path(__file__).parent / 'config.json'
with open(config_path, 'r') as f:
    CONFIG = json.load(f)

class IntegratedNewsCollector:
    """
    통합 뉴스 수집기 클래스

    기존 크롤링 시스템과 GDELT를 통합하여 뉴스를 수집합니다.
    """

    def __init__(self, db_connect: bool = True):
        """
        IntegratedNewsCollector 클래스 초기화

        Args:
            db_connect: MongoDB 연결 여부 (기본값: True)
        """
        self.config = CONFIG

        # MongoDB 연결 설정
        if db_connect:
            mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
            mongo_db_name = os.getenv("MONGO_DB_NAME", "jaepa")

            try:
                self.client = MongoClient(mongo_uri)
                self.db = self.client[mongo_db_name]
                self.news_collection = self.db[self.config['storage']['mongodb']['news_collection']]

                # 인덱스 생성
                self._create_indexes()

                logger.info("MongoDB 연결 성공")
            except Exception as e:
                logger.error(f"MongoDB 연결 실패: {str(e)}")
                self.client = None
                self.db = None
                self.news_collection = None
        else:
            self.client = None
            self.db = None
            self.news_collection = None

        # 뉴스 수집기 초기화
        self.news_crawler = NewsCrawler(db_connect=False)  # DB 연결은 이 클래스에서 관리
        self.enhanced_sources = NewsSourcesHandler(db_connect=False)  # DB 연결은 이 클래스에서 관리
        self.gdelt_client = GDELTClient()

        # 뉴스 수집기에 DB 연결 설정
        if self.db and self.news_collection:
            self.news_crawler.db = self.db
            self.news_crawler.news_collection = self.news_collection
            self.enhanced_sources.db = self.db
            self.enhanced_sources.news_collection = self.news_collection

    def _create_indexes(self):
        """인덱스 생성"""
        if not self.db or not self.news_collection:
            return

        try:
            # 기본 인덱스
            self.news_collection.create_index([("url", pymongo.ASCENDING)], unique=True, name="url_index")
            self.news_collection.create_index([("published_date", pymongo.DESCENDING)], name="published_date_index")
            self.news_collection.create_index([("source", pymongo.ASCENDING)], name="source_index")
            self.news_collection.create_index([("source_type", pymongo.ASCENDING)], name="source_type_index")
            self.news_collection.create_index([("related_symbols", pymongo.ASCENDING)], name="related_symbols_index")

            # 복합 인덱스
            self.news_collection.create_index([
                ("published_date", pymongo.DESCENDING),
                ("source", pymongo.ASCENDING)
            ], name="date_source_index")

            self.news_collection.create_index([
                ("related_symbols", pymongo.ASCENDING),
                ("published_date", pymongo.DESCENDING)
            ], name="symbols_date_index")

            # 텍스트 인덱스
            try:
                self.news_collection.create_index([
                    ("title", pymongo.TEXT),
                    ("content", pymongo.TEXT),
                    ("summary", pymongo.TEXT)
                ],
                weights={
                    "title": 10,
                    "content": 5,
                    "summary": 3
                },
                name="content_search_index")
            except pymongo.errors.OperationFailure as e:
                logger.warning(f"텍스트 인덱스 생성 중 오류 발생 (이미 존재할 수 있음): {str(e)}")

            logger.info("인덱스가 생성되었습니다.")

        except Exception as e:
            logger.error(f"인덱스 생성 실패: {str(e)}")

    def save_article(self, article: Dict[str, Any]) -> bool:
        """
        기사 저장

        Args:
            article: 저장할 기사 데이터

        Returns:
            bool: 저장 성공 여부
        """
        if not self.news_collection:
            logger.error("MongoDB 연결이 설정되지 않았습니다.")
            return False

        try:
            # URL이 이미 존재하는지 확인
            existing = self.news_collection.find_one({"url": article["url"]})
            if existing:
                logger.info(f"이미 저장된 기사입니다: {article['url']}")
                return False

            # 기사 저장
            result = self.news_collection.insert_one(article)
            logger.info(f"기사 저장 성공: {article['url']} (ID: {result.inserted_id})")
            return True

        except Exception as e:
            logger.error(f"기사 저장 중 오류: {str(e)}")
            return False

    def collect_news_from_all_sources(self,
                                     keywords: Optional[List[str]] = None,
                                     symbols: Optional[List[str]] = None,
                                     days: int = 3,
                                     limit: int = 100) -> Dict[str, int]:
        """
        모든 소스에서 뉴스 수집

        Args:
            keywords: 검색 키워드 목록
            symbols: 주식 심볼 목록
            days: 검색 기간 (일)
            limit: 소스별 최대 검색 결과 수

        Returns:
            Dict[str, int]: 소스별 수집된 뉴스 수
        """
        if not keywords:
            keywords = ["finance", "stock market", "investment"]

        if not symbols:
            symbols = ["AAPL", "MSFT", "GOOG", "AMZN", "META"]

        results = {
            "traditional_crawler": 0,
            "enhanced_sources": 0,
            "gdelt": 0
        }

        # 1. 기존 크롤러로 뉴스 수집
        try:
            for keyword in keywords:
                articles = self.news_crawler.search_news(keyword, max_results=limit)
                for article in articles:
                    if self.save_article(article):
                        results["traditional_crawler"] += 1

            logger.info(f"기존 크롤러로 {results['traditional_crawler']}개 뉴스 수집됨")
        except Exception as e:
            logger.error(f"기존 크롤러 뉴스 수집 중 오류: {str(e)}")

        # 2. 향상된 소스로 뉴스 수집
        try:
            for keyword in keywords:
                articles = self.enhanced_sources.search_news_with_apis(keyword, days=days)
                for article in articles:
                    if self.save_article(article):
                        results["enhanced_sources"] += 1

            logger.info(f"향상된 소스로 {results['enhanced_sources']}개 뉴스 수집됨")
        except Exception as e:
            logger.error(f"향상된 소스 뉴스 수집 중 오류: {str(e)}")

        # 3. GDELT로 뉴스 수집
        try:
            # 키워드 기반 검색
            for keyword in keywords:
                articles = self.gdelt_client.search_financial_news(
                    keywords=keyword,
                    symbols=symbols,
                    days=days,
                    max_records=limit
                )
                for article in articles:
                    if self.save_article(article):
                        results["gdelt"] += 1

            # 심볼 기반 검색
            for symbol in symbols:
                articles = self.gdelt_client.get_news_by_symbol(
                    symbol=symbol,
                    days=days,
                    max_records=limit
                )
                for article in articles:
                    if self.save_article(article):
                        results["gdelt"] += 1

            logger.info(f"GDELT로 {results['gdelt']}개 뉴스 수집됨")
        except Exception as e:
            logger.error(f"GDELT 뉴스 수집 중 오류: {str(e)}")

        total = sum(results.values())
        logger.info(f"총 {total}개 뉴스 수집됨")
        return results

    def collect_news_by_symbol(self,
                              symbol: str,
                              days: int = 7,
                              limit: int = 50) -> Dict[str, int]:
        """
        특정 주식 심볼에 대한 뉴스 수집

        Args:
            symbol: 주식 심볼 (예: AAPL)
            days: 검색 기간 (일)
            limit: 소스별 최대 검색 결과 수

        Returns:
            Dict[str, int]: 소스별 수집된 뉴스 수
        """
        results = {
            "traditional_crawler": 0,
            "enhanced_sources": 0,
            "gdelt": 0
        }

        # 1. 기존 크롤러로 뉴스 수집
        try:
            articles = self.news_crawler.search_news(symbol, max_results=limit)
            for article in articles:
                # 관련 심볼 추가
                if "related_symbols" not in article:
                    article["related_symbols"] = [symbol]
                elif symbol not in article["related_symbols"]:
                    article["related_symbols"].append(symbol)

                if self.save_article(article):
                    results["traditional_crawler"] += 1

            logger.info(f"기존 크롤러로 {symbol} 관련 {results['traditional_crawler']}개 뉴스 수집됨")
        except Exception as e:
            logger.error(f"기존 크롤러 뉴스 수집 중 오류: {str(e)}")

        # 2. 향상된 소스로 뉴스 수집
        try:
            articles = self.enhanced_sources.search_news_with_apis(symbol, days=days)
            for article in articles:
                # 관련 심볼 추가
                if "related_symbols" not in article:
                    article["related_symbols"] = [symbol]
                elif symbol not in article["related_symbols"]:
                    article["related_symbols"].append(symbol)

                if self.save_article(article):
                    results["enhanced_sources"] += 1

            logger.info(f"향상된 소스로 {symbol} 관련 {results['enhanced_sources']}개 뉴스 수집됨")
        except Exception as e:
            logger.error(f"향상된 소스 뉴스 수집 중 오류: {str(e)}")

        # 3. GDELT로 뉴스 수집
        try:
            articles = self.gdelt_client.get_news_by_symbol(
                symbol=symbol,
                days=days,
                max_records=limit
            )
            for article in articles:
                if self.save_article(article):
                    results["gdelt"] += 1

            logger.info(f"GDELT로 {symbol} 관련 {results['gdelt']}개 뉴스 수집됨")
        except Exception as e:
            logger.error(f"GDELT 뉴스 수집 중 오류: {str(e)}")

        total = sum(results.values())
        logger.info(f"{symbol} 관련 총 {total}개 뉴스 수집됨")
        return results

    def get_news_by_symbol(self,
                          symbol: str,
                          days: int = 7,
                          limit: int = 50,
                          force_update: bool = False) -> List[Dict[str, Any]]:
        """
        특정 주식 심볼에 대한 뉴스 조회

        Args:
            symbol: 주식 심볼 (예: AAPL)
            days: 검색 기간 (일)
            limit: 최대 검색 결과 수
            force_update: 강제 업데이트 여부

        Returns:
            List[Dict[str, Any]]: 뉴스 목록
        """
        if not self.news_collection:
            logger.error("MongoDB 연결이 설정되지 않았습니다.")
            return []

        # 날짜 범위 계산
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        start_date_str = start_date.isoformat()

        # 강제 업데이트인 경우 새로 수집
        if force_update:
            self.collect_news_by_symbol(symbol, days, limit)

        try:
            # DB에서 뉴스 조회
            news = list(self.news_collection.find(
                {
                    "related_symbols": symbol,
                    "published_date": {"$gte": start_date_str}
                },
                {"_id": 0}
            ).sort("published_date", pymongo.DESCENDING).limit(limit))

            # 결과가 부족한 경우 새로 수집
            if len(news) < limit * 0.5:  # 50% 미만인 경우
                logger.info(f"{symbol} 관련 뉴스가 부족하여 새로 수집합니다.")
                self.collect_news_by_symbol(symbol, days, limit)

                # 다시 조회
                news = list(self.news_collection.find(
                    {
                        "related_symbols": symbol,
                        "published_date": {"$gte": start_date_str}
                    },
                    {"_id": 0}
                ).sort("published_date", pymongo.DESCENDING).limit(limit))

            logger.info(f"{symbol} 관련 뉴스 {len(news)}개 조회됨")
            return news

        except Exception as e:
            logger.error(f"뉴스 조회 중 오류: {str(e)}")
            return []

    def search_news(self,
                   query: str,
                   days: int = 30,
                   limit: int = 100,
                   force_update: bool = False) -> List[Dict[str, Any]]:
        """
        키워드로 뉴스 검색

        Args:
            query: 검색어
            days: 검색 기간 (일)
            limit: 최대 검색 결과 수
            force_update: 강제 업데이트 여부

        Returns:
            List[Dict[str, Any]]: 검색 결과 목록
        """
        if not self.news_collection:
            logger.error("MongoDB 연결이 설정되지 않았습니다.")
            return []

        # 날짜 범위 계산
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        start_date_str = start_date.isoformat()

        # 강제 업데이트인 경우 새로 수집
        if force_update:
            self.collect_news_from_all_sources(keywords=[query], days=days, limit=limit)

        try:
            # 텍스트 검색 쿼리 구성
            search_results = list(self.news_collection.find(
                {
                    "$text": {"$search": query},
                    "published_date": {"$gte": start_date_str}
                },
                {
                    "_id": 0,
                    "score": {"$meta": "textScore"}
                }
            ).sort([("score", {"$meta": "textScore"})]).limit(limit))

            # 결과가 부족한 경우 새로 수집
            if len(search_results) < limit * 0.3:  # 30% 미만인 경우
                logger.info(f"'{query}' 검색 결과가 부족하여 새로 수집합니다.")
                self.collect_news_from_all_sources(keywords=[query], days=days, limit=limit)

                # 다시 검색
                search_results = list(self.news_collection.find(
                    {
                        "$text": {"$search": query},
                        "published_date": {"$gte": start_date_str}
                    },
                    {
                        "_id": 0,
                        "score": {"$meta": "textScore"}
                    }
                ).sort([("score", {"$meta": "textScore"})]).limit(limit))

            logger.info(f"'{query}' 검색 결과 {len(search_results)}개 조회됨")
            return search_results

        except Exception as e:
            logger.error(f"뉴스 검색 중 오류: {str(e)}")
            return []

    def close(self):
        """연결 종료"""
        if self.client:
            self.client.close()
            logger.info("MongoDB 연결이 종료되었습니다.")

# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    collector = IntegratedNewsCollector()

    # 모든 소스에서 뉴스 수집
    results = collector.collect_news_from_all_sources(
        keywords=["finance", "stock market"],
        symbols=["AAPL", "MSFT"],
        days=3,
        limit=10
    )
    print(f"수집 결과: {results}")

    # 특정 심볼에 대한 뉴스 조회
    apple_news = collector.get_news_by_symbol("AAPL", days=7, limit=5)
    print(f"애플 관련 뉴스: {len(apple_news)}개")
    for news in apple_news[:2]:  # 처음 2개만 출력
        print(f"제목: {news['title']}")
        print(f"출처: {news['source']} ({news['source_type']})")
        print(f"날짜: {news['published_date']}")
        print("---")

    # 키워드 검색
    search_results = collector.search_news("artificial intelligence", days=30, limit=5)
    print(f"'artificial intelligence' 검색 결과: {len(search_results)}개")
    for result in search_results[:2]:  # 처음 2개만 출력
        print(f"제목: {result['title']}")
        print(f"출처: {result['source']} ({result['source_type']})")
        print(f"날짜: {result['published_date']}")
        print("---")

    # 연결 종료
    collector.close()
