"""
설정 관리 모듈

애플리케이션 설정을 관리하는 모듈입니다.
환경별 설정 로딩 및 설정 객체 제공 기능을 구현합니다.
"""
import os
import logging
from typing import Dict, Any, Optional, Type, Union
from pathlib import Path

from .base import BaseSettings
from .development import DevelopmentSettings
from .testing import TestingSettings
from .production import ProductionSettings

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경별 설정 클래스 매핑
ENV_SETTINGS_MAP = {
    "development": DevelopmentSettings,
    "testing": TestingSettings,
    "production": ProductionSettings,
}

# 기본 환경
DEFAULT_ENV = "development"


def get_settings_class() -> Type[BaseSettings]:
    """
    현재 환경에 맞는 설정 클래스 반환
    
    Returns:
        Type[BaseSettings]: 설정 클래스
    """
    env = os.getenv("ENVIRONMENT", DEFAULT_ENV).lower()
    settings_class = ENV_SETTINGS_MAP.get(env)
    
    if settings_class is None:
        logger.warning(f"Unknown environment: {env}, using {DEFAULT_ENV} settings")
        settings_class = ENV_SETTINGS_MAP[DEFAULT_ENV]
    
    return settings_class


def load_settings(env_file: Optional[str] = None) -> BaseSettings:
    """
    설정 로드
    
    Args:
        env_file: 환경 변수 파일 경로 (기본값: None)
        
    Returns:
        BaseSettings: 설정 객체
    """
    settings_class = get_settings_class()
    
    # 환경 변수 파일이 지정된 경우
    if env_file:
        env_path = Path(env_file)
        if env_path.exists():
            logger.info(f"Loading settings from {env_file}")
            return settings_class(Config={"env_file": env_file})
    
    # 기본 환경 변수 파일 사용
    return settings_class()


def update_settings(settings: BaseSettings, new_values: Dict[str, Any]) -> BaseSettings:
    """
    설정 업데이트
    
    Args:
        settings: 기존 설정 객체
        new_values: 새 설정 값
        
    Returns:
        BaseSettings: 업데이트된 설정 객체
    """
    # 설정 복사
    updated_dict = settings.model_dump()
    
    # 새 값으로 업데이트
    for key, value in new_values.items():
        if key in updated_dict:
            if isinstance(updated_dict[key], dict) and isinstance(value, dict):
                # 중첩된 딕셔너리 업데이트
                updated_dict[key].update(value)
            else:
                # 일반 값 업데이트
                updated_dict[key] = value
    
    # 새 설정 객체 생성
    return settings.__class__(**updated_dict)


# 기본 설정 객체 생성
settings = load_settings()
