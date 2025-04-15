# JaePa 테스트 및 배포 가이드

이 문서는 JaePa 프로젝트의 테스트 및 배포 방법을 설명합니다.

## 테스트 환경

JaePa 프로젝트는 다음과 같은 테스트 도구를 사용합니다:

### 프론트엔드 테스트

- **Jest**: JavaScript 테스트 프레임워크
- **React Testing Library (RTL)**: React 컴포넌트 테스트 라이브러리
- **Playwright**: E2E(End-to-End) 테스트 프레임워크

### 백엔드 테스트

- **pytest**: Python 테스트 프레임워크

### 코드 품질 및 Git 훅

- **Husky**: Git 훅 관리
- **lint-staged**: 스테이징된 파일에 대한 린트 실행
- **commitlint**: 커밋 메시지 규칙 검사
- **Prettier**: 코드 포맷팅

## 테스트 실행 방법

### 프론트엔드 테스트

```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# 단위 테스트 실행
npm test

# 테스트 커버리지 보고서 생성
npm run test:coverage

# E2E 테스트 실행
npm run test:e2e

# E2E 테스트 UI 모드로 실행
npm run test:e2e:ui
```

### 백엔드 테스트

```bash
# 프로젝트 루트 디렉토리에서
python run_tests.py --type all

# 특정 모듈만 테스트
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type analysis
```

## Docker 및 Kubernetes 배포

### Docker Compose로 로컬 실행

```bash
# 환경 변수 설정
cp .env.example .env
# .env 파일 편집하여 필요한 값 설정

# 도커 컴포즈로 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### Kubernetes 배포

#### 사전 요구사항

- kubectl 설치
- Kubernetes 클러스터 접근 권한
- Docker 이미지 빌드 및 레지스트리 푸시 권한

#### 배포 단계

1. Docker 이미지 빌드 및 푸시

```bash
# 백엔드 이미지 빌드
docker build -t your-registry/jaepa-backend:latest .

# 프론트엔드 이미지 빌드
docker build -t your-registry/jaepa-frontend:latest ./frontend

# 이미지 푸시
docker push your-registry/jaepa-backend:latest
docker push your-registry/jaepa-frontend:latest
```

2. Kubernetes 리소스 배포

```bash
# 네임스페이스 생성
kubectl apply -f k8s/namespace.yaml

# Secret 값 업데이트 (실제 배포 전)
# k8s/secret.yaml 파일의 값을 base64로 인코딩된 실제 값으로 변경

# kustomize를 사용하여 모든 리소스 배포
kubectl apply -k k8s/

# 배포 상태 확인
kubectl get all -n jaepa
```

3. 인그레스 설정

로컬 개발 환경에서는 /etc/hosts 파일에 다음 항목을 추가합니다:

```
127.0.0.1 jaepa.local
```

## CI/CD 파이프라인

JaePa 프로젝트는 Git 커밋 시 자동으로 코드 품질 검사를 수행합니다:

- **pre-commit 훅**: 코드 린트 및 포맷팅 검사
- **commit-msg 훅**: 커밋 메시지 규칙 검사

커밋 메시지는 [Conventional Commits](https://www.conventionalcommits.org/) 규칙을 따릅니다:

```
<type>(<scope>): <subject>

<body>

<footer>
```

예시:
```
feat(frontend): 대시보드 차트 컴포넌트 추가

- 주가 변동 차트 추가
- 감성 분석 결과 시각화 추가

Closes #123
```
