"""
뉴스 통합 및 중복 제거 기능 테스트 모듈

NewsSourcesHandler 클래스의 데이터 통합 및 중복 제거 기능을 테스트합니다.
"""
import unittest
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock
import json

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parents[2]))

from crawling.news_sources_enhanced import NewsSourcesHandler


class TestNewsCombinerAPI(unittest.TestCase):
    """
    뉴스 통합 및 중복 제거 기능 테스트 클래스
    """
    
    def setUp(self):
        """
        테스트 설정
        """
        # MongoDB 연결 없이 핸들러 초기화
        self.handler = NewsSourcesHandler(db_connect=False)
        
        # 테스트 데이터 경로
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        
        # 테스트 기사 데이터
        self.test_articles = [
            # 기사 1
            {
                "title": "Bitcoin Surges to New High",
                "summary": "Bitcoin has reached a new all-time high price.",
                "url": "https://example.com/bitcoin1",
                "published_date": datetime.now().isoformat(),
                "source": "Source A",
                "source_type": "finnhub",
                "keywords": ["bitcoin", "price", "high"]
            },
            # 기사 2 (제목 유사, 다른 URL)
            {
                "title": "Bitcoin Reaches New All-Time High",
                "summary": "The price of Bitcoin has surged to a new record.",
                "url": "https://another-site.com/bitcoin-ath",
                "published_date": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "source": "Source B",
                "source_type": "newsdata",
                "keywords": ["bitcoin", "record", "price"]
            },
            # 기사 3 (완전히 다른 내용)
            {
                "title": "Ethereum 2.0 Update Coming Soon",
                "summary": "Ethereum 2.0 update is scheduled for next month.",
                "url": "https://example.com/ethereum",
                "published_date": datetime.now().isoformat(),
                "source": "Source A",
                "source_type": "finnhub",
                "keywords": ["ethereum", "update", "blockchain"]
            },
            # 기사 4 (기사 1과 동일 URL - 명확한 중복)
            {
                "title": "Bitcoin Surges to New High [Updated]",
                "summary": "Updated: Bitcoin has reached a new all-time high price with additional details.",
                "url": "https://example.com/bitcoin1",
                "published_date": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "source": "Source A",
                "source_type": "finnhub",
                "keywords": ["bitcoin", "price", "high", "update"]
            }
        ]
    
    def tearDown(self):
        """
        테스트 종료 후 정리
        """
        self.handler.close()
    
    def test_calculate_text_hash(self):
        """
        텍스트 해시값 계산 테스트
        """
        # 테스트 텍스트
        text1 = "This is a test text"
        text2 = "This is another test text"
        
        # 해시값 계산
        hash1 = self.handler._calculate_text_hash(text1)
        hash2 = self.handler._calculate_text_hash(text2)
        
        # 검증
        self.assertIsInstance(hash1, str)
        self.assertNotEqual(hash1, hash2)
        
        # 동일 텍스트 해시 검증
        hash3 = self.handler._calculate_text_hash(text1)
        self.assertEqual(hash1, hash3)
    
    def test_deduplicate_news_by_url(self):
        """
        URL 기반 뉴스 중복 제거 테스트
        """
        # 중복 제거 실행
        deduplicated = self.handler._deduplicate_news(self.test_articles)
        
        # 검증 - 기사 4는 기사 1과 URL이 같으므로 제거되어야 함
        self.assertEqual(len(deduplicated), 3)
        
        # URL 목록 추출 및 중복 확인
        urls = [article["url"] for article in deduplicated]
        self.assertEqual(len(urls), len(set(urls)))
        
        # 특정 URL 확인
        self.assertIn("https://example.com/bitcoin1", urls)
        self.assertIn("https://another-site.com/bitcoin-ath", urls)
        self.assertIn("https://example.com/ethereum", urls)
    
    def test_deduplicate_news_by_title_similarity(self):
        """
        제목 유사도 기반 뉴스 중복 제거 테스트
        """
        # 테스트 기사 (유사한 제목, 다른 URL)
        test_articles = [
            {
                "title": "Stocks Rally on Economic News",
                "summary": "Stock markets showed strong gains today.",
                "url": "https://example.com/stocks1",
                "published_date": datetime.now().isoformat(),
                "source": "Source A"
            },
            {
                "title": "Stock Markets Rally After Economic Data Release",
                "summary": "Global stock markets rallied after positive economic data.",
                "url": "https://example.com/stocks2",
                "published_date": (datetime.now() - timedelta(minutes=2)).isoformat(),
                "source": "Source B"
            }
        ]
        
        # 중복 제거 실행 (높은 유사도 임계값)
        deduplicated_high = self.handler._deduplicate_news(test_articles, title_threshold=95)
        
        # 검증 - 유사도가 95% 미만이므로 둘 다 유지되어야 함
        self.assertEqual(len(deduplicated_high), 2)
        
        # 중복 제거 실행 (낮은 유사도 임계값)
        deduplicated_low = self.handler._deduplicate_news(test_articles, title_threshold=70)
        
        # 검증 - 유사도가 70% 이상이므로 하나만 유지되어야 함
        self.assertEqual(len(deduplicated_low), 1)
    
    def test_deduplicate_news_source_merging(self):
        """
        뉴스 중복 제거 시 소스 정보 병합 테스트
        """
        # 테스트 기사 (동일 URL, 다른 소스)
        test_articles = [
            {
                "title": "Major Tech Announcement",
                "summary": "A major technology company made an announcement today.",
                "url": "https://example.com/tech",
                "published_date": datetime.now().isoformat(),
                "source": "Source A",
                "keywords": ["tech", "announcement"]
            },
            {
                "title": "Major Tech Announcement [Updated]",
                "summary": "Updated details on the technology announcement.",
                "url": "https://example.com/tech",
                "published_date": (datetime.now() - timedelta(minutes=10)).isoformat(),
                "source": "Source B",
                "keywords": ["technology", "news"]
            }
        ]
        
        # 중복 제거 실행
        deduplicated = self.handler._deduplicate_news(test_articles)
        
        # 검증 - URL이 같으므로 하나로 통합되어야 함
        self.assertEqual(len(deduplicated), 1)
        
        # 소스 정보 병합 확인
        self.assertIn("sources", deduplicated[0])
        self.assertIn("Source A", deduplicated[0]["sources"])
        self.assertIn("Source B", deduplicated[0]["sources"])
        
        # 키워드 병합 확인
        self.assertGreaterEqual(len(deduplicated[0]["keywords"]), 3)
        self.assertIn("tech", deduplicated[0]["keywords"])
        self.assertIn("technology", deduplicated[0]["keywords"])
    
    def test_deduplicate_news_time_threshold(self):
        """
        뉴스 중복 제거 시 시간 임계값 테스트
        """
        # 테스트 기사 (유사한 제목, 시간차 큼)
        now = datetime.now()
        test_articles = [
            {
                "title": "Market Update: Oil Prices Rise",
                "summary": "Oil prices increased today due to supply concerns.",
                "url": "https://example.com/oil1",
                "published_date": now.isoformat(),
                "source": "Source A"
            },
            {
                "title": "Market Update: Oil Prices Rising",
                "summary": "Oil prices are on the rise following production cuts.",
                "url": "https://example.com/oil2",
                "published_date": (now - timedelta(minutes=10)).isoformat(),
                "source": "Source B"
            }
        ]
        
        # 중복 제거 실행 (짧은 시간 임계값)
        deduplicated_short = self.handler._deduplicate_news(
            test_articles, title_threshold=80, time_threshold=300  # 5분(300초)
        )
        
        # 검증 - 시간차가 10분이므로 둘 다 유지되어야 함
        self.assertEqual(len(deduplicated_short), 2)
        
        # 중복 제거 실행 (긴 시간 임계값)
        deduplicated_long = self.handler._deduplicate_news(
            test_articles, title_threshold=80, time_threshold=900  # 15분(900초)
        )
        
        # 검증 - 시간차가 10분이고 제목 유사도가 80% 이상이므로 하나만 유지되어야 함
        self.assertEqual(len(deduplicated_long), 1)
    
    @patch.object(NewsSourcesHandler, 'get_news_from_finnhub')
    @patch.object(NewsSourcesHandler, 'get_news_from_newsdata')
    def test_get_combined_news(self, mock_newsdata, mock_finnhub):
        """
        통합 뉴스 수집 테스트
        """
        # 모의 응답 설정
        finnhub_news = [self.test_articles[0], self.test_articles[2]]
        newsdata_news = [self.test_articles[1]]
        
        mock_finnhub.return_value = finnhub_news
        mock_newsdata.return_value = newsdata_news
        
        # API 키 설정
        self.handler.finnhub_api_key = "test_finnhub_key"
        self.handler.newsdata_api_key = "test_newsdata_key"
        self.handler.finnhub_client = MagicMock()
        
        # MongoDB 저장 메서드 모킹
        with patch.object(self.handler, '_save_to_mongodb') as mock_save:
            # 통합 뉴스 수집 실행
            combined = self.handler.get_combined_news(keyword="bitcoin", days=7)
            
            # 검증
            self.assertEqual(len(combined), 3)
            
            # API 호출 확인
            mock_finnhub.assert_called_once_with(symbol="bitcoin", days=7)
            mock_newsdata.assert_called_once_with(keyword="bitcoin", category="business", days=7)
            
            # 저장 호출 확인
            mock_save.assert_called_once()
    
    def test_save_to_mongodb(self):
        """
        MongoDB 저장 기능 테스트
        """
        # 가상의 MongoDB 컬렉션 설정
        mock_collection = MagicMock()
        
        # 기존 문서 검색 결과 설정
        mock_collection.find_one.return_value = {
            "title": "Existing Article",
            "url": "https://example.com/bitcoin1",
            "sources": ["Source C"],
            "keywords": ["existing", "keyword"]
        }
        
        # 핸들러에 모의 컬렉션 설정
        self.handler.news_collection = mock_collection
        
        # 저장 실행
        self.handler._save_to_mongodb(self.test_articles)
        
        # 검증 - find_one 및 update_one/insert_one 호출 확인
        mock_collection.find_one.assert_called()
        
        # 호출 횟수 확인
        insert_count = 0
        update_count = 0
        for call in mock_collection.mock_calls:
            method_name = call[0]
            if method_name == "insert_one":
                insert_count += 1
            elif method_name == "update_one":
                update_count += 1
        
        # URL 중복을 고려하여 최소 1번의 update_one 호출이 있어야 함
        self.assertGreaterEqual(update_count, 1)


if __name__ == "__main__":
    unittest.main()
