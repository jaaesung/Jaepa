"""
주식 데이터 크롤러 테스트 모듈

이 모듈은 StockDataCrawler 클래스의 기능을 테스트합니다.
"""
import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
import requests

# 상위 디렉토리 추가하여 jaepa 패키지 import 가능하게 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from crawling.stock_data_crawler import StockDataCrawler

class TestStockDataCrawler(unittest.TestCase):
    """StockDataCrawler 클래스 테스트"""

    def setUp(self):
        """테스트 셋업: 크롤러 및 목 데이터 초기화"""
        # DB 연결 없이 크롤러 객체 생성
        self.crawler = StockDataCrawler(db_connect=False)
        
        # 목 응답 데이터 생성
        self.mock_stock_data = {
            "status": "OK",
            "request_id": "mock_request_id",
            "results": [
                {
                    "v": 1000000,  # volume
                    "o": 150.0,     # open
                    "c": 155.0,     # close
                    "h": 157.0,     # high
                    "l": 149.0,     # low
                    "t": 1625097600000  # timestamp (밀리초)
                },
                {
                    "v": 1200000,
                    "o": 155.0,
                    "c": 158.0,
                    "h": 160.0,
                    "l": 154.0,
                    "t": 1625184000000
                }
            ]
        }
        
        self.mock_crypto_data = {
            "status": "OK",
            "request_id": "mock_request_id",
            "results": [
                {
                    "v": 5000,       # volume
                    "o": 35000.0,    # open
                    "c": 36000.0,    # close
                    "h": 36500.0,    # high
                    "l": 34800.0,    # low
                    "t": 1625097600000,  # timestamp (밀리초)
                    "vw": 35750.0    # volume weighted price
                },
                {
                    "v": 5500,
                    "o": 36000.0,
                    "c": 37000.0,
                    "h": 37500.0,
                    "l": 35900.0,
                    "t": 1625184000000,
                    "vw": 36750.0
                }
            ]
        }

    @patch('requests.get')
    @patch('os.getenv')
    def test_get_stock_data_polygon_success(self, mock_getenv, mock_get):
        """Polygon API에서 주식 데이터 수집 테스트 (성공 케이스)"""
        # API 키 목 설정
        mock_getenv.return_value = "mock_api_key"
        
        # 요청 응답 목 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_stock_data
        mock_get.return_value = mock_response
        
        # 함수 호출
        from_date = "2021-07-01"
        to_date = "2021-07-02"
        result = self.crawler.get_stock_data_polygon("AAPL", from_date, to_date)
        
        # 결과 검증
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertTrue('symbol' in result.columns)
        self.assertEqual(result['symbol'].iloc[0], 'AAPL')
        self.assertTrue('date' in result.columns)
        self.assertTrue('open' in result.columns)
        self.assertTrue('close' in result.columns)
        self.assertTrue('high' in result.columns)
        self.assertTrue('low' in result.columns)
        self.assertTrue('volume' in result.columns)
        
        # API 호출 검증
        mock_get.assert_called_once()
        call_args = mock_get.call_args[0][0]
        self.assertIn("AAPL", call_args)
        self.assertIn("2021-07-01", call_args)
        self.assertIn("2021-07-02", call_args)
        self.assertIn("mock_api_key", call_args)

    @patch('requests.get')
    @patch('os.getenv')
    def test_get_stock_data_polygon_api_error(self, mock_getenv, mock_get):
        """Polygon API 오류 처리 테스트"""
        # API 키 목 설정
        mock_getenv.return_value = "mock_api_key"
        
        # API 오류 응답 목 설정
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized: Invalid API key"
        mock_get.return_value = mock_response
        
        # 함수 호출
        result = self.crawler.get_stock_data_polygon("AAPL", "2021-07-01", "2021-07-02")
        
        # 결과 검증: 오류 시 빈 DataFrame 반환
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)

    @patch('requests.get')
    @patch('os.getenv')
    def test_get_crypto_data_polygon_success(self, mock_getenv, mock_get):
        """암호화폐 데이터 수집 테스트 (성공 케이스)"""
        # API 키 목 설정
        mock_getenv.return_value = "mock_api_key"
        
        # 요청 응답 목 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_crypto_data
        mock_get.return_value = mock_response
        
        # 함수 호출
        from_date = "2021-07-01"
        to_date = "2021-07-02"
        result = self.crawler.get_crypto_data_polygon("BTC", from_date, to_date)
        
        # 결과 검증
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertTrue('symbol' in result.columns)
        self.assertEqual(result['symbol'].iloc[0], 'BTC')
        self.assertTrue('price' in result.columns)  # 추가된 컬럼
        self.assertTrue('volume_weighted_price' in result.columns)
        
        # API 호출 검증
        mock_get.assert_called_once()
        call_args = mock_get.call_args[0][0]
        self.assertIn("X:BTC-USD", call_args)  # 암호화폐 포맷 확인

    def test_calculate_indicators(self):
        """기술적 지표 계산 테스트"""
        # 테스트 데이터 생성
        data = pd.DataFrame({
            'open': [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0,
                    110.0, 111.0, 112.0, 113.0, 114.0, 115.0, 116.0, 117.0, 118.0, 119.0, 120.0],
            'high': [105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0,
                    115.0, 116.0, 117.0, 118.0, 119.0, 120.0, 121.0, 122.0, 123.0, 124.0, 125.0],
            'low': [95.0, 96.0, 97.0, 98.0, 99.0, 100.0, 101.0, 102.0, 103.0, 104.0,
                  105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0, 115.0],
            'close': [102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0, 
                     112.0, 113.0, 114.0, 115.0, 116.0, 117.0, 118.0, 119.0, 120.0, 121.0, 122.0],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 
                      2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000]
        })
        
        # 기술적 지표 계산
        result = self.crawler.calculate_indicators(data)
        
        # 결과 검증
        self.assertIsInstance(result, pd.DataFrame)
        
        # SMA 검증
        for period in self.crawler.stock_config['moving_averages']:
            self.assertIn(f'sma_{period}', result.columns)
            
        # EMA 검증
        for period in self.crawler.stock_config['moving_averages']:
            self.assertIn(f'ema_{period}', result.columns)
            
        # RSI 검증
        self.assertIn('rsi_14', result.columns)
        
        # 볼린저 밴드 검증
        self.assertIn('bb_middle', result.columns)
        self.assertIn('bb_upper', result.columns)
        self.assertIn('bb_lower', result.columns)
        
        # MACD 검증
        self.assertIn('macd', result.columns)
        self.assertIn('macd_signal', result.columns)
        self.assertIn('macd_hist', result.columns)

    @patch('requests.get')
    @patch('os.getenv')
    def test_get_multiple_stocks(self, mock_getenv, mock_get):
        """여러 주식 데이터 수집 테스트"""
        # API 키 목 설정
        mock_getenv.return_value = "mock_api_key"
        
        # 요청 응답 목 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_stock_data
        mock_get.return_value = mock_response
        
        # 함수 호출
        symbols = ["AAPL", "MSFT"]
        result = self.crawler.get_multiple_stocks(symbols, days=7)
        
        # 결과 검증
        self.assertIsInstance(result, dict)
        for symbol in symbols:
            self.assertIn(symbol, result)
            self.assertIsInstance(result[symbol], pd.DataFrame)
            
        # API 호출 횟수 검증 (심볼 개수만큼)
        self.assertEqual(mock_get.call_count, len(symbols))

    def test_api_key_missing(self):
        """API 키 누락 시 테스트"""
        with patch('os.getenv', return_value=None):
            result = self.crawler.get_stock_data_polygon("AAPL", "2021-07-01", "2021-07-02")
            self.assertTrue(result.empty)

    @patch('requests.get')
    def test_network_error(self, mock_get):
        """네트워크 오류 테스트"""
        # 네트워크 오류 시뮬레이션
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        with patch('os.getenv', return_value="mock_api_key"):
            result = self.crawler.get_stock_data_polygon("AAPL", "2021-07-01", "2021-07-02")
            self.assertTrue(result.empty)

    def tearDown(self):
        """테스트 완료 후 정리"""
        self.crawler.close()


if __name__ == '__main__':
    unittest.main()
