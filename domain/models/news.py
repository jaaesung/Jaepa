"""
뉴스 도메인 모델 모듈

뉴스 관련 도메인 모델을 제공합니다.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class News:
    """
    뉴스 모델
    
    뉴스 기사 정보를 나타냅니다.
    """
    
    title: str
    url: str
    source: str
    published_date: datetime
    content: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    image_url: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    symbols: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    sentiment: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None
    
    def __post_init__(self):
        """
        초기화 후처리
        """
        # 문자열 날짜를 datetime으로 변환
        if isinstance(self.published_date, str):
            try:
                # ISO 형식 (예: "2023-01-01T12:00:00Z")
                self.published_date = datetime.fromisoformat(self.published_date.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # 다른 형식 시도 (예: "2023-01-01 12:00:00")
                    self.published_date = datetime.strptime(self.published_date, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # 기본값: 현재 시간
                    self.published_date = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        딕셔너리로 변환
        
        Returns:
            Dict[str, Any]: 딕셔너리 표현
        """
        result = {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "published_date": self.published_date.isoformat(),
            "keywords": self.keywords,
            "symbols": self.symbols,
            "categories": self.categories,
            "metadata": self.metadata
        }
        
        # 선택적 필드 추가
        if self.content:
            result["content"] = self.content
            
        if self.summary:
            result["summary"] = self.summary
            
        if self.author:
            result["author"] = self.author
            
        if self.image_url:
            result["image_url"] = self.image_url
            
        if self.sentiment:
            result["sentiment"] = self.sentiment
            
        if self.id:
            result["id"] = self.id
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'News':
        """
        딕셔너리에서 생성
        
        Args:
            data: 딕셔너리 데이터
            
        Returns:
            News: 생성된 뉴스 객체
        """
        # 필수 필드 확인
        required_fields = ["title", "url", "source", "published_date"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"필수 필드 누락: {field}")
        
        # ID 처리
        id_value = data.get("id") or data.get("_id")
        
        # 객체 생성
        return cls(
            title=data["title"],
            url=data["url"],
            source=data["source"],
            published_date=data["published_date"],
            content=data.get("content"),
            summary=data.get("summary"),
            author=data.get("author"),
            image_url=data.get("image_url"),
            keywords=data.get("keywords", []),
            symbols=data.get("symbols", []),
            categories=data.get("categories", []),
            sentiment=data.get("sentiment"),
            metadata=data.get("metadata", {}),
            id=id_value
        )


@dataclass
class NewsSearchCriteria:
    """
    뉴스 검색 조건
    
    뉴스 검색에 사용되는 조건을 나타냅니다.
    """
    
    keyword: Optional[str] = None
    source: Optional[str] = None
    symbol: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    author: Optional[str] = None
    sentiment: Optional[str] = None
    page: int = 1
    limit: int = 20
    
    def to_query(self) -> Dict[str, Any]:
        """
        MongoDB 쿼리로 변환
        
        Returns:
            Dict[str, Any]: MongoDB 쿼리
        """
        query = {}
        
        # 키워드 검색
        if self.keyword:
            query["$text"] = {"$search": self.keyword}
        
        # 소스 필터링
        if self.source:
            query["source"] = self.source
        
        # 심볼 필터링
        if self.symbol:
            query["symbols"] = self.symbol
        
        # 카테고리 필터링
        if self.category:
            query["categories"] = self.category
        
        # 날짜 범위 필터링
        date_query = {}
        if self.start_date:
            date_query["$gte"] = self.start_date
        if self.end_date:
            date_query["$lte"] = self.end_date
        if date_query:
            query["published_date"] = date_query
        
        # 작성자 필터링
        if self.author:
            query["author"] = self.author
        
        # 감성 필터링
        if self.sentiment:
            query["sentiment.label"] = self.sentiment
        
        return query
    
    def get_skip(self) -> int:
        """
        건너뛸 개수 계산
        
        Returns:
            int: 건너뛸 개수
        """
        return (self.page - 1) * self.limit
