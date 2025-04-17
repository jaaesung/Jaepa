"""
뉴스 도메인 모델 단위 테스트

이 모듈은 뉴스 도메인 모델 클래스를 테스트합니다.
"""
import pytest
from datetime import datetime, timedelta

from domain.models.news import News, NewsSearchCriteria


class TestNews:
    """
    뉴스 모델 테스트 클래스
    """
    
    def test_init(self):
        """
        초기화 테스트
        """
        # 필수 필드만으로 초기화
        news = News(
            title="테스트 뉴스",
            url="https://example.com/news",
            source="테스트 소스",
            published_date=datetime.now()
        )
        
        # 검증
        assert news.title == "테스트 뉴스"
        assert news.url == "https://example.com/news"
        assert news.source == "테스트 소스"
        assert isinstance(news.published_date, datetime)
        assert news.content is None
        assert news.summary is None
        assert news.author is None
        assert news.image_url is None
        assert news.keywords == []
        assert news.symbols == []
        assert news.categories == []
        assert news.sentiment is None
        assert news.metadata == {}
        assert news.id is None
        
        # 모든 필드로 초기화
        now = datetime.now()
        news = News(
            title="테스트 뉴스",
            url="https://example.com/news",
            source="테스트 소스",
            published_date=now,
            content="뉴스 내용",
            summary="뉴스 요약",
            author="작성자",
            image_url="https://example.com/image.jpg",
            keywords=["키워드1", "키워드2"],
            symbols=["AAPL", "GOOGL"],
            categories=["기술", "경제"],
            sentiment={"label": "positive", "score": 0.8},
            metadata={"views": 100},
            id="news123"
        )
        
        # 검증
        assert news.title == "테스트 뉴스"
        assert news.url == "https://example.com/news"
        assert news.source == "테스트 소스"
        assert news.published_date == now
        assert news.content == "뉴스 내용"
        assert news.summary == "뉴스 요약"
        assert news.author == "작성자"
        assert news.image_url == "https://example.com/image.jpg"
        assert news.keywords == ["키워드1", "키워드2"]
        assert news.symbols == ["AAPL", "GOOGL"]
        assert news.categories == ["기술", "경제"]
        assert news.sentiment == {"label": "positive", "score": 0.8}
        assert news.metadata == {"views": 100}
        assert news.id == "news123"
    
    def test_post_init(self):
        """
        초기화 후처리 테스트
        """
        # 문자열 날짜로 초기화
        news = News(
            title="테스트 뉴스",
            url="https://example.com/news",
            source="테스트 소스",
            published_date="2023-01-01T12:00:00Z"
        )
        
        # 검증
        assert isinstance(news.published_date, datetime)
        assert news.published_date.year == 2023
        assert news.published_date.month == 1
        assert news.published_date.day == 1
        assert news.published_date.hour == 12
        assert news.published_date.minute == 0
        assert news.published_date.second == 0
        
        # 다른 형식의 문자열 날짜
        news = News(
            title="테스트 뉴스",
            url="https://example.com/news",
            source="테스트 소스",
            published_date="2023-01-01 12:00:00"
        )
        
        # 검증
        assert isinstance(news.published_date, datetime)
        assert news.published_date.year == 2023
        assert news.published_date.month == 1
        assert news.published_date.day == 1
        assert news.published_date.hour == 12
        assert news.published_date.minute == 0
        assert news.published_date.second == 0
        
        # 잘못된 형식의 문자열 날짜
        before = datetime.now()
        news = News(
            title="테스트 뉴스",
            url="https://example.com/news",
            source="테스트 소스",
            published_date="invalid_date"
        )
        after = datetime.now()
        
        # 검증 (현재 시간으로 설정되었는지)
        assert isinstance(news.published_date, datetime)
        assert before <= news.published_date <= after
    
    def test_to_dict(self):
        """
        딕셔너리 변환 테스트
        """
        # 모든 필드가 있는 뉴스
        now = datetime.now()
        news = News(
            title="테스트 뉴스",
            url="https://example.com/news",
            source="테스트 소스",
            published_date=now,
            content="뉴스 내용",
            summary="뉴스 요약",
            author="작성자",
            image_url="https://example.com/image.jpg",
            keywords=["키워드1", "키워드2"],
            symbols=["AAPL", "GOOGL"],
            categories=["기술", "경제"],
            sentiment={"label": "positive", "score": 0.8},
            metadata={"views": 100},
            id="news123"
        )
        
        # 딕셔너리 변환
        data = news.to_dict()
        
        # 검증
        assert data["title"] == "테스트 뉴스"
        assert data["url"] == "https://example.com/news"
        assert data["source"] == "테스트 소스"
        assert data["published_date"] == now.isoformat()
        assert data["content"] == "뉴스 내용"
        assert data["summary"] == "뉴스 요약"
        assert data["author"] == "작성자"
        assert data["image_url"] == "https://example.com/image.jpg"
        assert data["keywords"] == ["키워드1", "키워드2"]
        assert data["symbols"] == ["AAPL", "GOOGL"]
        assert data["categories"] == ["기술", "경제"]
        assert data["sentiment"] == {"label": "positive", "score": 0.8}
        assert data["metadata"] == {"views": 100}
        assert data["id"] == "news123"
        
        # 일부 필드만 있는 뉴스
        news = News(
            title="테스트 뉴스",
            url="https://example.com/news",
            source="테스트 소스",
            published_date=now
        )
        
        # 딕셔너리 변환
        data = news.to_dict()
        
        # 검증
        assert data["title"] == "테스트 뉴스"
        assert data["url"] == "https://example.com/news"
        assert data["source"] == "테스트 소스"
        assert data["published_date"] == now.isoformat()
        assert data["keywords"] == []
        assert data["symbols"] == []
        assert data["categories"] == []
        assert data["metadata"] == {}
        assert "content" not in data
        assert "summary" not in data
        assert "author" not in data
        assert "image_url" not in data
        assert "sentiment" not in data
        assert "id" not in data
    
    def test_from_dict(self):
        """
        딕셔너리에서 생성 테스트
        """
        # 모든 필드가 있는 딕셔너리
        now = datetime.now()
        data = {
            "title": "테스트 뉴스",
            "url": "https://example.com/news",
            "source": "테스트 소스",
            "published_date": now.isoformat(),
            "content": "뉴스 내용",
            "summary": "뉴스 요약",
            "author": "작성자",
            "image_url": "https://example.com/image.jpg",
            "keywords": ["키워드1", "키워드2"],
            "symbols": ["AAPL", "GOOGL"],
            "categories": ["기술", "경제"],
            "sentiment": {"label": "positive", "score": 0.8},
            "metadata": {"views": 100},
            "id": "news123"
        }
        
        # 딕셔너리에서 생성
        news = News.from_dict(data)
        
        # 검증
        assert news.title == "테스트 뉴스"
        assert news.url == "https://example.com/news"
        assert news.source == "테스트 소스"
        assert isinstance(news.published_date, datetime)
        assert news.content == "뉴스 내용"
        assert news.summary == "뉴스 요약"
        assert news.author == "작성자"
        assert news.image_url == "https://example.com/image.jpg"
        assert news.keywords == ["키워드1", "키워드2"]
        assert news.symbols == ["AAPL", "GOOGL"]
        assert news.categories == ["기술", "경제"]
        assert news.sentiment == {"label": "positive", "score": 0.8}
        assert news.metadata == {"views": 100}
        assert news.id == "news123"
        
        # 필수 필드만 있는 딕셔너리
        data = {
            "title": "테스트 뉴스",
            "url": "https://example.com/news",
            "source": "테스트 소스",
            "published_date": now.isoformat()
        }
        
        # 딕셔너리에서 생성
        news = News.from_dict(data)
        
        # 검증
        assert news.title == "테스트 뉴스"
        assert news.url == "https://example.com/news"
        assert news.source == "테스트 소스"
        assert isinstance(news.published_date, datetime)
        assert news.content is None
        assert news.summary is None
        assert news.author is None
        assert news.image_url is None
        assert news.keywords == []
        assert news.symbols == []
        assert news.categories == []
        assert news.sentiment is None
        assert news.metadata == {}
        assert news.id is None
        
        # _id 필드가 있는 딕셔너리
        data = {
            "title": "테스트 뉴스",
            "url": "https://example.com/news",
            "source": "테스트 소스",
            "published_date": now.isoformat(),
            "_id": "news456"
        }
        
        # 딕셔너리에서 생성
        news = News.from_dict(data)
        
        # 검증
        assert news.id == "news456"
        
        # 필수 필드가 누락된 딕셔너리
        data = {
            "title": "테스트 뉴스",
            "url": "https://example.com/news"
            # source와 published_date 누락
        }
        
        # 예외 발생 확인
        with pytest.raises(ValueError):
            News.from_dict(data)


class TestNewsSearchCriteria:
    """
    뉴스 검색 조건 테스트 클래스
    """
    
    def test_init(self):
        """
        초기화 테스트
        """
        # 기본 초기화
        criteria = NewsSearchCriteria()
        
        # 검증
        assert criteria.keyword is None
        assert criteria.source is None
        assert criteria.symbol is None
        assert criteria.category is None
        assert criteria.start_date is None
        assert criteria.end_date is None
        assert criteria.author is None
        assert criteria.sentiment is None
        assert criteria.page == 1
        assert criteria.limit == 20
        
        # 모든 필드 초기화
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        criteria = NewsSearchCriteria(
            keyword="테스트",
            source="뉴스 소스",
            symbol="AAPL",
            category="기술",
            start_date=start_date,
            end_date=end_date,
            author="작성자",
            sentiment="positive",
            page=2,
            limit=10
        )
        
        # 검증
        assert criteria.keyword == "테스트"
        assert criteria.source == "뉴스 소스"
        assert criteria.symbol == "AAPL"
        assert criteria.category == "기술"
        assert criteria.start_date == start_date
        assert criteria.end_date == end_date
        assert criteria.author == "작성자"
        assert criteria.sentiment == "positive"
        assert criteria.page == 2
        assert criteria.limit == 10
    
    def test_to_query(self):
        """
        MongoDB 쿼리 변환 테스트
        """
        # 빈 조건
        criteria = NewsSearchCriteria()
        query = criteria.to_query()
        
        # 검증
        assert query == {}
        
        # 키워드 검색
        criteria = NewsSearchCriteria(keyword="테스트")
        query = criteria.to_query()
        
        # 검증
        assert "$text" in query
        assert query["$text"] == {"$search": "테스트"}
        
        # 소스 필터링
        criteria = NewsSearchCriteria(source="뉴스 소스")
        query = criteria.to_query()
        
        # 검증
        assert "source" in query
        assert query["source"] == "뉴스 소스"
        
        # 심볼 필터링
        criteria = NewsSearchCriteria(symbol="AAPL")
        query = criteria.to_query()
        
        # 검증
        assert "symbols" in query
        assert query["symbols"] == "AAPL"
        
        # 카테고리 필터링
        criteria = NewsSearchCriteria(category="기술")
        query = criteria.to_query()
        
        # 검증
        assert "categories" in query
        assert query["categories"] == "기술"
        
        # 날짜 범위 필터링
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        criteria = NewsSearchCriteria(start_date=start_date, end_date=end_date)
        query = criteria.to_query()
        
        # 검증
        assert "published_date" in query
        assert query["published_date"]["$gte"] == start_date
        assert query["published_date"]["$lte"] == end_date
        
        # 작성자 필터링
        criteria = NewsSearchCriteria(author="작성자")
        query = criteria.to_query()
        
        # 검증
        assert "author" in query
        assert query["author"] == "작성자"
        
        # 감성 필터링
        criteria = NewsSearchCriteria(sentiment="positive")
        query = criteria.to_query()
        
        # 검증
        assert "sentiment.label" in query
        assert query["sentiment.label"] == "positive"
        
        # 복합 조건
        criteria = NewsSearchCriteria(
            keyword="테스트",
            source="뉴스 소스",
            symbol="AAPL",
            start_date=start_date,
            end_date=end_date,
            sentiment="positive"
        )
        query = criteria.to_query()
        
        # 검증
        assert "$text" in query
        assert "source" in query
        assert "symbols" in query
        assert "published_date" in query
        assert "sentiment.label" in query
    
    def test_get_skip(self):
        """
        건너뛸 개수 계산 테스트
        """
        # 첫 페이지
        criteria = NewsSearchCriteria(page=1, limit=20)
        skip = criteria.get_skip()
        
        # 검증
        assert skip == 0
        
        # 두 번째 페이지
        criteria = NewsSearchCriteria(page=2, limit=20)
        skip = criteria.get_skip()
        
        # 검증
        assert skip == 20
        
        # 세 번째 페이지, 다른 제한
        criteria = NewsSearchCriteria(page=3, limit=10)
        skip = criteria.get_skip()
        
        # 검증
        assert skip == 20
