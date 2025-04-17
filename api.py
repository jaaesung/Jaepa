#!/usr/bin/env python3
"""
금융 분석 API

이 모듈은 FinBERT 모델과 Polygon API를 사용한 금융 분석 기능을 제공하는 웹 API를 구현합니다.
"""
import os
import logging
from typing import Dict, Any

import uvicorn
from dotenv import load_dotenv

from api import create_app
from core.config import settings

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, settings.logging.level),
    format=settings.logging.format
)
logger = logging.getLogger(__name__)

# 애플리케이션 설정
config = {
    "title": settings.app_name,
    "description": settings.app_description,
    "version": settings.app_version,
    "debug": settings.debug,
    "host": settings.api.host,
    "port": settings.api.port,
    "reload": settings.debug,
    "static_dir": "static",
    "templates_dir": "templates",
    "cors_origins": settings.api.cors_origins,
    "cors_allow_credentials": settings.api.cors_allow_credentials,
    "cors_allow_methods": settings.api.cors_allow_methods,
    "cors_allow_headers": settings.api.cors_allow_headers,
    "rate_limit": settings.security.rate_limit_requests,
    "rate_limit_window": settings.security.rate_limit_period_seconds,
    "api_prefix": settings.api.prefix,
    "api_version": settings.api.version
}

# 애플리케이션 생성
app = create_app(config)

if __name__ == "__main__":
    # 서버 실행
    logger.info(f"서버 시작: {config['host']}:{config['port']} (디버그: {config['debug']})")
    uvicorn.run(
        "api:app",
        host=config["host"],
        port=config["port"],
        reload=config["reload"]
    )
