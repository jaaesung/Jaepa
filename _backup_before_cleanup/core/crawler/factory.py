"""
뉴스 크롤러 팩토리 모듈

뉴스 크롤러 구성 요소를 생성하는 팩토리 기능을 제공합니다.
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.crawler.http_client import AsyncHttpClient
from core.crawler.news_source_manager import NewsSourceManager
from core.crawler.rss_processor import RssProcessor
from core.crawler.article_processor import ArticleProcessor
from core.crawler.rss_news_source import RssNewsSource
from core.crawler.interfaces import (
    HttpClientInterface, NewsSourceManagerInterface,
    RssProcessorInterface, ArticleProcessorInterface,
    ArticleRepositoryInterface
)
from core.crawler.exceptions import ConfigurationException
from infrastructure.repository.article_repository import MongoArticleRepository

# 로깅 설정
logger = logging.getLogger(__name__)


class NewsCrawlerFactory:
    """
    뉴스 크롤러 팩토리
    
    뉴스 크롤러 구성 요소를 생성하는 팩토리 기능을 제공합니다.
    """
    
    @staticmethod
    async def create_http_client(timeout: float = 30.0, max_retries: int = 3, 
                               requests_per_minute: int = 60) -> HttpClientInterface:
        """
        HTTP 클라이언트 생성
        
        Args:
            timeout: 기본 타임아웃 (초)
            max_retries: 기본 최대 재시도 횟수
            requests_per_minute: 분당 최대 요청 수
            
        Returns:
            HttpClientInterface: HTTP 클라이언트
        """
        return AsyncHttpClient(
            timeout=timeout,
            max_retries=max_retries,
            requests_per_minute=requests_per_minute
        )
    
    @staticmethod
    async def create_article_processor(http_client: HttpClientInterface) -> ArticleProcessorInterface:
        """
        기사 처리기 생성
        
        Args:
            http_client: HTTP 클라이언트
            
        Returns:
            ArticleProcessorInterface: 기사 처리기
        """
        return ArticleProcessor(http_client=http_client)
    
    @staticmethod
    async def create_rss_processor(http_client: HttpClientInterface, 
                                 article_processor: ArticleProcessorInterface) -> RssProcessorInterface:
        """
        RSS 처리기 생성
        
        Args:
            http_client: HTTP 클라이언트
            article_processor: 기사 처리기
            
        Returns:
            RssProcessorInterface: RSS 처리기
        """
        return RssProcessor(
            http_client=http_client,
            article_processor=article_processor
        )
    
    @staticmethod
    async def create_news_source_manager(http_client: HttpClientInterface, 
                                       config_path: Optional[str] = None) -> NewsSourceManagerInterface:
        """
        뉴스 소스 관리자 생성
        
        Args:
            http_client: HTTP 클라이언트
            config_path: 설정 파일 경로
            
        Returns:
            NewsSourceManagerInterface: 뉴스 소스 관리자
        """
        return NewsSourceManager(
            http_client=http_client,
            config_path=config_path
        )
    
    @staticmethod
    async def create_article_repository(connection_string: str, database_name: str, 
                                      collection_name: str = 'news_articles') -> ArticleRepositoryInterface:
        """
        기사 저장소 생성
        
        Args:
            connection_string: MongoDB 연결 문자열
            database_name: 데이터베이스 이름
            collection_name: 컬렉션 이름
            
        Returns:
            ArticleRepositoryInterface: 기사 저장소
        """
        repo = MongoArticleRepository(
            connection_string=connection_string,
            database_name=database_name,
            collection_name=collection_name
        )
        
        # 저장소 초기화
        await repo.initialize()
        
        return repo
    
    @staticmethod
    async def create_rss_sources(http_client: HttpClientInterface, 
                               rss_processor: RssProcessorInterface, 
                               config_path: Optional[str] = None) -> List[RssNewsSource]:
        """
        RSS 뉴스 소스 생성
        
        Args:
            http_client: HTTP 클라이언트
            rss_processor: RSS 처리기
            config_path: 설정 파일 경로
            
        Returns:
            List[RssNewsSource]: RSS 뉴스 소스 목록
            
        Raises:
            ConfigurationException: 설정 파일 로드 실패 시
        """
        # 설정 파일 로드
        if not config_path:
            config_path = Path(__file__).parents[2] / 'crawling' / 'config.json'
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load configuration from {config_path}: {str(e)}")
            raise ConfigurationException(f"Failed to load configuration: {str(e)}", "config_file")
        
        # RSS 소스 설정 가져오기
        rss_sources = []
        
        if 'rss_feeds' in config:
            for source_id, source_config in config['rss_feeds'].items():
                name = source_config.get('name', source_id)
                feed_urls = source_config.get('feeds', {})
                
                if feed_urls:
                    rss_source = RssNewsSource(
                        source_id=source_id,
                        name=name,
                        feed_urls=feed_urls,
                        http_client=http_client,
                        rss_processor=rss_processor
                    )
                    
                    rss_sources.append(rss_source)
                    logger.info(f"Created RSS news source: {name} with {len(feed_urls)} feeds")
        
        return rss_sources
    
    @staticmethod
    async def create_complete_crawler(config_path: Optional[str] = None, 
                                    mongo_uri: Optional[str] = None, 
                                    db_name: Optional[str] = None) -> Dict[str, Any]:
        """
        완전한 뉴스 크롤러 구성 요소 생성
        
        Args:
            config_path: 설정 파일 경로
            mongo_uri: MongoDB 연결 문자열
            db_name: 데이터베이스 이름
            
        Returns:
            Dict[str, Any]: 크롤러 구성 요소
            {
                'http_client': HttpClientInterface,
                'article_processor': ArticleProcessorInterface,
                'rss_processor': RssProcessorInterface,
                'news_source_manager': NewsSourceManagerInterface,
                'article_repository': ArticleRepositoryInterface,
                'rss_sources': List[RssNewsSource]
            }
        """
        # 기본값 설정
        if not mongo_uri:
            mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        
        if not db_name:
            db_name = os.getenv('MONGO_DB_NAME', 'jaepa')
        
        # 구성 요소 생성
        http_client = await NewsCrawlerFactory.create_http_client()
        article_processor = await NewsCrawlerFactory.create_article_processor(http_client)
        rss_processor = await NewsCrawlerFactory.create_rss_processor(http_client, article_processor)
        news_source_manager = await NewsCrawlerFactory.create_news_source_manager(http_client, config_path)
        article_repository = await NewsCrawlerFactory.create_article_repository(mongo_uri, db_name)
        rss_sources = await NewsCrawlerFactory.create_rss_sources(http_client, rss_processor, config_path)
        
        # 뉴스 소스 등록
        for source in rss_sources:
            news_source_manager.register_source(source)
        
        return {
            'http_client': http_client,
            'article_processor': article_processor,
            'rss_processor': rss_processor,
            'news_source_manager': news_source_manager,
            'article_repository': article_repository,
            'rss_sources': rss_sources
        }
