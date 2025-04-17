"""
인터페이스 모듈 테스트
"""
import pytest
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from core.interfaces import (
    DatabaseClient, MongoDBClient, HttpClient,
    NewsSourceManager, SentimentAnalyzer
)


class TestDatabaseClientInterface:
    """데이터베이스 클라이언트 인터페이스 테스트"""
    
    def test_is_abstract_class(self):
        """추상 클래스 여부 테스트"""
        assert issubclass(DatabaseClient, ABC)
    
    def test_required_methods(self):
        """필수 메서드 테스트"""
        # 필수 추상 메서드 목록
        required_methods = [
            'connect',
            'close',
            'is_connected',
            'get_database',
            'get_collection',
            'health_check'
        ]
        
        # 각 메서드가 추상 메서드인지 확인
        for method_name in required_methods:
            method = getattr(DatabaseClient, method_name)
            assert getattr(method, '__isabstractmethod__', False)


class TestMongoDBClientInterface:
    """MongoDB 클라이언트 인터페이스 테스트"""
    
    def test_inherits_database_client(self):
        """DatabaseClient 상속 여부 테스트"""
        assert issubclass(MongoDBClient, DatabaseClient)


class TestHttpClientInterface:
    """HTTP 클라이언트 인터페이스 테스트"""
    
    def test_is_abstract_class(self):
        """추상 클래스 여부 테스트"""
        assert issubclass(HttpClient, ABC)
    
    def test_required_methods(self):
        """필수 메서드 테스트"""
        # 필수 추상 메서드 목록
        required_methods = [
            'get',
            'post',
            'put',
            'delete',
            'close'
        ]
        
        # 각 메서드가 추상 메서드인지 확인
        for method_name in required_methods:
            method = getattr(HttpClient, method_name)
            assert getattr(method, '__isabstractmethod__', False)


class TestNewsSourceManagerInterface:
    """뉴스 소스 관리자 인터페이스 테스트"""
    
    def test_is_abstract_class(self):
        """추상 클래스 여부 테스트"""
        assert issubclass(NewsSourceManager, ABC)
    
    def test_required_methods(self):
        """필수 메서드 테스트"""
        # 필수 추상 메서드 목록
        required_methods = [
            'register_source',
            'get_source',
            'get_all_sources',
            'get_latest_news_from_all',
            'search_news_from_all'
        ]
        
        # 각 메서드가 추상 메서드인지 확인
        for method_name in required_methods:
            method = getattr(NewsSourceManager, method_name)
            assert getattr(method, '__isabstractmethod__', False)


class TestSentimentAnalyzerInterface:
    """감성 분석기 인터페이스 테스트"""
    
    def test_is_abstract_class(self):
        """추상 클래스 여부 테스트"""
        assert issubclass(SentimentAnalyzer, ABC)
    
    def test_required_methods(self):
        """필수 메서드 테스트"""
        # 필수 추상 메서드 목록
        required_methods = [
            'analyze',
            'analyze_batch',
            'analyze_news',
            'analyze_news_batch'
        ]
        
        # 각 메서드가 추상 메서드인지 확인
        for method_name in required_methods:
            method = getattr(SentimentAnalyzer, method_name)
            assert getattr(method, '__isabstractmethod__', False)
