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
pip install -r requirements.txt

# 환경 설정
cp .env.example .env
# .env 파일을 수정하여 필요한 API 키와 DB 설정 입력
```

### 실행 방법

```bash
# CLI 인터페이스 실행
python main.py
```

## 프로젝트 구조

```
jaepa/
├── backend/           # 백엔드 API 서버
│   ├── app/           # 애플리케이션 코드
│   ├── api/           # REST API
│   └── README.md      # 백엔드 문서
│
├── crawling/          # 데이터 크롤링 모듈
│   ├── config.json    # 크롤링 설정
│   ├── news_crawler.py # 뉴스 크롤러
│   └── README.md      # 크롤링 문서
│
├── docs/              # 프로젝트 문서
│   ├── api.md         # API 문서
│   ├── architecture.md # 아키텍처 문서
│   └── README.md      # 문서 목록
│
├── project_status.md  # 현재 프로젝트 상태 요약
├── CHANGELOG.md       # 변경 이력
├── TODO.md            # 할 일 목록
├── .env.example       # 환경 변수 예시
└── README.md          # 프로젝트 개요
```

## 기여 방법

이 프로젝트에 기여하고 싶으시다면 이슈를 생성하거나 풀 리퀘스트를 제출해주세요.

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
