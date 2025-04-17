# 제파(JaePa) 프로젝트 의존성 주입(DI) 패턴 구현

이 문서는 제파(JaePa) 프로젝트에 의존성 주입(Dependency Injection) 패턴을 도입하여 모듈 간 결합도를 낮추고, 테스트 용이성과 확장성을 향상시키는 방법을 설명합니다.

## 목차

1. [개요](#개요)
2. [구현된 인터페이스](#구현된-인터페이스)
3. [의존성 주입 컨테이너](#의존성-주입-컨테이너)
4. [애플리케이션 부트스트랩](#애플리케이션-부트스트랩)
5. [API 엔드포인트에서 의존성 주입 사용](#api-엔드포인트에서-의존성-주입-사용)
6. [테스트에서 의존성 주입 사용](#테스트에서-의존성-주입-사용)
7. [설치 및 설정](#설치-및-설정)

## 개요

의존성 주입(DI)은 객체가 필요로 하는 의존성을 외부에서 주입받는 디자인 패턴입니다. 이 패턴을 통해 다음과 같은 이점을 얻을 수 있습니다:

- **결합도 감소**: 모듈 간 직접적인 의존성을 제거하여 결합도를 낮춥니다.
- **테스트 용이성**: 실제 구현체 대신 모의 객체(mock)를 주입하여 단위 테스트를 쉽게 작성할 수 있습니다.
- **코드 재사용성**: 동일한 인터페이스를 구현한 다양한 구현체를 쉽게 교체할 수 있습니다.
- **관심사 분리**: 객체 생성과 사용을 분리하여 단일 책임 원칙을 준수할 수 있습니다.

제파 프로젝트에서는 `dependency_injector` 라이브러리를 사용하여 의존성 주입 패턴을 구현했습니다.

## 구현된 인터페이스

### 데이터베이스 인터페이스

```python
from core.interfaces import DatabaseClient, MongoDBClient

# 인터페이스 구현
class MyMongoDBClient(MongoDBClient):
    def connect(self) -> bool:
        # 구현...
        
    def get_database(self, db_name: Optional[str] = None) -> Any:
        # 구현...
        
    # 기타 메서드 구현...
```

### HTTP 클라이언트 인터페이스

```python
from core.interfaces import HttpClient

# 인터페이스 구현
class MyHttpClient(HttpClient):
    def get(self, url: str, params: Optional[Dict[str, Any]] = None, 
           headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        # 구현...
        
    # 기타 메서드 구현...
```

### 뉴스 소스 관리자 인터페이스

```python
from core.interfaces import NewsSourceManager, NewsSource

# 인터페이스 구현
class MyNewsSourceManager(NewsSourceManager):
    def register_source(self, source: NewsSource) -> None:
        # 구현...
        
    # 기타 메서드 구현...
```

### 감성 분석기 인터페이스

```python
from core.interfaces import SentimentAnalyzer

# 인터페이스 구현
class MySentimentAnalyzer(SentimentAnalyzer):
    def analyze_text(self, text: str) -> Dict[str, Any]:
        # 구현...
        
    # 기타 메서드 구현...
```

## 의존성 주입 컨테이너

의존성 주입 컨테이너는 `core/di.py` 파일에 정의되어 있습니다. 이 컨테이너는 다음과 같은 기능을 제공합니다:

- 싱글톤 패턴으로 관리되는 공유 리소스 (데이터베이스 연결 등)
- 팩토리 패턴으로 생성되는 서비스 객체
- 설정 주입을 통한 환경별 동작 변경 지원

```python
from core import container

# 싱글톤 인스턴스 가져오기
mongodb_client = container.mongodb_client()
http_client = container.http_client()

# 팩토리 인스턴스 생성
news_crawler = container.news_crawler()
sentiment_analysis_service = container.sentiment_analysis_service()
```

## 애플리케이션 부트스트랩

애플리케이션 부트스트랩 로직은 `bootstrap.py` 파일에 정의되어 있습니다. 이 파일은 다음과 같은 기능을 수행합니다:

- 설정 로드
- 로깅 설정
- 데이터베이스 연결
- 의존성 주입 컨테이너 초기화
- 구현체 등록

```python
from bootstrap import bootstrap_app

# 애플리케이션 부트스트랩
bootstrap_app()
```

## API 엔드포인트에서 의존성 주입 사용

API 엔드포인트에서는 `@inject` 데코레이터와 `Depends(Provide[...])` 구문을 사용하여 의존성을 주입받을 수 있습니다:

```python
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from core import container
from core.interfaces import SentimentAnalyzer

router = APIRouter()

@router.get("/analyze")
@inject
async def analyze_text(
    text: str,
    analyzer: SentimentAnalyzer = Depends(Provide[container.sentiment_analyzer])
):
    result = analyzer.analyze_text(text)
    return result
```

## 테스트에서 의존성 주입 사용

테스트에서는 실제 구현체 대신 모의 객체(mock)를 주입하여 단위 테스트를 작성할 수 있습니다:

```python
from unittest import TestCase, mock
from core import container

class TestNewsService(TestCase):
    def setUp(self):
        # 모의 객체 생성
        self.mock_http_client = mock.Mock()
        self.mock_db_client = mock.Mock()
        
        # 의존성 오버라이드
        container.http_client.override(self.mock_http_client)
        container.mongodb_client.override(self.mock_db_client)
        
        # 테스트 대상 서비스 생성
        self.news_service = container.news_crawler()
    
    def test_search_news(self):
        # 모의 객체 동작 설정
        self.mock_http_client.get.return_value = {"articles": [...]}
        
        # 테스트 실행
        result = self.news_service.search_news("test")
        
        # 검증
        self.assertEqual(len(result), 10)
        self.mock_http_client.get.assert_called_once()
```

## 설치 및 설정

의존성 주입 패턴을 사용하기 위해 필요한 패키지를 설치합니다:

```bash
# 스크립트 실행 권한 부여
chmod +x install_dependencies.sh

# 스크립트 실행
./install_dependencies.sh
```

또는 직접 패키지를 설치할 수 있습니다:

```bash
pip install dependency-injector pydantic-settings
```

## 마이그레이션 가이드

기존 코드를 의존성 주입 패턴으로 마이그레이션하는 방법:

1. 인터페이스 정의: 기존 클래스의 인터페이스를 추상 클래스로 정의합니다.
2. 구현체 작성: 인터페이스를 구현하는 구현체를 작성합니다.
3. 의존성 주입 컨테이너에 등록: 구현체를 의존성 주입 컨테이너에 등록합니다.
4. 의존성 주입 사용: 기존 코드에서 직접 객체를 생성하는 대신 의존성 주입을 사용합니다.

예시:

```python
# 기존 코드
class NewsService:
    def __init__(self):
        self.http_client = HttpClient()  # 직접 생성
        self.db_client = MongoDBClient()  # 직접 생성

# 마이그레이션 후
class NewsService:
    def __init__(self, http_client: HttpClient, db_client: MongoDBClient):
        self.http_client = http_client  # 주입받음
        self.db_client = db_client  # 주입받음
```
