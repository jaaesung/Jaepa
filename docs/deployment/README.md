# JaePa 배포 가이드

이 문서는 JaePa 애플리케이션의 배포 과정을 설명합니다.

## 필수 조건

- Docker 및 Docker Compose 설치
- Git
- 서버 환경 (클라우드 또는 물리적 서버)
- MongoDB 데이터베이스 (로컬 또는 클라우드)

## 환경 준비

### 1. 프로젝트 복제

```bash
git clone https://github.com/yourusername/jaepa.git
cd jaepa
```

### 2. 환경 변수 설정

`.env.example` 파일을 `.env` 파일로 복사하고 값을 수정합니다:

```bash
cp .env.example .env
```

`.env` 파일을 열고 다음 변수들을 환경에 맞게 수정합니다:

```
MONGO_USERNAME=your_mongodb_username
MONGO_PASSWORD=your_secure_password
JWT_SECRET=your_jwt_secret_key
```

### 3. Docker 빌드 및 실행

Docker Compose를 사용하여 모든 서비스를 빌드하고 실행합니다:

```bash
docker-compose build
docker-compose up -d
```

## 배포 옵션

### 1. 수동 배포 (개발 환경)

개발 환경에서는 수동 배포를 사용할 수 있습니다:

```bash
# 변경사항 가져오기
git pull origin main

# 도커 이미지 다시 빌드
docker-compose build

# 서비스 재시작
docker-compose up -d
```

### 2. CI/CD 파이프라인을 통한 자동 배포 (운영 환경)

GitHub Actions 워크플로우를 사용하여 CI/CD 파이프라인을 구성했습니다:

1. GitHub 저장소 설정에서 다음 시크릿 변수들을 추가합니다:
   - `DOCKERHUB_USERNAME`: Docker Hub 사용자명
   - `DOCKERHUB_TOKEN`: Docker Hub 액세스 토큰
   - `SERVER_HOST`: 배포 서버 호스트
   - `SERVER_USERNAME`: 배포 서버 사용자명
   - `SERVER_SSH_KEY`: 배포 서버 SSH 키

2. 메인 브랜치에 변경사항을 푸시하면 자동으로 CI/CD 파이프라인이 실행됩니다.

## 서비스 관리

### 로그 확인

```bash
# 모든 서비스의 로그 확인
docker-compose logs

# 특정 서비스의 로그 확인 (예: 백엔드)
docker-compose logs backend

# 실시간 로그 스트림 확인
docker-compose logs -f
```

### 서비스 상태 확인

```bash
docker-compose ps
```

### 서비스 재시작

```bash
# 모든 서비스 재시작
docker-compose restart

# 특정 서비스 재시작 (예: 백엔드)
docker-compose restart backend
```

## 백업 및 복원

### MongoDB 데이터 백업

```bash
docker-compose exec mongodb mongodump --username $MONGO_USERNAME --password $MONGO_PASSWORD --out /data/backup
```

### MongoDB 데이터 복원

```bash
docker-compose exec mongodb mongorestore --username $MONGO_USERNAME --password $MONGO_PASSWORD /data/backup
```

## 모니터링

서비스 모니터링을 위해 다음과 같은 도구를 사용할 수 있습니다:

- Docker 상태 모니터링: `docker stats`
- 로그 모니터링: ELK 스택 (Elasticsearch, Logstash, Kibana) 또는 Grafana + Loki
- 시스템 모니터링: Prometheus + Grafana

## 트러블슈팅

### 1. 서비스가 시작되지 않는 경우

```bash
# 로그 확인
docker-compose logs <service_name>

# 설정 확인
cat .env

# 네트워크 확인
docker network ls
```

### 2. 데이터베이스 연결 오류

```bash
# MongoDB 서비스 상태 확인
docker-compose ps mongodb

# MongoDB 로그 확인
docker-compose logs mongodb
```

### 3. 프론트엔드에서 API 연결 오류

- Nginx 설정 확인
- CORS 설정 확인
- API URL 환경 변수 확인

## 보안 고려사항

- `.env` 파일을 Git에 커밋하지 마세요.
- 정기적으로 서버 및 컨테이너를 업데이트하세요.
- 중요 데이터는 정기적으로 백업하세요.
- JWT 시크릿 키는 복잡하고 안전하게 관리하세요.
