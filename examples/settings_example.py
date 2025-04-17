#!/usr/bin/env python3
"""
JaePa 설정 시스템 사용 예제

이 예제는 JaePa 프로젝트의 중앙화된 설정 시스템을 사용하는 방법을 보여줍니다.
"""

import os
import sys
import logging
from pathlib import Path

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# 설정 모듈 가져오기
from config import settings

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, settings.logging.level),
    format=settings.logging.format,
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


def main():
    """설정 시스템 사용 예제"""
    # 프로젝트 기본 설정
    logger.info("=== 프로젝트 기본 설정 ===")
    logger.info(f"프로젝트 이름: {settings.project_name}")
    logger.info(f"프로젝트 설명: {settings.project_description}")
    logger.info(f"버전: {settings.version}")
    logger.info(f"환경: {settings.environment}")
    logger.info(f"디버그 모드: {settings.debug}")
    
    # 데이터베이스 설정
    logger.info("\n=== 데이터베이스 설정 ===")
    logger.info(f"MongoDB URI: {settings.db.mongo_uri.replace(settings.db.mongo_password, '********')}")
    logger.info(f"MongoDB 데이터베이스: {settings.db.mongo_db_name}")
    logger.info(f"뉴스 컬렉션: {settings.db.news_collection}")
    logger.info(f"감성 컬렉션: {settings.db.sentiment_collection}")
    
    # API 설정
    logger.info("\n=== API 설정 ===")
    logger.info(f"호스트: {settings.api.host}")
    logger.info(f"포트: {settings.api.port}")
    logger.info(f"API 접두사: {settings.api.api_prefix}")
    logger.info(f"API 버전: {settings.api.api_version}")
    logger.info(f"CORS 원본: {settings.api.cors_origins}")
    
    # 크롤링 설정
    logger.info("\n=== 크롤링 설정 ===")
    logger.info(f"타임아웃: {settings.crawling.timeout}초")
    logger.info(f"재시도 횟수: {settings.crawling.retries}회")
    logger.info(f"사용자 에이전트: {settings.crawling.user_agent}")
    logger.info(f"RSS 피드 수: {len(settings.crawling.rss_feeds)}")
    logger.info(f"뉴스 소스 수: {len(settings.crawling.news_sources)}")
    
    # 감성 분석 설정
    logger.info("\n=== 감성 분석 설정 ===")
    logger.info(f"모델: {settings.sentiment.model}")
    logger.info(f"모델 경로: {settings.sentiment.model_path}")
    logger.info(f"배치 크기: {settings.sentiment.batch_size}")
    logger.info(f"긍정 임계값: {settings.sentiment.positive_threshold}")
    logger.info(f"부정 임계값: {settings.sentiment.negative_threshold}")
    
    # 로깅 설정
    logger.info("\n=== 로깅 설정 ===")
    logger.info(f"로그 레벨: {settings.logging.level}")
    logger.info(f"파일 로깅 활성화: {settings.logging.file_enabled}")
    logger.info(f"로그 파일 경로: {settings.logging.file_path}")
    logger.info(f"민감 정보 마스킹: {settings.logging.mask_sensitive_data}")
    
    # 보안 설정
    logger.info("\n=== 보안 설정 ===")
    logger.info(f"JWT 알고리즘: {settings.security.jwt_algorithm}")
    logger.info(f"액세스 토큰 만료 시간: {settings.security.access_token_expire_minutes}분")
    logger.info(f"리프레시 토큰 만료 시간: {settings.security.refresh_token_expire_days}일")
    logger.info(f"비밀번호 최소 길이: {settings.security.password_min_length}자")
    
    # 주식 데이터 설정
    logger.info("\n=== 주식 데이터 설정 ===")
    logger.info(f"기본 기간: {settings.stock.default_period}")
    logger.info(f"기본 간격: {settings.stock.default_interval}")
    logger.info(f"기술적 지표: {settings.stock.technical_indicators}")
    logger.info(f"이동 평균: {settings.stock.moving_averages}")
    
    # GDELT 설정
    logger.info("\n=== GDELT 설정 ===")
    logger.info(f"API 기본 URL: {settings.gdelt.api_base_url}")
    logger.info(f"문서 API URL: {settings.gdelt.doc_api_url}")
    logger.info(f"GKG API URL: {settings.gdelt.gkg_api_url}")
    logger.info(f"이벤트 API URL: {settings.gdelt.events_api_url}")
    logger.info(f"최대 레코드 수: {settings.gdelt.max_records}")


if __name__ == "__main__":
    main()
