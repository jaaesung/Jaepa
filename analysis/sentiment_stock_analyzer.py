"""
감성-주가 상관관계 분석 모듈

뉴스 감성과 주가 변동의 상관관계를 분석하는 기능을 제공합니다.
"""
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
import calendar

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from dotenv import load_dotenv

from crawling.gdelt_client import GDELTClient
from data.stock_data_store import StockDataStore

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

class SentimentStockAnalyzer:
    """
    뉴스 감성과 주가 상관관계 분석 클래스

    뉴스 감성과 주가 변동의 상관관계를 분석하고, 패턴을 식별하는 기능을 제공합니다.
    """

    def __init__(self, db_connect: bool = True):
        """
        SentimentStockAnalyzer 클래스 초기화

        Args:
            db_connect: MongoDB 연결 여부 (기본값: True)
        """
        self.gdelt_client = GDELTClient()
        self.stock_store = StockDataStore()

        # MongoDB 연결 설정
        if db_connect:
            mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
            mongo_db_name = os.getenv("MONGO_DB_NAME", "jaepa")

            try:
                from pymongo import MongoClient
                self.client = MongoClient(mongo_uri)
                self.db = self.client[mongo_db_name]
                self.correlation_collection = self.db['sentiment_stock_correlation']

                # 인덱스 생성
                self._create_indexes()

                logger.info("MongoDB 연결 성공")
            except Exception as e:
                logger.error(f"MongoDB 연결 실패: {str(e)}")
                self.client = None
                self.db = None
                self.correlation_collection = None
        else:
            self.client = None
            self.db = None
            self.correlation_collection = None

    def _create_indexes(self):
        """인덱스 생성"""
        if not self.db or not self.correlation_collection:
            return

        try:
            # 기본 인덱스
            self.correlation_collection.create_index([("symbol", 1)], name="symbol_index")
            self.correlation_collection.create_index([("period", 1)], name="period_index")
            self.correlation_collection.create_index([("analysis_date", -1)], name="analysis_date_index")

            # 복합 인덱스
            self.correlation_collection.create_index([
                ("symbol", 1),
                ("period", 1)
            ], unique=True, name="symbol_period_index")

            logger.info("인덱스가 생성되었습니다.")

        except Exception as e:
            logger.error(f"인덱스 생성 실패: {str(e)}")

    def analyze_correlation(self,
                           symbol: str,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           force_update: bool = False) -> Dict[str, Any]:
        """
        감성과 주가 변동의 상관관계 분석

        Args:
            symbol: 주식 심볼 (예: AAPL)
            start_date: 시작 날짜 (기본값: 90일 전)
            end_date: 종료 날짜 (기본값: 현재)
            force_update: 강제 업데이트 여부

        Returns:
            Dict[str, Any]: 상관관계 분석 결과
        """
        # 날짜 범위 설정
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=90)

        # 기존 분석 결과 확인 (캐싱)
        if not force_update and self.correlation_collection:
            period_key = f"{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}"
            existing = self.correlation_collection.find_one({
                "symbol": symbol,
                "period": period_key
            })

            if existing:
                logger.info(f"기존 분석 결과 사용: {symbol} ({period_key})")
                existing.pop('_id', None)  # MongoDB ID 제거
                return existing

        # 주가 데이터 가져오기
        days = (end_date - start_date).days + 20  # 여유있게 가져오기
        stock_data = self.stock_store.get_stock_price(
            symbol=symbol,
            days=days,
            force_update=force_update
        )

        # 주가 데이터 형식 변환
        formatted_stock_data = []
        for item in stock_data:
            formatted_stock_data.append({
                "date": item.get("date"),
                "close": item.get("close"),
                "change_pct": item.get("change_percentage", 0)
            })

        # GDELT 클라이언트로 상관관계 분석
        correlation = self.gdelt_client.analyze_sentiment_stock_correlation(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            stock_data=formatted_stock_data
        )

        # 분석 결과 저장
        if self.correlation_collection:
            period_key = f"{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}"

            # 저장할 데이터 준비
            save_data = {
                "symbol": symbol,
                "period": period_key,
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "analysis_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "correlation": correlation.get("correlation", {}),
                "sentiment_impact": correlation.get("sentiment_impact", []),
                "data_points": correlation.get("data_points", 0)
            }

            # 저장 또는 업데이트
            self.correlation_collection.update_one(
                {"symbol": symbol, "period": period_key},
                {"$set": save_data},
                upsert=True
            )

            logger.info(f"상관관계 분석 결과 저장됨: {symbol} ({period_key})")

        return correlation

    def identify_sentiment_patterns(self,
                                   symbol: str,
                                   lookback_days: int = 365,
                                   min_pattern_strength: float = 0.3) -> Dict[str, Any]:
        """
        주요 감성 패턴 식별

        Args:
            symbol: 주식 심볼 (예: AAPL)
            lookback_days: 분석 기간 (일)
            min_pattern_strength: 최소 패턴 강도

        Returns:
            Dict[str, Any]: 식별된 패턴 목록
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        # 감성 트렌드 가져오기
        sentiment_data = self.gdelt_client.get_news_sentiment_trends(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval='day'
        )

        if not sentiment_data['trends']:
            return {
                "symbol": symbol,
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "patterns": [],
                "pattern_count": 0
            }

        # 주가 데이터 가져오기
        days = lookback_days + 20  # 여유있게 가져오기
        stock_data = self.stock_store.get_stock_price(
            symbol=symbol,
            days=days
        )

        # 데이터프레임 생성
        sentiment_df = pd.DataFrame(sentiment_data['trends'])
        stock_df = pd.DataFrame(stock_data)

        # 날짜 형식 변환
        sentiment_df['date'] = pd.to_datetime(sentiment_df['interval'])
        stock_df['date'] = pd.to_datetime(stock_df['date'])

        # 감성 점수 추출
        sentiment_df['sentiment_score'] = sentiment_df['sentiment'].apply(lambda x: x.get('score', 0))

        # 데이터 병합
        merged_df = pd.merge_asof(
            sentiment_df.sort_values('date'),
            stock_df.sort_values('date'),
            on='date',
            direction='nearest'
        )

        if len(merged_df) < 10:  # 데이터가 너무 적으면 분석 불가
            return {
                "symbol": symbol,
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "patterns": [],
                "pattern_count": 0
            }

        # 다음 날 주가 변동 계산
        merged_df['next_day_close'] = merged_df['close'].shift(-1)
        merged_df['next_day_change'] = ((merged_df['next_day_close'] - merged_df['close']) / merged_df['close']) * 100

        # 다음 3일 주가 변동 계산
        merged_df['next_3_days_close'] = merged_df['close'].shift(-3)
        merged_df['next_3_days_change'] = ((merged_df['next_3_days_close'] - merged_df['close']) / merged_df['close']) * 100

        # 다음 주 주가 변동 계산
        merged_df['next_week_close'] = merged_df['close'].shift(-5)
        merged_df['next_week_change'] = ((merged_df['next_week_close'] - merged_df['close']) / merged_df['close']) * 100

        # 감성 변화 계산
        merged_df['sentiment_change'] = merged_df['sentiment_score'].diff()

        # 이동 평균 계산
        merged_df['sentiment_ma5'] = merged_df['sentiment_score'].rolling(window=5).mean()
        merged_df['sentiment_ma10'] = merged_df['sentiment_score'].rolling(window=10).mean()

        # NaN 제거
        merged_df = merged_df.dropna()

        # 패턴 식별
        patterns = []

        # 1. 급격한 감성 변화 패턴
        sentiment_std = merged_df['sentiment_score'].std()
        threshold = sentiment_std * 2

        # 급격한 긍정 변화
        positive_surge = merged_df[merged_df['sentiment_change'] > threshold].copy()
        if len(positive_surge) >= 3:
            avg_next_day = positive_surge['next_day_change'].mean()
            avg_next_3_days = positive_surge['next_3_days_change'].mean()
            avg_next_week = positive_surge['next_week_change'].mean()

            if abs(avg_next_day) > min_pattern_strength or abs(avg_next_3_days) > min_pattern_strength:
                patterns.append({
                    "pattern_type": "positive_sentiment_surge",
                    "description": "급격한 긍정적 감성 증가",
                    "occurrences": len(positive_surge),
                    "avg_price_change": {
                        "next_day": float(avg_next_day),
                        "next_3_days": float(avg_next_3_days),
                        "next_week": float(avg_next_week)
                    },
                    "strength": float(abs(avg_next_3_days) / sentiment_std)
                })

        # 급격한 부정 변화
        negative_surge = merged_df[merged_df['sentiment_change'] < -threshold].copy()
        if len(negative_surge) >= 3:
            avg_next_day = negative_surge['next_day_change'].mean()
            avg_next_3_days = negative_surge['next_3_days_change'].mean()
            avg_next_week = negative_surge['next_week_change'].mean()

            if abs(avg_next_day) > min_pattern_strength or abs(avg_next_3_days) > min_pattern_strength:
                patterns.append({
                    "pattern_type": "negative_sentiment_surge",
                    "description": "급격한 부정적 감성 증가",
                    "occurrences": len(negative_surge),
                    "avg_price_change": {
                        "next_day": float(avg_next_day),
                        "next_3_days": float(avg_next_3_days),
                        "next_week": float(avg_next_week)
                    },
                    "strength": float(abs(avg_next_3_days) / sentiment_std)
                })

        # 2. 감성 이동평균 교차 패턴
        merged_df['ma_cross'] = np.where(
            (merged_df['sentiment_ma5'].shift(1) < merged_df['sentiment_ma10'].shift(1)) &
            (merged_df['sentiment_ma5'] > merged_df['sentiment_ma10']),
            1,  # 골든 크로스
            np.where(
                (merged_df['sentiment_ma5'].shift(1) > merged_df['sentiment_ma10'].shift(1)) &
                (merged_df['sentiment_ma5'] < merged_df['sentiment_ma10']),
                -1,  # 데드 크로스
                0
            )
        )

        # 골든 크로스
        golden_cross = merged_df[merged_df['ma_cross'] == 1].copy()
        if len(golden_cross) >= 3:
            avg_next_day = golden_cross['next_day_change'].mean()
            avg_next_3_days = golden_cross['next_3_days_change'].mean()
            avg_next_week = golden_cross['next_week_change'].mean()

            if abs(avg_next_day) > min_pattern_strength or abs(avg_next_3_days) > min_pattern_strength:
                patterns.append({
                    "pattern_type": "sentiment_golden_cross",
                    "description": "감성 이동평균 골든 크로스 (단기>장기)",
                    "occurrences": len(golden_cross),
                    "avg_price_change": {
                        "next_day": float(avg_next_day),
                        "next_3_days": float(avg_next_3_days),
                        "next_week": float(avg_next_week)
                    },
                    "strength": float(abs(avg_next_3_days) / sentiment_std)
                })

        # 데드 크로스
        dead_cross = merged_df[merged_df['ma_cross'] == -1].copy()
        if len(dead_cross) >= 3:
            avg_next_day = dead_cross['next_day_change'].mean()
            avg_next_3_days = dead_cross['next_3_days_change'].mean()
            avg_next_week = dead_cross['next_week_change'].mean()

            if abs(avg_next_day) > min_pattern_strength or abs(avg_next_3_days) > min_pattern_strength:
                patterns.append({
                    "pattern_type": "sentiment_dead_cross",
                    "description": "감성 이동평균 데드 크로스 (단기<장기)",
                    "occurrences": len(dead_cross),
                    "avg_price_change": {
                        "next_day": float(avg_next_day),
                        "next_3_days": float(avg_next_3_days),
                        "next_week": float(avg_next_week)
                    },
                    "strength": float(abs(avg_next_3_days) / sentiment_std)
                })

        # 3. 극단적 감성 패턴
        extreme_positive = merged_df[merged_df['sentiment_score'] > 0.5].copy()
        if len(extreme_positive) >= 3:
            avg_next_day = extreme_positive['next_day_change'].mean()
            avg_next_3_days = extreme_positive['next_3_days_change'].mean()
            avg_next_week = extreme_positive['next_week_change'].mean()

            if abs(avg_next_day) > min_pattern_strength or abs(avg_next_3_days) > min_pattern_strength:
                patterns.append({
                    "pattern_type": "extreme_positive_sentiment",
                    "description": "매우 긍정적인 감성",
                    "occurrences": len(extreme_positive),
                    "avg_price_change": {
                        "next_day": float(avg_next_day),
                        "next_3_days": float(avg_next_3_days),
                        "next_week": float(avg_next_week)
                    },
                    "strength": float(abs(avg_next_3_days) / sentiment_std)
                })

        extreme_negative = merged_df[merged_df['sentiment_score'] < -0.5].copy()
        if len(extreme_negative) >= 3:
            avg_next_day = extreme_negative['next_day_change'].mean()
            avg_next_3_days = extreme_negative['next_3_days_change'].mean()
            avg_next_week = extreme_negative['next_week_change'].mean()

            if abs(avg_next_day) > min_pattern_strength or abs(avg_next_3_days) > min_pattern_strength:
                patterns.append({
                    "pattern_type": "extreme_negative_sentiment",
                    "description": "매우 부정적인 감성",
                    "occurrences": len(extreme_negative),
                    "avg_price_change": {
                        "next_day": float(avg_next_day),
                        "next_3_days": float(avg_next_3_days),
                        "next_week": float(avg_next_week)
                    },
                    "strength": float(abs(avg_next_3_days) / sentiment_std)
                })

        # 패턴 강도순 정렬
        patterns.sort(key=lambda x: x.get('strength', 0), reverse=True)

        return {
            "symbol": symbol,
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "patterns": patterns,
            "pattern_count": len(patterns)
        }

    def generate_insight_report(self, symbol: str, period_days: int = 90) -> Dict[str, Any]:
        """
        분석 인사이트 보고서 생성

        Args:
            symbol: 주식 심볼 (예: AAPL)
            period_days: 분석 기간 (일)

        Returns:
            Dict[str, Any]: 인사이트 보고서
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        # 상관관계 분석
        correlation = self.analyze_correlation(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )

        # 패턴 식별
        patterns = self.identify_sentiment_patterns(
            symbol=symbol,
            lookback_days=period_days
        )

        # 뉴스 볼륨 분석
        news_volume = self.gdelt_client.get_news_volume_by_symbol(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )

        # 관련 엔티티 분석
        entities = self.gdelt_client.get_related_entities(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )

        # 인사이트 생성
        insights = []

        # 상관관계 인사이트
        corr_data = correlation.get('correlation', {})
        if corr_data:
            max_corr = max(corr_data.items(), key=lambda x: abs(x[1]))
            max_corr_period, max_corr_value = max_corr

            if abs(max_corr_value) > 0.3:
                direction = "양의" if max_corr_value > 0 else "음의"
                period_map = {
                    "same_day": "당일",
                    "next_day": "다음 날",
                    "next_3_days": "3일 후",
                    "next_week": "1주일 후"
                }
                period_str = period_map.get(max_corr_period, max_corr_period)

                insights.append({
                    "type": "correlation",
                    "title": f"뉴스 감성과 {period_str} 주가 변동 사이에 {direction} 상관관계 발견",
                    "description": f"뉴스 감성과 {period_str} 주가 변동 사이에 {abs(max_corr_value):.2f}의 {direction} 상관관계가 있습니다.",
                    "strength": abs(max_corr_value)
                })

        # 패턴 인사이트
        for pattern in patterns.get('patterns', [])[:3]:  # 상위 3개 패턴만
            insights.append({
                "type": "pattern",
                "title": pattern.get('description'),
                "description": f"{pattern.get('occurrences')}회 발생했으며, 이후 3일간 평균 {pattern.get('avg_price_change', {}).get('next_3_days', 0):.2f}% 변동이 있었습니다.",
                "strength": pattern.get('strength', 0)
            })

        # 뉴스 볼륨 인사이트
        volumes = news_volume.get('volumes', [])
        if volumes:
            # 뉴스 볼륨 데이터프레임 생성
            volume_df = pd.DataFrame(volumes)
            if not volume_df.empty:
                volume_df['count'] = pd.to_numeric(volume_df['count'])

                # 평균 및 최대 볼륨
                avg_volume = volume_df['count'].mean()
                max_volume = volume_df['count'].max()
                max_date = volume_df.loc[volume_df['count'].idxmax(), 'interval']

                # 최근 볼륨 추세 (마지막 7일)
                recent_trend = 0
                if len(volume_df) > 7:
                    recent_df = volume_df.tail(7)
                    x = np.arange(len(recent_df))
                    y = recent_df['count'].values
                    slope, _, _, _, _ = stats.linregress(x, y)
                    recent_trend = slope

                if max_volume > avg_volume * 2:
                    insights.append({
                        "type": "volume",
                        "title": f"{max_date}에 비정상적으로 높은 뉴스 볼륨 발견",
                        "description": f"평균 대비 {max_volume/avg_volume:.1f}배 높은 뉴스 볼륨이 발생했습니다. 중요한 이벤트가 있었을 가능성이 높습니다.",
                        "strength": max_volume/avg_volume
                    })

                if abs(recent_trend) > avg_volume * 0.1:
                    direction = "증가" if recent_trend > 0 else "감소"
                    insights.append({
                        "type": "volume_trend",
                        "title": f"최근 뉴스 볼륨 {direction} 추세",
                        "description": f"최근 7일간 뉴스 볼륨이 지속적으로 {direction}하고 있습니다.",
                        "strength": abs(recent_trend) / avg_volume
                    })

        # 관련 엔티티 인사이트
        top_persons = entities.get('persons', [])[:3]
        top_orgs = entities.get('organizations', [])[:3]

        if top_persons or top_orgs:
            entity_desc = ""
            if top_persons:
                persons_str = ", ".join([f"{p['name']} ({p['count']}회)" for p in top_persons])
                entity_desc += f"주요 인물: {persons_str}. "
            if top_orgs:
                orgs_str = ", ".join([f"{o['name']} ({o['count']}회)" for o in top_orgs])
                entity_desc += f"주요 조직: {orgs_str}."

            insights.append({
                "type": "entities",
                "title": f"{symbol} 관련 주요 인물 및 조직",
                "description": entity_desc,
                "strength": 0.5  # 고정 강도
            })

        # 인사이트 강도순 정렬
        insights.sort(key=lambda x: x.get('strength', 0), reverse=True)

        return {
            "symbol": symbol,
            "company_name": self.gdelt_client.company_names.get(symbol, symbol),
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "insights": insights,
            "correlation": correlation.get('correlation', {}),
            "patterns": patterns.get('patterns', []),
            "total_news": news_volume.get('total_articles', 0),
            "top_entities": {
                "persons": top_persons,
                "organizations": top_orgs
            }
        }

    def close(self):
        """연결 종료"""
        if self.client:
            self.client.close()
            logger.info("MongoDB 연결이 종료되었습니다.")

        if hasattr(self.stock_store, 'close'):
            self.stock_store.close()

# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    analyzer = SentimentStockAnalyzer()

    # 애플 상관관계 분석
    print("애플 감성-주가 상관관계 분석 시작...")
    correlation = analyzer.analyze_correlation("AAPL", period_days=90)
    print(f"상관관계 분석 결과:")
    print(f"다음날 상관계수: {correlation['correlation']['next_day']:.4f}")
    print(f"다음주 상관계수: {correlation['correlation']['next_week']:.4f}")

    # 패턴 식별
    print("\n패턴 식별 시작...")
    patterns = analyzer.identify_sentiment_patterns("AAPL")
    print(f"식별된 패턴: {patterns['pattern_count']}개")
    for pattern in patterns['patterns']:
        print(f"- {pattern['description']}: 강도 {pattern['strength']:.2f}")

    # 인사이트 보고서
    print("\n인사이트 보고서 생성...")
    insights = analyzer.generate_insight_report("AAPL")
    print(f"생성된 인사이트: {len(insights['insights'])}개")
    for insight in insights['insights']:
        print(f"- {insight['title']}")
        print(f"  {insight['description']}")

    # 연결 종료
    analyzer.close()
