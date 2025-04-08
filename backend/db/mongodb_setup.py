"""
MongoDB 설정 및 인덱스 생성 모듈

MongoDB 데이터베이스, 컬렉션 및 인덱스를 설정합니다.
"""
import os
import logging
from pathlib import Path
from datetime import datetime

import pymongo
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
env_path = Path(__file__).parents[2] / '.env'
load_dotenv(dotenv_path=env_path)


class MongoDBSetup:
    """
    MongoDB 데이터베이스 설정 클래스
    
    데이터베이스, 컬렉션 및 인덱스를 생성하고 관리합니다.
    """
    
    def __init__(self):
        """
        MongoDBSetup 클래스 초기화
        """
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.mongo_db_name = os.getenv("MONGO_DB_NAME", "jaepa")
        self.client = None
        self.db = None
        
        # 컬렉션 이름 정의
        self.news_collection_name = "financial_news"
        self.sentiment_collection_name = "news_sentiment_trends"
        self.stock_data_collection_name = "stock_data"
        self.symbol_news_collection_name = "symbol_news_relation"
        self.sentiment_stock_collection_name = "sentiment_stock_correlation"
        
    def connect(self):
        """
        MongoDB 연결 설정
        """
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db_name]
            logger.info(f"MongoDB에 연결되었습니다: {self.mongo_uri}, DB: {self.mongo_db_name}")
            return True
        except Exception as e:
            logger.error(f"MongoDB 연결 실패: {str(e)}")
            return False
            
    def setup_collections(self):
        """
        필요한 모든 컬렉션 설정
        """
        if not self.client or not self.db:
            if not self.connect():
                return False
        
        try:
            # 1. 뉴스 컬렉션 설정
            self.setup_news_collection()
            
            # 2. 감성 트렌드 컬렉션 설정
            self.setup_sentiment_trends_collection()
            
            # 3. 주식 데이터 컬렉션 설정
            self.setup_stock_data_collection()
            
            # 4. 심볼-뉴스 관계 컬렉션 설정
            self.setup_symbol_news_relation_collection()
            
            # 5. 감성-주가 상관관계 컬렉션 설정
            self.setup_sentiment_stock_correlation_collection()
            
            logger.info("모든 MongoDB 컬렉션이 성공적으로 설정되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"컬렉션 설정 중 오류 발생: {str(e)}")
            return False
    
    def setup_news_collection(self):
        """
        뉴스 컬렉션 및 인덱스 설정
        """
        collection = self.db[self.news_collection_name]
        
        # 기본 인덱스 생성
        collection.create_index([(("url"), ASCENDING)], unique=True)
        collection.create_index([(("published_date"), DESCENDING)])
        collection.create_index([(("crawled_date"), DESCENDING)])
        collection.create_index([(("source"), ASCENDING)])
        collection.create_index([(("source_type"), ASCENDING)])
        collection.create_index([(("related_symbols"), ASCENDING)])
        
        # 복합 인덱스
        collection.create_index([
            (("published_date"), DESCENDING),
            (("source"), ASCENDING)
        ])
        
        collection.create_index([
            (("related_symbols"), ASCENDING),
            (("published_date"), DESCENDING)
        ])
        
        # 감성 분석 결과에 대한 인덱스
        collection.create_index([(("sentiment.positive"), DESCENDING)])
        collection.create_index([(("sentiment.negative"), DESCENDING)])
        
        # 텍스트 인덱스 처리 - MongoDB는 컬렉션당 하나의 텍스트 인덱스만 허용
        try:
            # 기존 텍스트 인덱스 확인 및 삭제
            existing_indexes = collection.index_information()
            for idx_name, idx_info in existing_indexes.items():
                if 'weights' in idx_info:  # 텍스트 인덱스 식별
                    try:
                        collection.drop_index(idx_name)
                        logger.info(f"기존 텍스트 인덱스 '{idx_name}' 삭제됨")
                    except Exception as e:
                        logger.warning(f"텍스트 인덱스 '{idx_name}' 삭제 중 오류: {str(e)}")
            
            # 복합 텍스트 인덱스 생성
            collection.create_index([
                (("title"), TEXT),
                (("keywords"), TEXT),
                (("content"), TEXT)
            ], 
            weights={
                "title": 10,      # 제목에 더 높은 가중치
                "keywords": 5,    # 키워드에 중간 가중치
                "content": 1      # 내용에 낮은 가중치
            },
            name="content_search_index")
            logger.info("복합 텍스트 인덱스 생성됨")
            
        except Exception as e:
            logger.warning(f"텍스트 인덱스 생성 중 오류: {str(e)}")
        
        logger.info(f"뉴스 컬렉션 '{self.news_collection_name}'이 설정되었습니다.")
    
    def setup_sentiment_trends_collection(self):
        """
        감성 트렌드 컬렉션 및 인덱스 설정
        시간대별 감성 지표를 집계하여 저장
        """
        collection = self.db[self.sentiment_collection_name]
        
        # 인덱스 생성
        collection.create_index([(("date"), DESCENDING)])
        collection.create_index([(("symbol"), ASCENDING)])
        collection.create_index([(("source"), ASCENDING)])
        
        # 복합 인덱스
        collection.create_index([
            (("symbol"), ASCENDING),
            (("date"), DESCENDING)
        ])
        
        collection.create_index([
            (("date"), DESCENDING),
            (("source"), ASCENDING)
        ])
        
        logger.info(f"감성 트렌드 컬렉션 '{self.sentiment_collection_name}'이 설정되었습니다.")
        
        # 샘플 구조:
        # {
        #   "date": "2025-04-08",
        #   "symbol": "BTC",
        #   "hourly_sentiment": [
        #     {"hour": 0, "positive": 0.65, "neutral": 0.25, "negative": 0.1, "volume": 12},
        #     {"hour": 1, "positive": 0.58, "neutral": 0.3, "negative": 0.12, "volume": 8},
        #     ...
        #   ],
        #   "daily_sentiment": {"positive": 0.62, "neutral": 0.27, "negative": 0.11, "volume": 156},
        #   "sources": ["Finnhub", "NewsData.io", "CoinDesk", "CoinTelegraph"]
        # }
    
    def setup_stock_data_collection(self):
        """
        주식 데이터 컬렉션 및 인덱스 설정
        """
        collection = self.db[self.stock_data_collection_name]
        
        # 인덱스 생성
        collection.create_index([(("symbol"), ASCENDING)])
        collection.create_index([(("date"), DESCENDING)])
        
        # 복합 인덱스
        collection.create_index([
            (("symbol"), ASCENDING),
            (("date"), DESCENDING)
        ], unique=True)
        
        logger.info(f"주식 데이터 컬렉션 '{self.stock_data_collection_name}'이 설정되었습니다.")
        
        # 샘플 구조:
        # {
        #   "symbol": "AAPL",
        #   "date": "2025-04-08",
        #   "open": 174.28,
        #   "high": 176.65,
        #   "low": 173.95,
        #   "close": 176.30,
        #   "volume": 64987210,
        #   "adjusted_close": 176.30,
        #   "technical_indicators": {
        #     "sma_20": 172.45,
        #     "sma_50": 168.73,
        #     "rsi_14": 58.64,
        #     "macd_12_26_9": {
        #       "macd": 3.75,
        #       "signal": 2.95,
        #       "histogram": 0.80
        #     }
        #   }
        # }
    
    def setup_symbol_news_relation_collection(self):
        """
        심볼-뉴스 관계 컬렉션 및 인덱스 설정
        특정 심볼과 관련된 뉴스 기사 맵핑
        """
        collection = self.db[self.symbol_news_collection_name]
        
        # 인덱스 생성
        collection.create_index([(("symbol"), ASCENDING)])
        collection.create_index([(("news_url"), ASCENDING)])
        collection.create_index([(("date"), DESCENDING)])
        collection.create_index([(("sentiment_score"), DESCENDING)])
        
        # 복합 인덱스
        collection.create_index([
            (("symbol"), ASCENDING),
            (("date"), DESCENDING)
        ])
        
        collection.create_index([
            (("news_url"), ASCENDING),
            (("symbol"), ASCENDING)
        ], unique=True)
        
        logger.info(f"심볼-뉴스 관계 컬렉션 '{self.symbol_news_collection_name}'이 설정되었습니다.")
        
        # 샘플 구조:
        # {
        #   "symbol": "AAPL",
        #   "news_url": "https://example.com/news/article-1",
        #   "news_title": "Apple Announces New iPhone Model",
        #   "date": "2025-04-08T10:30:00Z",
        #   "relevance_score": 0.85,  # 관련성 점수 (심볼이 얼마나 중요하게 언급되었는지)
        #   "sentiment_score": {
        #     "positive": 0.75,
        #     "neutral": 0.20,
        #     "negative": 0.05
        #   },
        #   "mentions": 3  # 기사 내 심볼 언급 횟수
        # }
    
    def setup_sentiment_stock_correlation_collection(self):
        """
        감성-주가 상관관계 컬렉션 및 인덱스 설정
        감성 지표와 주가 변동의 상관관계 분석 결과 저장
        """
        collection = self.db[self.sentiment_stock_collection_name]
        
        # 인덱스 생성
        collection.create_index([(("symbol"), ASCENDING)])
        collection.create_index([(("date"), DESCENDING)])
        collection.create_index([(("time_frame"), ASCENDING)])
        
        # 복합 인덱스
        collection.create_index([
            (("symbol"), ASCENDING),
            (("date"), DESCENDING),
            (("time_frame"), ASCENDING)
        ], unique=True)
        
        logger.info(f"감성-주가 상관관계 컬렉션 '{self.sentiment_stock_collection_name}'이 설정되었습니다.")
        
        # 샘플 구조:
        # {
        #   "symbol": "AAPL",
        #   "date": "2025-04-08",
        #   "time_frame": "daily",  # "hourly", "daily", "weekly", "monthly"
        #   "correlation": {
        #     "sentiment_vs_price": 0.65,  # 감성 점수와 가격 변동의 상관계수
        #     "sentiment_vs_volume": 0.48,  # 감성 점수와 거래량의 상관계수
        #     "sentiment_lead_hours": 2,  # 감성 변화가 가격 변화를 선행하는 평균 시간
        #     "news_impact_duration": 4  # 뉴스 영향이 지속되는 평균 시간 (시간)
        #   },
        #   "sentiment_analysis": {
        #     "bullish_accuracy": 0.72,  # 긍정적 감성이 상승장을 정확히 예측한 비율
        #     "bearish_accuracy": 0.68,  # 부정적 감성이 하락장을 정확히 예측한 비율
        #     "false_positive_rate": 0.15,  # 거짓 긍정 비율
        #     "false_negative_rate": 0.18  # 거짓 부정 비율
        #   }
        # }
    
    def update_sentiment_trends(self):
        """
        감성 트렌드 데이터 업데이트
        뉴스 컬렉션에서 감성 데이터를 집계하여 트렌드 컬렉션 업데이트
        """
        if not self.client or not self.db:
            if not self.connect():
                return False
                
        try:
            news_collection = self.db[self.news_collection_name]
            sentiment_collection = self.db[self.sentiment_collection_name]
            
            # 오늘 날짜
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 날짜 및 심볼별로 집계 파이프라인 실행
            pipeline = [
                # 감성 분석 결과가 있는 기사만 선택
                {"$match": {"sentiment": {"$ne": None}}},
                
                # 날짜 형식 변환 (ISO 문자열 → 날짜 객체)
                {"$addFields": {
                    "date_obj": {"$dateFromString": {"dateString": "$published_date"}},
                    "date_only": {"$substr": ["$published_date", 0, 10]}
                }},
                
                # 심볼별, 시간별 그룹화
                {"$group": {
                    "_id": {
                        "symbol": "$related_symbols",
                        "date": "$date_only",
                        "hour": {"$hour": "$date_obj"}
                    },
                    "avg_positive": {"$avg": "$sentiment.positive"},
                    "avg_neutral": {"$avg": "$sentiment.neutral"},
                    "avg_negative": {"$avg": "$sentiment.negative"},
                    "count": {"$sum": 1},
                    "sources": {"$addToSet": "$source"}
                }},
                
                # 결과 정형화
                {"$project": {
                    "_id": 0,
                    "symbol": "$_id.symbol",
                    "date": "$_id.date",
                    "hour": "$_id.hour",
                    "sentiment": {
                        "positive": "$avg_positive",
                        "neutral": "$avg_neutral",
                        "negative": "$avg_negative"
                    },
                    "volume": "$count",
                    "sources": 1
                }}
            ]
            
            results = list(news_collection.aggregate(pipeline))
            
            # 결과를 심볼별로 그룹화하여 시간별 데이터 구성
            symbol_data = {}
            for r in results:
                symbols = r.get("symbol", [])
                
                # 심볼이 없는 경우 "GENERAL" 카테고리로 분류
                if not symbols or len(symbols) == 0:
                    symbols = ["GENERAL"]
                    
                # 각 심볼에 대해 처리
                for symbol in symbols:
                    if symbol not in symbol_data:
                        symbol_data[symbol] = {
                            "date": r["date"],
                            "symbol": symbol,
                            "hourly_sentiment": [],
                            "sources": set()
                        }
                    
                    # 시간별 감성 데이터 추가
                    symbol_data[symbol]["hourly_sentiment"].append({
                        "hour": r["hour"],
                        "positive": r["sentiment"]["positive"],
                        "neutral": r["sentiment"]["neutral"],
                        "negative": r["sentiment"]["negative"],
                        "volume": r["volume"]
                    })
                    
                    # 소스 정보 추가
                    symbol_data[symbol]["sources"].update(r["sources"])
            
            # 일별 집계 계산 및 데이터베이스 업데이트
            for symbol, data in symbol_data.items():
                # 시간별 데이터 정렬
                data["hourly_sentiment"].sort(key=lambda x: x["hour"])
                
                # 일별 평균 계산
                hourly_data = data["hourly_sentiment"]
                if len(hourly_data) > 0 and sum(h["volume"] for h in hourly_data) > 0:
                    daily_positive = sum(h["positive"] * h["volume"] for h in hourly_data) / sum(h["volume"] for h in hourly_data)
                    daily_neutral = sum(h["neutral"] * h["volume"] for h in hourly_data) / sum(h["volume"] for h in hourly_data)
                    daily_negative = sum(h["negative"] * h["volume"] for h in hourly_data) / sum(h["volume"] for h in hourly_data)
                    daily_volume = sum(h["volume"] for h in hourly_data)
                    
                    # 일별 감성 데이터 추가
                    data["daily_sentiment"] = {
                        "positive": daily_positive,
                        "neutral": daily_neutral,
                        "negative": daily_negative,
                        "volume": daily_volume
                    }
                    
                    # 소스 목록을 리스트로 변환
                    data["sources"] = list(data["sources"])
                    
                    # 데이터베이스 업데이트 (upsert)
                    sentiment_collection.update_one(
                        {"date": data["date"], "symbol": symbol},
                        {"$set": data},
                        upsert=True
                    )
            
            logger.info(f"감성 트렌드 데이터가 업데이트되었습니다. 처리된 심볼: {len(symbol_data)}")
            return True
            
        except Exception as e:
            logger.error(f"감성 트렌드 업데이트 중 오류 발생: {str(e)}")
            return False
    
    def close(self):
        """
        MongoDB 연결 종료
        """
        if self.client:
            self.client.close()
            logger.info("MongoDB 연결이 종료되었습니다.")


# 직접 실행 시 MongoDB 설정 수행
if __name__ == "__main__":
    mongodb_setup = MongoDBSetup()
    
    # 모든 컬렉션 설정
    if mongodb_setup.setup_collections():
        print("MongoDB 설정이 완료되었습니다.")
    else:
        print("MongoDB 설정 중 오류가 발생했습니다.")
    
    # 감성 트렌드 업데이트 예시
    # mongodb_setup.update_sentiment_trends()
    
    mongodb_setup.close()
