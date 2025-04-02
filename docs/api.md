# JaePa API 문서

JaePa의 RESTful API 엔드포인트 및 사용법에 대한 문서입니다.

## 기본 정보

- 기본 URL: `http://localhost:5000/api/v1`
- 모든 응답은 JSON 형식으로 반환됩니다.
- 인증이 필요한 엔드포인트는 요청 헤더에 JWT 토큰을 포함해야 합니다.

### 인증

API 인증은 JWT(JSON Web Token)를 사용합니다.

```
Authorization: Bearer <your_token>
```

## 엔드포인트

### 인증 (Authentication)

#### 사용자 등록

```
POST /auth/signup
```

**요청 본문**:

```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "securepassword"
}
```

**응답**:

```json
{
  "status": "success",
  "message": "User registered successfully",
  "user_id": "60a1e2c3d4e5f6a7b8c9d0e1"
}
```

#### 로그인

```
POST /auth/login
```

**요청 본문**:

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**응답**:

```json
{
  "status": "success",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "60a1e2c3d4e5f6a7b8c9d0e1",
    "username": "user123",
    "email": "user@example.com"
  }
}
```

#### 토큰 갱신

```
POST /auth/refresh
```

**요청 본문**:

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**응답**:

```json
{
  "status": "success",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 뉴스 (News)

#### 뉴스 목록 조회

```
GET /news
```

**쿼리 파라미터**:

- `page` (선택): 페이지 번호 (기본값: 1)
- `per_page` (선택): 페이지당 항목 수 (기본값: 20)
- `source` (선택): 뉴스 소스 필터링
- `start_date` (선택): 시작 날짜 (YYYY-MM-DD)
- `end_date` (선택): 종료 날짜 (YYYY-MM-DD)

**응답**:

```json
{
  "status": "success",
  "data": {
    "news": [
      {
        "id": "60a1e2c3d4e5f6a7b8c9d0e1",
        "title": "Market rallies on positive economic data",
        "url": "https://example.com/article1",
        "source": "reuters",
        "published_date": "2025-04-01T12:00:00Z",
        "sentiment": {
          "positive": 0.75,
          "neutral": 0.20,
          "negative": 0.05
        }
      },
      {
        "id": "60a1e2c3d4e5f6a7b8c9d0e2",
        "title": "Company XYZ reports strong Q1 earnings",
        "url": "https://example.com/article2",
        "source": "bloomberg",
        "published_date": "2025-04-01T10:30:00Z",
        "sentiment": {
          "positive": 0.82,
          "neutral": 0.15,
          "negative": 0.03
        }
      }
    ],
    "pagination": {
      "total": 42,
      "page": 1,
      "per_page": 20,
      "pages": 3
    }
  }
}
```

#### 특정 뉴스 조회

```
GET /news/{id}
```

**응답**:

```json
{
  "status": "success",
  "data": {
    "id": "60a1e2c3d4e5f6a7b8c9d0e1",
    "title": "Market rallies on positive economic data",
    "url": "https://example.com/article1",
    "content": "The market rallied today following positive economic data...",
    "source": "reuters",
    "published_date": "2025-04-01T12:00:00Z",
    "keywords": ["market", "economy", "rally", "data"],
    "sentiment": {
      "positive": 0.75,
      "neutral": 0.20,
      "negative": 0.05
    }
  }
}
```

#### 뉴스 검색

```
GET /news/search
```

**쿼리 파라미터**:

- `q` (필수): 검색 키워드
- `page` (선택): 페이지 번호 (기본값: 1)
- `per_page` (선택): 페이지당 항목 수 (기본값: 20)
- `source` (선택): 뉴스 소스 필터링
- `start_date` (선택): 시작 날짜 (YYYY-MM-DD)
- `end_date` (선택): 종료 날짜 (YYYY-MM-DD)

**응답**:

```json
{
  "status": "success",
  "data": {
    "news": [
      {
        "id": "60a1e2c3d4e5f6a7b8c9d0e1",
        "title": "Market rallies on positive economic data",
        "url": "https://example.com/article1",
        "source": "reuters",
        "published_date": "2025-04-01T12:00:00Z",
        "sentiment": {
          "positive": 0.75,
          "neutral": 0.20,
          "negative": 0.05
        }
      }
    ],
    "pagination": {
      "total": 5,
      "page": 1,
      "per_page": 20,
      "pages": 1
    }
  }
}
```

#### 감성 분석 결과 조회

```
GET /news/sentiment
```

**쿼리 파라미터**:

- `symbol` (선택): 주식 심볼 필터링
- `days` (선택): 날짜 범위 (기본값: 30)
- `source` (선택): 뉴스 소스 필터링

**응답**:

```json
{
  "status": "success",
  "data": {
    "sentiment_trend": [
      {
        "date": "2025-04-01",
        "positive": 0.65,
        "neutral": 0.25,
        "negative": 0.10,
        "count": 12
      },
      {
        "date": "2025-03-31",
        "positive": 0.58,
        "neutral": 0.32,
        "negative": 0.10,
        "count": 15
      }
    ],
    "overall_sentiment": {
      "positive": 0.62,
      "neutral": 0.28,
      "negative": 0.10
    },
    "total_articles": 27
  }
}
```

### 주식 데이터 (Stocks)

#### 특정 주식 데이터 조회

```
GET /stocks/{symbol}
```

**쿼리 파라미터**:

- `period` (선택): 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
- `interval` (선택): 간격 (1d, 1wk, 1mo)

**응답**:

```json
{
  "status": "success",
  "data": {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "current_price": 175.23,
    "change": 2.34,
    "change_percent": 1.35,
    "market_cap": 2874562000000,
    "pe_ratio": 28.91,
    "eps": 6.06,
    "dividend_yield": 0.52,
    "volume": 67245800,
    "avg_volume": 59123456,
    "high_52w": 182.94,
    "low_52w": 124.17,
    "open": 173.75,
    "high": 175.89,
    "low": 173.11,
    "prev_close": 172.89
  }
}
```

#### 주식 히스토리 데이터 조회

```
GET /stocks/{symbol}/historical
```

**쿼리 파라미터**:

- `start_date` (선택): 시작 날짜 (YYYY-MM-DD)
- `end_date` (선택): 종료 날짜 (YYYY-MM-DD)
- `period` (선택): 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
- `interval` (선택): 간격 (1d, 1wk, 1mo)
- `indicators` (선택): 포함할 기술적 지표 (sma,ema,rsi,bb,macd)

**응답**:

```json
{
  "status": "success",
  "data": {
    "symbol": "AAPL",
    "historical": [
      {
        "date": "2025-04-01",
        "open": 173.75,
        "high": 175.89,
        "low": 173.11,
        "close": 175.23,
        "volume": 67245800,
        "sma_20": 172.68,
        "sma_50": 168.35,
        "rsi_14": 63.24
      },
      {
        "date": "2025-03-31",
        "open": 172.58,
        "high": 173.42,
        "low": 171.96,
        "close": 172.89,
        "volume": 51234500,
        "sma_20": 172.31,
        "sma_50": 168.12,
        "rsi_14": 61.78
      }
    ],
    "indicators": ["sma_20", "sma_50", "rsi_14"]
  }
}
```

#### 암호화폐 데이터 조회

```
GET /crypto/{symbol}
```

**쿼리 파라미터**:

- `days` (선택): 수집할 일수 (기본값: 30, 최대: 90)

**응답**:

```json
{
  "status": "success",
  "data": {
    "symbol": "bitcoin",
    "name": "Bitcoin",
    "current_price": 58432.67,
    "change_24h": 1243.58,
    "change_percent_24h": 2.18,
    "market_cap": 1098765432100,
    "volume_24h": 28765432100,
    "high_24h": 58987.32,
    "low_24h": 57123.45,
    "ath": 69000.00,
    "ath_date": "2024-11-10T14:24:11Z"
  }
}
```

### 분석 (Analysis)

#### 감성-가격 상관관계 분석

```
GET /analysis/correlation
```

**쿼리 파라미터**:

- `symbol` (필수): 주식 심볼
- `days` (선택): 날짜 범위 (기본값: 30)

**응답**:

```json
{
  "status": "success",
  "data": {
    "symbol": "AAPL",
    "correlation": {
      "positive_sentiment_price": 0.68,
      "negative_sentiment_price": -0.57,
      "sentiment_score_price_change": 0.72
    },
    "price_lag_analysis": [
      {
        "lag_days": 0,
        "correlation": 0.72
      },
      {
        "lag_days": 1,
        "correlation": 0.65
      },
      {
        "lag_days": 2,
        "correlation": 0.42
      },
      {
        "lag_days": 3,
        "correlation": 0.18
      }
    ],
    "period": {
      "start_date": "2025-03-03",
      "end_date": "2025-04-01"
    }
  }
}
```

#### 감성 트렌드 분석

```
GET /analysis/trends
```

**쿼리 파라미터**:

- `symbol` (선택): 주식 심볼
- `days` (선택): 날짜 범위 (기본값: 30)
- `interval` (선택): 시간 간격 (day, week, month) (기본값: day)

**응답**:

```json
{
  "status": "success",
  "data": {
    "symbol": "AAPL",
    "trends": [
      {
        "date": "2025-04-01",
        "sentiment_score": 0.68,
        "article_count": 12,
        "price_change": 1.35
      },
      {
        "date": "2025-03-31",
        "sentiment_score": 0.62,
        "article_count": 15,
        "price_change": 0.87
      }
    ],
    "top_keywords": [
      {
        "keyword": "earnings",
        "count": 47,
        "avg_sentiment": 0.72
      },
      {
        "keyword": "innovation",
        "count": 35,
        "avg_sentiment": 0.81
      },
      {
        "keyword": "competition",
        "count": 28,
        "avg_sentiment": 0.45
      }
    ],
    "period": {
      "start_date": "2025-03-03",
      "end_date": "2025-04-01"
    }
  }
}
```

#### 예측 데이터 조회 (개발 중)

```
GET /analysis/predictions
```

**쿼리 파라미터**:

- `symbol` (필수): 주식 심볼
- `days` (선택): 예측 기간(일) (기본값: 7)

**응답**:

```json
{
  "status": "success",
  "data": {
    "symbol": "AAPL",
    "disclaimer": "예측은 참고용이며 투자 결정에 직접 사용해서는 안 됩니다.",
    "predictions": [
      {
        "date": "2025-04-02",
        "predicted_close": 176.45,
        "confidence_interval": [175.32, 177.58],
        "prediction_factors": {
          "technical": 0.65,
          "sentiment": 0.78,
          "historical": 0.72
        }
      },
      {
        "date": "2025-04-03",
        "predicted_close": 177.23,
        "confidence_interval": [175.89, 178.57],
        "prediction_factors": {
          "technical": 0.67,
          "sentiment": 0.75,
          "historical": 0.71
        }
      }
    ],
    "model_performance": {
      "mape": 1.35,
      "rmse": 2.42,
      "accuracy": 0.78
    }
  }
}
```

## 에러 코드

API는 다음과 같은 표준화된 에러 응답 형식을 사용합니다:

```json
{
  "status": "error",
  "code": 400,
  "message": "Invalid request parameters",
  "details": {
    "symbol": "Required parameter is missing"
  }
}
```

### 주요 에러 코드

- `400` - Bad Request: 잘못된 요청 파라미터
- `401` - Unauthorized: 인증 실패
- `403` - Forbidden: 권한 없음
- `404` - Not Found: 리소스 없음
- `429` - Too Many Requests: 요청 한도 초과
- `500` - Internal Server Error: 서버 내부 오류

## 속도 제한

공개 API는 IP 주소당 다음과 같은 속도 제한이 적용됩니다:

- 인증된 사용자: 분당 60 요청
- 인증되지 않은 사용자: 분당 20 요청

속도 제한을 초과한 경우 `429 Too Many Requests` 응답이 반환됩니다.
