"""
개선된 Finnhub와 NewsData.io API를 사용한 뉴스 수집 모듈

레이트 리밋, 재시도 로직, 에러 처리 개선을 통해 안정적인 API 사용을 구현하고,
데이터 정규화 및 중복 제거 기능을 강화했습니다.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
import time
import hashlib
import random
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
import finnhub
from dateutil import parser as dateutil_parser
from rapidfuzz import fuzz

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
env_path = Path(__file__).parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

# 설정 파일 로드
config_path = Path(__file__).parent / 'config.json'
with open(config_path, 'r') as f:
    CONFIG = json.load(f)


class NewsSourcesHandler:
    """
    뉴스 소스 핸들러 클래스
    
    Finnhub와 NewsData.io API를 사용하여 뉴스를 수집하고
    데이터 정규화 및 중복 제거 기능을 제공합니다.
    """
    
    def __init__(self, db_connect: bool = True):
        """
        NewsSourcesHandler 클래스 초기화
        
        Args:
            db_connect: MongoDB 연결 여부 (기본값: True)
        """
        self.config = CONFIG
        
        # API 키 설정
        self.finnhub_api_key = os.getenv("FINNHUB_API_KEY", "")
        self.newsdata_api_key = os.getenv("NEWSDATA_API_KEY", "")
        self.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
        
        # API 클라이언트 초기화
        self.finnhub_client = None
        if self.finnhub_api_key:
            self.finnhub_client = finnhub.Client(api_key=self.finnhub_api_key)
            logger.info("Finnhub API 클라이언트 초기화 성공")
        else:
            logger.warning("FINNHUB_API_KEY 환경 변수가 설정되지 않았습니다.")
        
        # API 레이트 리밋 관리
        self.rate_limits = {
            "finnhub": {
                "requests_per_minute": 30,
                "last_request_time": None,
                "requests_count": 0,
                "reset_time": None
            },
            "newsdata": {
                "requests_per_day": 200,
                "last_request_time": None,
                "requests_count": 0,
                "reset_time": None
            },
            "alpha_vantage": {
                "requests_per_minute": 5,
                "requests_per_day": 500,
                "last_request_time": None,
                "requests_count": 0,
                "reset_time": None
            }
        }
            
        # MongoDB 연결 설정
        if db_connect:
            mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
            mongo_db_name = os.getenv("MONGO_DB_NAME", "jaepa")
            
            try:
                self.client = MongoClient(mongo_uri)
                self.db = self.client[mongo_db_name]
                self.news_collection = self.db[self.config['storage']['mongodb']['news_collection']]
                
                # 인덱스 생성
                self.news_collection.create_index([("url", pymongo.ASCENDING)], unique=True)
                self.news_collection.create_index([("published_date", pymongo.DESCENDING)])
                self.news_collection.create_index([("source", pymongo.ASCENDING)])
                self.news_collection.create_index([("keywords", pymongo.TEXT)])
                
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
        
        # 사용자 에이전트 목록
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
        ]
    
    def _get_random_user_agent(self) -> str:
        """
        랜덤 사용자 에이전트 반환
        
        Returns:
            str: 사용자 에이전트 문자열
        """
        return random.choice(self.user_agents)
    
    def _rate_limit_check(self, api_name: str) -> bool:
        """
        API 레이트 리밋 체크 및 대기
        
        Args:
            api_name: API 이름 (finnhub, newsdata, alpha_vantage)
            
        Returns:
            bool: API 호출 가능 여부
        """
        rate_limit = self.rate_limits.get(api_name)
        if not rate_limit:
            logger.warning(f"알 수 없는 API: {api_name}")
            return True
        
        now = datetime.now()
        
        # 첫 호출인 경우 초기화
        if rate_limit["last_request_time"] is None:
            rate_limit["last_request_time"] = now
            rate_limit["requests_count"] = 1
            rate_limit["reset_time"] = now + timedelta(minutes=1)
            return True
        
        # 일일 제한이 있는 경우 체크
        if "requests_per_day" in rate_limit:
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            if rate_limit["reset_time"] < today_start:
                # 날짜가 바뀌었으면 카운터 리셋
                rate_limit["requests_count"] = 1
                rate_limit["reset_time"] = now + timedelta(minutes=1)
                rate_limit["last_request_time"] = now
                return True
            
            # 일일 제한 초과 시
            if rate_limit["requests_count"] >= rate_limit["requests_per_day"]:
                logger.warning(f"{api_name} API 일일 제한 초과, 내일까지 대기 필요")
                return False
        
        # 분당 제한이 있는 경우 체크
        if "requests_per_minute" in rate_limit:
            minutes_passed = (now - rate_limit["reset_time"]).total_seconds() >= 0
            
            if minutes_passed:
                # 1분이 지났으면 카운터 리셋
                rate_limit["requests_count"] = 1
                rate_limit["reset_time"] = now + timedelta(minutes=1)
                rate_limit["last_request_time"] = now
                return True
            
            # 분당 제한 초과 시
            if rate_limit["requests_count"] >= rate_limit["requests_per_minute"]:
                wait_seconds = (rate_limit["reset_time"] - now).total_seconds()
                if wait_seconds > 0:
                    logger.info(f"{api_name} API 분당 제한 도달, {wait_seconds:.2f}초 대기 중...")
                    time.sleep(wait_seconds + 0.5)  # 안전을 위해 0.5초 추가
                
                # 카운터 리셋
                rate_limit["requests_count"] = 1
                rate_limit["reset_time"] = now + timedelta(minutes=1)
                rate_limit["last_request_time"] = now
                return True
        
        # 레이트 리밋에 걸리지 않은 경우 카운터 증가
        rate_limit["requests_count"] += 1
        rate_limit["last_request_time"] = now
        return True
    
    def _make_request_with_retry(self, url: str, params: Dict = None, headers: Dict = None, 
                                 max_retries: int = 3, backoff_factor: float = 1.5) -> Tuple[int, Optional[str]]:
        """
        지수 백오프 재시도 로직이 포함된 HTTP 요청
        
        Args:
            url: 요청 URL
            params: URL 파라미터
            headers: HTTP 헤더
            max_retries: 최대 재시도 횟수
            backoff_factor: 백오프 계수
            
        Returns:
            Tuple[int, Optional[str]]: 상태 코드와 응답 내용
        """
        if headers is None:
            headers = {
                "User-Agent": self._get_random_user_agent(),
                "Accept": "application/json, text/html",
                "Accept-Language": "en-US,en;q=0.9"
            }
        
        retries = 0
        
        while retries < max_retries:
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    return response.status_code, response.text
                
                elif response.status_code == 429:  # Too Many Requests
                    # 레이트 리밋으로 인한 제한, 백오프 후 재시도
                    wait_time = backoff_factor ** retries
                    logger.warning(f"레이트 리밋 감지, {wait_time:.2f}초 대기 후 재시도 ({retries+1}/{max_retries})")
                    time.sleep(wait_time)
                    retries += 1
                
                else:
                    logger.warning(f"HTTP 오류 ({response.status_code}): {url}")
                    if 400 <= response.status_code < 500:
                        # 클라이언트 오류는 재시도해도 해결되지 않을 수 있음
                        return response.status_code, None
                    
                    # 서버 오류는 백오프 후 재시도
                    wait_time = backoff_factor ** retries
                    logger.warning(f"서버 오류, {wait_time:.2f}초 대기 후 재시도 ({retries+1}/{max_retries})")
                    time.sleep(wait_time)
                    retries += 1
            
            except requests.exceptions.Timeout:
                # 타임아웃 발생 시 백오프 후 재시도
                wait_time = backoff_factor ** retries
                logger.warning(f"요청 타임아웃, {wait_time:.2f}초 대기 후 재시도 ({retries+1}/{max_retries})")
                time.sleep(wait_time)
                retries += 1
            
            except requests.exceptions.RequestException as e:
                logger.error(f"요청 예외 발생: {str(e)}")
                return -1, None
        
        logger.error(f"최대 재시도 횟수 초과: {url}")
        return -1, None
    
    def search_news_with_apis(self, keyword: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        여러 API를 사용한 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            days: 검색할 기간(일)
            
        Returns:
            List[Dict[str, Any]]: 검색된 뉴스 기사 목록
        """
        all_articles = []
        
        # 1. Finnhub API 사용
        if self.finnhub_client and self._rate_limit_check("finnhub"):
            try:
                finnhub_news = self._search_finnhub_news(keyword, days)
                all_articles.extend(finnhub_news)
                logger.info(f"Finnhub API에서 {len(finnhub_news)}개 뉴스 검색됨")
            except Exception as e:
                logger.error(f"Finnhub API 검색 오류: {str(e)}")
        
        # 2. NewsData.io API 사용
        if self.newsdata_api_key and self._rate_limit_check("newsdata"):
            try:
                newsdata_news = self._search_newsdata_news(keyword, days)
                all_articles.extend(newsdata_news)
                logger.info(f"NewsData.io API에서 {len(newsdata_news)}개 뉴스 검색됨")
            except Exception as e:
                logger.error(f"NewsData.io API 검색 오류: {str(e)}")
        
        # 3. Alpha Vantage News API 사용 (있는 경우)
        if self.alpha_vantage_api_key and self._rate_limit_check("alpha_vantage"):
            try:
                alpha_vantage_news = self._search_alpha_vantage_news(keyword, days)
                all_articles.extend(alpha_vantage_news)
                logger.info(f"Alpha Vantage API에서 {len(alpha_vantage_news)}개 뉴스 검색됨")
            except Exception as e:
                logger.error(f"Alpha Vantage API 검색 오류: {str(e)}")
        
        # 중복 제거 및 정렬
        deduplicated_news = self._deduplicate_news(all_articles)
        sorted_news = sorted(deduplicated_news, key=lambda x: x.get("published_date", ""), reverse=True)
        
        return sorted_news
    
    def _search_finnhub_news(self, keyword: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Finnhub API를 사용한 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            days: 검색할 기간(일)
            
        Returns:
            List[Dict[str, Any]]: 검색된 뉴스 기사 목록
        """
        if not self.finnhub_client:
            return []
        
        articles = []
        
        # 1. 키워드가 주식 심볼인 경우 (대부분의 경우)
        try:
            # 시작 및 종료 날짜 설정
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            # 주식 심볼에 대한 뉴스 가져오기
            company_news = self.finnhub_client.company_news(
                keyword.upper(), _from=start_date_str, to=end_date_str
            )
            
            # 뉴스 정규화
            for article in company_news:
                try:
                    normalized = {
                        "title": article.get("headline", ""),
                        "summary": article.get("summary", ""),
                        "content": article.get("summary", ""),  # Finnhub는 전체 내용을 제공하지 않음
                        "url": article.get("url", ""),
                        "published_date": self._format_finnhub_date(article.get("datetime", 0)),
                        "source": article.get("source", "Finnhub"),
                        "source_type": "finnhub",
                        "crawled_date": datetime.now().isoformat(),
                        "related_symbols": article.get("related", []),
                        "categories": article.get("category", "").split(",") if article.get("category") else [],
                        "image_url": article.get("image", None),
                        "keywords": []
                    }
                    
                    # URL이 없는 경우 건너뛰기
                    if not normalized["url"]:
                        continue
                    
                    # 키워드 추출
                    text_for_keywords = normalized["title"] + " " + normalized["summary"]
                    normalized["keywords"] = self._extract_keywords(text_for_keywords)
                    
                    articles.append(normalized)
                except Exception as e:
                    logger.error(f"Finnhub 기사 정규화 중 오류: {str(e)}")
        except Exception as e:
            logger.warning(f"Finnhub company_news API 호출 실패: {str(e)}")
        
        # 2. 일반 뉴스 검색 (키워드 기반으로 필터링)
        try:
            # 일반 뉴스 가져오기
            general_news = self.finnhub_client.general_news("general")
            
            # 키워드로 필터링
            keyword_lower = keyword.lower()
            filtered_news = []
            
            for article in general_news:
                title = article.get("headline", "").lower()
                summary = article.get("summary", "").lower()
                
                if keyword_lower in title or keyword_lower in summary:
                    filtered_news.append(article)
            
            # 뉴스 정규화
            for article in filtered_news:
                try:
                    normalized = {
                        "title": article.get("headline", ""),
                        "summary": article.get("summary", ""),
                        "content": article.get("summary", ""),
                        "url": article.get("url", ""),
                        "published_date": self._format_finnhub_date(article.get("datetime", 0)),
                        "source": article.get("source", "Finnhub"),
                        "source_type": "finnhub",
                        "crawled_date": datetime.now().isoformat(),
                        "related_symbols": article.get("related", []),
                        "categories": article.get("category", "").split(",") if article.get("category") else [],
                        "image_url": article.get("image", None),
                        "keywords": []
                    }
                    
                    # URL이 없는 경우 건너뛰기
                    if not normalized["url"]:
                        continue
                    
                    # 키워드 추출
                    text_for_keywords = normalized["title"] + " " + normalized["summary"]
                    normalized["keywords"] = self._extract_keywords(text_for_keywords)
                    
                    # 중복 방지 (URL 기준)
                    if normalized["url"] not in [a["url"] for a in articles]:
                        articles.append(normalized)
                except Exception as e:
                    logger.error(f"Finnhub 일반 뉴스 정규화 중 오류: {str(e)}")
        except Exception as e:
            logger.warning(f"Finnhub general_news API 호출 실패: {str(e)}")
        
        return articles
    
    def _search_newsdata_news(self, keyword: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        NewsData.io API를 사용한 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            days: 검색할 기간(일)
            
        Returns:
            List[Dict[str, Any]]: 검색된 뉴스 기사 목록
        """
        if not self.newsdata_api_key:
            return []
        
        api_url = "https://newsdata.io/api/1/news"
        
        # 날짜 계산 (NewsData.io는 YYYY-MM-DD 형식 사용)
        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        params = {
            "apikey": self.newsdata_api_key,
            "q": keyword,                   # 검색 키워드
            "language": "en",               # 영어 뉴스만
            "from_date": from_date,         # 시작 날짜
            "category": "business,technology", # 비즈니스 및 기술 카테고리
            "size": 100                     # 한 번에 가져올 최대 기사 수
        }
        
        articles = []
        next_page = None
        max_pages = 5  # 최대 가져올 페이지 수 제한
        page_count = 0
        
        while page_count < max_pages:
            page_count += 1
            
            # 다음 페이지 토큰이 있으면 추가
            if next_page:
                params["page"] = next_page
            
            # API 요청
            status_code, response_text = self._make_request_with_retry(api_url, params=params)
            
            if status_code != 200 or not response_text:
                logger.error(f"NewsData.io API 응답 오류: {status_code}")
                break
            
            try:
                response_data = json.loads(response_text)
                
                if response_data.get("status") != "success" or "results" not in response_data:
                    logger.error(f"NewsData.io API 응답 형식 오류: {response_data.get('message', '알 수 없는 오류')}")
                    break
                
                results = response_data.get("results", [])
                
                if not results:
                    logger.info("NewsData.io API 결과 없음")
                    break
                
                # 뉴스 정규화
                for article in results:
                    try:
                        normalized = {
                            "title": article.get("title", ""),
                            "summary": article.get("description", ""),
                            "content": article.get("content", article.get("description", "")),
                            "url": article.get("link", ""),
                            "published_date": self._format_newsdata_date(article.get("pubDate", "")),
                            "source": article.get("source_id", "NewsData"),
                            "source_type": "newsdata",
                            "crawled_date": datetime.now().isoformat(),
                            "creator": article.get("creator", []),
                            "categories": article.get("category", []),
                            "image_url": article.get("image_url", None),
                            "country": article.get("country", []),
                            "keywords": article.get("keywords", [])
                        }
                        
                        # URL이 없는 경우 건너뛰기
                        if not normalized["url"]:
                            continue
                        
                        # 키워드가 없는 경우 추출
                        if not normalized["keywords"]:
                            text_for_keywords = normalized["title"] + " " + normalized["summary"]
                            normalized["keywords"] = self._extract_keywords(text_for_keywords)
                        
                        articles.append(normalized)
                    except Exception as e:
                        logger.error(f"NewsData.io 기사 정규화 중 오류: {str(e)}")
                
                # 다음 페이지 토큰 확인
                next_page = response_data.get("nextPage")
                if not next_page:
                    break
                
                # API 요청 간 대기 (레이트 리밋 준수)
                time.sleep(1)
            
            except json.JSONDecodeError:
                logger.error(f"NewsData.io API 응답 JSON 파싱 오류")
                break
            except Exception as e:
                logger.error(f"NewsData.io API 처리 중 오류: {str(e)}")
                break
        
        return articles
    
    def _search_alpha_vantage_news(self, keyword: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Alpha Vantage API를 사용한 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            days: 검색할 기간(일)
            
        Returns:
            List[Dict[str, Any]]: 검색된 뉴스 기사 목록
        """
        if not self.alpha_vantage_api_key:
            return []
        
        api_url = "https://www.alphavantage.co/query"
        
        params = {
            "function": "NEWS_SENTIMENT",
            "apikey": self.alpha_vantage_api_key,
            "tickers": keyword.upper(),  # 주식 심볼
            "topics": "financial_markets,technology,economy_macro",  # 토픽
            "time_from": (datetime.now() - timedelta(days=days)).strftime('%Y%m%dT0000'),  # 시작 시간
            "limit": 200  # 최대 기사 수
        }
        
        articles = []
        
        # API 요청
        status_code, response_text = self._make_request_with_retry(api_url, params=params)
        
        if status_code != 200 or not response_text:
            logger.error(f"Alpha Vantage API 응답 오류: {status_code}")
            return []
        
        try:
            response_data = json.loads(response_text)
            
            if "feed" not in response_data:
                logger.error(f"Alpha Vantage API 응답 형식 오류: {response_data.get('Information', '알 수 없는 오류')}")
                return []
            
            feed = response_data.get("feed", [])
            
            if not feed:
                logger.info("Alpha Vantage API 결과 없음")
                return []
            
            # 뉴스 정규화
            for article in feed:
                try:
                    # 기사 발행 시간
                    published_time = article.get("time_published", "")
                    if published_time:
                        try:
                            # 형식: 20231201T0930 (YYYYMMDDThhmm)
                            dt = datetime.strptime(published_time, '%Y%m%dT%H%M')
                            published_date = dt.isoformat()
                        except ValueError:
                            published_date = datetime.now().isoformat()
                    else:
                        published_date = datetime.now().isoformat()
                    
                    # 감성 정보
                    sentiment = article.get("overall_sentiment_score", 0)
                    sentiment_label = article.get("overall_sentiment_label", "neutral")
                    
                    normalized = {
                        "title": article.get("title", ""),
                        "summary": article.get("summary", ""),
                        "content": article.get("summary", ""),
                        "url": article.get("url", ""),
                        "published_date": published_date,
                        "source": article.get("source", "Alpha Vantage"),
                        "source_type": "alpha_vantage",
                        "crawled_date": datetime.now().isoformat(),
                        "categories": [topic["topic"] for topic in article.get("topics", [])],
                        "sentiment_info": {
                            "score": sentiment,
                            "label": sentiment_label
                        },
                        "related_symbols": [ticker["ticker"] for ticker in article.get("ticker_sentiment", [])],
                        "keywords": []
                    }
                    
                    # URL이 없는 경우 건너뛰기
                    if not normalized["url"]:
                        continue
                    
                    # 키워드 추출
                    text_for_keywords = normalized["title"] + " " + normalized["summary"]
                    normalized["keywords"] = self._extract_keywords(text_for_keywords)
                    
                    articles.append(normalized)
                except Exception as e:
                    logger.error(f"Alpha Vantage 기사 정규화 중 오류: {str(e)}")
        
        except json.JSONDecodeError:
            logger.error(f"Alpha Vantage API 응답 JSON 파싱 오류")
        except Exception as e:
            logger.error(f"Alpha Vantage API 처리 중 오류: {str(e)}")
        
        return articles
    
    def get_news_from_finnhub(self, symbol: str = None, category: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """
        Finnhub API에서 뉴스 가져오기 (향상된 버전)
        
        Args:
            symbol: 주식 심볼 (예: 'AAPL', 'TSLA')
            category: 뉴스 카테고리 (None인 경우 general)
            days: 뉴스를 가져올 기간(일)
            
        Returns:
            List[Dict[str, Any]]: 수집된 뉴스 기사 목록
        """
        if not self.finnhub_client:
            logger.error("Finnhub API 클라이언트가 초기화되지 않았습니다.")
            return []
        
        if not self._rate_limit_check("finnhub"):
            logger.error("Finnhub API 레이트 리밋 도달")
            return []
            
        # 시작 및 종료 날짜 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 날짜 형식 변환 (YYYY-MM-DD)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        try:
            # Finnhub API 호출 (재시도 로직 적용)
            retries = 0
            max_retries = 3
            backoff_factor = 1.5
            
            while retries < max_retries:
                try:
                    # Finnhub API 호출
                    if symbol:
                        # 특정 주식 심볼에 대한 뉴스 가져오기
                        news = self.finnhub_client.company_news(symbol, _from=start_date_str, to=end_date_str)
                        logger.info(f"Finnhub API에서 {symbol}에 대한 뉴스 {len(news)}개 가져옴")
                    else:
                        # 일반 뉴스 가져오기
                        news = self.finnhub_client.general_news(category or 'general')
                        logger.info(f"Finnhub API에서 {category or 'general'} 카테고리 뉴스 {len(news)}개 가져옴")
                    
                    break
                except Exception as e:
                    retries += 1
                    wait_time = backoff_factor ** retries
                    logger.warning(f"Finnhub API 호출 실패, {wait_time:.2f}초 대기 후 재시도 ({retries}/{max_retries}): {str(e)}")
                    
                    if retries >= max_retries:
                        logger.error(f"Finnhub API 최대 재시도 횟수 초과")
                        return []
                    
                    time.sleep(wait_time)
            
            # 데이터 정규화
            normalized_news = []
            for article in news:
                try:
                    # 공통 스키마로 변환
                    normalized_article = {
                        "title": article.get("headline", ""),
                        "summary": article.get("summary", ""),
                        "content": article.get("summary", ""),  # Finnhub는 전체 내용을 제공하지 않음
                        "url": article.get("url", ""),
                        "published_date": self._format_finnhub_date(article.get("datetime", 0)),
                        "source": article.get("source", "Finnhub"),
                        "source_type": "finnhub",
                        "crawled_date": datetime.now().isoformat(),
                        "related_symbols": article.get("related", []),
                        "categories": article.get("category", "").split(",") if article.get("category") else [],
                        "image_url": article.get("image", None)
                    }
                    
                    # URL이 없는 경우 건너뛰기
                    if not normalized_article["url"]:
                        continue
                    
                    # 키워드 추출
                    normalized_article["keywords"] = self._extract_keywords(
                        normalized_article["title"] + " " + normalized_article["summary"]
                    )
                    
                    normalized_news.append(normalized_article)
                    
                except Exception as e:
                    logger.error(f"Finnhub 기사 정규화 중 오류: {str(e)}")
            
            return normalized_news
            
        except Exception as e:
            logger.error(f"Finnhub API 호출 중 오류: {str(e)}")
            return []
    
    def get_news_from_newsdata(self, keyword: str = None, category: str = None, country: str = 'us', days: int = 7) -> List[Dict[str, Any]]:
        """
        NewsData.io API에서 뉴스 가져오기 (향상된 버전)
        
        Args:
            keyword: 검색 키워드
            category: 뉴스 카테고리 (business, entertainment, health, science, sports, technology)
            country: 국가 코드 (기본값: 'us')
            days: 뉴스를 가져올 기간(일)
            
        Returns:
            List[Dict[str, Any]]: 수집된 뉴스 기사 목록
        """
        if not self.newsdata_api_key:
            logger.error("NewsData.io API 키가 설정되지 않았습니다.")
            return []
        
        if not self._rate_limit_check("newsdata"):
            logger.error("NewsData.io API 레이트 리밋 도달")
            return []
            
        api_url = "https://newsdata.io/api/1/news"
        
        # 날짜 계산 (NewsData.io는 다른 날짜 형식 사용)
        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        params = {
            "apikey": self.newsdata_api_key,
            "country": country,
            "language": "en",
            "from_date": from_date
        }
        
        # 카테고리 추가 (선택적)
        if category:
            params["category"] = category
            
        # 키워드 추가 (선택적)
        if keyword:
            params["q"] = keyword
            
        all_articles = []
        page = 1
        max_pages = 10  # 최대 페이지 수 제한
        
        try:
            while page <= max_pages:
                if next_page:
                    params["page"] = next_page
                
                # API 요청 (재시도 로직 사용)
                status_code, response_text = self._make_request_with_retry(api_url, params=params)
                
                if status_code != 200 or not response_text:
                    logger.error(f"NewsData.io API 응답 오류: {status_code}")
                    break
                
                try:
                    data = json.loads(response_text)
                except json.JSONDecodeError:
                    logger.error("NewsData.io API 응답 JSON 파싱 오류")
                    break
                
                if "results" not in data or not data["results"]:
                    logger.info("NewsData.io API에서 더 이상 결과가 없습니다.")
                    break
                    
                articles = data["results"]
                logger.info(f"NewsData.io API에서 페이지 {page}, 뉴스 {len(articles)}개 가져옴")
                
                # 데이터 정규화
                for article in articles:
                    try:
                        # 공통 스키마로 변환
                        normalized_article = {
                            "title": article.get("title", ""),
                            "summary": article.get("description", ""),
                            "content": article.get("content", article.get("description", "")),
                            "url": article.get("link", ""),
                            "published_date": self._format_newsdata_date(article.get("pubDate", "")),
                            "source": article.get("source_id", "NewsData.io"),
                            "source_type": "newsdata",
                            "crawled_date": datetime.now().isoformat(),
                            "creator": article.get("creator", None),
                            "categories": article.get("category", []),
                            "image_url": article.get("image_url", None),
                            "country": article.get("country", [])
                        }
                        
                        # URL이 없는 경우 건너뛰기
                        if not normalized_article["url"]:
                            continue
                        
                        # 키워드 추출
                        normalized_article["keywords"] = article.get("keywords", []) or self._extract_keywords(
                            normalized_article["title"] + " " + normalized_article["summary"]
                        )
                        
                        all_articles.append(normalized_article)
                        
                    except Exception as e:
                        logger.error(f"NewsData.io 기사 정규화 중 오류: {str(e)}")
                
                # 다음 페이지 토큰 확인
                next_page = data.get("nextPage")
                if not next_page:
                    logger.info("NewsData.io API에서 다음 페이지가 없습니다.")
                    break
                    
                page += 1
                
                # API 요청 간 대기 (레이트 리밋 준수)
                time.sleep(1.5)
                
            return all_articles
            
        except Exception as e:
            logger.error(f"NewsData.io API 호출 중 오류: {str(e)}")
            return []
    
    def get_combined_news(self, keyword: str = None, days: int = 7, save_to_db: bool = True) -> List[Dict[str, Any]]:
        """
        여러 API에서 뉴스를 가져와 통합하기 (향상된 버전)
        
        Args:
            keyword: 검색 키워드
            days: 뉴스를 가져올 기간(일)
            save_to_db: MongoDB에 저장 여부
            
        Returns:
            List[Dict[str, Any]]: 통합된 뉴스 기사 목록
        """
        # 키워드 자체 처리로 통합 검색 지원
        if keyword:
            all_news = self.search_news_with_apis(keyword, days)
        else:
            # 기존 메서드 사용 (키워드 없는 경우)
            # Finnhub에서 뉴스 가져오기
            finnhub_news = []
            if self.finnhub_client and self._rate_limit_check("finnhub"):
                finnhub_news = self.get_news_from_finnhub(days=days)
            
            # NewsData.io에서 뉴스 가져오기
            newsdata_news = []
            if self.newsdata_api_key and self._rate_limit_check("newsdata"):
                category = "business"  # 비즈니스 카테고리 기본 설정
                newsdata_news = self.get_news_from_newsdata(category=category, days=days)
            
            # 뉴스 통합
            all_news = finnhub_news + newsdata_news
        
        # 중복 제거
        deduplicated_news = self._deduplicate_news(all_news)
        
        # MongoDB에 저장
        if save_to_db and self.news_collection is not None:
            self._save_to_mongodb(deduplicated_news)
        
        return deduplicated_news
    
    def _format_finnhub_date(self, timestamp: int) -> str:
        """
        Finnhub 타임스탬프를 ISO 형식 날짜로 변환
        
        Args:
            timestamp: 유닉스 타임스탬프
            
        Returns:
            str: ISO 형식 날짜 문자열
        """
        try:
            # Finnhub는 유닉스 타임스탬프 사용 (초 단위)
            dt = datetime.fromtimestamp(timestamp)
            return dt.isoformat()
        except Exception as e:
            logger.error(f"날짜 변환 중 오류 (Finnhub): {str(e)}")
            return datetime.now().isoformat()
    
    def _format_newsdata_date(self, date_str: str) -> str:
        """
        NewsData.io 날짜를 ISO 형식으로 변환
        
        Args:
            date_str: 날짜 문자열
            
        Returns:
            str: ISO 형식 날짜 문자열
        """
        try:
            # NewsData.io는 다양한 날짜 형식 사용 (예: "2023-04-05 12:34:56")
            dt = dateutil_parser.parse(date_str)
            return dt.isoformat()
        except Exception as e:
            logger.error(f"날짜 변환 중 오류 (NewsData.io): {str(e)}")
            return datetime.now().isoformat()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        텍스트에서 키워드 추출
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            List[str]: 추출된 키워드 목록
        """
        # 불용어 정의
        stopwords = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", 
                     "for", "with", "by", "of", "is", "are", "was", "were", "be", "been",
                     "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they"}
        
        # 텍스트 전처리
        import re
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)  # 영문자와 공백만 유지
        words = text.split()
        
        # 불용어 제거 및 빈도수 계산
        word_freq = {}
        for word in words:
            if word not in stopwords and len(word) > 3:  # 3글자 이상 단어만 포함
                word_freq[word] = word_freq.get(word, 0) + 1
                
        # 빈도수 기준 상위 10개 키워드 반환
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_keywords[:10]]
    
    def _calculate_text_hash(self, text: str) -> str:
        """
        텍스트의 해시값 계산
        
        Args:
            text: 계산할 텍스트
            
        Returns:
            str: 텍스트 해시값
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _deduplicate_news(self, articles: List[Dict[str, Any]], title_threshold: int = 90, time_threshold: int = 300) -> List[Dict[str, Any]]:
        """
        뉴스 기사 중복 제거
        
        Args:
            articles: 뉴스 기사 목록
            title_threshold: 제목 유사도 기준 (0-100)
            time_threshold: 발행 시간 간격 기준 (초)
            
        Returns:
            List[Dict[str, Any]]: 중복 제거된 뉴스 기사 목록
        """
        if not articles:
            return []
            
        logger.info(f"중복 제거 전 기사 수: {len(articles)}")
        
        # URL 기반 중복 확인을 위한 사전
        url_dict = {}
        
        # 최종 결과 리스트
        final_articles = []
        
        # 제목 기반 유사도 체크를 위한 사전
        title_hash_dict = {}
        
        # 기사 정렬 (발행 시간 기준)
        sorted_articles = sorted(articles, key=lambda x: x.get("published_date", ""), reverse=True)
        
        for article in sorted_articles:
            url = article.get("url", "")
            title = article.get("title", "").lower()
            
            # URL이 없는 경우 건너뛰기
            if not url:
                continue
                
            # URL 기반 중복 체크
            if url in url_dict:
                logger.debug(f"URL 중복 발견: {url}")
                
                # 소스 정보 추가
                source_info = article.get("source", "Unknown")
                if source_info not in url_dict[url]["sources"]:
                    url_dict[url]["sources"].append(source_info)
                
                # 카테고리 병합
                if "categories" in article and article["categories"]:
                    url_dict[url]["categories"].extend(article.get("categories", []))
                    url_dict[url]["categories"] = list(set(url_dict[url]["categories"]))
                
                # 키워드 병합
                if "keywords" in article and article["keywords"]:
                    url_dict[url]["keywords"].extend(article.get("keywords", []))
                    url_dict[url]["keywords"] = list(set(url_dict[url]["keywords"]))
                
                continue
                
            # 제목 기반 유사도 및 시간 간격 체크
            title_hash = self._calculate_text_hash(title)
            is_duplicate = False
            
            for saved_hash, saved_article in title_hash_dict.items():
                saved_title = saved_article.get("title", "").lower()
                
                # 제목 유사도 계산
                title_similarity = fuzz.ratio(title, saved_title)
                
                if title_similarity >= title_threshold:
                    # 발행 시간 간격 확인
                    try:
                        article_time = dateutil_parser.parse(article.get("published_date", ""))
                        saved_time = dateutil_parser.parse(saved_article.get("published_date", ""))
                        time_diff = abs((article_time - saved_time).total_seconds())
                        
                        if time_diff <= time_threshold:
                            # 중복 기사로 판단
                            logger.debug(f"제목 유사성 및 시간 간격 기준 중복 발견: {title} ({title_similarity}%, {time_diff}초)")
                            is_duplicate = True
                            
                            # 소스 정보 추가
                            source_info = article.get("source", "Unknown")
                            if "sources" not in saved_article:
                                saved_article["sources"] = [saved_article.get("source", "Unknown")]
                            
                            if source_info not in saved_article["sources"]:
                                saved_article["sources"].append(source_info)
                            
                            # 카테고리 병합
                            if "categories" in article and article["categories"]:
                                if "categories" not in saved_article:
                                    saved_article["categories"] = []
                                saved_article["categories"].extend(article.get("categories", []))
                                saved_article["categories"] = list(set(saved_article["categories"]))
                            
                            # 키워드 병합
                            if "keywords" in article and article["keywords"]:
                                if "keywords" not in saved_article:
                                    saved_article["keywords"] = []
                                saved_article["keywords"].extend(article.get("keywords", []))
                                saved_article["keywords"] = list(set(saved_article["keywords"]))
                            
                            break
                    except Exception as e:
                        logger.error(f"시간 간격 계산 중 오류: {str(e)}")
            
            if not is_duplicate:
                # 중복이 아닌 경우 추가
                url_dict[url] = article
                title_hash_dict[title_hash] = article
                
                # 소스 정보 추가
                if "sources" not in article:
                    article["sources"] = [article.get("source", "Unknown")]
                
                final_articles.append(article)
        
        logger.info(f"중복 제거 후 기사 수: {len(final_articles)}")
        return final_articles
    
    def _save_to_mongodb(self, articles: List[Dict[str, Any]]) -> None:
        """
        뉴스 기사를 MongoDB에 저장
        
        Args:
            articles: 저장할 뉴스 기사 목록
        """
        if not self.news_collection:
            logger.warning("MongoDB 연결이 없어 저장할 수 없습니다.")
            return
            
        saved_count = 0
        duplicate_count = 0
        
        for article in articles:
            try:
                # URL 기반으로 중복 체크 후 저장 또는 업데이트
                url = article.get("url", "")
                
                # URL이 없는 경우 건너뛰기
                if not url:
                    continue
                    
                existing_article = self.news_collection.find_one({"url": url})
                
                if existing_article:
                    # 기존 기사가 있는 경우 업데이트
                    update_data = {}
                    
                    # 소스 정보 업데이트
                    if "sources" in article and article["sources"]:
                        existing_sources = existing_article.get("sources", [])
                        if not existing_sources:
                            existing_sources = [existing_article.get("source", "Unknown")]
                            
                        for source in article["sources"]:
                            if source not in existing_sources:
                                existing_sources.append(source)
                                
                        update_data["sources"] = existing_sources
                    
                    # 카테고리 업데이트
                    if "categories" in article and article["categories"]:
                        existing_categories = existing_article.get("categories", [])
                        for category in article["categories"]:
                            if category not in existing_categories:
                                existing_categories.append(category)
                                
                        update_data["categories"] = existing_categories
                    
                    # 키워드 업데이트
                    if "keywords" in article and article["keywords"]:
                        existing_keywords = existing_article.get("keywords", [])
                        for keyword in article["keywords"]:
                            if keyword not in existing_keywords:
                                existing_keywords.append(keyword)
                                
                        update_data["keywords"] = existing_keywords
                    
                    # 업데이트할 데이터가 있는 경우에만 업데이트
                    if update_data:
                        self.news_collection.update_one({"url": url}, {"$set": update_data})
                        logger.debug(f"기존 기사 업데이트됨: {url}")
                        
                    duplicate_count += 1
                else:
                    # 새 기사 저장
                    self.news_collection.insert_one(article)
                    logger.debug(f"새 기사 저장됨: {url}")
                    saved_count += 1
                    
            except pymongo.errors.DuplicateKeyError:
                logger.debug(f"중복 기사 (DB에서 확인됨): {article.get('url', '')}")
                duplicate_count += 1
            except Exception as e:
                logger.error(f"기사 저장 중 오류: {str(e)}")
        
        logger.info(f"MongoDB 저장 결과: 새 기사 {saved_count}개, 중복/업데이트 {duplicate_count}개")
    
    def close(self):
        """
        MongoDB 연결 종료
        """
        if self.client:
            self.client.close()
            logger.info("MongoDB 연결 종료")


if __name__ == "__main__":
    # 직접 실행 시 간단한 테스트 코드
    handler = NewsSourcesHandler(db_connect=False)
    
    # API 기반 검색 테스트
    keyword = "AAPL"
    search_results = handler.search_news_with_apis(keyword, days=3)
    
    print(f"\n'{keyword}' 검색 결과:")
    for i, article in enumerate(search_results[:5]):  # 처음 5개만 출력
        print(f"\n기사 #{i+1}")
        print(f"제목: {article['title']}")
        print(f"날짜: {article['published_date']}")
        print(f"URL: {article['url']}")
        print(f"출처: {article.get('source', 'Unknown')} ({article.get('source_type', 'unknown')})")
        if 'sources' in article:
            print(f"통합된 출처: {', '.join(article['sources'])}")
        print(f"키워드: {', '.join(article.get('keywords', []))}")
        print("-" * 50)
    
    print(f"총 {len(search_results)}개 기사가 검색되었습니다.")
    
    handler.close()
