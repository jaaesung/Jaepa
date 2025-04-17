"""
뉴스 저장소 통합 테스트

이 모듈은 뉴스 저장소와 데이터베이스 간의 통합을 테스트합니다.
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId

from domain.models.news import News
from infrastructure.repository.news_repository import NewsRepository


@pytest.mark.integration
@pytest.mark.database
class TestNewsRepositoryIntegration:
    """
    뉴스 저장소 통합 테스트 클래스
    """
    
    @pytest.fixture(autouse=True)
    async def setup_repository(self, async_mongo_client, async_mongo_db):
        """
        테스트 설정
        
        Args:
            async_mongo_client: 비동기 MongoDB 클라이언트 fixture
            async_mongo_db: 비동기 MongoDB 데이터베이스 fixture
        """
        # 저장소 생성
        self.repository = NewsRepository(
            client=async_mongo_client,
            db_name=async_mongo_db.name,
            collection_name="test_news"
        )
        
        # 인덱스 생성
        await self.repository.create_indexes()
        
        # 테스트 데이터
        self.test_news = [
            News(
                title="테스트 뉴스 1",
                url="https://example.com/news1",
                source="테스트 소스 1",
                published_date=datetime.now() - timedelta(days=1),
                content="테스트 뉴스 1의 내용입니다.",
                summary="테스트 뉴스 1의 요약입니다.",
                keywords=["테스트", "뉴스", "키워드1"],
                symbols=["AAPL"],
                categories=["기술"]
            ),
            News(
                title="테스트 뉴스 2",
                url="https://example.com/news2",
                source="테스트 소스 2",
                published_date=datetime.now() - timedelta(days=2),
                content="테스트 뉴스 2의 내용입니다.",
                summary="테스트 뉴스 2의 요약입니다.",
                keywords=["테스트", "뉴스", "키워드2"],
                symbols=["GOOGL"],
                categories=["경제"]
            ),
            News(
                title="테스트 뉴스 3",
                url="https://example.com/news3",
                source="테스트 소스 1",
                published_date=datetime.now() - timedelta(days=3),
                content="테스트 뉴스 3의 내용입니다.",
                summary="테스트 뉴스 3의 요약입니다.",
                keywords=["테스트", "뉴스", "키워드3"],
                symbols=["AAPL", "MSFT"],
                categories=["기술", "경제"]
            )
        ]
        
        # 테스트 데이터 저장
        self.saved_news = await self.repository.save_many(self.test_news)
        
        yield
        
        # 테스트 후 데이터 정리
        await async_mongo_db.drop_collection("test_news")
    
    async def test_find_by_id(self):
        """
        ID로 뉴스 조회 테스트
        """
        # 첫 번째 뉴스 ID로 조회
        news_id = self.saved_news[0].id
        news = await self.repository.find_by_id(news_id)
        
        # 검증
        assert news is not None
        assert news.id == news_id
        assert news.title == "테스트 뉴스 1"
        assert news.url == "https://example.com/news1"
        
        # 존재하지 않는 ID로 조회
        news = await self.repository.find_by_id("non_existent_id")
        
        # 검증
        assert news is None
    
    async def test_find_all(self):
        """
        모든 뉴스 조회 테스트
        """
        # 모든 뉴스 조회
        news_list = await self.repository.find_all()
        
        # 검증
        assert len(news_list) == 3
        
        # 정렬 확인 (기본: 발행일 내림차순)
        assert news_list[0].title == "테스트 뉴스 1"
        assert news_list[1].title == "테스트 뉴스 2"
        assert news_list[2].title == "테스트 뉴스 3"
        
        # 페이지네이션 테스트
        news_list = await self.repository.find_all(skip=1, limit=1)
        
        # 검증
        assert len(news_list) == 1
        assert news_list[0].title == "테스트 뉴스 2"
    
    async def test_find_by_url(self):
        """
        URL로 뉴스 조회 테스트
        """
        # URL로 조회
        news = await self.repository.find_by_url("https://example.com/news2")
        
        # 검증
        assert news is not None
        assert news.title == "테스트 뉴스 2"
        assert news.source == "테스트 소스 2"
        
        # 존재하지 않는 URL로 조회
        news = await self.repository.find_by_url("https://example.com/non_existent")
        
        # 검증
        assert news is None
    
    async def test_find_by_symbol(self):
        """
        심볼로 뉴스 조회 테스트
        """
        # 심볼로 조회
        news_list = await self.repository.find_by_symbol("AAPL")
        
        # 검증
        assert len(news_list) == 2
        assert news_list[0].title == "테스트 뉴스 1"
        assert news_list[1].title == "테스트 뉴스 3"
        
        # 다른 심볼로 조회
        news_list = await self.repository.find_by_symbol("GOOGL")
        
        # 검증
        assert len(news_list) == 1
        assert news_list[0].title == "테스트 뉴스 2"
        
        # 존재하지 않는 심볼로 조회
        news_list = await self.repository.find_by_symbol("UNKNOWN")
        
        # 검증
        assert len(news_list) == 0
    
    async def test_find_by_source(self):
        """
        소스로 뉴스 조회 테스트
        """
        # 소스로 조회
        news_list = await self.repository.find_by_source("테스트 소스 1")
        
        # 검증
        assert len(news_list) == 2
        assert news_list[0].title == "테스트 뉴스 1"
        assert news_list[1].title == "테스트 뉴스 3"
        
        # 다른 소스로 조회
        news_list = await self.repository.find_by_source("테스트 소스 2")
        
        # 검증
        assert len(news_list) == 1
        assert news_list[0].title == "테스트 뉴스 2"
        
        # 존재하지 않는 소스로 조회
        news_list = await self.repository.find_by_source("존재하지 않는 소스")
        
        # 검증
        assert len(news_list) == 0
    
    async def test_find_by_date_range(self):
        """
        날짜 범위로 뉴스 조회 테스트
        """
        # 날짜 범위 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=2)
        
        # 날짜 범위로 조회
        news_list = await self.repository.find_by_date_range(start_date, end_date)
        
        # 검증
        assert len(news_list) == 2
        assert news_list[0].title == "테스트 뉴스 1"
        assert news_list[1].title == "테스트 뉴스 2"
        
        # 다른 날짜 범위로 조회
        start_date = end_date - timedelta(days=5)
        end_date = end_date - timedelta(days=2)
        
        news_list = await self.repository.find_by_date_range(start_date, end_date)
        
        # 검증
        assert len(news_list) == 2
        assert news_list[0].title == "테스트 뉴스 2"
        assert news_list[1].title == "테스트 뉴스 3"
    
    async def test_find_latest(self):
        """
        최신 뉴스 조회 테스트
        """
        # 최신 뉴스 조회
        news_list = await self.repository.find_latest(limit=2)
        
        # 검증
        assert len(news_list) == 2
        assert news_list[0].title == "테스트 뉴스 1"
        assert news_list[1].title == "테스트 뉴스 2"
    
    async def test_update_sentiment(self):
        """
        뉴스 감성 업데이트 테스트
        """
        # 첫 번째 뉴스 ID
        news_id = self.saved_news[0].id
        
        # 감성 정보
        sentiment = {
            "label": "positive",
            "score": 0.85,
            "scores": {
                "positive": 0.85,
                "neutral": 0.10,
                "negative": 0.05
            }
        }
        
        # 감성 업데이트
        result = await self.repository.update_sentiment(news_id, sentiment)
        
        # 검증
        assert result is True
        
        # 업데이트된 뉴스 조회
        news = await self.repository.find_by_id(news_id)
        
        # 검증
        assert news.sentiment == sentiment
        assert news.sentiment["label"] == "positive"
        assert news.sentiment["score"] == 0.85
        
        # 존재하지 않는 ID로 업데이트
        result = await self.repository.update_sentiment("non_existent_id", sentiment)
        
        # 검증
        assert result is False
    
    async def test_get_sentiment_stats(self):
        """
        감성 통계 조회 테스트
        """
        # 감성 정보 업데이트
        await self.repository.update_sentiment(self.saved_news[0].id, {
            "label": "positive",
            "score": 0.85,
            "scores": {"positive": 0.85, "neutral": 0.10, "negative": 0.05}
        })
        
        await self.repository.update_sentiment(self.saved_news[1].id, {
            "label": "negative",
            "score": 0.75,
            "scores": {"positive": 0.15, "neutral": 0.10, "negative": 0.75}
        })
        
        await self.repository.update_sentiment(self.saved_news[2].id, {
            "label": "neutral",
            "score": 0.60,
            "scores": {"positive": 0.20, "neutral": 0.60, "negative": 0.20}
        })
        
        # 전체 감성 통계 조회
        stats = await self.repository.get_sentiment_stats()
        
        # 검증
        assert stats["total"] == 3
        assert stats["positive"] == 1
        assert stats["negative"] == 1
        assert stats["neutral"] == 1
        assert stats["positive_ratio"] == 1/3
        assert stats["negative_ratio"] == 1/3
        assert stats["neutral_ratio"] == 1/3
        assert "avg_scores" in stats
        
        # 심볼별 감성 통계 조회
        stats = await self.repository.get_sentiment_stats(symbol="AAPL")
        
        # 검증
        assert stats["total"] == 2
        assert stats["positive"] == 1
        assert stats["neutral"] == 1
        assert stats["negative"] == 0
        assert stats["positive_ratio"] == 0.5
        assert stats["neutral_ratio"] == 0.5
        assert stats["negative_ratio"] == 0.0
    
    async def test_get_sentiment_trend(self):
        """
        감성 트렌드 조회 테스트
        """
        # 감성 정보 업데이트
        await self.repository.update_sentiment(self.saved_news[0].id, {
            "label": "positive",
            "score": 0.85,
            "scores": {"positive": 0.85, "neutral": 0.10, "negative": 0.05}
        })
        
        await self.repository.update_sentiment(self.saved_news[1].id, {
            "label": "negative",
            "score": 0.75,
            "scores": {"positive": 0.15, "neutral": 0.10, "negative": 0.75}
        })
        
        await self.repository.update_sentiment(self.saved_news[2].id, {
            "label": "neutral",
            "score": 0.60,
            "scores": {"positive": 0.20, "neutral": 0.60, "negative": 0.20}
        })
        
        # 감성 트렌드 조회
        trend = await self.repository.get_sentiment_trend(interval="day", days=7)
        
        # 검증
        assert len(trend) > 0
        
        # 각 트렌드 항목 검증
        for item in trend:
            assert "date" in item
            assert "total" in item
            assert "positive" in item
            assert "negative" in item
            assert "neutral" in item
            assert "positive_ratio" in item
            assert "negative_ratio" in item
            assert "neutral_ratio" in item
            assert "avg_scores" in item
        
        # 심볼별 감성 트렌드 조회
        trend = await self.repository.get_sentiment_trend(symbol="AAPL", interval="day", days=7)
        
        # 검증
        assert len(trend) > 0
