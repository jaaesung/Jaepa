FROM python:3.11-slim AS base

WORKDIR /app

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    PYTHONPATH=/app

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 의존성 설치 레이어 분리
FROM base AS dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 테스트 단계
FROM dependencies AS test

COPY tests/ /app/tests/
COPY backend/ /app/backend/
COPY analysis/ /app/analysis/
COPY crawling/ /app/crawling/
COPY data/ /app/data/
COPY run_tests.py /app/

RUN pytest -xvs

# 최종 이미지
FROM dependencies AS final

# 애플리케이션 코드 복사
COPY . .

# 애플리케이션 포트 노출
EXPOSE 8000

# 실행 명령
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
