#!/usr/bin/env python3
"""
감성-가격 분석기

이 모듈은 뉴스 감성과 주가 데이터를 결합하여 분석합니다.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

import pandas as pd
import numpy as np
from dotenv import load_dotenv

from data.stock_data_store import StockDataStore
from analysis.finbert_sentiment import FinBERTSentiment

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
env_path = Path(__file__).parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

class SentimentPriceAnalyzer:
    """
    감성-가격 분석기

    이 클래스는 뉴스 감성과 주가 데이터를 결합하여 분석합니다.
    """

    def __init__(self):
        """
        감성-가격 분석기 초기화
        """
        # 주식 데이터 저장소 초기화
        self.stock_data_store = StockDataStore()

        # FinBERT 감성 분석기 초기화
        self.sentiment_analyzer = FinBERTSentiment()

        logger.info("감성-가격 분석기 초기화 완료")

    def analyze_sentiment_price_correlation(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """
        감성과 가격 간의 상관관계 분석

        Args:
            symbol: 주식 심볼 (예: AAPL, MSFT)
            days: 분석할 일수 (기본값: 30)

        Returns:
            Dict[str, Any]: 분석 결과
        """
        # 날짜 범위 계산
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        # 주가 데이터 가져오기
        price_data = self.stock_data_store.get_daily_bars(symbol, start_date, end_date)

        # 뉴스 데이터 가져오기
        news_data = self.stock_data_store.get_stock_news(symbol, limit=100)

        # 뉴스 데이터가 없는 경우
        if not news_data:
            logger.warning(f"{symbol}에 대한 뉴스 데이터가 없습니다.")
            return {
                "symbol": symbol,
                "period": f"{start_date} ~ {end_date}",
                "correlation": None,
                "sentiment_trend": None,
                "price_trend": None,
                "analysis": f"{symbol}에 대한 뉴스 데이터가 없어 분석할 수 없습니다."
            }

        # 주가 데이터가 없는 경우
        if price_data.empty:
            logger.warning(f"{symbol}에 대한 주가 데이터가 없습니다.")
            return {
                "symbol": symbol,
                "period": f"{start_date} ~ {end_date}",
                "correlation": None,
                "sentiment_trend": None,
                "price_trend": None,
                "analysis": f"{symbol}에 대한 주가 데이터가 없어 분석할 수 없습니다."
            }

        # 뉴스 감성 분석
        news_with_sentiment = []
        for news in news_data:
            # 뉴스 날짜 파싱
            try:
                if isinstance(news.get("published_utc"), str):
                    news_date = datetime.fromisoformat(news.get("published_utc").replace("Z", "+00:00"))
                else:
                    news_date = datetime.now() - timedelta(days=np.random.randint(1, days))

                # 분석 기간 내의 뉴스만 포함
                if news_date.strftime('%Y-%m-%d') >= start_date and news_date.strftime('%Y-%m-%d') <= end_date:
                    # 뉴스 감성 분석
                    news_with_sentiment.append(self.sentiment_analyzer.analyze_news({
                        "title": news.get("title", ""),
                        "content": news.get("description", ""),
                        "url": news.get("article_url", ""),
                        "published_date": news_date.strftime('%Y-%m-%d')
                    }))
            except Exception as e:
                logger.error(f"뉴스 날짜 파싱 중 오류 발생: {str(e)}")
                continue

        # 날짜별 감성 점수 계산
        sentiment_by_date = {}
        for news in news_with_sentiment:
            date = news.get("published_date")
            sentiment = news.get("sentiment", {})

            if date not in sentiment_by_date:
                sentiment_by_date[date] = []

            # 감성 점수 변환 (negative: -1, neutral: 0, positive: 1)
            sentiment_score = 0
            if sentiment.get("label") == "positive":
                sentiment_score = sentiment.get("score", 0)
            elif sentiment.get("label") == "negative":
                sentiment_score = -sentiment.get("score", 0)

            sentiment_by_date[date].append(sentiment_score)

        # 날짜별 평균 감성 점수 계산
        sentiment_df = pd.DataFrame(columns=["date", "sentiment_score"])
        for date, scores in sentiment_by_date.items():
            sentiment_df = pd.concat([sentiment_df, pd.DataFrame({
                "date": [date],
                "sentiment_score": [sum(scores) / len(scores)]
            })], ignore_index=True)

        sentiment_df["date"] = pd.to_datetime(sentiment_df["date"])
        sentiment_df.set_index("date", inplace=True)

        # 주가 데이터와 감성 데이터 결합
        combined_df = price_data.copy()
        combined_df["sentiment_score"] = np.nan

        for date, row in sentiment_df.iterrows():
            if date in combined_df.index:
                combined_df.at[date, "sentiment_score"] = row["sentiment_score"]

        # 결측값 처리 (이전 값으로 채우기)
        combined_df["sentiment_score"].fillna(method="ffill", inplace=True)

        # 결측값이 있는 행 제거
        combined_df.dropna(subset=["sentiment_score"], inplace=True)

        # 상관관계 계산
        correlation = combined_df["close"].pct_change().corr(combined_df["sentiment_score"])

        # 감성 추세 계산
        sentiment_trend = "neutral"
        if not combined_df.empty:
            avg_sentiment = combined_df["sentiment_score"].mean()
            if avg_sentiment > 0.1:
                sentiment_trend = "positive"
            elif avg_sentiment < -0.1:
                sentiment_trend = "negative"

        # 가격 추세 계산
        price_trend = "neutral"
        if not combined_df.empty:
            first_price = combined_df["close"].iloc[0]
            last_price = combined_df["close"].iloc[-1]
            price_change_pct = (last_price - first_price) / first_price * 100

            if price_change_pct > 2:
                price_trend = "positive"
            elif price_change_pct < -2:
                price_trend = "negative"

        # 분석 결과 생성
        analysis = f"{symbol}의 뉴스 감성과 주가 간의 상관관계는 {correlation:.4f}입니다. "

        if correlation > 0.3:
            analysis += "뉴스 감성과 주가 사이에 강한 양의 상관관계가 있습니다. 긍정적인 뉴스가 주가 상승과 연관되어 있습니다."
        elif correlation < -0.3:
            analysis += "뉴스 감성과 주가 사이에 강한 음의 상관관계가 있습니다. 긍정적인 뉴스가 주가 하락과 연관되어 있습니다."
        else:
            analysis += "뉴스 감성과 주가 사이에 뚜렷한 상관관계가 없습니다."

        analysis += f" 분석 기간 동안의 감성 추세는 {sentiment_trend}이며, 주가 추세는 {price_trend}입니다."

        return {
            "symbol": symbol,
            "period": f"{start_date} ~ {end_date}",
            "correlation": correlation,
            "sentiment_trend": sentiment_trend,
            "price_trend": price_trend,
            "analysis": analysis,
            "data": combined_df.reset_index().to_dict(orient="records")
        }

    def get_sentiment_summary(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """
        최근 뉴스의 감성 요약

        Args:
            symbol: 주식 심볼 (예: AAPL, MSFT)
            days: 분석할 일수 (기본값: 7)

        Returns:
            Dict[str, Any]: 감성 요약
        """
        # 뉴스 데이터 가져오기
        news_data = self.stock_data_store.get_stock_news(symbol, limit=20)

        # 뉴스 데이터가 없는 경우
        if not news_data:
            logger.warning(f"{symbol}에 대한 뉴스 데이터가 없습니다.")
            return {
                "symbol": symbol,
                "period": f"최근 {days}일",
                "sentiment": "neutral",
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "total_count": 0,
                "summary": f"{symbol}에 대한 최근 뉴스가 없습니다."
            }

        # 뉴스 감성 분석
        news_with_sentiment = []
        for news in news_data:
            # 뉴스 날짜 파싱
            try:
                if isinstance(news.get("published_utc"), str):
                    news_date = datetime.fromisoformat(news.get("published_utc").replace("Z", "+00:00"))
                else:
                    news_date = datetime.now() - timedelta(days=np.random.randint(1, days))

                # 최근 n일 내의 뉴스만 포함
                if (datetime.now() - news_date).days <= days:
                    # 뉴스 감성 분석
                    news_with_sentiment.append(self.sentiment_analyzer.analyze_news({
                        "title": news.get("title", ""),
                        "content": news.get("description", ""),
                        "url": news.get("article_url", ""),
                        "published_date": news_date.strftime('%Y-%m-%d')
                    }))
            except Exception as e:
                logger.error(f"뉴스 날짜 파싱 중 오류 발생: {str(e)}")
                continue

        # 감성 카운트
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for news in news_with_sentiment:
            sentiment = news.get("sentiment", {})
            label = sentiment.get("label", "neutral")

            if label == "positive":
                positive_count += 1
            elif label == "negative":
                negative_count += 1
            else:
                neutral_count += 1

        total_count = positive_count + negative_count + neutral_count

        # 전체 감성 결정
        overall_sentiment = "neutral"
        if total_count > 0:
            positive_ratio = positive_count / total_count
            negative_ratio = negative_count / total_count

            if positive_ratio > 0.5 and positive_ratio > negative_ratio:
                overall_sentiment = "positive"
            elif negative_ratio > 0.5 and negative_ratio > positive_ratio:
                overall_sentiment = "negative"

        # 요약 생성
        summary = f"{symbol}에 대한 최근 {days}일간의 뉴스 감성은 "

        if total_count == 0:
            summary = f"{symbol}에 대한 최근 {days}일간의 뉴스가 없습니다."
        elif overall_sentiment == "positive":
            summary += f"긍정적입니다. 전체 {total_count}개의 뉴스 중 {positive_count}개({positive_count/total_count*100:.1f}%)가 긍정적입니다."
        elif overall_sentiment == "negative":
            summary += f"부정적입니다. 전체 {total_count}개의 뉴스 중 {negative_count}개({negative_count/total_count*100:.1f}%)가 부정적입니다."
        else:
            summary += f"중립적입니다. 전체 {total_count}개의 뉴스 중 {neutral_count}개({neutral_count/total_count*100:.1f}%)가 중립적입니다."

        return {
            "symbol": symbol,
            "period": f"최근 {days}일",
            "sentiment": overall_sentiment,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "total_count": total_count,
            "summary": summary,
            "news": news_with_sentiment
        }

    def close(self):
        """
        리소스 정리
        """
        self.stock_data_store.close()
        logger.info("감성-가격 분석기 리소스 정리 완료")


# 테스트 코드
if __name__ == "__main__":
    # 감성-가격 분석기 초기화
    analyzer = SentimentPriceAnalyzer()

    # 테스트할 심볼
    symbols = ["AAPL", "MSFT", "GOOGL"]

    # 감성-가격 상관관계 분석
    print("\n=== 감성-가격 상관관계 분석 ===")
    for symbol in symbols:
        result = analyzer.analyze_sentiment_price_correlation(symbol, days=30)
        print(f"\n{symbol} 분석 결과:")
        print(f"기간: {result['period']}")
        print(f"상관관계: {result['correlation']}")
        print(f"감성 추세: {result['sentiment_trend']}")
        print(f"가격 추세: {result['price_trend']}")
        print(f"분석: {result['analysis']}")

    # 감성 요약
    print("\n=== 감성 요약 ===")
    for symbol in symbols:
        result = analyzer.get_sentiment_summary(symbol, days=7)
        print(f"\n{symbol} 감성 요약:")
        print(f"기간: {result['period']}")
        print(f"감성: {result['sentiment']}")
        print(f"긍정: {result['positive_count']}, 부정: {result['negative_count']}, 중립: {result['neutral_count']}")
        print(f"요약: {result['summary']}")

    # 리소스 정리
    analyzer.close()
