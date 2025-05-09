"""
API 메인 애플리케이션 모듈

FastAPI 애플리케이션을 실행합니다.
"""
import os
import logging
import json
from typing import Dict, Any

import uvicorn
from dotenv import load_dotenv

from api import create_app

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:
    """
    설정 로드
    
    Returns:
        Dict[str, Any]: 설정 정보
    """
    # 기본 설정
    config = {
        "title": "금융 분석 API",
        "description": "FinBERT 모델과 Polygon API를 사용한 금융 분석 API",
        "version": "1.0.0",
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", "8000")),
        "reload": os.getenv("RELOAD", "false").lower() == "true",
        "static_dir": "static",
        "templates_dir": "templates",
        "cors_origins": os.getenv("CORS_ORIGINS", "*").split(","),
        "cors_allow_credentials": os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true",
        "cors_allow_methods": os.getenv("CORS_ALLOW_METHODS", "*").split(","),
        "cors_allow_headers": os.getenv("CORS_ALLOW_HEADERS", "*").split(","),
        "rate_limit": int(os.getenv("RATE_LIMIT", "100")),
        "rate_limit_window": int(os.getenv("RATE_LIMIT_WINDOW", "60")),
        "slow_response_threshold": float(os.getenv("SLOW_RESPONSE_THRESHOLD", "1.0")),
        "log_request_body": os.getenv("LOG_REQUEST_BODY", "false").lower() == "true",
        "log_response_body": os.getenv("LOG_RESPONSE_BODY", "false").lower() == "true"
    }
    
    # 설정 파일 로드
    config_file = os.getenv("CONFIG_FILE")
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                file_config = json.load(f)
                config.update(file_config)
            logger.info(f"설정 파일 로드 완료: {config_file}")
        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {str(e)}")
    
    return config


def main():
    """
    메인 함수
    """
    # 설정 로드
    config = load_config()
    
    # 애플리케이션 생성
    app = create_app(config)
    
    # 서버 실행
    logger.info(f"서버 시작: {config['host']}:{config['port']} (디버그: {config['debug']})")
    uvicorn.run(
        "api_main:app",
        host=config["host"],
        port=config["port"],
        reload=config["reload"]
    )


# 애플리케이션 인스턴스
app = create_app(load_config())

if __name__ == "__main__":
    main()
