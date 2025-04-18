"""
GDELT 클라이언트 모듈

GDELT API를 사용하여 글로벌 뉴스 데이터를 수집하고 처리합니다.
과거 뉴스 데이터 수집, 감성 분석, 트렌드 분석 등의 기능을 제공합니다.
"""
import os
import logging
import json
import time
import re
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Union, Tuple
import urllib.parse
import calendar

import pandas as pd
import numpy as np
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
    과거 데이터 수집, 감성 분석, 트렌드 분석 등의 기능을 제공합니다.
    """

    def __init__(self):
        """
        GDELTClient 클래스 초기화
        """
        # GDELT API 엔드포인트
        self.gdelt_v2_api = "https://api.gdeltproject.org/api/v2/doc/doc"
        self.gdelt_gkg_api = "https://api.gdeltproject.org/api/v2/gkg/gkg"
        self.gdelt_events_api = "https://api.gdeltproject.org/api/v2/events/events"
        self.gdelt_context_api = "https://api.gdeltproject.org/api/v2/context/context"

        # 요청 간격 (초)
        self.request_interval = 1.0
        self.last_request_time = 0

        # 회사 이름 매핑 (주요 회사만 추가, 실제로는 더 많은 회사 정보 필요)
        self.company_names = {
            "AAPL": "Apple",
            "MSFT": "Microsoft",
            "GOOG": "Google",
            "GOOGL": "Google",
            "AMZN": "Amazon",
            "META": "Facebook",
            "TSLA": "Tesla",
            "NVDA": "NVIDIA",
            "JPM": "JPMorgan",
            "BAC": "Bank of America",
            "WMT": "Walmart",
            "JNJ": "Johnson & Johnson",
            "PG": "Procter & Gamble",
            "V": "Visa",
            "MA": "Mastercard",
            "DIS": "Disney",
            "NFLX": "Netflix",
            "INTC": "Intel",
            "AMD": "AMD",
            "IBM": "IBM"
        }

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

        # 검색 키워드 구성
        keywords = [symbol]
        if symbol in self.company_names:
            keywords.append(self.company_names[symbol])

        return self.search_financial_news(
            keywords=keywords,
            symbols=[symbol],
            start_date=start_date,
            end_date=end_date,
            max_records=max_records
        )

    def get_historical_news_by_symbol(self,
                                     symbol: str,
                                     start_date: Optional[datetime] = None,
                                     end_date: Optional[datetime] = None,
                                     max_records: int = 1000) -> List[Dict[str, Any]]:
        """
        특정 주식 심볼에 대한 과거 뉴스 검색

        Args:
            symbol: 주식 심볼 (예: AAPL)
            start_date: 시작 날짜 (기본값: 1년 전)
            end_date: 종료 날짜 (기본값: 현재)
            max_records: 최대 검색 결과 수

        Returns:
            List[Dict[str, Any]]: 검색 결과 목록
        """
        # 날짜 범위 설정
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)  # 기본값: 1년 전

        # 검색 키워드 구성
        keywords = [symbol]
        if symbol in self.company_names:
            keywords.append(self.company_names[symbol])

        # 기간이 길 경우 여러 번 나누어 검색
        all_articles = []
        current_start = start_date

        while current_start < end_date and len(all_articles) < max_records:
            # 최대 3개월 단위로 검색
            current_end = min(current_start + timedelta(days=90), end_date)

            articles = self.search_financial_news(
                keywords=keywords,
                symbols=[symbol],
                start_date=current_start,
                end_date=current_end,
                max_records=min(250, max_records - len(all_articles))  # GDELT API 한 번에 최대 250개
            )

            all_articles.extend(articles)
            logger.info(f"{symbol} 관련 뉴스 {len(articles)}개 검색됨 ({current_start.strftime('%Y-%m-%d')} ~ {current_end.strftime('%Y-%m-%d')})")

            # 다음 기간으로 이동
            current_start = current_end + timedelta(days=1)

            # API 요청 간격 조절
            time.sleep(2.0)

        logger.info(f"{symbol} 관련 과거 뉴스 총 {len(all_articles)}개 검색됨 ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})")
        return all_articles

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

    def get_news_sentiment_trends(self,
                                 symbol: str,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None,
                                 interval: str = 'day') -> Dict[str, Any]:
        """
        시간 간격별 감성 트렌드 분석

        Args:
            symbol: 주식 심볼 (예: AAPL)
            start_date: 시작 날짜 (기본값: 30일 전)
            end_date: 종료 날짜 (기본값: 현재)
            interval: 시간 간격 ('hour', 'day', 'week', 'month')

        Returns:
            Dict[str, Any]: 감성 트렌드 분석 결과
        """
        # 날짜 범위 설정
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            if interval == 'hour':
                start_date = end_date - timedelta(days=2)  # 시간별 분석은 짧은 기간
            elif interval == 'day':
                start_date = end_date - timedelta(days=30)
            elif interval == 'week':
                start_date = end_date - timedelta(days=90)
            else:  # month
                start_date = end_date - timedelta(days=365)

        # 뉴스 수집
        articles = self.get_historical_news_by_symbol(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            max_records=1000
        )

        if not articles:
            return {
                "symbol": symbol,
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "interval": interval,
                "trends": [],
                "summary": {
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "average_score": 0,
                    "article_count": 0
                }
            }

        # 데이터 정리
        df = pd.DataFrame(articles)

        # 날짜 형식 변환
        df['date_obj'] = pd.to_datetime(df['published_date'])

        # 시간 간격에 따른 그룹화
        if interval == 'hour':
            df['interval'] = df['date_obj'].dt.strftime('%Y-%m-%d %H:00')
        elif interval == 'day':
            df['interval'] = df['date_obj'].dt.strftime('%Y-%m-%d')
        elif interval == 'week':
            df['interval'] = df['date_obj'].dt.to_period('W').dt.start_time.dt.strftime('%Y-%m-%d')
        else:  # month
            df['interval'] = df['date_obj'].dt.strftime('%Y-%m')

        # 감성 점수 추출
        df['positive'] = df['sentiment'].apply(lambda x: x.get('positive', 0) if x else 0)
        df['negative'] = df['sentiment'].apply(lambda x: x.get('negative', 0) if x else 0)
        df['neutral'] = df['sentiment'].apply(lambda x: x.get('neutral', 0) if x else 0)
        df['score'] = df['sentiment'].apply(lambda x: x.get('score', 0) if x else 0)

        # 간격별 집계
        grouped = df.groupby('interval').agg({
            'positive': 'mean',
            'negative': 'mean',
            'neutral': 'mean',
            'score': 'mean',
            'url': 'count'
        }).reset_index()

        grouped = grouped.rename(columns={'url': 'article_count'})
        grouped = grouped.sort_values('interval')

        # 결과 형식화
        trends = []
        for _, row in grouped.iterrows():
            trends.append({
                "interval": row['interval'],
                "sentiment": {
                    "positive": float(row['positive']),
                    "negative": float(row['negative']),
                    "neutral": float(row['neutral']),
                    "score": float(row['score'])
                },
                "article_count": int(row['article_count'])
            })

        # 전체 기간 요약
        summary = {
            "positive": float(df['positive'].mean()),
            "negative": float(df['negative'].mean()),
            "neutral": float(df['neutral'].mean()),
            "average_score": float(df['score'].mean()),
            "article_count": len(df)
        }

        return {
            "symbol": symbol,
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "interval": interval,
            "trends": trends,
            "summary": summary
        }

    def get_news_volume_by_symbol(self,
                                symbol: str,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None,
                                interval: str = 'day') -> Dict[str, Any]:
        """
        시간 간격별 뉴스 볼륨 분석

        Args:
            symbol: 주식 심볼 (예: AAPL)
            start_date: 시작 날짜 (기본값: 30일 전)
            end_date: 종료 날짜 (기본값: 현재)
            interval: 시간 간격 ('day', 'week', 'month')

        Returns:
            Dict[str, Any]: 뉴스 볼륨 분석 결과
        """
        # 날짜 범위 설정
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            if interval == 'day':
                start_date = end_date - timedelta(days=30)
            elif interval == 'week':
                start_date = end_date - timedelta(days=90)
            else:  # month
                start_date = end_date - timedelta(days=365)

        # 뉴스 수집
        articles = self.get_historical_news_by_symbol(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            max_records=1000
        )

        if not articles:
            return {
                "symbol": symbol,
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "interval": interval,
                "volumes": [],
                "total_articles": 0
            }

        # 데이터 정리
        df = pd.DataFrame(articles)

        # 날짜 형식 변환
        df['date_obj'] = pd.to_datetime(df['published_date'])

        # 시간 간격에 따른 그룹화
        if interval == 'day':
            df['interval'] = df['date_obj'].dt.strftime('%Y-%m-%d')
        elif interval == 'week':
            df['interval'] = df['date_obj'].dt.to_period('W').dt.start_time.dt.strftime('%Y-%m-%d')
        else:  # month
            df['interval'] = df['date_obj'].dt.strftime('%Y-%m')

        # 간격별 집계
        volume_data = df.groupby('interval').size().reset_index(name='count')
        volume_data = volume_data.sort_values('interval')

        # 결과 형식화
        volumes = []
        for _, row in volume_data.iterrows():
            volumes.append({
                "interval": row['interval'],
                "count": int(row['count'])
            })

        return {
            "symbol": symbol,
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "interval": interval,
            "volumes": volumes,
            "total_articles": len(df)
        }

    def get_related_entities(self,
                           symbol: str,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           min_count: int = 2) -> Dict[str, List[Dict[str, Any]]]:
        """
        관련 엔티티(인물, 조직, 장소 등) 분석

        Args:
            symbol: 주식 심볼 (예: AAPL)
            start_date: 시작 날짜 (기본값: 30일 전)
            end_date: 종료 날짜 (기본값: 현재)
            min_count: 최소 언급 횟수

        Returns:
            Dict[str, List[Dict[str, Any]]]: 관련 엔티티 분석 결과
        """
        # 날짜 범위 설정
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        # 뉴스 수집
        articles = self.get_historical_news_by_symbol(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            max_records=500
        )

        if not articles:
            return {
                "persons": [],
                "organizations": [],
                "locations": [],
                "themes": []
            }

        # 엔티티 카운트
        persons = {}
        organizations = {}
        locations = {}
        themes = {}

        for article in articles:
            gdelt_data = article.get('gdelt_data', {})

            # 인물
            for person in gdelt_data.get('persons', []):
                persons[person] = persons.get(person, 0) + 1

            # 조직
            for org in gdelt_data.get('organizations', []):
                organizations[org] = organizations.get(org, 0) + 1

            # 장소
            for location in gdelt_data.get('locations', []):
                locations[location] = locations.get(location, 0) + 1

            # 테마
            for theme in gdelt_data.get('themes', []):
                themes[theme] = themes.get(theme, 0) + 1

        # 결과 형식화
        result = {
            "persons": [
                {"name": person, "count": count}
                for person, count in sorted(persons.items(), key=lambda x: x[1], reverse=True)
                if count >= min_count
            ],
            "organizations": [
                {"name": org, "count": count}
                for org, count in sorted(organizations.items(), key=lambda x: x[1], reverse=True)
                if count >= min_count
            ],
            "locations": [
                {"name": location, "count": count}
                for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)
                if count >= min_count
            ],
            "themes": [
                {"name": theme, "count": count}
                for theme, count in sorted(themes.items(), key=lambda x: x[1], reverse=True)
                if count >= min_count
            ]
        }

        return result

    def analyze_sentiment_stock_correlation(self,
                                          symbol: str,
                                          start_date: Optional[datetime] = None,
                                          end_date: Optional[datetime] = None,
                                          stock_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        감성과 주가 변동의 상관관계 분석

        Args:
            symbol: 주식 심볼 (예: AAPL)
            start_date: 시작 날짜 (기본값: 90일 전)
            end_date: 종료 날짜 (기본값: 현재)
            stock_data: 주가 데이터 (외부에서 제공하는 경우)

        Returns:
            Dict[str, Any]: 감성-주가 상관관계 분석 결과
        """
        # 날짜 범위 설정
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=90)  # 기본값: 90일 전

        # 감성 트렌드 가져오기
        sentiment_data = self.get_news_sentiment_trends(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval='day'
        )

        if not sentiment_data['trends']:
            return {
                "symbol": symbol,
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "correlation": {
                    "same_day": 0,
                    "next_day": 0,
                    "next_3_days": 0,
                    "next_week": 0
                },
                "sentiment_impact": [],
                "data_points": 0
            }

        # 주가 데이터가 없는 경우 더미 데이터 생성 (실제로는 외부에서 주가 데이터를 가져와야 함)
        if stock_data is None:
            # 더미 데이터 생성 (실제 구현에서는 주가 API를 통해 가져와야 함)
            stock_data = []
            base_date = start_date - timedelta(days=7)  # 시작일 이전 데이터도 포함
            current_date = base_date
            price = 150.0  # 임의의 시작 가격

            while current_date <= end_date + timedelta(days=7):  # 종료일 이후 데이터도 포함
                # 주말이면 건너뛰기
                if current_date.weekday() >= 5:  # 5: 토요일, 6: 일요일
                    current_date += timedelta(days=1)
                    continue

                # 임의의 가격 변동 (-2% ~ +2%)
                change_pct = (np.random.random() * 4) - 2
                price = price * (1 + change_pct / 100)

                stock_data.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "close": price,
                    "change_pct": change_pct
                })

                current_date += timedelta(days=1)

        # 데이터프레임 생성
        sentiment_df = pd.DataFrame(sentiment_data['trends'])
        stock_df = pd.DataFrame(stock_data)

        # 날짜 형식 변환
        sentiment_df['date'] = pd.to_datetime(sentiment_df['interval'])
        stock_df['date'] = pd.to_datetime(stock_df['date'])

        # 감성 점수 추출
        sentiment_df['sentiment_score'] = sentiment_df['sentiment'].apply(lambda x: x.get('score', 0))

        # 데이터 병합
        merged_df = pd.merge(sentiment_df, stock_df, on='date', how='inner')

        if len(merged_df) < 5:  # 데이터가 너무 적으면 분석 불가
            return {
                "symbol": symbol,
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "correlation": {
                    "same_day": 0,
                    "next_day": 0,
                    "next_3_days": 0,
                    "next_week": 0
                },
                "sentiment_impact": [],
                "data_points": len(merged_df)
            }

        # 다음 날 주가 변동 계산
        merged_df['next_day_close'] = merged_df['close'].shift(-1)
        merged_df['next_day_change'] = ((merged_df['next_day_close'] - merged_df['close']) / merged_df['close']) * 100

        # 3일 후 주가 변동 계산
        merged_df['next_3_days_close'] = merged_df['close'].shift(-3)
        merged_df['next_3_days_change'] = ((merged_df['next_3_days_close'] - merged_df['close']) / merged_df['close']) * 100

        # 1주일 후 주가 변동 계산
        merged_df['next_week_close'] = merged_df['close'].shift(-5)  # 주식 시장은 보통 주 5일
        merged_df['next_week_change'] = ((merged_df['next_week_close'] - merged_df['close']) / merged_df['close']) * 100

        # NaN 제거
        merged_df = merged_df.dropna()

        # 상관관계 계산
        correlation = {
            "same_day": float(merged_df['sentiment_score'].corr(merged_df['change_pct'])),
            "next_day": float(merged_df['sentiment_score'].corr(merged_df['next_day_change'])),
            "next_3_days": float(merged_df['sentiment_score'].corr(merged_df['next_3_days_change'])),
            "next_week": float(merged_df['sentiment_score'].corr(merged_df['next_week_change']))
        }

        # 감성 영향 분석
        # 감성 점수를 기준으로 그룹화
        merged_df['sentiment_group'] = pd.cut(
            merged_df['sentiment_score'],
            bins=[-1, -0.5, -0.2, 0.2, 0.5, 1],
            labels=['very_negative', 'negative', 'neutral', 'positive', 'very_positive']
        )

        sentiment_impact = []
        for group in ['very_negative', 'negative', 'neutral', 'positive', 'very_positive']:
            group_data = merged_df[merged_df['sentiment_group'] == group]
            if len(group_data) > 0:
                impact = {
                    "sentiment_group": group,
                    "count": len(group_data),
                    "avg_price_change": {
                        "same_day": float(group_data['change_pct'].mean()),
                        "next_day": float(group_data['next_day_change'].mean()),
                        "next_3_days": float(group_data['next_3_days_change'].mean()),
                        "next_week": float(group_data['next_week_change'].mean())
                    }
                }
                sentiment_impact.append(impact)

        return {
            "symbol": symbol,
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "correlation": correlation,
            "sentiment_impact": sentiment_impact,
            "data_points": len(merged_df)
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

    # 감성 트렌드 분석
    print("\n감성 트렌드 분석 시작...")
    sentiment_trends = client.get_news_sentiment_trends("AAPL", interval='day')
    print(f"감성 트렌드 분석 결과: {len(sentiment_trends['trends'])}개 기간")
    print(f"전체 기간 평균 감성 점수: {sentiment_trends['summary']['average_score']:.4f}")

    # 감성-주가 상관관계 분석
    print("\n감성-주가 상관관계 분석 시작...")
    correlation = client.analyze_sentiment_stock_correlation("AAPL")
    print(f"감성-주가 상관관계:")
    print(f"다음날 상관계수: {correlation['correlation']['next_day']:.4f}")
    print(f"다음주 상관계수: {correlation['correlation']['next_week']:.4f}")
