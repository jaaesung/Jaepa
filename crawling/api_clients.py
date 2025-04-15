"""
API 클라이언트 모듈

여러 API 서비스에 대한 통합 클라이언트 제공
"""

import os
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

import finnhub
import requests
from dotenv import load_dotenv

from crawling.enhanced_request import make_request_with_retry, get_random_user_agent

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

class FinnhubClient:
    """Finnhub API 클라이언트"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Finnhub API 클라이언트 초기화

        Args:
            api_key: Finnhub API 키 (없으면 환경 변수에서 로드)
        """
        self.api_key = api_key or os.getenv("FINNHUB_API_KEY")
        self.client = None

        if self.api_key:
            try:
                self.client = finnhub.Client(api_key=self.api_key)
                logger.info("Finnhub API 클라이언트 초기화 성공")
            except Exception as e:
                logger.error(f"Finnhub API 클라이언트 초기화 실패: {str(e)}")
        else:
            logger.warning("Finnhub API 키가 설정되지 않았습니다.")

    def company_news(self, symbol: str, _from: str, to: str) -> List[Dict[str, Any]]:
        """
        특정 기업의 뉴스 가져오기

        Args:
            symbol: 주식 심볼
            _from: 시작 날짜 (YYYY-MM-DD)
            to: 종료 날짜 (YYYY-MM-DD)

        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        if not self.client:
            logger.warning("Finnhub API 클라이언트가 초기화되지 않았습니다.")
            return []

        try:
            news = self.client.company_news(symbol, _from=_from, to=to)
            logger.info(f"Finnhub API에서 {symbol}에 대한 뉴스 {len(news)}개 가져옴")
            return news
        except Exception as e:
            logger.error(f"Finnhub company_news API 호출 중 오류: {str(e)}")
            return []

    def general_news(self, category: str, min_id: int = 0) -> List[Dict[str, Any]]:
        """
        일반 뉴스 가져오기

        Args:
            category: 뉴스 카테고리 (general, forex, crypto, merger)
            min_id: 최소 뉴스 ID

        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        if not self.client:
            logger.warning("Finnhub API 클라이언트가 초기화되지 않았습니다.")
            return []

        try:
            news = self.client.general_news(category, min_id=min_id)
            logger.info(f"Finnhub API에서 {category} 카테고리 뉴스 {len(news)}개 가져옴")
            return news
        except Exception as e:
            logger.error(f"Finnhub general_news API 호출 중 오류: {str(e)}")
            return []

    def format_date(self, timestamp: int) -> str:
        """
        Finnhub 타임스탬프를 ISO 형식으로 변환

        Args:
            timestamp: Unix 타임스탬프

        Returns:
            str: ISO 형식 날짜 문자열
        """
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.isoformat()
        except Exception as e:
            logger.error(f"날짜 변환 중 오류 (Finnhub): {str(e)}")
            return datetime.now().isoformat()


class NewsDataClient:
    """NewsData.io API 클라이언트"""

    def __init__(self, api_key: Optional[str] = None):
        """
        NewsData.io API 클라이언트 초기화

        Args:
            api_key: NewsData.io API 키 (없으면 환경 변수에서 로드)
        """
        self.api_key = api_key or os.getenv("NEWSDATA_API_KEY")
        self.base_url = "https://newsdata.io/api/1/news"

        if not self.api_key:
            logger.warning("NewsData.io API 키가 설정되지 않았습니다.")

    def search_news(self, keyword: str, language: str = "en",
                   days: int = 7, page: Optional[str] = None) -> Dict[str, Any]:
        """
        키워드로 뉴스 검색

        Args:
            keyword: 검색 키워드
            language: 언어 코드
            days: 검색할 기간(일)
            page: 페이지 토큰

        Returns:
            Dict[str, Any]: 검색 결과
        """
        if not self.api_key:
            logger.warning("NewsData.io API 키가 설정되지 않았습니다.")
            return {"status": "error", "results": []}

        # 날짜 범위 계산
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # API 파라미터 설정
        params = {
            "apikey": self.api_key,
            "q": keyword,
            "language": language,
            "from_date": start_date.strftime("%Y-%m-%d"),
            "to_date": end_date.strftime("%Y-%m-%d"),
            "size": 10  # 한 번에 가져올 결과 수
        }

        # 페이지 토큰이 있으면 추가
        if page:
            params["page"] = page

        try:
            # API 요청
            status_code, response_text = make_request_with_retry(self.base_url, params=params)

            if status_code != 200 or not response_text:
                logger.error(f"NewsData.io API 응답 오류: {status_code}")
                return {"status": "error", "results": []}

            # JSON 파싱
            import json
            response = json.loads(response_text)

            if response.get("status") != "success":
                logger.error(f"NewsData.io API 응답 실패: {response.get('results', {}).get('message', '알 수 없는 오류')}")
                return {"status": "error", "results": []}

            logger.info(f"NewsData.io API에서 {keyword}에 대한 뉴스 {len(response.get('results', []))}개 가져옴")
            return response

        except Exception as e:
            logger.error(f"NewsData.io API 호출 중 오류: {str(e)}")
            return {"status": "error", "results": []}

    def format_date(self, date_str: str) -> str:
        """
        NewsData.io 날짜 문자열을 ISO 형식으로 변환

        Args:
            date_str: 날짜 문자열

        Returns:
            str: ISO 형식 날짜 문자열
        """
        try:
            from dateutil import parser as dateutil_parser
            dt = dateutil_parser.parse(date_str)
            return dt.isoformat()
        except Exception as e:
            logger.error(f"날짜 변환 중 오류 (NewsData.io): {str(e)}")
            return datetime.now().isoformat()


class AlphaVantageClient:
    """Alpha Vantage API 클라이언트"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Alpha Vantage API 클라이언트 초기화

        Args:
            api_key: Alpha Vantage API 키 (없으면 환경 변수에서 로드)
        """
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"

        if not self.api_key:
            logger.warning("Alpha Vantage API 키가 설정되지 않았습니다.")

    def news_sentiment(self, tickers: Optional[str] = None, topics: Optional[str] = None,
                      time_from: Optional[str] = None, time_to: Optional[str] = None,
                      limit: int = 50) -> Dict[str, Any]:
        """
        뉴스 감성 분석 데이터 가져오기

        Args:
            tickers: 주식 심볼 (쉼표로 구분)
            topics: 토픽 (쉼표로 구분)
            time_from: 시작 시간 (YYYYMMDDTHHMM 형식)
            time_to: 종료 시간 (YYYYMMDDTHHMM 형식)
            limit: 결과 제한 수

        Returns:
            Dict[str, Any]: 뉴스 감성 분석 결과
        """
        if not self.api_key:
            logger.warning("Alpha Vantage API 키가 설정되지 않았습니다.")
            return {"feed": []}

        # API 파라미터 설정
        params = {
            "function": "NEWS_SENTIMENT",
            "apikey": self.api_key,
            "limit": limit
        }

        if tickers:
            params["tickers"] = tickers

        if topics:
            params["topics"] = topics

        if time_from:
            params["time_from"] = time_from

        if time_to:
            params["time_to"] = time_to

        try:
            # API 요청
            status_code, response_text = make_request_with_retry(self.base_url, params=params)

            if status_code != 200 or not response_text:
                logger.error(f"Alpha Vantage API 응답 오류: {status_code}")
                return {"feed": []}

            # JSON 파싱
            import json
            response = json.loads(response_text)

            if "feed" not in response:
                logger.error(f"Alpha Vantage API 응답 형식 오류: {response.get('Information', '알 수 없는 오류')}")
                return {"feed": []}

            logger.info(f"Alpha Vantage API에서 뉴스 {len(response.get('feed', []))}개 가져옴")
            return response

        except Exception as e:
            logger.error(f"Alpha Vantage API 호출 중 오류: {str(e)}")
            return {"feed": []}

    def format_date(self, date_str: str) -> str:
        """
        Alpha Vantage 날짜 문자열을 ISO 형식으로 변환

        Args:
            date_str: 날짜 문자열

        Returns:
            str: ISO 형식 날짜 문자열
        """
        try:
            from dateutil import parser as dateutil_parser
            dt = dateutil_parser.parse(date_str)
            return dt.isoformat()
        except Exception as e:
            logger.error(f"날짜 변환 중 오류 (Alpha Vantage): {str(e)}")
            return datetime.now().isoformat()
