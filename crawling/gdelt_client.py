"""
GDELT 클라이언트 모듈

GDELT API를 사용하여 글로벌 뉴스 데이터를 수집하고 처리합니다.
"""
import os
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import urllib.parse

import pandas as pd
import requests
from dotenv import load_dotenv

from crawling.enhanced_request import make_request_with_retry, get_random_user_agent

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

class GDELTClient:
    """
    GDELT API 클라이언트

    GDELT API를 사용하여 글로벌 뉴스 데이터를 수집하고 처리합니다.
    """

    def __init__(self):
        """
        GDELTClient 클래스 초기화
        """
        # GDELT API 엔드포인트
        self.gdelt_v2_api = "https://api.gdeltproject.org/api/v2/doc/doc"
        self.gdelt_gkg_api = "https://api.gdeltproject.org/api/v2/gkg/gkg"

        # 요청 간격 (초)
        self.request_interval = 1.0
        self.last_request_time = 0

    def _wait_for_rate_limit(self):
        """
        API 요청 간격 조절을 위한 대기
        """
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        if elapsed < self.request_interval:
            wait_time = self.request_interval - elapsed
            time.sleep(wait_time)

        self.last_request_time = time.time()

    def search_news(self,
                   query: str,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   max_records: int = 250,
                   format_type: str = "json") -> List[Dict[str, Any]]:
        """
        GDELT에서 뉴스 검색

        Args:
            query: 검색어 (GDELT 쿼리 형식)
            start_date: 시작 날짜 (기본값: 7일 전)
            end_date: 종료 날짜 (기본값: 현재)
            max_records: 최대 검색 결과 수 (기본값: 250, 최대 250)
            format_type: 응답 형식 (json, csv, html)

        Returns:
            List[Dict[str, Any]]: 검색 결과 목록
        """
        # 날짜 범위 설정
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=7)

        # 날짜 형식 변환
        start_str = start_date.strftime("%Y%m%d%H%M%S")
        end_str = end_date.strftime("%Y%m%d%H%M%S")

        # 쿼리 파라미터 구성
        params = {
            "query": query,
            "format": format_type,
            "timespan": f"{start_str} {end_str}",
            "maxrecords": max_records,
            "sort": "DateDesc"  # 최신순 정렬
        }

        # URL 인코딩
        query_string = urllib.parse.urlencode(params)
        url = f"{self.gdelt_v2_api}?{query_string}"

        # API 요청 간격 조절
        self._wait_for_rate_limit()

        try:
            # API 요청
            status_code, response_text = make_request_with_retry(url)

            if status_code != 200 or not response_text:
                logger.error(f"GDELT API 응답 오류: {status_code}")
                return []

            # JSON 파싱
            if format_type == "json":
                response = json.loads(response_text)
                articles = response.get("articles", [])
                logger.info(f"GDELT에서 {len(articles)}개 뉴스 검색됨")
                return articles
            else:
                logger.error(f"지원하지 않는 형식: {format_type}")
                return []

        except Exception as e:
            logger.error(f"GDELT 뉴스 검색 중 오류: {str(e)}")
            return []

    def search_financial_news(self,
                             keywords: Union[str, List[str]],
                             symbols: Optional[List[str]] = None,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             max_records: int = 250) -> List[Dict[str, Any]]:
        """
        금융 관련 뉴스 검색

        Args:
            keywords: 검색 키워드 (문자열 또는 목록)
            symbols: 주식 심볼 목록 (예: ["AAPL", "MSFT"])
            start_date: 시작 날짜
            end_date: 종료 날짜
            max_records: 최대 검색 결과 수

        Returns:
            List[Dict[str, Any]]: 검색 결과 목록
        """
        # 키워드 처리
        if isinstance(keywords, list):
            keyword_str = " OR ".join([f'"{k}"' for k in keywords])
        else:
            keyword_str = f'"{keywords}"'

        # 주식 심볼 처리
        symbol_query = ""
        if symbols and len(symbols) > 0:
            symbol_str = " OR ".join([f'"{s}"' for s in symbols])
            symbol_query = f" ({symbol_str})"

        # 금융 관련 키워드 추가
        finance_terms = '("stock market" OR "financial market" OR "stock price" OR "investor" OR "investment" OR "trading" OR "finance" OR "economy" OR "economic")'

        # 최종 쿼리 구성
        query = f"({keyword_str}){symbol_query} AND {finance_terms}"

        # 뉴스 검색
        articles = self.search_news(
            query=query,
            start_date=start_date,
            end_date=end_date,
            max_records=max_records
        )

        # 결과 정규화
        normalized_articles = []
        for article in articles:
            try:
                # 날짜 변환
                published_date = datetime.fromtimestamp(int(article.get("seendate", 0))/1000.0).isoformat()

                # 관련 심볼 추출
                related_symbols = []
                if symbols:
                    article_text = (article.get("title", "") + " " + article.get("snippet", "")).lower()
                    for symbol in symbols:
                        if symbol.lower() in article_text:
                            related_symbols.append(symbol)

                # 정규화된 기사 데이터
                normalized = {
                    "title": article.get("title", ""),
                    "content": article.get("snippet", ""),
                    "summary": article.get("snippet", ""),
                    "url": article.get("url", ""),
                    "published_date": published_date,
                    "source": article.get("domain", ""),
                    "source_type": "gdelt",
                    "crawled_date": datetime.now().isoformat(),
                    "related_symbols": related_symbols,
                    "language": article.get("language", ""),
                    "sentiment": {
                        "score": float(article.get("tone", 0)),
                        "positive": max(0, float(article.get("tone", 0))),
                        "negative": max(0, -float(article.get("tone", 0))),
                        "neutral": 1.0 - abs(float(article.get("tone", 0)))
                    },
                    "gdelt_data": {
                        "themes": article.get("themes", []),
                        "locations": article.get("locations", []),
                        "persons": article.get("persons", []),
                        "organizations": article.get("organizations", [])
                    }
                }

                normalized_articles.append(normalized)

            except Exception as e:
                logger.error(f"기사 정규화 중 오류: {str(e)}")
                continue

        logger.info(f"금융 관련 뉴스 {len(normalized_articles)}개 정규화됨")
        return normalized_articles

    def get_news_by_symbol(self,
                          symbol: str,
                          days: int = 7,
                          max_records: int = 100) -> List[Dict[str, Any]]:
        """
        특정 주식 심볼에 대한 뉴스 검색

        Args:
            symbol: 주식 심볼 (예: AAPL)
            days: 검색 기간 (일)
            max_records: 최대 검색 결과 수

        Returns:
            List[Dict[str, Any]]: 검색 결과 목록
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 회사 이름 추가 검색을 위한 매핑 (실제로는 더 많은 회사 정보가 필요)
        company_names = {
            "AAPL": "Apple",
            "MSFT": "Microsoft",
            "GOOG": "Google",
            "AMZN": "Amazon",
            "META": "Facebook",
            "TSLA": "Tesla",
            "NVDA": "NVIDIA",
            "JPM": "JPMorgan",
            "BAC": "Bank of America",
            "WMT": "Walmart"
        }

        # 검색 키워드 구성
        keywords = [symbol]
        if symbol in company_names:
            keywords.append(company_names[symbol])

        return self.search_financial_news(
            keywords=keywords,
            symbols=[symbol],
            start_date=start_date,
            end_date=end_date,
            max_records=max_records
        )

    def get_market_sentiment(self, days: int = 1) -> Dict[str, Any]:
        """
        전체 시장 감성 지표 가져오기

        Args:
            days: 검색 기간 (일)

        Returns:
            Dict[str, Any]: 시장 감성 지표
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 시장 관련 키워드로 검색
        market_keywords = ["stock market", "financial market", "wall street", "market sentiment"]

        articles = self.search_financial_news(
            keywords=market_keywords,
            start_date=start_date,
            end_date=end_date,
            max_records=250
        )

        # 감성 지표 집계
        if not articles:
            return {
                "date": end_date.strftime("%Y-%m-%d"),
                "sentiment": {
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "average_score": 0
                },
                "article_count": 0
            }

        # 감성 점수 평균 계산
        total_positive = sum(article["sentiment"]["positive"] for article in articles)
        total_negative = sum(article["sentiment"]["negative"] for article in articles)
        total_neutral = sum(article["sentiment"]["neutral"] for article in articles)
        average_score = sum(article["sentiment"]["score"] for article in articles) / len(articles)

        return {
            "date": end_date.strftime("%Y-%m-%d"),
            "sentiment": {
                "positive": total_positive / len(articles),
                "negative": total_negative / len(articles),
                "neutral": total_neutral / len(articles),
                "average_score": average_score
            },
            "article_count": len(articles)
        }

# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    client = GDELTClient()

    # 애플 관련 뉴스 검색
    apple_news = client.get_news_by_symbol("AAPL", days=3, max_records=5)
    print(f"애플 관련 뉴스: {len(apple_news)}개")
    for news in apple_news:
        print(f"제목: {news['title']}")
        print(f"날짜: {news['published_date']}")
        print(f"감성 점수: {news['sentiment']['score']}")
        print("---")

    # 시장 감성 지표
    market_sentiment = client.get_market_sentiment(days=1)
    print(f"시장 감성 지표:")
    print(f"날짜: {market_sentiment['date']}")
    print(f"평균 감성 점수: {market_sentiment['sentiment']['average_score']}")
    print(f"기사 수: {market_sentiment['article_count']}")
