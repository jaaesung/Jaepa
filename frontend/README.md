# JaePa 프론트엔드

JaePa(재파) 프로젝트의 웹 프론트엔드 애플리케이션입니다.

## 기술 스택

- React 18
- Redux Toolkit (상태 관리)
- React Router (라우팅)
- Axios (API 통신)
- Chart.js (데이터 시각화)
- Tailwind CSS (스타일링)

## 시작하기

### 필수 조건

- Node.js 16.x 이상
- npm 8.x 이상 또는 yarn 1.22.x 이상

### 설치

1. 저장소를 클론하거나 소스 코드를 다운로드합니다.
2. 프로젝트 디렉토리로 이동합니다.
   ```
   cd jaepa/frontend
   ```
3. 의존성을 설치합니다.
   ```
   npm install
   # 또는
   yarn install
   ```

### 개발 서버 실행

```
npm start
# 또는
yarn start
```

애플리케이션은 기본적으로 http://localhost:3000 에서 실행됩니다.

### 빌드

프로덕션 빌드를 생성하려면 다음 명령어를 실행합니다.

```
npm run build
# 또는
yarn build
```

빌드된 파일은 `build` 디렉토리에 생성됩니다.

## 프로젝트 구조

```
frontend/
├── public/              # 정적 자산
├── src/                 # 소스 코드
│   ├── components/      # 재사용 가능한 컴포넌트
│   ├── pages/           # 페이지 컴포넌트
│   ├── services/        # API 서비스
│   ├── store/           # Redux 스토어
│   │   └── slices/      # Redux 슬라이스
│   ├── utils/           # 유틸리티 함수
│   ├── App.js           # 애플리케이션 진입점
│   └── index.js         # React 렌더링 진입점
├── package.json         # 프로젝트 의존성 및 스크립트
└── tailwind.config.js   # Tailwind CSS 구성
```

## 기능

- 사용자 인증 (로그인/회원가입)
- 대시보드 (핵심 지표 요약)
- 뉴스 분석 (리스트, 감성 분석, 키워드 분석)
- 주식 분석 (가격 데이터, 상관관계 분석)
- 설정 및 사용자 프로필

## 환경 변수

애플리케이션 구성을 위한 환경 변수:

- `REACT_APP_API_URL`: API 서버 URL (기본값: http://localhost:8000/api)
- `REACT_APP_ENV`: 애플리케이션 환경 (development, production)

## 개발자

- 개발자 이름 - [이메일]