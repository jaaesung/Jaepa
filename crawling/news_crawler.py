"""
뉴스 크롤링 모듈

금융 뉴스 사이트에서 기사를 수집하고, 감성 분석을 수행하는 모듈입니다.
"""
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import feedparser
import requests
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import pandas as pd

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


class NewsCrawler:
    """
    금융 뉴스 크롤링 클래스

    금융 뉴스 웹사이트에서 기사를 수집하고 저장합니다.
    """

    def __init__(self, db_connect: bool = True):
        """
        NewsCrawler 클래스 초기화

        Args:
            db_connect: MongoDB 연결 여부 (기본값: True)
        """
        self.config = CONFIG
        self.sources = self.config['news_sources']
        self.rss_feeds = self.config['rss_feeds']
        self.request_settings = self.config['request_settings']
        self.rate_limits = self.config['rate_limits']

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
            
        # 감성 분석기 초기화
        self.sentiment_analyzer = None

    def _get_request_headers(self) -> Dict[str, str]:
        """
        HTTP 요청 헤더 생성

        Returns:
            Dict[str, str]: HTTP 헤더 사전
        """
        headers = self.request_settings['headers'].copy()
        headers['User-Agent'] = self.request_settings['user_agent']
        return headers

    def _make_request(self, url: str) -> Optional[str]:
        """
        HTTP GET 요청 실행

        Args:
            url: 요청할 URL

        Returns:
            Optional[str]: HTML 응답 또는 None (실패 시)
        """
        headers = self._get_request_headers()
        proxies = {"http": self.request_settings['proxy'], "https": self.request_settings['proxy']} \
            if self.request_settings['proxy'] else None
        
        for attempt in range(self.request_settings['retries'] + 1):
            try:
                response = requests.get(
                    url, 
                    headers=headers,
                    proxies=proxies,
                    timeout=self.request_settings['timeout']
                )
                
                if response.status_code == 200:
                    return response.text
                else:
                    logger.warning(f"HTTP 오류 ({response.status_code}): {url}")
                    
            except requests.RequestException as e:
                logger.error(f"요청 실패 ({attempt+1}/{self.request_settings['retries']+1}): {url} - {str(e)}")
                
            # 재시도 전 대기
            if attempt < self.request_settings['retries']:
                time.sleep(self.request_settings['retry_delay'])
                
        return None

    def search_news(self, keyword: str, days: int = 7, sources: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        키워드로 뉴스 검색 (삭제 예정: RSS 피드 기반 검색으로 대체)
        
        이 함수는 더 이상 사용되지 않으며, 대신 search_news_from_rss 함수를 사용하세요.

        Args:
            keyword: 검색 키워드
            days: 검색할 기간(일)
            sources: 뉴스 소스 목록 (None인 경우 모든 소스)

        Returns:
            List[Dict[str, Any]]: 수집된 뉴스 기사 목록
        """
        logger.warning("search_news 함수는 더 이상 사용되지 않습니다. 대신 search_news_from_rss 함수를 사용하세요.")
        return self.search_news_from_rss(keyword, days, sources)

    def get_latest_news(self, sources: Optional[List[str]] = None, count: int = 5) -> List[Dict[str, Any]]:
        """
        최신 뉴스 수집 (삭제 예정: RSS 피드 기반 검색으로 대체)
        
        이 함수는 더 이상 사용되지 않으며, 대신 get_news_from_rss 함수를 사용하세요.

        Args:
            sources: 뉴스 소스 목록 (None인 경우 모든 소스)
            count: 각 소스별 수집할 기사 수

        Returns:
            List[Dict[str, Any]]: 수집된 최신 뉴스 기사 목록
        """
        logger.warning("get_latest_news 함수는 더 이상 사용되지 않습니다. 대신 get_news_from_rss 함수를 사용하세요.")
        return self.get_news_from_rss(sources, count)

    def _scrape_article(self, url: str, source_name: str) -> Optional[Dict[str, Any]]:
        """
        기사 내용 스크래핑

        Args:
            url: 기사 URL
            source_name: 뉴스 소스 이름

        Returns:
            Optional[Dict[str, Any]]: 기사 정보 또는 None (실패 시)
        """
        source_config = self.sources[source_name]
        
        html = self._make_request(url)
        if not html:
            logger.error(f"기사를 가져오지 못했습니다: {url}")
            return None
            
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 제목 추출
            title = soup.title.text.strip() if soup.title else ""
            
            # 내용 추출
            content_elements = soup.select(source_config['content_selector'])
            content = ' '.join([p.text.strip() for p in content_elements])
            
            # 날짜 추출
            date_element = soup.select_one(source_config['date_selector'])
            published_date = None
            
            if date_element:
                date_text = date_element.text.strip()
                try:
                    date_obj = datetime.strptime(date_text, source_config['date_format'])
                    published_date = date_obj.isoformat()
                except Exception as e:
                    logger.warning(f"날짜 파싱 실패: {date_text} - {str(e)}")
                    published_date = datetime.now().isoformat()
            else:
                published_date = datetime.now().isoformat()
                
            # 키워드 추출 (간단한 구현)
            keywords = self._extract_keywords(title + " " + content)
            
            # 감성 분석
            sentiment = None
            if self.sentiment_analyzer:
                sentiment = self.sentiment_analyzer.analyze(content)
                
            article_data = {
                "url": url,
                "title": title,
                "content": content,
                "source": source_name,
                "published_date": published_date,
                "crawled_date": datetime.now().isoformat(),
                "keywords": keywords,
                "sentiment": sentiment
            }
            
            return article_data
            
        except Exception as e:
            logger.error(f"기사 파싱 중 오류: {url} - {str(e)}")
            return None

    def _extract_keywords(self, text: str) -> List[str]:
        """
        텍스트에서 키워드 추출 (간단한 구현)

        Args:
            text: 분석할 텍스트

        Returns:
            List[str]: 추출된 키워드 목록
        """
        # 불용어 정의 (필요에 따라 확장)
        stopwords = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "of", "is", "are", "was", "were"}
        
        # 텍스트 전처리
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

    def initialize_sentiment_analyzer(self):
        """
        감성 분석기 초기화
        """
        self.sentiment_analyzer = SentimentAnalyzer()

    def _process_nasdaq_rss(self, entry, source_name):
        """
        Nasdaq RSS 피드에 특화된 처리
        """
        # Nasdaq의 경우 title에 대대문자로 된 제목이 있을 수 있음
        title = entry.title.strip()
        
        # Nasdaq의 경우 'mediaImage' 속성이 있는지 확인
        image_url = None
        if hasattr(entry, 'mediaImage'):
            image_url = entry.mediaImage
        
        # 날짜 파싱 - Nasdaq은 published_parsed를 주로 사용
        published_date = datetime.now().isoformat()
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published_date = datetime(*entry.published_parsed[:6]).isoformat()
        
        # 내용 추출
        content = ""
        # Nasdaq은 주로 summary에 내용이 있음
        if hasattr(entry, 'summary') and entry.summary:
            content = entry.summary
        
        return {
            "title": title,
            "content": BeautifulSoup(content, 'html.parser').get_text(),
            "published_date": published_date,
            "image_url": image_url,
            "source": source_name,
            "source_type": "rss"
        }
        
    def _process_coindesk_rss(self, entry, source_name):
        """
        CoinDesk RSS 피드에 특화된 처리
        """
        # CoinDesk는 content 필드에 내용이 있을 수 있음
        content = ""
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value
        elif hasattr(entry, 'summary') and entry.summary:
            content = entry.summary
        
        # 날짜 파싱 - CoinDesk는 주로 published_parsed 사용
        published_date = datetime.now().isoformat()
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published_date = datetime(*entry.published_parsed[:6]).isoformat()
        
        # 저자 정보 추출
        author = None
        if hasattr(entry, 'author'):
            author = entry.author
        
        return {
            "title": entry.title.strip(),
            "content": BeautifulSoup(content, 'html.parser').get_text(),
            "published_date": published_date,
            "author": author,
            "source": source_name,
            "source_type": "rss"
        }
        
    def _process_cointelegraph_rss(self, entry, source_name):
        """
        CoinTelegraph RSS 피드에 특화된 처리
        """
        # CoinTelegraph는 description에 내용이 있을 수 있음
        content = ""
        if hasattr(entry, 'description') and entry.description:
            content = entry.description
        
        # 날짜 파싱 - CoinTelegraph는 주로 published_parsed 사용
        published_date = datetime.now().isoformat()
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published_date = datetime(*entry.published_parsed[:6]).isoformat()
        
        # 카테고리 정보 추출
        categories = []
        if hasattr(entry, 'tags'):
            categories = [tag.term for tag in entry.tags]
        
        return {
            "title": entry.title.strip(),
            "content": BeautifulSoup(content, 'html.parser').get_text(),
            "published_date": published_date,
            "categories": categories,
            "source": source_name,
            "source_type": "rss"
        }
        
    def _process_investing_rss(self, entry, source_name):
        """
        Investing.com RSS 피드에 특화된 처리
        """
        # Investing.com은 description에 내용이 있을 수 있음
        content = ""
        if hasattr(entry, 'description') and entry.description:
            content = entry.description
        
        # 날짜 파싱 - Investing.com은 published_parsed 사용
        published_date = datetime.now().isoformat()
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published_date = datetime(*entry.published_parsed[:6]).isoformat()
        
        return {
            "title": entry.title.strip(),
            "content": BeautifulSoup(content, 'html.parser').get_text(),
            "published_date": published_date,
            "source": source_name,
            "source_type": "rss"
        }
        
    def _process_generic_rss(self, entry, source_name):
        """
        일반적인 RSS 피드 처리
        """
        # 날짜 파싱
        published_date = datetime.now().isoformat()
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published_date = datetime(*entry.published_parsed[:6]).isoformat()
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            published_date = datetime(*entry.updated_parsed[:6]).isoformat()
        
        # 내용 추출
        content = ""
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value
        elif hasattr(entry, 'summary') and entry.summary:
            content = entry.summary
        elif hasattr(entry, 'description') and entry.description:
            content = entry.description
        
        return {
            "title": entry.title.strip(),
            "content": BeautifulSoup(content, 'html.parser').get_text(),
            "published_date": published_date,
            "source": source_name,
            "source_type": "rss"
        }
    
    def get_news_from_rss(self, sources: Optional[List[str]] = None, count: int = 10) -> List[Dict[str, Any]]:
        """
        RSS 피드에서 최신 뉴스 가져오기

        Args:
            sources: RSS 소스 목록 (None인 경우 모든 소스)
            count: 각 소스별 가져올 기사 수

        Returns:
            List[Dict[str, Any]]: 수집된 뉴스 기사 목록
        """
        if sources is None:
            sources = list(self.rss_feeds.keys())
        else:
            # 존재하지 않는 소스 필터링
            sources = [s for s in sources if s in self.rss_feeds]
            
        if not sources:
            logger.warning("유효한 RSS 피드가 지정되지 않았습니다.")
            return []
            
        all_articles = []
        
        # 소스별 처리 함수 매핑
        source_processors = {
            "nasdaq": self._process_nasdaq_rss,
            "coindesk": self._process_coindesk_rss,
            "cointelegraph": self._process_cointelegraph_rss,
            "investing": self._process_investing_rss
        }
        
        for source_id in sources:
            source_config = self.rss_feeds[source_id]
            source_name = source_config['name']
            rss_url = source_config['url']
            
            logger.info(f"{source_name} RSS 피드에서 뉴스 가져오는 중: {rss_url}")
            
            try:
                # RSS 피드 파싱 (타임아웃 설정을 위해 requests로 먼저 가져오기)
                try:
                    response = requests.get(rss_url, timeout=10)
                    if response.status_code != 200:
                        # Nasdaq의 경우 fallback URL 사용 시도
                        if source_id == "nasdaq" and "fallback_url" in source_config:
                            logger.warning(f"Nasdaq RSS 기본 URL 실패, fallback URL 시도: {source_config['fallback_url']}")
                            fallback_response = requests.get(source_config['fallback_url'], timeout=10)
                            if fallback_response.status_code == 200:
                                feed = feedparser.parse(fallback_response.content)
                            else:
                                logger.error(f"{source_name} RSS fallback URL 접근 실패. 상태 코드: {fallback_response.status_code}")
                                continue
                        else:
                            logger.error(f"{source_name} RSS 피드 접근 실패. 상태 코드: {response.status_code}")
                            continue
                    else:
                        feed = feedparser.parse(response.content)
                except requests.exceptions.Timeout:
                    # Nasdaq의 경우 fallback URL 사용 시도
                    if source_id == "nasdaq" and "fallback_url" in source_config:
                        try:
                            logger.warning(f"Nasdaq RSS 기본 URL 타임아웃, fallback URL 시도: {source_config['fallback_url']}")
                            fallback_response = requests.get(source_config['fallback_url'], timeout=15)  # 타임아웃 증가
                            if fallback_response.status_code == 200:
                                feed = feedparser.parse(fallback_response.content)
                            else:
                                logger.error(f"{source_name} RSS fallback URL 접근 실패. 상태 코드: {fallback_response.status_code}")
                                continue
                        except requests.exceptions.RequestException as e:
                            logger.error(f"{source_name} RSS fallback URL 요청 실패: {str(e)}")
                            continue
                    else:
                        logger.error(f"{source_name} RSS 피드 요청 타임아웃")
                        continue
                except requests.exceptions.RequestException as e:
                    # Nasdaq의 경우 fallback URL 사용 시도
                    if source_id == "nasdaq" and "fallback_url" in source_config:
                        try:
                            logger.warning(f"Nasdaq RSS 기본 URL 접속 오류, fallback URL 시도: {source_config['fallback_url']}")
                            fallback_response = requests.get(source_config['fallback_url'], timeout=15)  # 타임아웃 증가
                            if fallback_response.status_code == 200:
                                feed = feedparser.parse(fallback_response.content)
                            else:
                                logger.error(f"{source_name} RSS fallback URL 접근 실패. 상태 코드: {fallback_response.status_code}")
                                continue
                        except requests.exceptions.RequestException as e2:
                            logger.error(f"{source_name} RSS fallback URL 요청 실패: {str(e2)}")
                            continue
                    else:
                        logger.error(f"{source_name} RSS 피드 요청 실패: {str(e)}")
                        continue
                
                if not feed.entries:
                    logger.warning(f"{source_name}\uc758 피드에 항목이 없습니다.")
                    continue
                    
                # 각 소스에서 count개의 기사만 가져오기
                for entry in feed.entries[:count]:
                    try:
                        article_url = entry.link
                        
                        # 이미 수집된 기사 건너뛰기
                        if self.news_collection is not None and self.news_collection.find_one({"url": article_url}) is not None:
                            logger.debug(f"이미 수집된 기사: {article_url}")
                            continue
                        
                        # 이 소스에 대한 전용 처리기가 있는지 확인
                        if source_id in source_processors:
                            article_base = source_processors[source_id](entry, source_name)
                        else:
                            article_base = self._process_generic_rss(entry, source_name)
                        
                        # 기본 정보 추가
                        article_data = {
                            "url": article_url,
                            "crawled_date": datetime.now().isoformat(),
                            "keywords": self._extract_keywords(article_base["title"] + " " + article_base["content"]),
                            "sentiment": None,
                        }
                        
                        # 기본 정보와 소스별 처리기에서 가져온 정보 합치기
                        article_data.update(article_base)
                        
                        # 감성 분석 추가
                        if self.sentiment_analyzer:
                            article_data["sentiment"] = self.sentiment_analyzer.analyze(article_data["content"])
                        
                        all_articles.append(article_data)
                        
                        # MongoDB에 저장
                        if self.news_collection is not None:
                            try:
                                self.news_collection.insert_one(article_data)
                                logger.debug(f"RSS 기사 저장됨: {article_url}")
                            except pymongo.errors.DuplicateKeyError:
                                logger.debug(f"중복 기사: {article_url}")
                            except Exception as e:
                                logger.error(f"기사 저장 실패: {str(e)}")
                                
                    except Exception as e:
                        logger.error(f"RSS 항목 처리 중 오류: {str(e)}")
                        
                # 요청 간 대기 (RSS 서버 부하 경감)
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"RSS 피드 처리 중 오류: {str(e)}")
                
        return all_articles

    def search_news_from_rss(self, keyword: str, days: int = 7, sources: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        RSS 피드에서 키워드로 뉴스 검색

        Args:
            keyword: 검색 키워드
            days: 검색할 기간(일)
            sources: RSS 소스 목록 (None인 경우 모든 소스)

        Returns:
            List[Dict[str, Any]]: 수집된 뉴스 기사 목록
        """
        if sources is None:
            sources = list(self.rss_feeds.keys())
        else:
            # 존재하지 않는 소스 필터링
            sources = [s for s in sources if s in self.rss_feeds]
            
        all_articles = []
        keyword_lower = keyword.lower()
        
        # 각 소스에 대해 피드별 검색 전략 적용
        for source_id in sources:
            source_config = self.rss_feeds[source_id]
            source_name = source_config['name']
            rss_url = source_config['url']
            
            # 일부 뉴스 사이트는 키워드 기반 RSS URL 지원
            search_url = None
            
            # 소스별 특수 처리
            if source_id == "nasdaq":
                # Nasdaq은 검색 RSS를 지원하지 않음 - 일반 RSS를 가져와서 필터링
                logger.info(f"{source_name} RSS 피드에서 '{keyword}' 검색 중")
                
            elif source_id == "coindesk":
                # CoinDesk는 카테고리별 RSS 제공
                if "/" in rss_url:
                    base_url = rss_url.rsplit('/', 1)[0]
                    search_url = f"{base_url}/tag/{keyword}/feed/" 
                    logger.info(f"{source_name} '{keyword}' 태그 RSS 피드 사용: {search_url}")
                
            elif source_id == "cointelegraph":
                # CoinTelegraph는 태그별 RSS 피드 제공
                search_url = f"https://cointelegraph.com/tags/{keyword}/feed"
                logger.info(f"{source_name} '{keyword}' 태그 RSS 피드 사용: {search_url}")
                
            elif source_id == "investing":
                # Investing.com은 카테고리별 RSS 제공을 하지만 키워드 검색은 없음
                logger.info(f"{source_name} RSS 피드에서 '{keyword}' 검색 중")
            
            try:
                # 검색 URL이 있는 경우 사용, 없는 경우 기본 URL 사용
                feed_url = search_url if search_url else rss_url
                
                # RSS 피드 파싱 (타임아웃 설정을 위해 requests로 먼저 가져오기)
                try:
                    response = requests.get(feed_url, timeout=10)
                    if response.status_code != 200:
                        # Nasdaq의 경우 fallback URL 사용 시도
                        if source_id == "nasdaq" and "fallback_url" in source_config:
                            logger.warning(f"Nasdaq RSS 검색 URL 실패, fallback URL 시도: {source_config['fallback_url']}")
                            fallback_response = requests.get(source_config['fallback_url'], timeout=10)
                            if fallback_response.status_code == 200:
                                feed = feedparser.parse(fallback_response.content)
                            else:
                                logger.error(f"{source_name} RSS fallback URL 접근 실패. 상태 코드: {fallback_response.status_code}")
                                continue
                        else:
                            logger.error(f"{source_name} RSS 피드 접근 실패. 상태 코드: {response.status_code}")
                            continue
                    else:
                        feed = feedparser.parse(response.content)
                except requests.exceptions.Timeout:
                    # Nasdaq의 경우 fallback URL 사용 시도
                    if source_id == "nasdaq" and "fallback_url" in source_config:
                        try:
                            logger.warning(f"Nasdaq RSS 검색 URL 타임아웃, fallback URL 시도: {source_config['fallback_url']}")
                            fallback_response = requests.get(source_config['fallback_url'], timeout=15)  # 타임아웃 증가
                            if fallback_response.status_code == 200:
                                feed = feedparser.parse(fallback_response.content)
                            else:
                                logger.error(f"{source_name} RSS fallback URL 접근 실패. 상태 코드: {fallback_response.status_code}")
                                continue
                        except requests.exceptions.RequestException as e:
                            logger.error(f"{source_name} RSS fallback URL 요청 실패: {str(e)}")
                            continue
                    else:
                        logger.error(f"{source_name} RSS 피드 요청 타임아웃")
                        continue
                except requests.exceptions.RequestException as e:
                    # Nasdaq의 경우 fallback URL 사용 시도
                    if source_id == "nasdaq" and "fallback_url" in source_config:
                        try:
                            logger.warning(f"Nasdaq RSS 검색 URL 접속 오류, fallback URL 시도: {source_config['fallback_url']}")
                            fallback_response = requests.get(source_config['fallback_url'], timeout=15)  # 타임아웃 증가
                            if fallback_response.status_code == 200:
                                feed = feedparser.parse(fallback_response.content)
                            else:
                                logger.error(f"{source_name} RSS fallback URL 접근 실패. 상태 코드: {fallback_response.status_code}")
                                continue
                        except requests.exceptions.RequestException as e2:
                            logger.error(f"{source_name} RSS fallback URL 요청 실패: {str(e2)}")
                            continue
                    else:
                        logger.error(f"{source_name} RSS 피드 요청 실패: {str(e)}")
                        continue
                
                if not feed.entries:
                    logger.warning(f"{source_name}\uc758 피드에 항목이 없습니다.")
                    continue
                
                # 기간 설정 (일 수)
                date_limit = datetime.now() - timedelta(days=days)
                
                # 소스별 처리 함수 매핑
                source_processors = {
                    "nasdaq": self._process_nasdaq_rss,
                    "coindesk": self._process_coindesk_rss,
                    "cointelegraph": self._process_cointelegraph_rss,
                    "investing": self._process_investing_rss
                }
                
                for entry in feed.entries:
                    try:
                        article_url = entry.link
                        
                        # 이미 수집된 기사 건너뛰기
                        if self.news_collection is not None and self.news_collection.find_one({"url": article_url}) is not None:
                            logger.debug(f"이미 수집된 기사: {article_url}")
                            continue
                        
                        # 소스별 처리 함수 사용
                        if source_id in source_processors:
                            article_base = source_processors[source_id](entry, source_name)
                        else:
                            article_base = self._process_generic_rss(entry, source_name)
                        
                        # 날짜 필터링
                        try:
                            article_date = datetime.fromisoformat(article_base['published_date'])
                            if article_date < date_limit:
                                continue
                        except (ValueError, KeyError):
                            # 날짜 형식이 잘못되었거나 날짜가 없는 경우, 현재 날짜 사용
                            pass
                        
                        # 키워드 검색 - 검색 URL 사용 시에도 한번 더 확인
                        title = article_base.get('title', '').lower()
                        content = article_base.get('content', '').lower()
                        
                        # 검색 URL을 사용하지 않았을 경우에만 키워드 필터링
                        if search_url is None and keyword_lower not in title and keyword_lower not in content:
                            continue
                        
                        # 기본 정보 추가
                        article_data = {
                            "url": article_url,
                            "crawled_date": datetime.now().isoformat(),
                            "keywords": self._extract_keywords(article_base["title"] + " " + article_base["content"]),
                            "sentiment": None,
                        }
                        
                        # 기본 정보와 소스별 처리기에서 가져온 정보 합치기
                        article_data.update(article_base)
                        
                        # 감성 분석 추가
                        if self.sentiment_analyzer:
                            article_data["sentiment"] = self.sentiment_analyzer.analyze(article_data["content"])
                        
                        all_articles.append(article_data)
                        
                        # MongoDB에 저장
                        if self.news_collection is not None:
                            try:
                                self.news_collection.insert_one(article_data)
                                logger.debug(f"RSS 검색 기사 저장됨: {article_url}")
                            except pymongo.errors.DuplicateKeyError:
                                logger.debug(f"중복 기사: {article_url}")
                            except Exception as e:
                                logger.error(f"기사 저장 실패: {str(e)}")
                    
                    except Exception as e:
                        logger.error(f"RSS 항목 처리 중 오류: {str(e)}")
                
                # 요청 간 대기 (RSS 서버 부하 경감)
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"RSS 피드 검색 중 오류: {str(e)}")
                    
        return all_articles

    def close(self):
        """
        MongoDB 연결 종료
        """
        if self.client:
            self.client.close()
            logger.info("MongoDB 연결 종료")


class SentimentAnalyzer:
    """
    금융 뉴스 감성 분석 클래스

    FinBERT 모델을 사용하여 금융 뉴스의 감성을 분석합니다.
    """

    def __init__(self):
        """
        SentimentAnalyzer 클래스 초기화
        """
        self.config = CONFIG['sentiment_analysis']
        model_path = os.getenv("FINBERT_MODEL_PATH", "yiyanghkust/finbert-tone")
        
        try:
            # FinBERT 모델 및 토크나이저 로드
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.labels = ["negative", "neutral", "positive"]
            
            # GPU 사용 가능 시 GPU로 모델 이동
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            logger.info(f"감성 분석 모델 로드 완료: {model_path} (장치: {self.device})")
        except Exception as e:
            logger.error(f"감성 분석 모델 로드 실패: {str(e)}")
            self.tokenizer = None
            self.model = None

    def analyze(self, text: str) -> Optional[Dict[str, float]]:
        """
        텍스트 감성 분석

        Args:
            text: 분석할 텍스트

        Returns:
            Optional[Dict[str, float]]: 감성 점수 또는 None (실패 시)
        """
        if not self.model or not self.tokenizer:
            logger.error("감성 분석 모델이 초기화되지 않았습니다.")
            return None
            
        try:
            # 텍스트가 너무 길면 첫 512 토큰만 사용
            inputs = self.tokenizer(text[:1024], return_tensors="pt", truncation=True, padding=True)
            inputs = {key: val.to(self.device) for key, val in inputs.items()}
            
            # 모델 추론
            with torch.no_grad():
                outputs = self.model(**inputs)
                
            # 소프트맥스로 클래스별 확률 계산
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
            probabilities = probabilities[0].cpu().numpy()
            
            # 결과 사전 생성
            result = {
                self.labels[i]: float(probabilities[i])
                for i in range(len(self.labels))
            }
            
            return result
            
        except Exception as e:
            logger.error(f"감성 분석 중 오류: {str(e)}")
            return None

    def analyze_batch(self, texts: List[str]) -> List[Optional[Dict[str, float]]]:
        """
        여러 텍스트 배치 감성 분석

        Args:
            texts: 분석할 텍스트 목록

        Returns:
            List[Optional[Dict[str, float]]]: 각 텍스트의 감성 점수 목록
        """
        if not self.model or not self.tokenizer:
            logger.error("감성 분석 모델이 초기화되지 않았습니다.")
            return [None] * len(texts)
            
        batch_size = self.config['batch_size']
        results = []
        
        # 배치 단위로 처리
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            
            try:
                # 텍스트가 너무 길면 첫 512 토큰만 사용
                inputs = self.tokenizer(
                    [text[:1024] for text in batch_texts],
                    return_tensors="pt",
                    truncation=True,
                    padding=True
                )
                inputs = {key: val.to(self.device) for key, val in inputs.items()}
                
                # 모델 추론
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    
                # 소프트맥스로 클래스별 확률 계산
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
                probabilities = probabilities.cpu().numpy()
                
                # 결과 리스트에 추가
                for j in range(len(batch_texts)):
                    result = {
                        self.labels[k]: float(probabilities[j][k])
                        for k in range(len(self.labels))
                    }
                    results.append(result)
                    
            except Exception as e:
                logger.error(f"배치 감성 분석 중 오류: {str(e)}")
                results.extend([None] * len(batch_texts))
                
        return results


if __name__ == "__main__":
    # 직접 실행 시 간단한 테스트 코드
    crawler = NewsCrawler(db_connect=False)
    crawler.initialize_sentiment_analyzer()
    
    # 최신 뉴스 수집 테스트
    articles = crawler.get_latest_news(sources=["reuters"], count=2)
    
    for article in articles:
        print(f"제목: {article['title']}")
        print(f"날짜: {article['published_date']}")
        print(f"URL: {article['url']}")
        print(f"키워드: {', '.join(article['keywords'])}")
        if article['sentiment']:
            print(f"감성: {article['sentiment']}")
        print("-" * 50)
    
    crawler.close()
