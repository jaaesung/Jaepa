"""
의존성 주입 모듈 테스트
"""
import pytest
from unittest.mock import MagicMock, patch

from core.di import (
    container, register_mongodb_client, register_http_client,
    register_news_source_manager, register_sentiment_analyzer,
    register_news_crawler, register_sentiment_analysis_service,
    register_stock_data_service
)
from core.interfaces import (
    DatabaseClient, MongoDBClient, HttpClient,
    NewsSourceManager, SentimentAnalyzer
)


class TestDependencyInjection:
    """의존성 주입 시스템 테스트"""
    
    def test_container_exists(self):
        """컨테이너 존재 여부 테스트"""
        assert container is not None
    
    def test_register_mongodb_client(self):
        """MongoDB 클라이언트 등록 테스트"""
        # 모의 클래스 생성
        mock_class = MagicMock(spec=MongoDBClient)
        
        # 클래스 등록
        register_mongodb_client(mock_class)
        
        # 등록된 클래스 확인
        assert container.mongodb_client_cls() == mock_class
    
    def test_register_http_client(self):
        """HTTP 클라이언트 등록 테스트"""
        # 모의 클래스 생성
        mock_class = MagicMock(spec=HttpClient)
        
        # 클래스 등록
        register_http_client(mock_class)
        
        # 등록된 클래스 확인
        assert container.http_client_cls() == mock_class
    
    def test_register_news_source_manager(self):
        """뉴스 소스 관리자 등록 테스트"""
        # 모의 클래스 생성
        mock_class = MagicMock(spec=NewsSourceManager)
        
        # 클래스 등록
        register_news_source_manager(mock_class)
        
        # 등록된 클래스 확인
        assert container.news_source_manager_cls() == mock_class
    
    def test_register_sentiment_analyzer(self):
        """감성 분석기 등록 테스트"""
        # 모의 클래스 생성
        mock_class = MagicMock(spec=SentimentAnalyzer)
        
        # 클래스 등록
        register_sentiment_analyzer(mock_class)
        
        # 등록된 클래스 확인
        assert container.sentiment_analyzer_cls() == mock_class
    
    def test_register_news_crawler(self):
        """뉴스 크롤러 등록 테스트"""
        # 모의 클래스 생성
        mock_class = MagicMock()
        
        # 클래스 등록
        register_news_crawler(mock_class)
        
        # 등록된 클래스 확인
        assert container.news_crawler_cls() == mock_class
    
    def test_register_sentiment_analysis_service(self):
        """감성 분석 서비스 등록 테스트"""
        # 모의 클래스 생성
        mock_class = MagicMock()
        
        # 클래스 등록
        register_sentiment_analysis_service(mock_class)
        
        # 등록된 클래스 확인
        assert container.sentiment_analysis_service_cls() == mock_class
    
    def test_register_stock_data_service(self):
        """주식 데이터 서비스 등록 테스트"""
        # 모의 클래스 생성
        mock_class = MagicMock()
        
        # 클래스 등록
        register_stock_data_service(mock_class)
        
        # 등록된 클래스 확인
        assert container.stock_data_service_cls() == mock_class
    
    def test_mongodb_client_instance(self):
        """MongoDB 클라이언트 인스턴스 테스트"""
        # 모의 클래스 생성
        mock_class = MagicMock(spec=MongoDBClient)
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        
        # 클래스 등록
        register_mongodb_client(mock_class)
        
        # 인스턴스 생성
        client = container.mongodb_client()
        
        # 인스턴스 확인
        assert client == mock_instance
        mock_class.assert_called_once()
    
    def test_http_client_instance(self):
        """HTTP 클라이언트 인스턴스 테스트"""
        # 모의 클래스 생성
        mock_class = MagicMock(spec=HttpClient)
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        
        # 클래스 등록
        register_http_client(mock_class)
        
        # 인스턴스 생성
        client = container.http_client()
        
        # 인스턴스 확인
        assert client == mock_instance
        mock_class.assert_called_once()
    
    def test_singleton_instance(self):
        """싱글톤 인스턴스 테스트"""
        # 모의 클래스 생성
        mock_class = MagicMock()
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        
        # 싱글톤 등록
        container.register_singleton("test_singleton", mock_class)
        
        # 인스턴스 생성
        instance1 = container.test_singleton()
        instance2 = container.test_singleton()
        
        # 동일한 인스턴스인지 확인
        assert instance1 == instance2
        assert instance1 == mock_instance
        mock_class.assert_called_once()
