# JaePa 설정 시스템

JaePa 프로젝트의 중앙화된 설정 관리 시스템입니다.

## 개요

이 설정 시스템은 다음과 같은 특징을 가지고 있습니다:

- 환경 변수, JSON 파일, 기본값 순으로 설정을 로드합니다.
- Pydantic 기반의 타입 검증 및 기본값 처리를 제공합니다.
- 중첩 설정을 지원합니다.
- 설정 값을 캐싱하여 성능을 최적화합니다.
- 민감 정보(비밀번호, API 키 등)를 로깅하지 않습니다.

## 설정 카테고리

설정 시스템은 다음과 같은 카테고리로 구성되어 있습니다:

- **데이터베이스 설정**: MongoDB URI, 데이터베이스 이름, 컬렉션 이름
- **API 설정**: 호스트, 포트, 버전, CORS 원본
- **크롤링 설정**: 타임아웃, 재시도 횟수, 사용자 에이전트
- **감성 분석 설정**: 모델 경로, 배치 크기
- **로깅 설정**: 로그 레벨, 파일 경로
- **보안 설정**: JWT 시크릿, 알고리즘, 만료 시간
- **주식 데이터 설정**: 기본 기간, 간격, 기술적 지표
- **GDELT 설정**: API URL, 요청 간격, 최대 레코드 수

## 사용 방법

### 설정 가져오기

```python
from config import settings

# 프로젝트 기본 설정
project_name = settings.project_name
debug_mode = settings.debug

# 데이터베이스 설정
mongo_uri = settings.db.mongo_uri
db_name = settings.db.mongo_db_name

# API 설정
api_host = settings.api.host
api_port = settings.api.port

# 크롤링 설정
timeout = settings.crawling.timeout
user_agent = settings.crawling.user_agent

# 감성 분석 설정
model_path = settings.sentiment.model_path
batch_size = settings.sentiment.batch_size

# 로깅 설정
log_level = settings.logging.level
log_file_path = settings.logging.file_path

# 보안 설정
jwt_secret = settings.security.jwt_secret_key
jwt_algorithm = settings.security.jwt_algorithm

# 주식 데이터 설정
default_period = settings.stock.default_period
technical_indicators = settings.stock.technical_indicators

# GDELT 설정
gdelt_api_url = settings.gdelt.api_base_url
max_records = settings.gdelt.max_records
```

### 환경 변수 설정

환경 변수는 `.env` 파일 또는 시스템 환경 변수로 설정할 수 있습니다:

```bash
# 프로젝트 기본 설정
PROJECT_NAME=JaePa
DEBUG=true

# 데이터베이스 설정
MONGO_USERNAME=jaepa_user
MONGO_PASSWORD=secure_password
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=jaepa

# API 설정
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:80,http://frontend

# 감성 분석 설정
SENTIMENT_MODEL=finbert
SENTIMENT_BATCH_SIZE=32

# 로깅 설정
LOG_LEVEL=INFO
LOG_FILE_ENABLED=true
LOG_FILE_PATH=logs/jaepa.log

# 보안 설정
JWT_SECRET_KEY=your_secure_secret_key
JWT_ALGORITHM=HS256
```

### JSON 설정 파일

JSON 설정 파일은 `config/config.json` 또는 `CONFIG_FILE` 환경 변수로 지정된 경로에 위치할 수 있습니다:

```json
{
  "project_name": "JaePa",
  "debug": true,
  "db": {
    "mongo_uri": "mongodb://localhost:27017/",
    "mongo_db_name": "jaepa"
  },
  "api": {
    "host": "0.0.0.0",
    "port": 8000,
    "cors_origins": ["http://localhost:80", "http://frontend"]
  },
  "crawling": {
    "timeout": 30,
    "retries": 3,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
  },
  "sentiment": {
    "model": "finbert",
    "batch_size": 16
  }
}
```

## 설정 우선순위

설정 값은 다음 순서로 로드됩니다:

1. 환경 변수 (최우선)
2. 초기화 인자
3. JSON 설정 파일
4. .env 파일
5. 기본값 (최하위)

## 예제

전체 예제는 `examples/settings_example.py`를 참조하세요:

```bash
python examples/settings_example.py
```
