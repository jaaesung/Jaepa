# 뉴스 크롤링 테스트 가이드

이 디렉토리에는 JaePa 프로젝트의 뉴스 크롤링 관련 테스트 파일들이 포함되어 있습니다. 테스트는 API별로 분리되어 있어 개별적으로 실행하거나 전체를 한 번에 실행할 수 있습니다.

## 테스트 구성

테스트 파일은 다음과 같이 API별로 분리되어 있습니다:

- `test_rss_crawler_api.py`: RSS 크롤링 API 테스트
- `test_finnhub_api.py`: Finnhub API 테스트
- `test_newsdata_api.py`: NewsData.io API 테스트
- `test_sentiment_analysis_api.py`: 감성 분석 API 테스트
- `test_news_combiner_api.py`: 뉴스 통합 및 중복 제거 API 테스트
- `test_news_integrator_api.py`: 뉴스 통합 API 테스트
- `test_news_integrator.py`: 뉴스 통합 시스템 통합 테스트

## 테스트 실행 방법

### 특정 API 테스트 실행

특정 API의 테스트만 실행하려면 다음 명령을 사용합니다:

```bash
python run_crawling_tests.py --api=rss
```

가능한 API 옵션:
- `rss`: RSS 크롤링 API 테스트
- `finnhub`: Finnhub API 테스트
- `newsdata`: NewsData.io API 테스트
- `sentiment`: 감성 분석 API 테스트
- `combiner`: 뉴스 통합 및 중복 제거 API 테스트
- `integrator_api`: 뉴스 통합 API 테스트
- `integrator`: 뉴스 통합 시스템 통합 테스트
- `all`: 모든 테스트 실행 (기본값)

### 모든 API 테스트 실행

모든 API 테스트를 순서대로 실행하려면 다음 명령을 사용합니다:

```bash
python run_all_tests.py
```

### 테스트 결과 저장

테스트 결과를 파일로 저장하려면 `--save` 옵션을 추가합니다:

```bash
python run_crawling_tests.py --api=rss --save
```

또는 모든 테스트 실행 시:

```bash
python run_all_tests.py --save
```

결과는 `results` 디렉토리에 저장됩니다.

### 상세 출력

자세한 테스트 출력을 보려면 `--verbose` 옵션을 추가합니다:

```bash
python run_crawling_tests.py --api=rss --verbose
```

### 테스트 수집만 수행

테스트를 실행하지 않고 어떤 테스트 케이스가 있는지만 확인하려면 `--collect-only` 옵션을 사용합니다:

```bash
python run_crawling_tests.py --api=rss --collect-only
```

## 테스트 개발 가이드

### 새 테스트 추가

새로운 테스트를 추가할 때는 다음 규칙을 따라주세요:

1. API 기능별로 테스트 파일을 분리합니다.
2. 테스트 클래스는 `unittest.TestCase`를 상속받아야 합니다.
3. 각 테스트 메서드는 `test_`로 시작해야 합니다.
4. 필요한 설정과 정리 작업은 `setUp`과 `tearDown` 메서드에 구현합니다.
5. 외부 서비스에 의존하는 테스트는 `unittest.mock`을 사용하여 모킹합니다.

### 통합 테스트 개발

통합 테스트를 개발할 때는 다음 사항을 고려해주세요:

1. 통합 테스트는 `test_news_integrator.py`에 구현합니다.
2. 가능한 모든 의존성은 모킹하여 실제 API 호출을 피합니다.
3. 에지 케이스와 오류 상황을 테스트에 포함시킵니다.
4. 테스트 데이터는 `test_data` 디렉토리에 저장합니다.

## 테스트 의존성 순서

테스트는 다음 순서로 실행하는 것이 좋습니다:

1. RSS 크롤링 API 테스트
2. Finnhub API 테스트
3. NewsData.io API 테스트
4. 감성 분석 API 테스트
5. 뉴스 통합 및 중복 제거 API 테스트
6. 뉴스 통합 API 테스트
7. 뉴스 통합 시스템 통합 테스트

이 순서는 `run_all_tests.py` 스크립트에 반영되어 있습니다.
