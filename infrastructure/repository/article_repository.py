"""
기사 저장소 모듈

MongoDB를 사용하여 기사를 저장하고 조회하는 기능을 제공합니다.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple

import motor.motor_asyncio
from pymongo import ASCENDING, DESCENDING, TEXT

from core.crawler.interfaces import ArticleRepositoryInterface
from core.crawler.exceptions import StorageException

# 로깅 설정
logger = logging.getLogger(__name__)


class MongoArticleRepository(ArticleRepositoryInterface):
    """
    MongoDB 기사 저장소
    
    MongoDB를 사용하여 기사를 저장하고 조회하는 기능을 제공합니다.
    """
    
    def __init__(self, connection_string: str, database_name: str, collection_name: str = 'news_articles'):
        """
        MongoArticleRepository 초기화
        
        Args:
            connection_string: MongoDB 연결 문자열
            database_name: 데이터베이스 이름
            collection_name: 컬렉션 이름
        """
        try:
            self._client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
            self._db = self._client[database_name]
            self._collection = self._db[collection_name]
            logger.info(f"Connected to MongoDB: {database_name}.{collection_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise StorageException(f"Failed to connect to MongoDB: {str(e)}", "connect")
    
    async def initialize(self) -> None:
        """
        저장소 초기화
        
        인덱스 생성 등의 초기화 작업을 수행합니다.
        
        Raises:
            StorageException: 초기화 실패 시
        """
        try:
            # URL 인덱스 (중복 방지)
            await self._collection.create_index([('url', ASCENDING)], unique=True)
            
            # 검색 인덱스
            await self._collection.create_index([('title', TEXT), ('content', TEXT), ('keywords', TEXT)])
            
            # 날짜 인덱스
            await self._collection.create_index([('published_date', DESCENDING)])
            
            # 소스 인덱스
            await self._collection.create_index([('source', ASCENDING)])
            
            # 관련 심볼 인덱스
            await self._collection.create_index([('related_symbols', ASCENDING)])
            
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB indexes: {str(e)}")
            raise StorageException(f"Failed to initialize MongoDB indexes: {str(e)}", "initialize")
    
    async def save(self, article: Dict[str, Any]) -> str:
        """
        기사 저장
        
        Args:
            article: 저장할 기사 정보
            
        Returns:
            str: 저장된 기사 ID
            
        Raises:
            StorageException: 저장 실패 시
        """
        if not article or 'url' not in article:
            raise StorageException("Article URL is required", "save")
        
        try:
            # 기존 기사 확인
            existing = await self._collection.find_one({'url': article['url']})
            
            if existing:
                # 기존 기사 업데이트
                article['_id'] = existing['_id']
                article['updated_date'] = datetime.now().isoformat()
                
                result = await self._collection.replace_one({'_id': existing['_id']}, article)
                
                if result.modified_count > 0:
                    logger.debug(f"Updated article: {article['url']}")
                    return str(existing['_id'])
                else:
                    logger.warning(f"No changes in article: {article['url']}")
                    return str(existing['_id'])
            else:
                # 새 기사 삽입
                article['created_date'] = datetime.now().isoformat()
                
                result = await self._collection.insert_one(article)
                
                if result.inserted_id:
                    logger.debug(f"Inserted new article: {article['url']}")
                    return str(result.inserted_id)
                else:
                    raise StorageException(f"Failed to insert article: {article['url']}", "save")
                
        except Exception as e:
            logger.error(f"Failed to save article {article.get('url', 'unknown')}: {str(e)}")
            raise StorageException(f"Failed to save article: {str(e)}", "save")
    
    async def save_many(self, articles: List[Dict[str, Any]]) -> List[str]:
        """
        여러 기사 저장
        
        Args:
            articles: 저장할 기사 목록
            
        Returns:
            List[str]: 저장된 기사 ID 목록
            
        Raises:
            StorageException: 저장 실패 시
        """
        if not articles:
            return []
        
        try:
            # 각 기사 개별 저장 (중복 처리를 위해)
            tasks = []
            for article in articles:
                tasks.append(self._save_safe(article))
            
            # 모든 작업 완료 대기
            results = await asyncio.gather(*tasks)
            
            # 성공한 ID만 필터링
            saved_ids = [id for id in results if id is not None]
            
            logger.info(f"Saved {len(saved_ids)} articles out of {len(articles)}")
            return saved_ids
            
        except Exception as e:
            logger.error(f"Failed to save multiple articles: {str(e)}")
            raise StorageException(f"Failed to save multiple articles: {str(e)}", "save_many")
    
    async def find_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        URL로 기사 찾기
        
        Args:
            url: 기사 URL
            
        Returns:
            Optional[Dict[str, Any]]: 찾은 기사 또는 None
        """
        try:
            article = await self._collection.find_one({'url': url})
            return article
        except Exception as e:
            logger.error(f"Failed to find article by URL {url}: {str(e)}")
            return None
    
    async def find_by_keyword(self, keyword: str, days: int = 7, limit: int = 100) -> List[Dict[str, Any]]:
        """
        키워드로 기사 찾기
        
        Args:
            keyword: 검색 키워드
            days: 검색할 기간(일)
            limit: 최대 결과 수
            
        Returns:
            List[Dict[str, Any]]: 찾은 기사 목록
        """
        try:
            # 검색 기간 계산
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # 검색 쿼리 구성
            query = {
                '$or': [
                    {'title': {'$regex': keyword, '$options': 'i'}},
                    {'content': {'$regex': keyword, '$options': 'i'}},
                    {'keywords': keyword}
                ],
                'published_date': {'$gte': start_date}
            }
            
            # 검색 실행
            cursor = self._collection.find(query).sort('published_date', DESCENDING).limit(limit)
            articles = await cursor.to_list(length=limit)
            
            logger.info(f"Found {len(articles)} articles for keyword '{keyword}'")
            return articles
            
        except Exception as e:
            logger.error(f"Failed to find articles by keyword '{keyword}': {str(e)}")
            return []
    
    async def find_latest(self, days: int = 7, limit: int = 100) -> List[Dict[str, Any]]:
        """
        최신 기사 찾기
        
        Args:
            days: 검색할 기간(일)
            limit: 최대 결과 수
            
        Returns:
            List[Dict[str, Any]]: 찾은 기사 목록
        """
        try:
            # 검색 기간 계산
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # 검색 쿼리 구성
            query = {'published_date': {'$gte': start_date}}
            
            # 검색 실행
            cursor = self._collection.find(query).sort('published_date', DESCENDING).limit(limit)
            articles = await cursor.to_list(length=limit)
            
            logger.info(f"Found {len(articles)} latest articles")
            return articles
            
        except Exception as e:
            logger.error(f"Failed to find latest articles: {str(e)}")
            return []
    
    async def find_by_source(self, source: str, days: int = 7, limit: int = 100) -> List[Dict[str, Any]]:
        """
        소스별 기사 찾기
        
        Args:
            source: 뉴스 소스
            days: 검색할 기간(일)
            limit: 최대 결과 수
            
        Returns:
            List[Dict[str, Any]]: 찾은 기사 목록
        """
        try:
            # 검색 기간 계산
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # 검색 쿼리 구성
            query = {
                'source': source,
                'published_date': {'$gte': start_date}
            }
            
            # 검색 실행
            cursor = self._collection.find(query).sort('published_date', DESCENDING).limit(limit)
            articles = await cursor.to_list(length=limit)
            
            logger.info(f"Found {len(articles)} articles from source '{source}'")
            return articles
            
        except Exception as e:
            logger.error(f"Failed to find articles from source '{source}': {str(e)}")
            return []
    
    async def close(self) -> None:
        """
        저장소 연결 종료
        """
        if hasattr(self, '_client') and self._client:
            self._client.close()
            logger.info("MongoDB connection closed")
    
    async def _save_safe(self, article: Dict[str, Any]) -> Optional[str]:
        """
        안전하게 기사 저장
        
        Args:
            article: 저장할 기사 정보
            
        Returns:
            Optional[str]: 저장된 기사 ID 또는 None
        """
        try:
            return await self.save(article)
        except Exception as e:
            logger.error(f"Error saving article {article.get('url', 'unknown')}: {str(e)}")
            return None
