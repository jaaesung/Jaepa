"""
RSS 뉴스 소스 모듈

RSS 피드를 사용하여 뉴스를 수집하는 기능을 제공합니다.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple

from core.crawler.interfaces import (
    NewsSourceInterface, HttpClientInterface, RssProcessorInterface
)
from core.crawler.exceptions import SourceException

# 로깅 설정
logger = logging.getLogger(__name__)


class RssNewsSource(NewsSourceInterface):
    """
    RSS 뉴스 소스
    
    RSS 피드를 사용하여 뉴스를 수집하는 기능을 제공합니다.
    """
    
    def __init__(self, source_id: str, name: str, feed_urls: Dict[str, str], 
                http_client: HttpClientInterface, rss_processor: RssProcessorInterface):
        """
        RssNewsSource 초기화
        
        Args:
            source_id: 소스 ID
            name: 소스 이름
            feed_urls: RSS 피드 URL 목록 (이름: URL)
            http_client: HTTP 클라이언트
            rss_processor: RSS 처리기
        """
        self._source_id = source_id
        self._name = name
        self._feed_urls = feed_urls
        self._http_client = http_client
        self._rss_processor = rss_processor
    
    @property
    def source_id(self) -> str:
        """소스 ID"""
        return self._source_id
    
    @property
    def name(self) -> str:
        """소스 이름"""
        return self._name
    
    async def get_latest_news(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        최신 뉴스 가져오기
        
        Args:
            count: 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
            
        Raises:
            SourceException: 뉴스 가져오기 실패 시
        """
        try:
            all_articles = []
            
            # 각 피드에서 비동기로 뉴스 가져오기
            tasks = []
            for feed_name, feed_url in self._feed_urls.items():
                tasks.append(self._get_news_from_feed(feed_name, feed_url))
            
            # 모든 작업 완료 대기
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 처리
            for i, result in enumerate(results):
                feed_name = list(self._feed_urls.keys())[i]
                
                if isinstance(result, Exception):
                    logger.error(f"Error getting news from feed '{feed_name}': {str(result)}")
                    continue
                
                logger.info(f"Got {len(result)} news from feed '{feed_name}'")
                all_articles.extend(result)
            
            # 날짜순 정렬
            all_articles.sort(key=lambda x: x.get('published_date', ''), reverse=True)
            
            # 최대 개수 제한
            return all_articles[:count]
            
        except Exception as e:
            logger.error(f"Failed to get latest news from {self.name}: {str(e)}")
            raise SourceException(f"Failed to get latest news: {str(e)}", self.source_id)
    
    async def search_news(self, keyword: str, days: int = 7, count: int = 10) -> List[Dict[str, Any]]:
        """
        키워드로 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            days: 검색할 기간(일)
            count: 가져올 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
            
        Raises:
            SourceException: 뉴스 검색 실패 시
        """
        try:
            # 최신 뉴스 가져오기
            all_articles = await self.get_latest_news(count * 3)  # 더 많은 기사를 가져와서 필터링
            
            # 검색 기간 계산
            start_date = datetime.now() - timedelta(days=days)
            
            # 키워드 및 기간으로 필터링
            keyword_lower = keyword.lower()
            filtered_articles = []
            
            for article in all_articles:
                # 발행일 확인
                published_date = article.get('published_date', '')
                if published_date:
                    try:
                        pub_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                        if pub_date < start_date:
                            continue
                    except (ValueError, TypeError):
                        # 날짜 파싱 오류 시 포함
                        pass
                
                # 키워드 확인
                title = article.get('title', '').lower()
                content = article.get('content', '').lower()
                summary = article.get('summary', '').lower()
                
                if (keyword_lower in title or 
                    keyword_lower in content or 
                    keyword_lower in summary or
                    keyword_lower in ' '.join(article.get('keywords', []))):
                    filtered_articles.append(article)
            
            # 최대 개수 제한
            return filtered_articles[:count]
            
        except Exception as e:
            logger.error(f"Failed to search news from {self.name}: {str(e)}")
            raise SourceException(f"Failed to search news: {str(e)}", self.source_id)
    
    async def _get_news_from_feed(self, feed_name: str, feed_url: str) -> List[Dict[str, Any]]:
        """
        피드에서 뉴스 가져오기
        
        Args:
            feed_name: 피드 이름
            feed_url: 피드 URL
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
            
        Raises:
            SourceException: 뉴스 가져오기 실패 시
        """
        try:
            # RSS 피드 파싱
            feed_info = await self._rss_processor.parse_feed(feed_url)
            
            if not feed_info or 'entries' not in feed_info:
                logger.warning(f"No entries found in feed '{feed_name}'")
                return []
            
            # 항목 처리
            entries = feed_info['entries']
            source_name = f"{self.name} - {feed_name}"
            
            articles = await self._rss_processor.process_entries_batch(entries, source_name)
            
            # 소스 정보 추가
            for article in articles:
                article['source'] = self.name
                article['source_type'] = 'rss'
                article['feed_name'] = feed_name
            
            return articles
            
        except Exception as e:
            logger.error(f"Failed to get news from feed '{feed_name}': {str(e)}")
            raise SourceException(f"Failed to get news from feed: {str(e)}", self.source_id)
