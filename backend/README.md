# JaePa 백엔드

JaePa 프로젝트의 백엔드 API 서버입니다.

## 구조

백엔드는 다음과 같은 구조로 구성되어 있습니다:

```
backend/
├── app/           # 애플리케이션 코드
│   ├── models/    # 데이터 모델
│   ├── services/  # 비즈니스 로직 서비스
│   ├── utils/     # 유틸리티 함수
│   └── config.py  # 애플리케이션 설정
│
├── api/           # REST API
│   ├── routes/    # API 라우트
│   ├── schemas/   # 요청/응답 스키마
│   └── middlewares/ # API 미들웨어
│
└── main.py        # 애플리케이션 진입점
```

## 기술 스택

- **웹 프레임워크**: FastAPI
- **데이터베이스**: MongoDB (with Motor 비동기 드라이버)
- **인증**: JWT 기반 인증
- **문서화**: OpenAPI (Swagger)

## 개발 환경 설정

1. 필요한 패키지 설치:

```bash
pip install fastapi uvicorn motor pydantic python-jose[cryptography] passlib[bcrypt] python-multipart
```

2. 환경 변수 설정 (프로젝트 루트의 .env 파일 참조)

3. 개발 서버 실행:

```bash
uvicorn backend.main:app --reload
```

## API 엔드포인트

API는 다음과 같은 주요 엔드포인트를 제공합니다:

### 인증

- `POST /api/auth/signup` - 사용자 등록
- `POST /api/auth/login` - 로그인 및 토큰 발급
- `POST /api/auth/refresh` - 액세스 토큰 갱신

### 뉴스

- `GET /api/news` - 뉴스 목록 조회
- `GET /api/news/{id}` - 특정 뉴스 조회
- `GET /api/news/search` - 키워드로 뉴스 검색
- `GET /api/news/sentiment` - 감성 분석 결과 조회

### 주식 데이터

- `GET /api/stocks/{symbol}` - 특정 주식 데이터 조회
- `GET /api/stocks/{symbol}/historical` - 주식 히스토리 데이터 조회
- `GET /api/crypto/{symbol}` - 암호화폐 데이터 조회

### 분석

- `GET /api/analysis/correlation` - 감성-가격 상관관계 분석
- `GET /api/analysis/trends` - 감성 트렌드 분석
- `GET /api/analysis/predictions` - 예측 데이터 조회 (개발 중)

## 인증 및 보안

API는 JWT 기반 인증을 사용합니다. 대부분의 엔드포인트는 인증이 필요하며, 요청 시 `Authorization` 헤더에 Bearer 토큰을 포함해야 합니다.

## 에러 처리

모든 API 엔드포인트는 표준화된 에러 응답 형식을 사용합니다:

```json
{
  "status": "error",
  "code": 404,
  "message": "Resource not found",
  "details": { ... }
}
```
