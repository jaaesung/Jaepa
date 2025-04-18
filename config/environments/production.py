"""
프로덕션 환경 설정 모듈

프로덕션 환경에서 사용되는 설정을 정의합니다.
"""

# 디버그 모드 비활성화
DEBUG = False

# 로깅 설정
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 데이터베이스 설정 (환경 변수에서 가져옴)
DATABASE_URL = "${DATABASE_URL}"

# API 설정
API_PREFIX = "/api"
API_DEBUG = False

# 프론트엔드 설정
FRONTEND_URL = "${FRONTEND_URL}"

# 백엔드 설정
BACKEND_URL = "${BACKEND_URL}"

# CORS 설정
CORS_ORIGINS = [
    "${FRONTEND_URL}",
    "${BACKEND_URL}",
]

# 토큰 설정
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 크롤링 설정
CRAWLING_INTERVAL_MINUTES = 60
