# 제파(JaePa) 뉴스 크롤링 모듈

이 프로젝트는 제파(JaePa) 프로젝트의 뉴스 크롤링 모듈을 단일 책임 원칙(SRP)에 따라 리팩토링하고, 비동기 처리를 통해 성능을 최적화한 것입니다.

## 주요 기능

- 여러 뉴스 소스(RSS, API 등)에서 뉴스 수집
- 비동기 HTTP 요청 처리로 성능 최적화
- 기사 내용 추출 및 정규화
- 키워드 추출 및 중복 제거
- MongoDB를 사용한 기사 저장 및 조회

## 구조

프로젝트는 다음과 같은 구조로 구성되어 있습니다:

```
core/crawler/
  ├── __init__.py
  ├── interfaces.py       # 인터페이스 정의
  ├── exceptions.py       # 예외 클래스 정의
  ├── http_client.py      # HTTP 요청 처리
  ├── news_source_manager.py  # 뉴스 소스 관리
  ├── rss_processor.py    # RSS 피드 처리
  ├── article_processor.py  # 기사 처리
  ├── rss_news_source.py  # RSS 뉴스 소스 구현
  ├── factory.py          # 팩토리 클래스
  └── news_crawler.py     # 메인 뉴스 크롤러

infrastructure/repository/
  ├── __init__.py
  └── article_repository.py  # 기사 저장소

tests/
  └── core/crawler/
      ├── __init__.py
      └── test_http_client.py  # HTTP 클라이언트 테스트

examples/
  └── news_crawler_example.py  # 사용 예제
```

## 설치

1. 필요한 패키지 설치:

```bash
pip install -r requirements.txt
```

2. MongoDB 설정:

```bash
# .env 파일 생성
echo "MONGO_URI=mongodb://localhost:27017/" > .env
echo "MONGO_DB_NAME=jaepa" >> .env
```

## 사용 방법

### 기본 사용법

```python
import asyncio
from core.crawler.factory import NewsCrawlerFactory
from core.crawler.news_crawler import NewsCrawler

async def main():
    # 크롤러 구성 요소 생성
    components = await NewsCrawlerFactory.create_complete_crawler()
    
    # 뉴스 크롤러 생성
    crawler = NewsCrawler(
        news_source_manager=components['news_source_manager'],
        article_processor=components['article_processor'],
        article_repository=components['article_repository']
    )
    
    # 최신 뉴스 가져오기
    latest_news = await crawler.get_latest_news(count=10)
    
    # 키워드로 뉴스 검색
    search_results = await crawler.search_news(keyword="AAPL", days=7, count=10)
    
    # 주식 심볼로 뉴스 가져오기
    symbol_news = await crawler.get_news_by_symbol(symbol="AAPL", days=7, count=10)
    
    # 리소스 정리
    await crawler.close()

# 비동기 이벤트 루프 실행
asyncio.run(main())
```

### 예제 실행

```bash
python examples/news_crawler_example.py
```

## 테스트

```bash
# 모든 테스트 실행
pytest

# 특정 모듈 테스트
pytest tests/core/crawler/test_http_client.py
```

## 주요 클래스 설명

### AsyncHttpClient

비동기 HTTP 요청을 처리하는 클래스입니다. aiohttp를 사용하여 병렬 요청을 처리하고, 재시도 로직과 레이트 리밋 관리 기능을 제공합니다.

### NewsSourceManager

여러 뉴스 소스를 관리하고 통합 검색 기능을 제공하는 클래스입니다. 각 소스에서 비동기로 뉴스를 수집하고 결과를 통합합니다.

### RssProcessor

RSS 피드를 파싱하고 처리하는 클래스입니다. feedparser를 사용하여 RSS 피드를 파싱하고, 항목을 뉴스 기사 형식으로 변환합니다.

### ArticleProcessor

기사 내용을 추출하고 처리하는 클래스입니다. BeautifulSoup을 사용하여 HTML에서 기사 내용을 추출하고, NLTK를 사용하여 키워드를 추출합니다.

### MongoArticleRepository

MongoDB를 사용하여 기사를 저장하고 조회하는 클래스입니다. motor를 사용하여 비동기 MongoDB 작업을 처리합니다.

### NewsCrawler

모든 구성 요소를 통합한 메인 뉴스 크롤러 클래스입니다. 최신 뉴스 가져오기, 키워드 검색, 주식 심볼 검색 등의 기능을 제공합니다.

## 의존성

- Python 3.8 이상
- aiohttp: 비동기 HTTP 요청
- motor: 비동기 MongoDB 드라이버
- feedparser: RSS 피드 파싱
- beautifulsoup4: HTML 파싱
- nltk: 자연어 처리
- pytest: 테스트 프레임워크

## 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다.
