"""
뉴스 저장소 모듈

뉴스 데이터 저장소를 제공합니다.
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from bson import ObjectId

from infrastructure.database.database_client import DatabaseClientInterface
from infrastructure.repository.repository import BaseMongoRepository
from domain.models.news import News, NewsSearchCriteria

# 로깅 설정
logger = logging.getLogger(__name__)


class NewsRepository(BaseMongoRepository[News, str]):
    """
    뉴스 저장소
    
    뉴스 데이터 저장소를 구현합니다.
    """
    
    def __init__(self, client: DatabaseClientInterface, db_name: str, collection_name: str = "news"):
        """
        NewsRepository 초기화
        
        Args:
            client: 데이터베이스 클라이언트
            db_name: 데이터베이스 이름
            collection_name: 컬렉션 이름
        """
        super().__init__(client, db_name, collection_name)
    
    def _define_indexes(self) -> List[Dict[str, Any]]:
        """
        인덱스 정의
        
        Returns:
            List[Dict[str, Any]]: 인덱스 정의 목록
        """
        return [
            # URL 고유 인덱스
            {
                "keys": [("url", 1)],
                "name": "url_unique_idx",
                "unique": True
            },
            # 발행일 인덱스
            {
                "keys": [("published_date", -1)],
                "name": "published_date_idx"
            },
            # 소스 인덱스
            {
                "keys": [("source", 1)],
                "name": "source_idx"
            },
            # 심볼 인덱스
            {
                "keys": [("symbols", 1)],
                "name": "symbols_idx"
            },
            # 카테고리 인덱스
            {
                "keys": [("categories", 1)],
                "name": "categories_idx"
            },
            # 감성 인덱스
            {
                "keys": [("sentiment.label", 1)],
                "name": "sentiment_label_idx"
            },
            # 복합 인덱스: 심볼 + 발행일
            {
                "keys": [("symbols", 1), ("published_date", -1)],
                "name": "symbols_published_date_idx"
            },
            # 텍스트 인덱스
            {
                "keys": [("title", "text"), ("content", "text"), ("summary", "text")],
                "name": "text_idx",
                "weights": {"title": 10, "content": 5, "summary": 3}
            }
        ]
    
    def _convert_id(self, id: str) -> Any:
        """
        ID 변환
        
        Args:
            id: 엔티티 ID
            
        Returns:
            Any: 변환된 ID
        """
        try:
            return ObjectId(id)
        except Exception:
            return id
    
    def _to_entity(self, document: Dict[str, Any]) -> News:
        """
        문서를 엔티티로 변환
        
        Args:
            document: MongoDB 문서
            
        Returns:
            News: 변환된 뉴스 엔티티
        """
        # ID 변환
        if "_id" in document:
            document["id"] = str(document["_id"])
            del document["_id"]
        
        # 엔티티 생성
        return News.from_dict(document)
    
    def _to_document(self, entity: News) -> Dict[str, Any]:
        """
        엔티티를 문서로 변환
        
        Args:
            entity: 뉴스 엔티티
            
        Returns:
            Dict[str, Any]: 변환된 문서
        """
        # 딕셔너리 변환
        document = entity.to_dict()
        
        # ID 처리
        if "id" in document:
            try:
                document["_id"] = ObjectId(document["id"])
            except Exception:
                document["_id"] = document["id"]
            del document["id"]
        
        return document
    
    async def find_by_url(self, url: str) -> Optional[News]:
        """
        URL로 뉴스 조회
        
        Args:
            url: 뉴스 URL
            
        Returns:
            Optional[News]: 조회된 뉴스 또는 None
        """
        return await self.find_one_by_query({"url": url})
    
    async def find_by_symbol(self, symbol: str, limit: int = 20, skip: int = 0) -> List[News]:
        """
        심볼로 뉴스 조회
        
        Args:
            symbol: 주식 심볼
            limit: 최대 개수
            skip: 건너뛸 개수
            
        Returns:
            List[News]: 조회된 뉴스 목록
        """
        return await self.find_by_query(
            {"symbols": symbol},
            skip=skip,
            limit=limit
        )
    
    async def find_by_source(self, source: str, limit: int = 20, skip: int = 0) -> List[News]:
        """
        소스로 뉴스 조회
        
        Args:
            source: 뉴스 소스
            limit: 최대 개수
            skip: 건너뛸 개수
            
        Returns:
            List[News]: 조회된 뉴스 목록
        """
        return await self.find_by_query(
            {"source": source},
            skip=skip,
            limit=limit
        )
    
    async def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 20,
        skip: int = 0
    ) -> List[News]:
        """
        날짜 범위로 뉴스 조회
        
        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
            limit: 최대 개수
            skip: 건너뛸 개수
            
        Returns:
            List[News]: 조회된 뉴스 목록
        """
        return await self.find_by_query(
            {
                "published_date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            },
            skip=skip,
            limit=limit
        )
    
    async def find_by_keyword(self, keyword: str, limit: int = 20, skip: int = 0) -> List[News]:
        """
        키워드로 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            limit: 최대 개수
            skip: 건너뛸 개수
            
        Returns:
            List[News]: 검색된 뉴스 목록
        """
        return await self.find_by_query(
            {"$text": {"$search": keyword}},
            skip=skip,
            limit=limit
        )
    
    async def find_by_criteria(self, criteria: NewsSearchCriteria) -> Tuple[List[News], int]:
        """
        검색 조건으로 뉴스 검색
        
        Args:
            criteria: 검색 조건
            
        Returns:
            Tuple[List[News], int]: 검색된 뉴스 목록과 총 개수
        """
        # 쿼리 생성
        query = criteria.to_query()
        
        # 정렬 설정
        sort = [("published_date", -1)]  # 기본: 발행일 내림차순
        
        # 키워드 검색인 경우 관련성 점수 추가
        projection = None
        if criteria.keyword:
            projection = {"score": {"$meta": "textScore"}}
            sort = [("score", {"$meta": "textScore"})]
        
        try:
            # 검색 실행
            cursor = self.collection.find(query, projection)
            
            # 정렬 및 페이지네이션 적용
            cursor = cursor.sort(sort)
            cursor = cursor.skip(criteria.get_skip()).limit(criteria.limit)
            
            # 결과 변환
            documents = await cursor.to_list(length=criteria.limit)
            news_list = [self._to_entity(doc) for doc in documents]
            
            # 총 개수 조회
            total = await self.count_by_query(query)
            
            return news_list, total
            
        except Exception as e:
            logger.error(f"검색 조건으로 뉴스 검색 실패: {str(e)}")
            return [], 0
    
    async def find_latest(self, limit: int = 20) -> List[News]:
        """
        최신 뉴스 조회
        
        Args:
            limit: 최대 개수
            
        Returns:
            List[News]: 최신 뉴스 목록
        """
        try:
            # 최신 뉴스 조회
            cursor = self.collection.find().sort("published_date", -1).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # 결과 변환
            return [self._to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"최신 뉴스 조회 실패: {str(e)}")
            return []
    
    async def update_sentiment(self, news_id: str, sentiment: Dict[str, Any]) -> bool:
        """
        뉴스 감성 업데이트
        
        Args:
            news_id: 뉴스 ID
            sentiment: 감성 정보
            
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            # ID 변환
            object_id = self._convert_id(news_id)
            
            # 업데이트
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$set": {"sentiment": sentiment}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"뉴스 감성 업데이트 실패: {str(e)}")
            return False
    
    async def get_sentiment_stats(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        감성 통계 조회
        
        Args:
            symbol: 주식 심볼 (None인 경우 전체)
            start_date: 시작 날짜 (None인 경우 제한 없음)
            end_date: 종료 날짜 (None인 경우 현재)
            
        Returns:
            Dict[str, Any]: 감성 통계
        """
        try:
            # 쿼리 생성
            match_stage = {}
            
            if symbol:
                match_stage["symbols"] = symbol
            
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date
                if end_date:
                    date_query["$lte"] = end_date
                match_stage["published_date"] = date_query
            
            # 감성 필드가 있는 뉴스만 선택
            match_stage["sentiment"] = {"$exists": True}
            
            # 집계 파이프라인
            pipeline = [
                {"$match": match_stage},
                {"$group": {
                    "_id": "$sentiment.label",
                    "count": {"$sum": 1},
                    "avg_score": {"$avg": "$sentiment.score"}
                }},
                {"$sort": {"count": -1}}
            ]
            
            # 집계 실행
            results = await self.aggregate(pipeline)
            
            # 결과 변환
            stats = {
                "total": 0,
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
                "neutral_ratio": 0.0,
                "avg_scores": {}
            }
            
            for result in results:
                label = result["_id"]
                count = result["count"]
                avg_score = result["avg_score"]
                
                stats[label] = count
                stats["total"] += count
                stats["avg_scores"][label] = avg_score
            
            # 비율 계산
            if stats["total"] > 0:
                stats["positive_ratio"] = stats["positive"] / stats["total"]
                stats["negative_ratio"] = stats["negative"] / stats["total"]
                stats["neutral_ratio"] = stats["neutral"] / stats["total"]
            
            return stats
            
        except Exception as e:
            logger.error(f"감성 통계 조회 실패: {str(e)}")
            return {
                "total": 0,
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
                "neutral_ratio": 0.0,
                "avg_scores": {}
            }
    
    async def get_sentiment_trend(
        self,
        symbol: Optional[str] = None,
        interval: str = 'day',
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        감성 트렌드 조회
        
        Args:
            symbol: 주식 심볼 (None인 경우 전체)
            interval: 집계 간격 ('hour', 'day', 'week', 'month')
            days: 조회 기간 (일)
            
        Returns:
            List[Dict[str, Any]]: 감성 트렌드
        """
        try:
            # 시간 범위 계산
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 쿼리 생성
            match_stage = {
                "published_date": {"$gte": start_date, "$lte": end_date},
                "sentiment": {"$exists": True}
            }
            
            if symbol:
                match_stage["symbols"] = symbol
            
            # 날짜 포맷 설정
            date_format = {
                'hour': '%Y-%m-%d %H:00:00',
                'day': '%Y-%m-%d',
                'week': '%Y-%U',
                'month': '%Y-%m'
            }.get(interval, '%Y-%m-%d')
            
            # 집계 파이프라인
            pipeline = [
                {"$match": match_stage},
                {"$group": {
                    "_id": {
                        "date": {"$dateToString": {"format": date_format, "date": "$published_date"}},
                        "sentiment": "$sentiment.label"
                    },
                    "count": {"$sum": 1},
                    "avg_score": {"$avg": "$sentiment.score"}
                }},
                {"$sort": {"_id.date": 1}}
            ]
            
            # 집계 실행
            results = await self.aggregate(pipeline)
            
            # 결과 변환
            trend_map = {}
            
            for result in results:
                date_str = result["_id"]["date"]
                sentiment = result["_id"]["sentiment"]
                count = result["count"]
                avg_score = result["avg_score"]
                
                if date_str not in trend_map:
                    trend_map[date_str] = {
                        "date": date_str,
                        "total": 0,
                        "positive": 0,
                        "negative": 0,
                        "neutral": 0,
                        "avg_scores": {}
                    }
                
                trend_map[date_str][sentiment] = count
                trend_map[date_str]["total"] += count
                trend_map[date_str]["avg_scores"][sentiment] = avg_score
            
            # 비율 계산 및 정렬
            trend_list = []
            
            for date_str, data in trend_map.items():
                if data["total"] > 0:
                    data["positive_ratio"] = data["positive"] / data["total"]
                    data["negative_ratio"] = data["negative"] / data["total"]
                    data["neutral_ratio"] = data["neutral"] / data["total"]
                else:
                    data["positive_ratio"] = 0.0
                    data["negative_ratio"] = 0.0
                    data["neutral_ratio"] = 0.0
                
                trend_list.append(data)
            
            # 날짜순 정렬
            trend_list.sort(key=lambda x: x["date"])
            
            return trend_list
            
        except Exception as e:
            logger.error(f"감성 트렌드 조회 실패: {str(e)}")
            return []
