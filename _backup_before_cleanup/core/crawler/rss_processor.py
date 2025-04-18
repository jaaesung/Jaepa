"""
RSS 피드 처리 모듈

RSS 피드를 파싱하고 처리하는 기능을 제공합니다.
"""
import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from urllib.parse import urlparse

import feedparser
from bs4 import BeautifulSoup

from core.crawler.interfaces import RssProcessorInterface, HttpClientInterface, ArticleProcessorInterface
from core.crawler.exceptions import ParsingException

# 로깅 설정
logger = logging.getLogger(__name__)


class RssProcessor(RssProcessorInterface):
    """
    RSS 피드 처리기
    
    RSS 피드를 파싱하고 처리하는 기능을 제공합니다.
    """
    
    def __init__(self, http_client: HttpClientInterface, article_processor: ArticleProcessorInterface):
        """
        RssProcessor 초기화
        
        Args:
            http_client: HTTP 클라이언트
            article_processor: 기사 처리기
        """
        self._http_client = http_client
        self._article_processor = article_processor
    
    async def parse_feed(self, feed_url: str) -> Dict[str, Any]:
        """
        RSS 피드 파싱
        
        Args:
            feed_url: RSS 피드 URL
            
        Returns:
            Dict[str, Any]: 파싱된 피드 정보
            
        Raises:
            ParsingException: 피드 파싱 실패 시
        """
        try:
            # HTTP 요청으로 피드 내용 가져오기
            status_code, content = await self._http_client.get_with_retry(feed_url)
            
            if status_code != 200:
                raise ParsingException(f"Failed to fetch RSS feed: HTTP {status_code}", feed_url)
            
            # feedparser로 파싱
            feed = feedparser.parse(content)
            
            if feed.bozo and feed.bozo_exception:
                # 파싱 오류가 있지만 일부 내용이 있는 경우 계속 진행
                logger.warning(f"RSS feed parsing warning: {feed.bozo_exception}")
            
            # 피드 정보 추출
            feed_info = {
                'title': feed.feed.get('title', ''),
                'link': feed.feed.get('link', ''),
                'description': feed.feed.get('description', ''),
                'language': feed.feed.get('language', 'en'),
                'updated': feed.feed.get('updated', ''),
                'entries': feed.entries
            }
            
            return feed_info
            
        except Exception as e:
            logger.error(f"Failed to parse RSS feed {feed_url}: {str(e)}")
            raise ParsingException(f"Failed to parse RSS feed: {str(e)}", feed_url)
    
    async def process_entry(self, entry: Dict[str, Any], source_name: str) -> Dict[str, Any]:
        """
        RSS 항목 처리
        
        Args:
            entry: RSS 항목
            source_name: 소스 이름
            
        Returns:
            Dict[str, Any]: 처리된 뉴스 기사 정보
            
        Raises:
            ParsingException: 항목 처리 실패 시
        """
        try:
            # 기본 정보 추출
            title = entry.get('title', '').strip()
            link = entry.get('link', '')
            
            if not title or not link:
                raise ParsingException("Missing title or link in RSS entry", source_name)
            
            # 내용 추출
            content = ''
            if 'content' in entry and entry.content:
                for content_item in entry.content:
                    if content_item.get('type') == 'text/html':
                        content = content_item.value
                        break
            
            if not content and 'summary' in entry:
                content = entry.summary
            
            if not content and 'description' in entry:
                content = entry.description
            
            # HTML 태그 제거
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                content = soup.get_text(separator=' ', strip=True)
            
            # 발행일 파싱
            published_date = None
            for date_field in ['published', 'pubDate', 'updated']:
                if date_field in entry:
                    try:
                        published_date = entry.get(date_field)
                        break
                    except (ValueError, TypeError):
                        pass
            
            # 발행일이 없는 경우 현재 시간 사용
            if not published_date:
                published_date = datetime.now().isoformat()
            
            # 기사 정보 구성
            article = {
                'title': title,
                'url': link,
                'content': content,
                'summary': content[:300] + '...' if len(content) > 300 else content,
                'published_date': published_date,
                'source': source_name,
                'source_type': 'rss',
                'crawled_date': datetime.now().isoformat()
            }
            
            # 키워드 추출
            text_for_keywords = f"{title} {content[:1000]}"
            keywords = await self._article_processor.extract_keywords(text_for_keywords)
            article['keywords'] = keywords
            
            # 도메인 추출
            parsed_url = urlparse(link)
            article['domain'] = parsed_url.netloc
            
            return article
            
        except Exception as e:
            logger.error(f"Failed to process RSS entry: {str(e)}")
            raise ParsingException(f"Failed to process RSS entry: {str(e)}", source_name, entry)
    
    async def process_entries_batch(self, entries: List[Dict[str, Any]], source_name: str) -> List[Dict[str, Any]]:
        """
        RSS 항목 배치 처리
        
        Args:
            entries: RSS 항목 목록
            source_name: 소스 이름
            
        Returns:
            List[Dict[str, Any]]: 처리된 뉴스 기사 정보 목록
        """
        if not entries:
            return []
        
        # 비동기 작업 생성
        tasks = []
        for entry in entries:
            tasks.append(self._process_entry_safe(entry, source_name))
        
        # 모든 작업 완료 대기
        results = await asyncio.gather(*tasks)
        
        # 성공한 결과만 필터링
        articles = [article for article in results if article is not None]
        
        return articles
    
    async def _process_entry_safe(self, entry: Dict[str, Any], source_name: str) -> Optional[Dict[str, Any]]:
        """
        안전하게 RSS 항목 처리
        
        Args:
            entry: RSS 항목
            source_name: 소스 이름
            
        Returns:
            Optional[Dict[str, Any]]: 처리된 뉴스 기사 정보 또는 None
        """
        try:
            return await self.process_entry(entry, source_name)
        except Exception as e:
            logger.error(f"Error processing RSS entry from {source_name}: {str(e)}")
            return None
