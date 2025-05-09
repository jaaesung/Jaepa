"""
개발 환경 설정 모듈

개발 환경에서 사용되는 설정을 정의합니다.
"""

# 디버그 모드
DEBUG = True

# 로깅 설정
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 데이터베이스 설정
DATABASE_URL = "sqlite:///./jaepa_dev.db"

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
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 개발 환경에서는 더 긴 만료 시간

# 크롤링 설정
CRAWLING_INTERVAL_MINUTES = 30  # 개발 환경에서는 더 짧은 간격
