"""
뉴스 소스 관리자 모듈

여러 뉴스 소스를 관리하고 통합 검색 기능을 제공합니다.
"""
import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

from core.crawler.interfaces import (
    NewsSourceManagerInterface, NewsSourceInterface, HttpClientInterface
)
from core.crawler.exceptions import (
    ConfigurationException, SourceException
)

# 로깅 설정
logger = logging.getLogger(__name__)


class NewsSourceManager(NewsSourceManagerInterface):
    """
    뉴스 소스 관리자
    
    여러 뉴스 소스를 관리하고 통합 검색 기능을 제공합니다.
    """
    
    def __init__(self, http_client: HttpClientInterface, config_path: Optional[str] = None):
        """
        NewsSourceManager 초기화
        
        Args:
            http_client: HTTP 클라이언트
            config_path: 설정 파일 경로 (기본값: crawling/config.json)
        """
        self._http_client = http_client
        self._sources: Dict[str, NewsSourceInterface] = {}
        self._config: Dict[str, Any] = {}
        
        # 설정 파일 로드
        if config_path:
            self._load_config(config_path)
        else:
            default_config_path = Path(__file__).parents[2] / 'crawling' / 'config.json'
            if default_config_path.exists():
                self._load_config(str(default_config_path))
    
    def register_source(self, source: NewsSourceInterface) -> None:
        """
        뉴스 소스 등록
        
        Args:
            source: 등록할 뉴스 소스
            
        Raises:
            ConfigurationException: 소스 등록 실패 시
        """
        source_id = source.source_id
        
        if source_id in self._sources:
            logger.warning(f"Overwriting existing news source: {source_id}")
        
        self._sources[source_id] = source
        logger.info(f"Registered news source: {source_id} ({source.name})")
    
    def get_source(self, source_id: str) -> Optional[NewsSourceInterface]:
        """
        뉴스 소스 가져오기
        
        Args:
            source_id: 소스 ID
            
        Returns:
            Optional[NewsSourceInterface]: 뉴스 소스 또는 None
        """
        return self._sources.get(source_id)
    
    def get_all_sources(self) -> List[NewsSourceInterface]:
        """
        모든 뉴스 소스 가져오기
        
        Returns:
            List[NewsSourceInterface]: 뉴스 소스 목록
        """
        return list(self._sources.values())
    
    async def get_latest_news(self, sources: Optional[List[str]] = None, count: int = 10) -> List[Dict[str, Any]]:
        """
        최신 뉴스 가져오기
        
        Args:
            sources: 뉴스 소스 ID 목록 (None인 경우 모든 소스)
            count: 각 소스별 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        # 소스 목록 결정
        source_list = self._get_source_list(sources)
        
        if not source_list:
            logger.warning("No news sources available")
            return []
        
        # 각 소스에서 비동기로 뉴스 가져오기
        tasks = []
        for source in source_list:
            tasks.append(self._get_news_from_source(source, count))
        
        # 모든 작업 완료 대기
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 처리
        all_news = []
        for i, result in enumerate(results):
            source_id = source_list[i].source_id
            
            if isinstance(result, Exception):
                logger.error(f"Error getting news from {source_id}: {str(result)}")
                continue
            
            logger.info(f"Got {len(result)} news from {source_id}")
            all_news.extend(result)
        
        # 날짜순 정렬
        all_news.sort(key=lambda x: x.get('published_date', ''), reverse=True)
        
        return all_news
    
    async def search_news(self, keyword: str, days: int = 7, sources: Optional[List[str]] = None, 
                         count: int = 10) -> List[Dict[str, Any]]:
        """
        키워드로 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            days: 검색할 기간(일)
            sources: 뉴스 소스 ID 목록 (None인 경우 모든 소스)
            count: 각 소스별 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        # 소스 목록 결정
        source_list = self._get_source_list(sources)
        
        if not source_list:
            logger.warning("No news sources available")
            return []
        
        # 각 소스에서 비동기로 뉴스 검색
        tasks = []
        for source in source_list:
            tasks.append(self._search_news_from_source(source, keyword, days, count))
        
        # 모든 작업 완료 대기
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 처리
        all_news = []
        for i, result in enumerate(results):
            source_id = source_list[i].source_id
            
            if isinstance(result, Exception):
                logger.error(f"Error searching news from {source_id}: {str(result)}")
                continue
            
            logger.info(f"Found {len(result)} news from {source_id} for keyword '{keyword}'")
            all_news.extend(result)
        
        # 날짜순 정렬
        all_news.sort(key=lambda x: x.get('published_date', ''), reverse=True)
        
        # 중복 제거
        deduplicated_news = self._deduplicate_news(all_news)
        
        return deduplicated_news
    
    def _load_config(self, config_path: str) -> None:
        """
        설정 파일 로드
        
        Args:
            config_path: 설정 파일 경로
            
        Raises:
            ConfigurationException: 설정 파일 로드 실패 시
        """
        try:
            with open(config_path, 'r') as f:
                self._config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load configuration from {config_path}: {str(e)}")
            raise ConfigurationException(f"Failed to load configuration: {str(e)}", "config_file")
    
    def _get_source_list(self, sources: Optional[List[str]] = None) -> List[NewsSourceInterface]:
        """
        소스 목록 가져오기
        
        Args:
            sources: 소스 ID 목록 (None인 경우 모든 소스)
            
        Returns:
            List[NewsSourceInterface]: 소스 목록
        """
        if not sources:
            return list(self._sources.values())
        
        source_list = []
        for source_id in sources:
            source = self.get_source(source_id)
            if source:
                source_list.append(source)
            else:
                logger.warning(f"Unknown news source: {source_id}")
        
        return source_list
    
    async def _get_news_from_source(self, source: NewsSourceInterface, count: int) -> List[Dict[str, Any]]:
        """
        소스에서 뉴스 가져오기
        
        Args:
            source: 뉴스 소스
            count: 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
            
        Raises:
            SourceException: 뉴스 가져오기 실패 시
        """
        try:
            return await source.get_latest_news(count)
        except Exception as e:
            raise SourceException(f"Failed to get news from {source.source_id}: {str(e)}", source.source_id)
    
    async def _search_news_from_source(self, source: NewsSourceInterface, keyword: str, 
                                      days: int, count: int) -> List[Dict[str, Any]]:
        """
        소스에서 뉴스 검색
        
        Args:
            source: 뉴스 소스
            keyword: 검색 키워드
            days: 검색할 기간(일)
            count: 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
            
        Raises:
            SourceException: 뉴스 검색 실패 시
        """
        try:
            return await source.search_news(keyword, days, count)
        except Exception as e:
            raise SourceException(f"Failed to search news from {source.source_id}: {str(e)}", source.source_id)
    
    def _deduplicate_news(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        중복 기사 제거
        
        Args:
            articles: 기사 목록
            
        Returns:
            List[Dict[str, Any]]: 중복이 제거된 기사 목록
        """
        if not articles:
            return []
        
        # URL 기준 중복 제거
        unique_articles = {}
        url_set = set()
        
        for article in articles:
            url = article.get('url', '')
            if not url or url in url_set:
                continue
            
            url_set.add(url)
            unique_articles[url] = article
        
        # 제목 유사도 기준 중복 제거
        title_groups = self._group_by_title_similarity(list(unique_articles.values()))
        
        # 각 그룹에서 가장 좋은 기사 선택
        deduplicated = []
        for group in title_groups:
            if len(group) == 1:
                deduplicated.append(group[0])
            else:
                # 여러 소스에서 온 기사는 통합
                best_article = self._merge_similar_articles(group)
                deduplicated.append(best_article)
        
        return deduplicated
    
    def _group_by_title_similarity(self, articles: List[Dict[str, Any]], 
                                  threshold: float = 0.85) -> List[List[Dict[str, Any]]]:
        """
        제목 유사도 기준으로 기사 그룹화
        
        Args:
            articles: 기사 목록
            threshold: 유사도 임계값 (0.0 ~ 1.0)
            
        Returns:
            List[List[Dict[str, Any]]]: 그룹화된 기사 목록
        """
        if not articles:
            return []
        
        # 그룹 초기화
        groups = []
        processed = set()
        
        for i, article1 in enumerate(articles):
            if i in processed:
                continue
            
            title1 = article1.get('title', '').lower()
            if not title1:
                continue
            
            # 새 그룹 생성
            group = [article1]
            processed.add(i)
            
            # 유사한 기사 찾기
            for j, article2 in enumerate(articles):
                if j in processed or i == j:
                    continue
                
                title2 = article2.get('title', '').lower()
                if not title2:
                    continue
                
                # 제목 유사도 계산
                similarity = self._calculate_similarity(title1, title2)
                
                if similarity >= threshold:
                    group.append(article2)
                    processed.add(j)
            
            groups.append(group)
        
        return groups
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        텍스트 유사도 계산
        
        Args:
            text1: 첫 번째 텍스트
            text2: 두 번째 텍스트
            
        Returns:
            float: 유사도 (0.0 ~ 1.0)
        """
        # 간단한 자카드 유사도 계산
        set1 = set(text1.split())
        set2 = set(text2.split())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _merge_similar_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        유사한 기사 통합
        
        Args:
            articles: 유사한 기사 목록
            
        Returns:
            Dict[str, Any]: 통합된 기사
        """
        if not articles:
            return {}
        
        if len(articles) == 1:
            return articles[0]
        
        # 가장 최신 기사 선택
        articles.sort(key=lambda x: x.get('published_date', ''), reverse=True)
        base_article = articles[0].copy()
        
        # 소스 및 관련 심볼 통합
        sources = set()
        related_symbols = set()
        keywords = set()
        
        for article in articles:
            # 소스 추가
            source = article.get('source', '')
            if source:
                sources.add(source)
            
            # 관련 심볼 추가
            symbols = article.get('related_symbols', [])
            if symbols:
                related_symbols.update(symbols)
            
            # 키워드 추가
            article_keywords = article.get('keywords', [])
            if article_keywords:
                keywords.update(article_keywords)
        
        # 통합 정보 설정
        base_article['sources'] = list(sources)
        base_article['related_symbols'] = list(related_symbols)
        base_article['keywords'] = list(keywords)[:20]  # 최대 20개 키워드
        
        return base_article
