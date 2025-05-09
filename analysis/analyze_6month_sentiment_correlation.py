#!/usr/bin/env python3
"""
6개월 기간의 뉴스 감성과 주가 상관관계 분석 스크립트

이 스크립트는 GDELT 뉴스 감성과 주가 변동 간의 상관관계를 6개월 기간으로 분석합니다.
감성은 긍정적, 부정적, 중립적 세 가지로 단순화하여 분석합니다.
"""
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# 모의 GDELT 클라이언트 사용
from crawling.mock_gdelt_client import MockGDELTClient as GDELTClient
from data.stock_data_store import StockDataStore

class SentimentCorrelationAnalyzer:
    """
    감성-주가 상관관계 분석기
    """
    
    def __init__(self):
        """
        SentimentCorrelationAnalyzer 초기화
        """
        self.gdelt_client = GDELTClient()
        self.stock_store = StockDataStore()
        
        # 결과 저장 디렉토리
        self.results_dir = os.path.join(os.getcwd(), "results")
        os.makedirs(self.results_dir, exist_ok=True)
    
    def analyze_correlation(self, symbol: str, days: int = 180) -> Dict[str, Any]:
        """
        감성-주가 상관관계 분석
        
        Args:
            symbol: 주식 심볼 (예: AAPL)
            days: 분석 기간 (일)
            
        Returns:
            Dict[str, Any]: 분석 결과
        """
        logger.info(f"{symbol} 감성-주가 상관관계 분석 시작 (기간: {days}일)")
        
        # 날짜 범위 계산
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 주가 데이터 가져오기
        stock_data = self.stock_store.get_stock_price(symbol, days=days)
        
        if not stock_data:
            logger.error(f"{symbol} 주가 데이터를 가져오지 못했습니다.")
            return {}
        
        # 뉴스 데이터 가져오기
        news_data = self.gdelt_client.get_historical_news_by_symbol(symbol, max_records=250)
        
        if not news_data:
            logger.error(f"{symbol} 뉴스 데이터를 가져오지 못했습니다.")
            return {}
        
        # 감성 분석 결과 단순화 (긍정, 부정, 중립)
        simplified_news = self._simplify_sentiment(news_data)
        
        # 날짜별 감성 분포 계산
        sentiment_distribution = self._calculate_sentiment_distribution(simplified_news)
        
        # 주가 데이터 변환
        stock_df = self._prepare_stock_data(stock_data)
        
        # 감성 분포와 주가 변동 결합
        combined_data = self._combine_sentiment_stock_data(sentiment_distribution, stock_df)
        
        # 감성 분포 패턴별 주가 변동 분석
        pattern_analysis = self._analyze_sentiment_patterns(combined_data)
        
        # 상관관계 분석
        correlation = self._calculate_correlation(combined_data)
        
        # 결과 저장
        result = {
            "symbol": symbol,
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "days": days,
            "news_count": len(news_data),
            "stock_data_count": len(stock_data),
            "combined_data_count": len(combined_data),
            "correlation": correlation,
            "pattern_analysis": pattern_analysis
        }
        
        # 차트 생성
        self._generate_charts(symbol, result, combined_data)
        
        return result
    
    def _simplify_sentiment(self, news_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        감성 분석 결과를 긍정, 부정, 중립으로 단순화
        
        Args:
            news_data: 뉴스 데이터
            
        Returns:
            List[Dict[str, Any]]: 단순화된 감성 분석 결과
        """
        simplified_news = []
        
        for news in news_data:
            # 원본 감성 점수
            sentiment_score = 0.0
            if "sentiment" in news and isinstance(news["sentiment"], dict):
                sentiment_score = news["sentiment"].get("score", 0.0)
            elif "tone" in news:
                sentiment_score = float(news["tone"])
            
            # 감성 단순화
            if sentiment_score > 0.1:
                sentiment_type = "positive"
            elif sentiment_score < -0.1:
                sentiment_type = "negative"
            else:
                sentiment_type = "neutral"
            
            # 날짜 추출
            published_date = None
            if "published_date" in news:
                published_date = news["published_date"]
            elif "published_utc" in news:
                published_date = news["published_utc"]
            elif "seendate" in news:
                # 밀리초 타임스탬프를 날짜로 변환
                published_date = datetime.fromtimestamp(news["seendate"]/1000.0).isoformat()
            
            if published_date:
                # 날짜 형식 통일 (YYYY-MM-DD)
                if "T" in published_date:
                    published_date = published_date.split("T")[0]
                
                simplified_news.append({
                    "title": news.get("title", ""),
                    "date": published_date,
                    "sentiment_score": sentiment_score,
                    "sentiment_type": sentiment_type
                })
        
        return simplified_news
    
    def _calculate_sentiment_distribution(self, news_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        """
        날짜별 감성 분포 계산
        
        Args:
            news_data: 단순화된 뉴스 데이터
            
        Returns:
            Dict[str, Dict[str, int]]: 날짜별 감성 분포
        """
        sentiment_distribution = {}
        
        for news in news_data:
            date = news["date"]
            sentiment_type = news["sentiment_type"]
            
            if date not in sentiment_distribution:
                sentiment_distribution[date] = {
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "total": 0
                }
            
            sentiment_distribution[date][sentiment_type] += 1
            sentiment_distribution[date]["total"] += 1
        
        return sentiment_distribution
    
    def _prepare_stock_data(self, stock_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        주가 데이터 준비
        
        Args:
            stock_data: 주가 데이터
            
        Returns:
            pd.DataFrame: 준비된 주가 데이터
        """
        # 데이터프레임 변환
        stock_df = pd.DataFrame(stock_data)
        
        # 날짜 형식 변환
        stock_df["date"] = pd.to_datetime(stock_df["date"])
        stock_df["date_str"] = stock_df["date"].dt.strftime("%Y-%m-%d")
        
        # 가격 변동 계산
        stock_df["price_change"] = stock_df["close"].pct_change() * 100
        stock_df["price_change_next_day"] = stock_df["price_change"].shift(-1)
        stock_df["price_change_3day"] = stock_df["close"].pct_change(periods=3) * 100
        stock_df["price_change_week"] = stock_df["close"].pct_change(periods=5) * 100
        
        return stock_df
    
    def _combine_sentiment_stock_data(self, 
                                     sentiment_distribution: Dict[str, Dict[str, int]], 
                                     stock_df: pd.DataFrame) -> pd.DataFrame:
        """
        감성 분포와 주가 데이터 결합
        
        Args:
            sentiment_distribution: 날짜별 감성 분포
            stock_df: 주가 데이터
            
        Returns:
            pd.DataFrame: 결합된 데이터
        """
        combined_data = []
        
        for date_str, sentiment_counts in sentiment_distribution.items():
            # 해당 날짜의 주가 데이터 찾기
            stock_row = stock_df[stock_df["date_str"] == date_str]
            
            if not stock_row.empty:
                # 감성 분포 계산
                total = sentiment_counts["total"]
                if total > 0:
                    positive_ratio = sentiment_counts["positive"] / total
                    negative_ratio = sentiment_counts["negative"] / total
                    neutral_ratio = sentiment_counts["neutral"] / total
                    
                    # 주요 감성 결정
                    if positive_ratio >= negative_ratio and positive_ratio >= neutral_ratio:
                        primary_sentiment = "positive"
                    elif negative_ratio >= positive_ratio and negative_ratio >= neutral_ratio:
                        primary_sentiment = "negative"
                    else:
                        primary_sentiment = "neutral"
                    
                    # 두 번째 감성 결정
                    if primary_sentiment != "positive" and positive_ratio >= negative_ratio and positive_ratio >= neutral_ratio:
                        secondary_sentiment = "positive"
                    elif primary_sentiment != "negative" and negative_ratio >= positive_ratio and negative_ratio >= neutral_ratio:
                        secondary_sentiment = "negative"
                    else:
                        secondary_sentiment = "neutral"
                    
                    # 감성 패턴 (예: positive-neutral)
                    sentiment_pattern = f"{primary_sentiment}-{secondary_sentiment}"
                    
                    # 결합 데이터 추가
                    combined_data.append({
                        "date": date_str,
                        "positive_count": sentiment_counts["positive"],
                        "negative_count": sentiment_counts["negative"],
                        "neutral_count": sentiment_counts["neutral"],
                        "total_count": total,
                        "positive_ratio": positive_ratio,
                        "negative_ratio": negative_ratio,
                        "neutral_ratio": neutral_ratio,
                        "primary_sentiment": primary_sentiment,
                        "secondary_sentiment": secondary_sentiment,
                        "sentiment_pattern": sentiment_pattern,
                        "price": float(stock_row["close"].values[0]),
                        "price_change": float(stock_row["price_change"].values[0]) if not pd.isna(stock_row["price_change"].values[0]) else 0.0,
                        "price_change_next_day": float(stock_row["price_change_next_day"].values[0]) if not pd.isna(stock_row["price_change_next_day"].values[0]) else 0.0,
                        "price_change_3day": float(stock_row["price_change_3day"].values[0]) if not pd.isna(stock_row["price_change_3day"].values[0]) else 0.0,
                        "price_change_week": float(stock_row["price_change_week"].values[0]) if not pd.isna(stock_row["price_change_week"].values[0]) else 0.0
                    })
        
        return pd.DataFrame(combined_data)
    
    def _analyze_sentiment_patterns(self, combined_data: pd.DataFrame) -> Dict[str, Any]:
        """
        감성 분포 패턴별 주가 변동 분석
        
        Args:
            combined_data: 결합된 데이터
            
        Returns:
            Dict[str, Any]: 패턴별 분석 결과
        """
        pattern_analysis = {}
        
        # 감성 패턴별 그룹화
        pattern_groups = combined_data.groupby("sentiment_pattern")
        
        for pattern, group in pattern_groups:
            pattern_analysis[pattern] = {
                "count": len(group),
                "avg_price_change": group["price_change"].mean(),
                "avg_price_change_next_day": group["price_change_next_day"].mean(),
                "avg_price_change_3day": group["price_change_3day"].mean(),
                "avg_price_change_week": group["price_change_week"].mean()
            }
        
        # 주요 감성별 그룹화
        primary_groups = combined_data.groupby("primary_sentiment")
        
        primary_analysis = {}
        for sentiment, group in primary_groups:
            primary_analysis[sentiment] = {
                "count": len(group),
                "avg_price_change": group["price_change"].mean(),
                "avg_price_change_next_day": group["price_change_next_day"].mean(),
                "avg_price_change_3day": group["price_change_3day"].mean(),
                "avg_price_change_week": group["price_change_week"].mean()
            }
        
        return {
            "patterns": pattern_analysis,
            "primary_sentiment": primary_analysis
        }
    
    def _calculate_correlation(self, combined_data: pd.DataFrame) -> Dict[str, float]:
        """
        감성 비율과 주가 변동 간의 상관관계 계산
        
        Args:
            combined_data: 결합된 데이터
            
        Returns:
            Dict[str, float]: 상관관계 계수
        """
        correlation = {}
        
        # 긍정 감성 비율과 주가 변동 상관관계
        correlation["positive_ratio_same_day"] = combined_data["positive_ratio"].corr(combined_data["price_change"])
        correlation["positive_ratio_next_day"] = combined_data["positive_ratio"].corr(combined_data["price_change_next_day"])
        correlation["positive_ratio_3day"] = combined_data["positive_ratio"].corr(combined_data["price_change_3day"])
        correlation["positive_ratio_week"] = combined_data["positive_ratio"].corr(combined_data["price_change_week"])
        
        # 부정 감성 비율과 주가 변동 상관관계
        correlation["negative_ratio_same_day"] = combined_data["negative_ratio"].corr(combined_data["price_change"])
        correlation["negative_ratio_next_day"] = combined_data["negative_ratio"].corr(combined_data["price_change_next_day"])
        correlation["negative_ratio_3day"] = combined_data["negative_ratio"].corr(combined_data["price_change_3day"])
        correlation["negative_ratio_week"] = combined_data["negative_ratio"].corr(combined_data["price_change_week"])
        
        return correlation
    
    def _generate_charts(self, symbol: str, result: Dict[str, Any], combined_data: pd.DataFrame) -> None:
        """
        분석 결과 차트 생성
        
        Args:
            symbol: 주식 심볼
            result: 분석 결과
            combined_data: 결합된 데이터
        """
        # 감성 패턴별 주가 변동 차트
        self._generate_pattern_chart(symbol, result["pattern_analysis"]["patterns"])
        
        # 주요 감성별 주가 변동 차트
        self._generate_primary_sentiment_chart(symbol, result["pattern_analysis"]["primary_sentiment"])
        
        # 감성 비율과 주가 변동 시계열 차트
        self._generate_time_series_chart(symbol, combined_data)
    
    def _generate_pattern_chart(self, symbol: str, pattern_analysis: Dict[str, Dict[str, float]]) -> None:
        """
        감성 패턴별 주가 변동 차트 생성
        
        Args:
            symbol: 주식 심볼
            pattern_analysis: 패턴별 분석 결과
        """
        # 데이터 준비
        patterns = []
        counts = []
        same_day = []
        next_day = []
        three_day = []
        week = []
        
        for pattern, data in pattern_analysis.items():
            if data["count"] >= 3:  # 최소 3개 이상의 데이터가 있는 패턴만 포함
                patterns.append(pattern)
                counts.append(data["count"])
                same_day.append(data["avg_price_change"])
                next_day.append(data["avg_price_change_next_day"])
                three_day.append(data["avg_price_change_3day"])
                week.append(data["avg_price_change_week"])
        
        if not patterns:
            return
        
        # 차트 생성
        plt.figure(figsize=(12, 8))
        
        x = np.arange(len(patterns))
        width = 0.2
        
        plt.bar(x - width*1.5, same_day, width, label='Same Day')
        plt.bar(x - width*0.5, next_day, width, label='Next Day')
        plt.bar(x + width*0.5, three_day, width, label='3 Days')
        plt.bar(x + width*1.5, week, width, label='1 Week')
        
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.xlabel('Sentiment Pattern (Primary-Secondary)')
        plt.ylabel('Average Price Change (%)')
        plt.title(f'{symbol} Price Change by Sentiment Pattern (6 Months)')
        plt.xticks(x, patterns, rotation=45, ha='right')
        
        # 데이터 포인트 수 표시
        for i, count in enumerate(counts):
            plt.annotate(f'n={count}', xy=(i, max(same_day[i], next_day[i], three_day[i], week[i]) + 0.5), 
                        ha='center', va='bottom', fontsize=8)
        
        plt.legend()
        plt.tight_layout()
        
        # 저장
        file_path = os.path.join(self.results_dir, f"{symbol}_sentiment_pattern_6month.png")
        plt.savefig(file_path, dpi=300)
        plt.close()
        
        logger.info(f"감성 패턴별 주가 변동 차트가 저장되었습니다: {file_path}")
    
    def _generate_primary_sentiment_chart(self, symbol: str, primary_analysis: Dict[str, Dict[str, float]]) -> None:
        """
        주요 감성별 주가 변동 차트 생성
        
        Args:
            symbol: 주식 심볼
            primary_analysis: 주요 감성별 분석 결과
        """
        # 데이터 준비
        sentiments = []
        counts = []
        same_day = []
        next_day = []
        three_day = []
        week = []
        
        for sentiment, data in primary_analysis.items():
            sentiments.append(sentiment)
            counts.append(data["count"])
            same_day.append(data["avg_price_change"])
            next_day.append(data["avg_price_change_next_day"])
            three_day.append(data["avg_price_change_3day"])
            week.append(data["avg_price_change_week"])
        
        # 차트 생성
        plt.figure(figsize=(10, 6))
        
        x = np.arange(len(sentiments))
        width = 0.2
        
        plt.bar(x - width*1.5, same_day, width, label='Same Day')
        plt.bar(x - width*0.5, next_day, width, label='Next Day')
        plt.bar(x + width*0.5, three_day, width, label='3 Days')
        plt.bar(x + width*1.5, week, width, label='1 Week')
        
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.xlabel('Primary Sentiment')
        plt.ylabel('Average Price Change (%)')
        plt.title(f'{symbol} Price Change by Primary Sentiment (6 Months)')
        plt.xticks(x, sentiments)
        
        # 데이터 포인트 수 표시
        for i, count in enumerate(counts):
            plt.annotate(f'n={count}', xy=(i, max(same_day[i], next_day[i], three_day[i], week[i]) + 0.5), 
                        ha='center', va='bottom')
        
        plt.legend()
        plt.tight_layout()
        
        # 저장
        file_path = os.path.join(self.results_dir, f"{symbol}_primary_sentiment_6month.png")
        plt.savefig(file_path, dpi=300)
        plt.close()
        
        logger.info(f"주요 감성별 주가 변동 차트가 저장되었습니다: {file_path}")
    
    def _generate_time_series_chart(self, symbol: str, combined_data: pd.DataFrame) -> None:
        """
        감성 비율과 주가 변동 시계열 차트 생성
        
        Args:
            symbol: 주식 심볼
            combined_data: 결합된 데이터
        """
        if combined_data.empty:
            return
        
        # 날짜순 정렬
        combined_data["date"] = pd.to_datetime(combined_data["date"])
        combined_data = combined_data.sort_values("date")
        
        # 차트 생성
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        # 주가 변동 차트
        ax1.plot(combined_data["date"], combined_data["price"], 'b-', label='Price')
        ax1.set_ylabel('Price ($)')
        ax1.set_title(f'{symbol} Price and Sentiment (6 Months)')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 감성 비율 차트
        ax2.bar(combined_data["date"], combined_data["positive_ratio"], color='green', alpha=0.7, label='Positive')
        ax2.bar(combined_data["date"], combined_data["negative_ratio"], bottom=combined_data["positive_ratio"], 
               color='red', alpha=0.7, label='Negative')
        ax2.bar(combined_data["date"], combined_data["neutral_ratio"], 
               bottom=combined_data["positive_ratio"] + combined_data["negative_ratio"], 
               color='gray', alpha=0.7, label='Neutral')
        
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Sentiment Ratio')
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 저장
        file_path = os.path.join(self.results_dir, f"{symbol}_time_series_6month.png")
        plt.savefig(file_path, dpi=300)
        plt.close()
        
        logger.info(f"시계열 차트가 저장되었습니다: {file_path}")

def main():
    """
    메인 함수
    """
    # 분석할 심볼 목록
    symbols = ["AAPL", "MSFT", "GOOGL"]
    
    # 분석기 초기화
    analyzer = SentimentCorrelationAnalyzer()
    
    # 각 심볼 분석
    for symbol in symbols:
        print(f"\n{'='*50}\n  {symbol} 6개월 감성-주가 상관관계 분석\n{'='*50}")
        
        # 6개월(180일) 기간 분석
        result = analyzer.analyze_correlation(symbol, days=180)
        
        if not result:
            print(f"{symbol} 분석 실패")
            continue
        
        # 결과 출력
        print(f"기간: {result['period']}")
        print(f"뉴스 데이터: {result['news_count']}개")
        print(f"주가 데이터: {result['stock_data_count']}개")
        print(f"결합 데이터: {result['combined_data_count']}개")
        
        # 상관관계 출력
        print("\n감성 비율과 주가 변동 상관관계:")
        for key, value in result["correlation"].items():
            print(f"  {key}: {value:.4f}")
        
        # 주요 감성별 주가 변동 출력
        print("\n주요 감성별 주가 변동:")
        for sentiment, data in result["pattern_analysis"]["primary_sentiment"].items():
            print(f"\n  {sentiment.upper()} (데이터 수: {data['count']}개)")
            print(f"    당일: {data['avg_price_change']:.4f}%")
            print(f"    다음날: {data['avg_price_change_next_day']:.4f}%")
            print(f"    3일 후: {data['avg_price_change_3day']:.4f}%")
            print(f"    1주일 후: {data['avg_price_change_week']:.4f}%")
        
        # 감성 패턴별 주가 변동 출력
        print("\n감성 패턴별 주가 변동 (상위 3개):")
        pattern_data = [(pattern, data["count"], data["avg_price_change_next_day"]) 
                       for pattern, data in result["pattern_analysis"]["patterns"].items()]
        pattern_data.sort(key=lambda x: x[1], reverse=True)  # 데이터 수 기준 정렬
        
        for i, (pattern, count, change) in enumerate(pattern_data[:3]):
            data = result["pattern_analysis"]["patterns"][pattern]
            print(f"\n  {i+1}. {pattern} (데이터 수: {count}개)")
            print(f"    당일: {data['avg_price_change']:.4f}%")
            print(f"    다음날: {data['avg_price_change_next_day']:.4f}%")
            print(f"    3일 후: {data['avg_price_change_3day']:.4f}%")
            print(f"    1주일 후: {data['avg_price_change_week']:.4f}%")
        
        print(f"\n분석 결과 차트가 {analyzer.results_dir} 디렉토리에 저장되었습니다.")

if __name__ == "__main__":
    main()
