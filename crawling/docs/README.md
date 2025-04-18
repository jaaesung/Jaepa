# JaePa 크롤링 모듈

JaePa 프로젝트의 데이터 크롤링 및 수집 모듈입니다.

## 개요

이 모듈은 금융 뉴스 사이트 및 주식 시장 데이터를 수집하여 분석에 필요한 데이터를 제공합니다.

## 주요 기능

### 뉴스 크롤링 (`news_crawler.py`)

- Reuters, Bloomberg, Financial Times, CNBC, WSJ 등 주요 금융 뉴스 사이트 데이터 수집
- 키워드 기반 검색 기능
- 최신 뉴스 자동 수집 기능
- 뉴스 본문 추출 및 전처리

### 감성 분석 (`sentiment_analyzer.py`)

- FinBERT 모델을 활용한 금융 뉴스 감성 분석
- 긍정/중립/부정 감성 점수 계산
- 감성 분석 결과의 신뢰도 평가

### 주식 데이터 수집 (`stock_data_crawler.py`)

- yfinance 라이브러리를 활용한 주식 데이터 수집
- CoinGecko API를 통한 암호화폐 데이터 수집
- 기술적 지표 계산 (이동평균선, RSI, 볼린저 밴드, MACD 등)

## 사용 방법

### 뉴스 크롤링

```python
from jaepa.crawling.news_crawler import NewsCrawler

# 뉴스 크롤러 인스턴스 생성
crawler = NewsCrawler()

# 키워드로 뉴스 검색
articles = crawler.search_news(keyword="tesla earnings", days=7)

# 최신 뉴스 수집
latest_articles = crawler.get_latest_news(sources=["reuters", "bloomberg"], count=10)
```

### 감성 분석

```python
from jaepa.crawling.sentiment_analyzer import SentimentAnalyzer

# 감성 분석기 인스턴스 생성
analyzer = SentimentAnalyzer()

# 텍스트 감성 분석
sentiment = analyzer.analyze("Tesla reported better than expected earnings this quarter.")
print(sentiment)  # {'positive': 0.85, 'neutral': 0.12, 'negative': 0.03}

# 여러 텍스트 분석
texts = ["Tesla reported losses", "Apple announces new product", "Market crashes"]
sentiments = analyzer.analyze_batch(texts)
```

### 주식 데이터 수집

```python
from jaepa.crawling.stock_data_crawler import StockDataCrawler

# 주식 데이터 크롤러 인스턴스 생성
stock_crawler = StockDataCrawler()

# 주식 데이터 수집
tesla_data = stock_crawler.get_stock_data("TSLA", start_date="2023-01-01")

# 암호화폐 데이터 수집
bitcoin_data = stock_crawler.get_crypto_data("bitcoin", days=30)

# 기술적 지표 계산
indicators = stock_crawler.calculate_indicators(tesla_data)
```

## 설정

크롤링 설정은 `config.json` 파일에서 관리됩니다. 다음과 같은 설정을 변경할 수 있습니다:

- 크롤링 대상 뉴스 소스
- 요청 간격 및 타임아웃
- 사용자 에이전트 설정
- 프록시 설정 (선택 사항)

## 의존성

- requests
- beautifulsoup4
- yfinance
- transformers (FinBERT 모델용)
- pymongo (데이터 저장용)
- pandas
