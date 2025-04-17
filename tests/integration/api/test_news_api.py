"""
뉴스 API 통합 테스트

이 모듈은 뉴스 API 엔드포인트를 테스트합니다.
"""
import pytest
import json
from datetime import datetime, timedelta

from domain.models.news import News


@pytest.mark.integration
@pytest.mark.api
class TestNewsAPI:
    """
    뉴스 API 통합 테스트 클래스
    """
    
    @pytest.fixture(autouse=True)
    async def setup_test_data(self, async_mongo_db, api_client):
        """
        테스트 데이터 설정
        
        Args:
            async_mongo_db: 비동기 MongoDB 데이터베이스 fixture
            api_client: FastAPI 테스트 클라이언트 fixture
        """
        self.api_client = api_client
        
        # 테스트 데이터
        self.test_news = [
            {
                "title": "테스트 뉴스 1",
                "url": "https://example.com/news1",
                "source": "테스트 소스 1",
                "published_date": datetime.now() - timedelta(days=1),
                "content": "테스트 뉴스 1의 내용입니다.",
                "summary": "테스트 뉴스 1의 요약입니다.",
                "keywords": ["테스트", "뉴스", "키워드1"],
                "symbols": ["AAPL"],
                "categories": ["기술"]
            },
            {
                "title": "테스트 뉴스 2",
                "url": "https://example.com/news2",
                "source": "테스트 소스 2",
                "published_date": datetime.now() - timedelta(days=2),
                "content": "테스트 뉴스 2의 내용입니다.",
                "summary": "테스트 뉴스 2의 요약입니다.",
                "keywords": ["테스트", "뉴스", "키워드2"],
                "symbols": ["GOOGL"],
                "categories": ["경제"]
            },
            {
                "title": "테스트 뉴스 3",
                "url": "https://example.com/news3",
                "source": "테스트 소스 1",
                "published_date": datetime.now() - timedelta(days=3),
                "content": "테스트 뉴스 3의 내용입니다.",
                "summary": "테스트 뉴스 3의 요약입니다.",
                "keywords": ["테스트", "뉴스", "키워드3"],
                "symbols": ["AAPL", "MSFT"],
                "categories": ["기술", "경제"]
            }
        ]
        
        # 데이터베이스에 테스트 데이터 저장
        collection = async_mongo_db["news"]
        
        # 기존 데이터 삭제
        await collection.delete_many({})
        
        # 테스트 데이터 삽입
        for news in self.test_news:
            # datetime 객체를 문자열로 변환
            if isinstance(news["published_date"], datetime):
                news["published_date"] = news["published_date"].isoformat()
            
            await collection.insert_one(news)
        
        # 인덱스 생성
        await collection.create_index([("url", 1)], unique=True)
        await collection.create_index([("published_date", -1)])
        await collection.create_index([("symbols", 1)])
        await collection.create_index([("source", 1)])
        await collection.create_index([("title", "text"), ("content", "text"), ("summary", "text")])
        
        yield
        
        # 테스트 후 데이터 정리
        await collection.delete_many({})
    
    def test_get_latest_news(self):
        """
        최신 뉴스 조회 API 테스트
        """
        # API 호출
        response = self.api_client.get("/api/news/latest")
        
        # 검증
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0
        
        # 첫 번째 뉴스 검증
        first_news = data["items"][0]
        assert "title" in first_news
        assert "url" in first_news
        assert "source" in first_news
        assert "published_date" in first_news
        
        # 페이지네이션 테스트
        response = self.api_client.get("/api/news/latest?limit=1")
        
        # 검증
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
    
    def test_get_news_by_id(self):
        """
        ID로 뉴스 조회 API 테스트
        """
        # 먼저 뉴스 목록 조회
        response = self.api_client.get("/api/news/latest")
        data = response.json()
        news_id = data["items"][0]["id"]
        
        # ID로 뉴스 조회
        response = self.api_client.get(f"/api/news/{news_id}")
        
        # 검증
        assert response.status_code == 200
        news = response.json()
        assert news["id"] == news_id
        assert "title" in news
        assert "url" in news
        assert "source" in news
        assert "published_date" in news
        
        # 존재하지 않는 ID로 조회
        response = self.api_client.get("/api/news/non_existent_id")
        
        # 검증
        assert response.status_code == 404
    
    def test_search_news(self):
        """
        뉴스 검색 API 테스트
        """
        # 키워드 검색
        response = self.api_client.get("/api/news/search?keyword=테스트")
        
        # 검증
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert len(data["items"]) > 0
        
        # 심볼 검색
        response = self.api_client.get("/api/news/search?symbol=AAPL")
        
        # 검증
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0
        for news in data["items"]:
            assert "AAPL" in news["symbols"]
        
        # 소스 검색
        response = self.api_client.get("/api/news/search?source=테스트 소스 1")
        
        # 검증
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0
        for news in data["items"]:
            assert news["source"] == "테스트 소스 1"
        
        # 카테고리 검색
        response = self.api_client.get("/api/news/search?category=기술")
        
        # 검증
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0
        for news in data["items"]:
            assert "기술" in news["categories"]
        
        # 복합 검색
        response = self.api_client.get("/api/news/search?symbol=AAPL&category=기술")
        
        # 검증
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0
        for news in data["items"]:
            assert "AAPL" in news["symbols"]
            assert "기술" in news["categories"]
    
    def test_get_news_sources(self):
        """
        뉴스 소스 목록 조회 API 테스트
        """
        # API 호출
        response = self.api_client.get("/api/news/sources")
        
        # 검증
        assert response.status_code == 200
        sources = response.json()
        assert isinstance(sources, list)
        assert len(sources) > 0
        assert "테스트 소스 1" in sources
        assert "테스트 소스 2" in sources
    
    def test_get_news_categories(self):
        """
        뉴스 카테고리 목록 조회 API 테스트
        """
        # API 호출
        response = self.api_client.get("/api/news/categories")
        
        # 검증
        assert response.status_code == 200
        categories = response.json()
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "기술" in categories
        assert "경제" in categories
    
    def test_get_news_by_symbol(self):
        """
        심볼별 뉴스 조회 API 테스트
        """
        # API 호출
        response = self.api_client.get("/api/news/symbol/AAPL")
        
        # 검증
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0
        for news in data["items"]:
            assert "AAPL" in news["symbols"]
        
        # 존재하지 않는 심볼로 조회
        response = self.api_client.get("/api/news/symbol/UNKNOWN")
        
        # 검증
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0
    
    def test_create_news(self):
        """
        뉴스 생성 API 테스트
        """
        # 새 뉴스 데이터
        new_news = {
            "title": "새로운 테스트 뉴스",
            "url": "https://example.com/new_news",
            "source": "테스트 소스 3",
            "published_date": datetime.now().isoformat(),
            "content": "새로운 테스트 뉴스의 내용입니다.",
            "summary": "새로운 테스트 뉴스의 요약입니다.",
            "keywords": ["새로운", "테스트", "뉴스"],
            "symbols": ["TSLA"],
            "categories": ["기술", "자동차"]
        }
        
        # API 호출
        response = self.api_client.post(
            "/api/news",
            json=new_news
        )
        
        # 검증
        assert response.status_code == 201
        created_news = response.json()
        assert created_news["title"] == new_news["title"]
        assert created_news["url"] == new_news["url"]
        assert created_news["source"] == new_news["source"]
        assert "id" in created_news
        
        # 중복 URL로 생성 시도
        response = self.api_client.post(
            "/api/news",
            json=new_news
        )
        
        # 검증
        assert response.status_code == 409  # 충돌
    
    def test_update_news(self):
        """
        뉴스 업데이트 API 테스트
        """
        # 먼저 뉴스 목록 조회
        response = self.api_client.get("/api/news/latest")
        data = response.json()
        news_id = data["items"][0]["id"]
        
        # 업데이트 데이터
        update_data = {
            "title": "업데이트된 뉴스 제목",
            "summary": "업데이트된 뉴스 요약입니다.",
            "keywords": ["업데이트", "테스트", "뉴스"]
        }
        
        # API 호출
        response = self.api_client.patch(
            f"/api/news/{news_id}",
            json=update_data
        )
        
        # 검증
        assert response.status_code == 200
        updated_news = response.json()
        assert updated_news["id"] == news_id
        assert updated_news["title"] == update_data["title"]
        assert updated_news["summary"] == update_data["summary"]
        assert updated_news["keywords"] == update_data["keywords"]
        
        # 존재하지 않는 ID로 업데이트
        response = self.api_client.patch(
            "/api/news/non_existent_id",
            json=update_data
        )
        
        # 검증
        assert response.status_code == 404
    
    def test_delete_news(self):
        """
        뉴스 삭제 API 테스트
        """
        # 새 뉴스 생성
        new_news = {
            "title": "삭제할 테스트 뉴스",
            "url": "https://example.com/delete_news",
            "source": "테스트 소스",
            "published_date": datetime.now().isoformat(),
            "content": "삭제할 테스트 뉴스의 내용입니다."
        }
        
        response = self.api_client.post(
            "/api/news",
            json=new_news
        )
        
        created_news = response.json()
        news_id = created_news["id"]
        
        # API 호출
        response = self.api_client.delete(f"/api/news/{news_id}")
        
        # 검증
        assert response.status_code == 204
        
        # 삭제 확인
        response = self.api_client.get(f"/api/news/{news_id}")
        assert response.status_code == 404
        
        # 존재하지 않는 ID로 삭제
        response = self.api_client.delete("/api/news/non_existent_id")
        
        # 검증
        assert response.status_code == 404
