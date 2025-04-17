"""
설정 모듈 테스트
"""
import os
import pytest
from unittest.mock import patch

from core.config import Settings, get_settings


class TestSettings:
    """설정 클래스 테스트"""
    
    def test_default_settings(self):
        """기본 설정 테스트"""
        settings = Settings()
        
        # 기본값 확인
        assert settings.app_name == "JaePa"
        assert settings.app_version == "0.1.0"
        assert settings.debug is False
        
        # 데이터베이스 설정 확인
        assert settings.db.engine == "mongodb"
        assert "mongodb://" in settings.db.mongo_uri
        
        # API 설정 확인
        assert settings.api.host == "0.0.0.0"
        assert settings.api.port == 8000
        
        # 로깅 설정 확인
        assert settings.logging.level == "INFO"
    
    def test_environment_override(self):
        """환경 변수 오버라이드 테스트"""
        with patch.dict(os.environ, {
            "APP_NAME": "TestApp",
            "APP_VERSION": "1.0.0",
            "DEBUG": "true",
            "DB_ENGINE": "sqlite",
            "DB_SQLITE_URL": "sqlite:///test.db",
            "API_HOST": "127.0.0.1",
            "API_PORT": "9000",
            "LOGGING_LEVEL": "DEBUG"
        }):
            settings = Settings()
            
            # 환경 변수로 오버라이드된 값 확인
            assert settings.app_name == "TestApp"
            assert settings.app_version == "1.0.0"
            assert settings.debug is True
            
            # 데이터베이스 설정 확인
            assert settings.db.engine == "sqlite"
            assert settings.db.sqlite_url == "sqlite:///test.db"
            
            # API 설정 확인
            assert settings.api.host == "127.0.0.1"
            assert settings.api.port == 9000
            
            # 로깅 설정 확인
            assert settings.logging.level == "DEBUG"
    
    def test_get_settings(self):
        """get_settings 함수 테스트"""
        settings = get_settings()
        
        # 싱글톤 패턴 확인
        assert settings is get_settings()
        
        # 설정 값 확인
        assert settings.app_name == "JaePa"
        assert isinstance(settings.app_version, str)
