"""
뉴스 크롤러 모듈

여러 소스에서 뉴스를 수집하고 처리하는 기능을 제공합니다.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple

from core.crawler.interfaces import (
    NewsSourceManagerInterface, ArticleProcessorInterface, ArticleRepositoryInterface
)
from core.crawler.exceptions import CrawlerException

# 로깅 설정
logger = logging.getLogger(__name__)


class NewsCrawler:
    """
    뉴스 크롤러
    
    여러 소스에서 뉴스를 수집하고 처리하는 기능을 제공합니다.
    """
    
    def __init__(self, news_source_manager: NewsSourceManagerInterface, 
                article_processor: ArticleProcessorInterface, 
                article_repository: ArticleRepositoryInterface):
        """
        NewsCrawler 초기화
        
        Args:
            news_source_manager: 뉴스 소스 관리자
            article_processor: 기사 처리기
            article_repository: 기사 저장소
        """
        self._news_source_manager = news_source_manager
        self._article_processor = article_processor
        self._article_repository = article_repository
    
    async def get_latest_news(self, sources: Optional[List[str]] = None, 
                            count: int = 10, save: bool = True) -> List[Dict[str, Any]]:
        """
        최신 뉴스 가져오기
        
        Args:
            sources: 뉴스 소스 ID 목록 (None인 경우 모든 소스)
            count: 각 소스별 가져올 뉴스 수
            save: 기사 저장 여부
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        try:
            # 뉴스 소스 관리자에서 최신 뉴스 가져오기
            articles = await self._news_source_manager.get_latest_news(sources, count)
            
            if not articles:
                logger.warning("No latest news found")
                return []
            
            # 기사 정규화
            normalized_articles = await self._normalize_articles(articles)
            
            # 중복 제거
            deduplicated_articles = await self._article_processor.deduplicate_articles(normalized_articles)
            
            # 기사 저장
            if save:
                await self._save_articles(deduplicated_articles)
            
            return deduplicated_articles
            
        except Exception as e:
            logger.error(f"Failed to get latest news: {str(e)}")
            raise CrawlerException(f"Failed to get latest news: {str(e)}")
    
    async def search_news(self, keyword: str, days: int = 7, sources: Optional[List[str]] = None, 
                         count: int = 10, save: bool = True, force_update: bool = False) -> List[Dict[str, Any]]:
        """
        키워드로 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            days: 검색할 기간(일)
            sources: 뉴스 소스 ID 목록 (None인 경우 모든 소스)
            count: 각 소스별 가져올 뉴스 수
            save: 기사 저장 여부
            force_update: 강제 업데이트 여부
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        try:
            # 저장소에서 먼저 검색 (강제 업데이트가 아닌 경우)
            if not force_update:
                db_articles = await self._article_repository.find_by_keyword(keyword, days, count * 2)
                
                if db_articles and len(db_articles) >= count:
                    logger.info(f"Found {len(db_articles)} articles in repository for keyword '{keyword}'")
                    return db_articles[:count]
            
            # 뉴스 소스 관리자에서 뉴스 검색
            articles = await self._news_source_manager.search_news(keyword, days, sources, count)
            
            if not articles:
                logger.warning(f"No news found for keyword '{keyword}'")
                return []
            
            # 기사 정규화
            normalized_articles = await self._normalize_articles(articles)
            
            # 중복 제거
            deduplicated_articles = await self._article_processor.deduplicate_articles(normalized_articles)
            
            # 기사 저장
            if save:
                await self._save_articles(deduplicated_articles)
            
            return deduplicated_articles
            
        except Exception as e:
            logger.error(f"Failed to search news for keyword '{keyword}': {str(e)}")
            raise CrawlerException(f"Failed to search news: {str(e)}")
    
    async def get_news_by_symbol(self, symbol: str, days: int = 7, 
                               count: int = 10, save: bool = True, 
                               force_update: bool = False) -> List[Dict[str, Any]]:
        """
        주식 심볼로 뉴스 가져오기
        
        Args:
            symbol: 주식 심볼 (예: AAPL)
            days: 검색할 기간(일)
            count: 가져올 뉴스 수
            save: 기사 저장 여부
            force_update: 강제 업데이트 여부
            
        Returns:
            List[Dict[str, Any]]: 뉴스 기사 목록
        """
        try:
            # 키워드 검색 활용
            articles = await self.search_news(
                keyword=symbol,
                days=days,
                count=count,
                save=save,
                force_update=force_update
            )
            
            # 관련 심볼 추가
            for article in articles:
                if 'related_symbols' not in article:
                    article['related_symbols'] = [symbol]
                elif symbol not in article['related_symbols']:
                    article['related_symbols'].append(symbol)
            
            # 기사 저장 (관련 심볼 업데이트)
            if save:
                await self._save_articles(articles)
            
            return articles
            
        except Exception as e:
            logger.error(f"Failed to get news for symbol '{symbol}': {str(e)}")
            raise CrawlerException(f"Failed to get news for symbol: {str(e)}")
    
    async def collect_news_from_all_sources(self, keywords: Optional[List[str]] = None, 
                                          symbols: Optional[List[str]] = None, 
                                          days: int = 7, limit: int = 50) -> Dict[str, int]:
        """
        모든 소스에서 뉴스 수집
        
        Args:
            keywords: 검색 키워드 목록
            symbols: 주식 심볼 목록
            days: 검색할 기간(일)
            limit: 각 키워드/심볼별 최대 결과 수
            
        Returns:
            Dict[str, int]: 수집 결과 통계
            {
                'total': 전체 수집 기사 수,
                'keywords': 키워드별 수집 기사 수,
                'symbols': 심볼별 수집 기사 수
            }
        """
        try:
            results = {
                'total': 0,
                'keywords': {},
                'symbols': {}
            }
            
            # 키워드로 뉴스 수집
            if keywords:
                for keyword in keywords:
                    articles = await self.search_news(
                        keyword=keyword,
                        days=days,
                        count=limit,
                        save=True,
                        force_update=True
                    )
                    
                    results['keywords'][keyword] = len(articles)
                    results['total'] += len(articles)
            
            # 심볼로 뉴스 수집
            if symbols:
                for symbol in symbols:
                    articles = await self.get_news_by_symbol(
                        symbol=symbol,
                        days=days,
                        count=limit,
                        save=True,
                        force_update=True
                    )
                    
                    results['symbols'][symbol] = len(articles)
                    results['total'] += len(articles)
            
            # 키워드나 심볼이 없는 경우 최신 뉴스 수집
            if not keywords and not symbols:
                articles = await self.get_latest_news(
                    count=limit,
                    save=True
                )
                
                results['total'] = len(articles)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to collect news from all sources: {str(e)}")
            raise CrawlerException(f"Failed to collect news: {str(e)}")
    
    async def close(self) -> None:
        """
        리소스 정리
        """
        try:
            if hasattr(self, '_article_repository'):
                await self._article_repository.close()
        except Exception as e:
            logger.error(f"Error closing resources: {str(e)}")
    
    async def _normalize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        기사 정규화
        
        Args:
            articles: 기사 목록
            
        Returns:
            List[Dict[str, Any]]: 정규화된 기사 목록
        """
        if not articles:
            return []
        
        # 비동기 작업 생성
        tasks = []
        for article in articles:
            tasks.append(self._article_processor.normalize_article(article))
        
        # 모든 작업 완료 대기
        normalized = await asyncio.gather(*tasks)
        
        return normalized
    
    async def _save_articles(self, articles: List[Dict[str, Any]]) -> None:
        """
        기사 저장
        
        Args:
            articles: 저장할 기사 목록
        """
        if not articles:
            return
        
        try:
            # 기사 저장
            saved_ids = await self._article_repository.save_many(articles)
            logger.info(f"Saved {len(saved_ids)} articles to repository")
        except Exception as e:
            logger.error(f"Failed to save articles: {str(e)}")
            # 저장 실패는 크리티컬하지 않으므로 예외를 다시 발생시키지 않음
