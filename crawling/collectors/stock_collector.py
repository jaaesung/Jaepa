"""
주식 및 암호화폐 데이터 수집 모듈

Polygon.io API를 사용하여 주식 및 암호화폐 데이터를 수집합니다.
"""
import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import pandas as pd
import numpy as np
import requests
from pymongo import MongoClient
import pymongo
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
env_path = Path(__file__).parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

# 설정 파일 로드
config_path = Path(__file__).parents[1] / 'config' / 'sources.json'
try:
    with open(config_path, 'r') as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    logger.error(f"설정 파일을 찾을 수 없습니다: {config_path}")
    CONFIG = {
        "stock_data": {
            "technical_indicators": ["sma", "ema", "rsi", "bollinger_bands", "macd"],
            "moving_averages": [5, 10, 20, 50, 200]
        },
        "storage": {
            "mongodb": {
                "stock_data_collection": "stock_data",
                "crypto_data_collection": "crypto_data"
            }
        }
    }


class StockDataCrawler:
    """
    주식 및 암호화폐 데이터 수집 클래스

    Polygon.io API를 사용하여 금융 데이터를 수집하고 기술적 지표를 계산합니다.
    """

    def __init__(self, db_connect: bool = True):
        """
        StockDataCrawler 클래스 초기화

        Args:
            db_connect: MongoDB 연결 여부 (기본값: True)
        """
        self.config = CONFIG
        self.stock_config = self.config['stock_data']

        # MongoDB 연결 설정
        if db_connect:
            mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
            mongo_db_name = os.getenv("MONGO_DB_NAME", "jaepa")

            try:
                self.client = MongoClient(mongo_uri)
                self.db = self.client[mongo_db_name]
                self.stock_collection = self.db[self.config['storage']['mongodb']['stock_data_collection']]
                self.crypto_collection = self.db[self.config['storage']['mongodb']['crypto_data_collection']]

                # 인덱스 생성
                self.stock_collection.create_index([("symbol", pymongo.ASCENDING), ("date", pymongo.DESCENDING)])
                self.crypto_collection.create_index([("symbol", pymongo.ASCENDING), ("date", pymongo.DESCENDING)])

                logger.info("MongoDB 연결 성공")
            except Exception as e:
                logger.error(f"MongoDB 연결 실패: {str(e)}")
                self.client = None
                self.db = None
                self.stock_collection = None
                self.crypto_collection = None
        else:
            self.client = None
            self.db = None
            self.stock_collection = None
            self.crypto_collection = None

    def get_stock_data_polygon(self, symbol: str, from_date: str, to_date: str) -> pd.DataFrame:
        """
        Polygon.io API를 사용하여 주식 데이터 수집

        Args:
            symbol: 주식 심볼 (예: AAPL)
            from_date: 시작 날짜 (YYYY-MM-DD)
            to_date: 종료 날짜 (YYYY-MM-DD)

        Returns:
            pd.DataFrame: 주식 데이터
        """
        try:
            api_key = os.getenv("POLYGON_API_KEY")
            if not api_key:
                logger.error("Polygon API 키가 설정되지 않았습니다.")
                return pd.DataFrame()

            base_url = "https://api.polygon.io/v2/aggs/ticker"
            url = f"{base_url}/{symbol}/range/1/day/{from_date}/{to_date}?apiKey={api_key}"

            response = requests.get(url)

            if response.status_code != 200:
                logger.error(f"Polygon API 오류 ({response.status_code}): {response.text}")
                return pd.DataFrame()

            data = response.json()

            if not data.get('results'):
                logger.warning(f"Polygon API에서 데이터를 찾을 수 없습니다: {symbol}")
                return pd.DataFrame()

            # 결과를 데이터프레임으로 변환
            df = pd.DataFrame(data['results'])

            # 컬럼 이름 변경
            df = df.rename(columns={
                'v': 'volume',
                'o': 'open',
                'c': 'close',
                'h': 'high',
                'l': 'low',
                't': 'timestamp'
            })

            # 타임스탬프를 날짜로 변환 (밀리초에서 변환)
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d')

            # 추가 정보 컬럼
            df['symbol'] = symbol
            df['crawled_date'] = datetime.now().strftime('%Y-%m-%d')

            # MongoDB에 저장
            if self.stock_collection is not None:
                data_dicts = df.to_dict('records')
                for record in data_dicts:
                    # 이미 존재하는 레코드는 업데이트
                    self.stock_collection.update_one(
                        {"symbol": record["symbol"], "date": record["date"]},
                        {"$set": record},
                        upsert=True
                    )
                logger.info(f"{symbol} 주식 데이터 저장 완료 ({len(df)} 레코드)")

            return df

        except Exception as e:
            logger.error(f"Polygon API 데이터 수집 실패: {symbol} - {str(e)}")
            return pd.DataFrame()

    def get_stock_data(self, symbol: str, start_date: Optional[str] = None,
                       end_date: Optional[str] = None, period: Optional[str] = None,
                       interval: Optional[str] = None) -> pd.DataFrame:
        """
        주식 데이터 수집 (Polygon.io API 사용)

        Args:
            symbol: 주식 심볼 (예: AAPL)
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            period: 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: 간격 (1d, 1wk, 1mo) - 현재 Polygon에서는 1d만 지원

        Returns:
            pd.DataFrame: 주식 데이터
        """
        try:
            # 날짜 범위 계산
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')

            if not start_date:
                if period:
                    # 기간을 기준으로 시작 날짜 계산
                    days_map = {
                        '1d': 1, '5d': 5, '1mo': 30, '3mo': 90,
                        '6mo': 180, '1y': 365, '2y': 730, '5y': 1825,
                        'max': 3650  # 약 10년
                    }
                    days = days_map.get(period, 30)
                    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                else:
                    # 기본 기간은 1개월
                    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            # Polygon API 사용
            return self.get_stock_data_polygon(symbol, start_date, end_date)

        except Exception as e:
            logger.error(f"주식 데이터 수집 실패: {symbol} - {str(e)}")
            return pd.DataFrame()

    def get_crypto_data_polygon(self, symbol: str, from_date: str, to_date: str) -> pd.DataFrame:
        """
        Polygon.io API를 사용하여 암호화폐 데이터 수집

        Args:
            symbol: 암호화폐 심볼 (예: X:BTC-USD)
            from_date: 시작 날짜 (YYYY-MM-DD)
            to_date: 종료 날짜 (YYYY-MM-DD)

        Returns:
            pd.DataFrame: 암호화폐 데이터
        """
        try:
            api_key = os.getenv("POLYGON_API_KEY")
            if not api_key:
                logger.error("Polygon API 키가 설정되지 않았습니다.")
                return pd.DataFrame()

            # 암호화폐 티커 포맷 확인 (Polygon은 보통 X:BTC-USD 형식을 사용)
            if not symbol.startswith("X:"):
                crypto_symbol = f"X:{symbol}-USD"
            else:
                crypto_symbol = symbol

            base_url = "https://api.polygon.io/v2/aggs/ticker"
            url = f"{base_url}/{crypto_symbol}/range/1/day/{from_date}/{to_date}?apiKey={api_key}"

            response = requests.get(url)

            if response.status_code != 200:
                logger.error(f"Polygon API 오류 ({response.status_code}): {response.text}")
                return pd.DataFrame()

            data = response.json()

            if not data.get('results'):
                logger.warning(f"Polygon API에서 데이터를 찾을 수 없습니다: {crypto_symbol}")
                return pd.DataFrame()

            # 결과를 데이터프레임으로 변환
            df = pd.DataFrame(data['results'])

            # 컬럼 이름 변경
            df = df.rename(columns={
                'v': 'volume',
                'o': 'open',
                'c': 'close',
                'h': 'high',
                'l': 'low',
                't': 'timestamp',
                'vw': 'volume_weighted_price'
            })

            # 타임스탬프를 날짜로 변환 (밀리초에서 변환)
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d')

            # 추가 정보 컬럼
            df['symbol'] = symbol
            df['price'] = df['close']  # 호환성을 위해 price 컬럼 추가
            df['crawled_date'] = datetime.now().strftime('%Y-%m-%d')

            # MongoDB에 저장
            if self.crypto_collection is not None:
                data_dicts = df.to_dict('records')
                for record in data_dicts:
                    self.crypto_collection.update_one(
                        {"symbol": record["symbol"], "date": record["date"]},
                        {"$set": record},
                        upsert=True
                    )
                logger.info(f"{symbol} 암호화폐 데이터 저장 완료 ({len(df)} 레코드)")

            return df

        except Exception as e:
            logger.error(f"암호화폐 데이터 수집 실패: {symbol} - {str(e)}")
            return pd.DataFrame()

    def get_crypto_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """
        암호화폐 데이터 수집 (Polygon.io API 사용)

        Args:
            symbol: 암호화폐 ID (예: BTC, ETH)
            days: 수집할 일수

        Returns:
            pd.DataFrame: 암호화폐 데이터
        """
        try:
            # 날짜 범위 계산
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            # Polygon API 사용
            return self.get_crypto_data_polygon(symbol, start_date, end_date)

        except Exception as e:
            logger.error(f"암호화폐 데이터 수집 실패: {symbol} - {str(e)}")
            return pd.DataFrame()

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        기술적 지표 계산

        Args:
            data: 주가 데이터 (OHLCV 포함)

        Returns:
            pd.DataFrame: 기술적 지표가 추가된 데이터프레임
        """
        if data.empty:
            return data

        # 컬럼명 확인 및 대소문자 통일
        required_columns = ['open', 'high', 'low', 'close', 'volume']

        # 데이터프레임 복사
        df = data.copy()

        # 컬럼명 소문자로 변환
        df.columns = [col.lower() if isinstance(col, str) else col for col in df.columns]

        # 필수 컬럼 존재 확인
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"기술적 지표 계산을 위한 필수 컬럼 누락: {missing_columns}")
            return data

        try:
            # 이동평균선 (SMA)
            if 'sma' in self.stock_config['technical_indicators']:
                for period in self.stock_config['moving_averages']:
                    df[f'sma_{period}'] = df['close'].rolling(window=period).mean()

            # 지수이동평균선 (EMA)
            if 'ema' in self.stock_config['technical_indicators']:
                for period in self.stock_config['moving_averages']:
                    df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()

            # 상대강도지수 (RSI)
            if 'rsi' in self.stock_config['technical_indicators']:
                # 가격 변화 계산
                delta = df['close'].diff()

                # 상승/하락 구분
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)

                # 평균 상승/하락 계산 (14일 기준)
                avg_gain = gain.rolling(window=14).mean()
                avg_loss = loss.rolling(window=14).mean()

                # 상대강도 (RS) 계산
                rs = avg_gain / avg_loss

                # RSI 계산
                df['rsi_14'] = 100 - (100 / (1 + rs))

            # 볼린저 밴드
            if 'bollinger_bands' in self.stock_config['technical_indicators']:
                # 20일 이동평균선
                df['bb_middle'] = df['close'].rolling(window=20).mean()

                # 20일 표준편차
                df['bb_std'] = df['close'].rolling(window=20).std()

                # 상단/하단 밴드 (2 표준편차)
                df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
                df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)

            # MACD (Moving Average Convergence Divergence)
            if 'macd' in self.stock_config['technical_indicators']:
                # 12일 지수이동평균
                ema_12 = df['close'].ewm(span=12, adjust=False).mean()

                # 26일 지수이동평균
                ema_26 = df['close'].ewm(span=26, adjust=False).mean()

                # MACD 라인
                df['macd'] = ema_12 - ema_26

                # 시그널 라인 (9일 MACD의 지수이동평균)
                df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

                # MACD 히스토그램
                df['macd_hist'] = df['macd'] - df['macd_signal']

            return df

        except Exception as e:
            logger.error(f"기술적 지표 계산 실패: {str(e)}")
            return data

    def get_stock_info_polygon(self, symbol: str) -> Dict[str, Any]:
        """
        Polygon.io API를 사용하여 주식 기본 정보 조회

        Args:
            symbol: 주식 심볼 (예: AAPL)

        Returns:
            Dict[str, Any]: 주식 정보
        """
        try:
            api_key = os.getenv("POLYGON_API_KEY")
            if not api_key:
                logger.error("Polygon API 키가 설정되지 않았습니다.")
                return {'symbol': symbol, 'error': 'API 키 없음'}

            url = f"https://api.polygon.io/v3/reference/tickers/{symbol}?apiKey={api_key}"

            response = requests.get(url)

            if response.status_code != 200:
                logger.error(f"Polygon API 오류 ({response.status_code}): {response.text}")
                return {'symbol': symbol, 'error': f'API 오류: {response.status_code}'}

            data = response.json()
            result = data.get('results', {})

            # 필요한 정보만 선택
            stock_info = {
                'symbol': symbol,
                'name': result.get('name', ''),
                'type': result.get('type', ''),
                'market': result.get('market', ''),
                'primary_exchange': result.get('primary_exchange', ''),
                'currency': result.get('currency_name', ''),
                'cik': result.get('cik', ''),
                'description': result.get('description', ''),
                'sic_code': result.get('sic_code', ''),
                'sic_description': result.get('sic_description', ''),
                'homepage_url': result.get('homepage_url', ''),
                'total_employees': result.get('total_employees', 0),
                'list_date': result.get('list_date', ''),
                'crawled_date': datetime.now().strftime('%Y-%m-%d')
            }

            return stock_info

        except Exception as e:
            logger.error(f"주식 정보 조회 실패: {symbol} - {str(e)}")
            return {'symbol': symbol, 'error': str(e)}

    def get_multiple_stocks(self, symbols: List[str], days: int = 30) -> Dict[str, pd.DataFrame]:
        """
        여러 주식 데이터 수집

        Args:
            symbols: 주식 심볼 목록
            days: 수집할 기간(일)

        Returns:
            Dict[str, pd.DataFrame]: 심볼별 주식 데이터
        """
        result = {}

        for symbol in symbols:
            # 시작 날짜 계산
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')

            # 데이터 수집
            data = self.get_stock_data_polygon(symbol, start_date, end_date)

            if not data.empty:
                # 기술적 지표 계산
                data_with_indicators = self.calculate_indicators(data)
                result[symbol] = data_with_indicators

        return result

    def close(self):
        """
        MongoDB 연결 종료
        """
        if self.client:
            self.client.close()
            logger.info("MongoDB 연결 종료")


if __name__ == "__main__":
    # 직접 실행 시 간단한 테스트 코드
    crawler = StockDataCrawler(db_connect=False)

    # 주식 데이터 수집 테스트
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    data = crawler.get_stock_data_polygon("AAPL", start_date, end_date)

    if not data.empty:
        # 기술적 지표 계산
        data_with_indicators = crawler.calculate_indicators(data)

        # 결과 출력
        print(f"AAPL 데이터 수집 완료: {len(data)} 레코드")
        print(data_with_indicators.tail(3))

    # 암호화폐 데이터 수집 테스트
    crypto_data = crawler.get_crypto_data_polygon("BTC", start_date, end_date)

    if not crypto_data.empty:
        print(f"Bitcoin 데이터 수집 완료: {len(crypto_data)} 레코드")
        print(crypto_data.tail(3))

    crawler.close()
