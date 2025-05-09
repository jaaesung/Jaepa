# JaePa (재파) - 금융 뉴스 감성 분석 도구

JaePa는 해외 금융 뉴스 크롤링과 감성 분석을 통해 투자 의사결정을 돕는 도구입니다.

## 프로젝트 개요

JaePa는 주요 금융 뉴스 사이트에서 데이터를 수집하고, 금융 특화 자연어 처리 모델을 사용하여 뉴스의 감성을 분석합니다. 분석된 감성 정보는 주식 가격 데이터와 결합되어 투자 의사결정에 도움이 되는 통찰력을 제공합니다.

## 주요 기능

- **뉴스 크롤링**: Reuters, Bloomberg, Financial Times, CNBC, WSJ 등 주요 금융 뉴스 사이트 데이터 수집
- **감성 분석**: FinBERT 모델을 활용한 금융 뉴스 감성 분석
- **주식 데이터 수집**: yfinance 라이브러리와 CoinGecko API를 통한 주식 및 암호화폐 데이터 수집
- **데이터 분석**: 뉴스 감성과 주가 변동의 상관관계 분석 및 시각화
- **CLI 인터페이스**: 명령행을 통한 다양한 기능 접근

## 시작하기

### 필수 요구사항

- Python 3.8 이상
- MongoDB
- 필요한 Python 패키지 (requirements.txt 참조)

### 설치 방법

```bash
# 저장소 클론
git clone https://github.com/yourusername/jaepa.git
cd jaepa

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필요한 패키지 설치
pip install -r config/backend/requirements.txt

# 환경 설정
cp .env.example .env
# .env 파일을 수정하여 필요한 API 키와 DB 설정 입력
```

### 실행 방법

```bash
# 백엔드 서버 실행
python backend/main.py

# 프론트엔드 서버 실행
npm start

# 크롤링 스케줄러 실행
python crawling/scheduler.py

# Docker를 사용한 실행
npm run docker:up
```

## 프로젝트 구조

```
jaepa/
├── src/                # 프론트엔드 코드
│   ├── assets/         # 정적 자산 파일들
│   ├── components/     # UI 컴포넌트
│   ├── core/           # 핵심 공통 코드
│   ├── features/       # 기능별 모듈
│   ├── pages/          # 페이지 컴포넌트
│   ├── routes/         # 라우팅 관련
│   ├── services/       # 외부 서비스와의 통신
│   ├── store/          # 글로벌 상태 관리
│   ├── App.tsx         # 앱 진입점 컴포넌트
│   └── index.tsx       # React 렌더링 진입점
│
├── backend/            # 백엔드 코드
│   ├── api/            # API 모듈
│   ├── core/           # 핵심 기능 모듈
│   ├── main.py         # 백엔드 진입점
│   └── __init__.py
│
├── crawling/           # 크롤링 모듈
│   ├── collectors/     # 데이터 수집기
│   ├── processors/     # 데이터 처리기
│   ├── config/         # 크롤링 설정
│   ├── utils/          # 크롤링 유틸리티
│   ├── scheduler.py    # 크롤링 스케줄러
│   └── __init__.py
│
├── config/             # 전역 설정
│   ├── frontend/       # 프론트엔드 설정
│   │   ├── craco.config.js
│   │   ├── tsconfig.json
│   │   ├── tsconfig.paths.json
│   │   └── jest.config.js
│   ├── backend/        # 백엔드 설정
│   │   ├── requirements.txt
│   │   └── pytest.ini
│   ├── docker/         # Docker 설정
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   ├── environments/   # 환경별 설정
│   └── __init__.py
│
├── tests/              # 테스트 코드
│
├── logs/               # 로그 파일
│
├── .env.example        # 환경 변수 예시
├── package.json        # npm 패키지 설정
└── README.md           # 프로젝트 문서
```
