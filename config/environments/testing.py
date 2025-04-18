"""
테스트 환경 설정 모듈

테스트 환경에서 사용되는 설정을 정의합니다.
"""

# 테스트 모드
TESTING = True

# 디버그 모드
DEBUG = True

# 로깅 설정
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 데이터베이스 설정 (인메모리 SQLite)
DATABASE_URL = "sqlite:///:memory:"

# API 설정
API_PREFIX = "/api"
API_DEBUG = True

# 프론트엔드 설정
FRONTEND_URL = "http://localhost:3000"

# 백엔드 설정
BACKEND_URL = "http://localhost:8000"

# CORS 설정
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]

# 토큰 설정
ACCESS_TOKEN_EXPIRE_MINUTES = 5  # 테스트에서는 짧은 만료 시간

# 크롤링 설정
CRAWLING_INTERVAL_MINUTES = 5  # 테스트에서는 매우 짧은 간격
