"""
감성 분석 저장소 모듈

감성 분석 데이터 저장소를 제공합니다.
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from bson import ObjectId

from infrastructure.database.database_client import DatabaseClientInterface
from infrastructure.repository.repository import BaseMongoRepository
from domain.models.sentiment import SentimentAnalysis, SentimentTrend

# 로깅 설정
logger = logging.getLogger(__name__)


class SentimentRepository(BaseMongoRepository[SentimentAnalysis, str]):
    """
    감성 분석 저장소
    
    감성 분석 데이터 저장소를 구현합니다.
    """
    
    def __init__(self, client: DatabaseClientInterface, db_name: str, collection_name: str = "sentiment_analysis"):
        """
        SentimentRepository 초기화
        
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
            # 텍스트 ID 인덱스
            {
                "keys": [("text_id", 1)],
                "name": "text_id_idx"
            },
            # 텍스트 유형 인덱스
            {
                "keys": [("text_type", 1)],
                "name": "text_type_idx"
            },
            # 감성 레이블 인덱스
            {
                "keys": [("label", 1)],
                "name": "label_idx"
            },
            # 분석 시간 인덱스
            {
                "keys": [("analyzed_at", -1)],
                "name": "analyzed_at_idx"
            },
            # 복합 인덱스: 텍스트 ID + 텍스트 유형
            {
                "keys": [("text_id", 1), ("text_type", 1)],
                "name": "text_id_type_idx",
                "unique": True
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
    
    def _to_entity(self, document: Dict[str, Any]) -> SentimentAnalysis:
        """
        문서를 엔티티로 변환
        
        Args:
            document: MongoDB 문서
            
        Returns:
            SentimentAnalysis: 변환된 감성 분석 엔티티
        """
        # ID 변환
        if "_id" in document:
            document["id"] = str(document["_id"])
            del document["_id"]
        
        # 엔티티 생성
        return SentimentAnalysis.from_dict(document)
    
    def _to_document(self, entity: SentimentAnalysis) -> Dict[str, Any]:
        """
        엔티티를 문서로 변환
        
        Args:
            entity: 감성 분석 엔티티
            
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
    
    async def find_by_text_id(self, text_id: str, text_type: str = "news") -> Optional[SentimentAnalysis]:
        """
        텍스트 ID로 감성 분석 조회
        
        Args:
            text_id: 텍스트 ID
            text_type: 텍스트 유형
            
        Returns:
            Optional[SentimentAnalysis]: 조회된 감성 분석 또는 None
        """
        return await self.find_one_by_query({
            "text_id": text_id,
            "text_type": text_type
        })
    
    async def find_by_label(self, label: str, limit: int = 20, skip: int = 0) -> List[SentimentAnalysis]:
        """
        감성 레이블로 감성 분석 조회
        
        Args:
            label: 감성 레이블
            limit: 최대 개수
            skip: 건너뛸 개수
            
        Returns:
            List[SentimentAnalysis]: 조회된 감성 분석 목록
        """
        return await self.find_by_query(
            {"label": label},
            skip=skip,
            limit=limit
        )
    
    async def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        text_type: Optional[str] = None,
        limit: int = 20,
        skip: int = 0
    ) -> List[SentimentAnalysis]:
        """
        날짜 범위로 감성 분석 조회
        
        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
            text_type: 텍스트 유형 (None인 경우 모든 유형)
            limit: 최대 개수
            skip: 건너뛸 개수
            
        Returns:
            List[SentimentAnalysis]: 조회된 감성 분석 목록
        """
        # 쿼리 생성
        query = {
            "analyzed_at": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        if text_type:
            query["text_type"] = text_type
        
        return await self.find_by_query(
            query,
            skip=skip,
            limit=limit
        )
    
    async def get_sentiment_stats(
        self,
        text_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        감성 통계 조회
        
        Args:
            text_type: 텍스트 유형 (None인 경우 모든 유형)
            start_date: 시작 날짜 (None인 경우 제한 없음)
            end_date: 종료 날짜 (None인 경우 현재)
            
        Returns:
            Dict[str, Any]: 감성 통계
        """
        try:
            # 쿼리 생성
            match_stage = {}
            
            if text_type:
                match_stage["text_type"] = text_type
            
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date
                if end_date:
                    date_query["$lte"] = end_date
                match_stage["analyzed_at"] = date_query
            
            # 집계 파이프라인
            pipeline = [
                {"$match": match_stage},
                {"$group": {
                    "_id": "$label",
                    "count": {"$sum": 1},
                    "avg_score": {"$avg": "$score"}
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


class SentimentTrendRepository(BaseMongoRepository[SentimentTrend, str]):
    """
    감성 트렌드 저장소
    
    감성 트렌드 데이터 저장소를 구현합니다.
    """
    
    def __init__(self, client: DatabaseClientInterface, db_name: str, collection_name: str = "sentiment_trends"):
        """
        SentimentTrendRepository 초기화
        
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
            # 심볼 인덱스
            {
                "keys": [("symbol", 1)],
                "name": "symbol_idx"
            },
            # 날짜 인덱스
            {
                "keys": [("date", -1)],
                "name": "date_idx"
            },
            # 복합 인덱스: 심볼 + 날짜
            {
                "keys": [("symbol", 1), ("date", -1)],
                "name": "symbol_date_idx",
                "unique": True
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
    
    def _to_entity(self, document: Dict[str, Any]) -> SentimentTrend:
        """
        문서를 엔티티로 변환
        
        Args:
            document: MongoDB 문서
            
        Returns:
            SentimentTrend: 변환된 감성 트렌드 엔티티
        """
        # ID 변환
        if "_id" in document:
            document["id"] = str(document["_id"])
            del document["_id"]
        
        # 엔티티 생성
        return SentimentTrend.from_dict(document)
    
    def _to_document(self, entity: SentimentTrend) -> Dict[str, Any]:
        """
        엔티티를 문서로 변환
        
        Args:
            entity: 감성 트렌드 엔티티
            
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
    
    async def find_by_symbol(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 30,
        skip: int = 0
    ) -> List[SentimentTrend]:
        """
        심볼로 감성 트렌드 조회
        
        Args:
            symbol: 주식 심볼
            start_date: 시작 날짜 (None인 경우 제한 없음)
            end_date: 종료 날짜 (None인 경우 현재)
            limit: 최대 개수
            skip: 건너뛸 개수
            
        Returns:
            List[SentimentTrend]: 조회된 감성 트렌드 목록
        """
        # 쿼리 생성
        query = {"symbol": symbol}
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["date"] = date_query
        
        # 정렬 및 페이지네이션
        cursor = self.collection.find(query).sort("date", -1).skip(skip).limit(limit)
        
        try:
            # 결과 조회
            documents = await cursor.to_list(length=limit)
            
            # 엔티티 변환
            return [self._to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"심볼로 감성 트렌드 조회 실패: {str(e)}")
            return []
    
    async def get_latest_trend(self, symbol: str) -> Optional[SentimentTrend]:
        """
        최신 감성 트렌드 조회
        
        Args:
            symbol: 주식 심볼
            
        Returns:
            Optional[SentimentTrend]: 최신 감성 트렌드 또는 None
        """
        try:
            # 최신 트렌드 조회
            document = await self.collection.find_one(
                {"symbol": symbol},
                sort=[("date", -1)]
            )
            
            if document:
                return self._to_entity(document)
            return None
            
        except Exception as e:
            logger.error(f"최신 감성 트렌드 조회 실패: {str(e)}")
            return None
    
    async def get_sentiment_summary(
        self,
        symbol: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        감성 요약 조회
        
        Args:
            symbol: 주식 심볼
            days: 조회 기간 (일)
            
        Returns:
            Dict[str, Any]: 감성 요약
        """
        try:
            # 시간 범위 계산
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 트렌드 조회
            trends = await self.find_by_symbol(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                limit=days
            )
            
            if not trends:
                return {
                    "symbol": symbol,
                    "period": f"{days} days",
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_count": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0,
                    "positive_ratio": 0.0,
                    "negative_ratio": 0.0,
                    "neutral_ratio": 0.0,
                    "average_score": 0.0,
                    "trend": []
                }
            
            # 요약 계산
            total_count = sum(trend.total_count for trend in trends)
            positive_count = sum(trend.positive_count for trend in trends)
            negative_count = sum(trend.negative_count for trend in trends)
            neutral_count = sum(trend.neutral_count for trend in trends)
            
            # 비율 계산
            positive_ratio = positive_count / total_count if total_count > 0 else 0.0
            negative_ratio = negative_count / total_count if total_count > 0 else 0.0
            neutral_ratio = neutral_count / total_count if total_count > 0 else 0.0
            
            # 평균 점수 계산
            weighted_scores = sum(trend.average_score * trend.total_count for trend in trends)
            average_score = weighted_scores / total_count if total_count > 0 else 0.0
            
            # 트렌드 데이터 변환
            trend_data = [
                {
                    "date": trend.date.isoformat(),
                    "total_count": trend.total_count,
                    "positive_count": trend.positive_count,
                    "negative_count": trend.negative_count,
                    "neutral_count": trend.neutral_count,
                    "positive_ratio": trend.positive_ratio,
                    "negative_ratio": trend.negative_ratio,
                    "neutral_ratio": trend.neutral_ratio,
                    "average_score": trend.average_score
                }
                for trend in trends
            ]
            
            # 날짜순 정렬
            trend_data.sort(key=lambda x: x["date"])
            
            return {
                "symbol": symbol,
                "period": f"{days} days",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_count": total_count,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "positive_ratio": positive_ratio,
                "negative_ratio": negative_ratio,
                "neutral_ratio": neutral_ratio,
                "average_score": average_score,
                "trend": trend_data
            }
            
        except Exception as e:
            logger.error(f"감성 요약 조회 실패: {str(e)}")
            return {
                "symbol": symbol,
                "period": f"{days} days",
                "error": str(e)
            }
