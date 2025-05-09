#!/usr/bin/env python3
"""
뉴스 감성 모멘텀 분석 모듈

이 모듈은 뉴스 기사의 감성 점수를 기반으로 감성 모멘텀을 계산하고 분석합니다.
"""
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SentimentMomentumAnalyzer:
    """
    뉴스 감성 모멘텀 분석기
    """

    def __init__(self, results_dir: str = None):
        """
        SentimentMomentumAnalyzer 초기화

        Args:
            results_dir: 결과 저장 디렉토리
        """
        # 결과 저장 디렉토리
        if results_dir is None:
            self.results_dir = os.path.join(os.getcwd(), "results")
        else:
            self.results_dir = results_dir

        os.makedirs(self.results_dir, exist_ok=True)

        # 감성 모멘텀 계산을 위한 기본 파라미터
        self.short_window = 3  # 단기 이동평균 기간 (일)
        self.long_window = 7   # 장기 이동평균 기간 (일)

    def calculate_daily_sentiment(self, news_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        일별 평균 감성 점수 계산

        Args:
            news_data: 뉴스 데이터 목록

        Returns:
            pd.DataFrame: 일별 감성 데이터
        """
        # 데이터프레임 변환
        news_df = pd.DataFrame(news_data)

        # 날짜 형식 변환
        news_df['date'] = pd.to_datetime(news_df['date'])
        news_df['date_str'] = news_df['date'].dt.strftime('%Y-%m-%d')

        # 일별 그룹화 및 감성 통계 계산
        daily_sentiment = news_df.groupby('date_str').agg({
            'sentiment_score': ['mean', 'std', 'count'],
            'sentiment_type': lambda x: x.value_counts().index[0]  # 가장 많은 감성 유형
        })

        # 컬럼명 재설정
        daily_sentiment.columns = ['avg_sentiment', 'std_sentiment', 'article_count', 'primary_sentiment']
        daily_sentiment = daily_sentiment.reset_index()

        # 날짜순 정렬
        daily_sentiment['date'] = pd.to_datetime(daily_sentiment['date_str'])
        daily_sentiment = daily_sentiment.sort_values('date')

        return daily_sentiment

    def calculate_sentiment_moving_averages(self, daily_sentiment: pd.DataFrame) -> pd.DataFrame:
        """
        감성 이동평균 계산

        Args:
            daily_sentiment: 일별 감성 데이터

        Returns:
            pd.DataFrame: 이동평균이 추가된 감성 데이터
        """
        # 날짜순 정렬 확인
        daily_sentiment = daily_sentiment.sort_values('date')

        # 단기 이동평균 계산
        daily_sentiment[f'sentiment_ma_{self.short_window}d'] = daily_sentiment['avg_sentiment'].rolling(
            window=self.short_window, min_periods=1).mean()

        # 장기 이동평균 계산
        daily_sentiment[f'sentiment_ma_{self.long_window}d'] = daily_sentiment['avg_sentiment'].rolling(
            window=self.long_window, min_periods=1).mean()

        return daily_sentiment

    def calculate_sentiment_momentum(self, daily_sentiment: pd.DataFrame) -> pd.DataFrame:
        """
        감성 모멘텀 계산

        Args:
            daily_sentiment: 이동평균이 포함된 일별 감성 데이터

        Returns:
            pd.DataFrame: 모멘텀이 추가된 감성 데이터
        """
        # 감성 모멘텀 계산 (단기 이동평균 - 장기 이동평균)
        daily_sentiment['sentiment_momentum'] = (
            daily_sentiment[f'sentiment_ma_{self.short_window}d'] -
            daily_sentiment[f'sentiment_ma_{self.long_window}d']
        )

        # 모멘텀 변화 계산
        daily_sentiment['momentum_change'] = daily_sentiment['sentiment_momentum'].diff()

        # 모멘텀 방향 분류
        conditions = [
            (daily_sentiment['sentiment_momentum'] > 0.1),
            (daily_sentiment['sentiment_momentum'] < -0.1),
            (daily_sentiment['sentiment_momentum'].abs() <= 0.1)
        ]
        choices = ['improving', 'deteriorating', 'stable']
        daily_sentiment['momentum_direction'] = np.select(conditions, choices, default='stable')

        # 모멘텀 변곡점 식별
        daily_sentiment['momentum_turning_point'] = (
            (daily_sentiment['sentiment_momentum'].shift(1) < 0) &
            (daily_sentiment['sentiment_momentum'] > 0) |
            (daily_sentiment['sentiment_momentum'].shift(1) > 0) &
            (daily_sentiment['sentiment_momentum'] < 0)
        )

        return daily_sentiment

    def analyze_sentiment_momentum(self, news_data: List[Dict[str, Any]],
                                  stock_data: Optional[List[Dict[str, Any]]] = None,
                                  short_window: int = None,
                                  long_window: int = None) -> Dict[str, Any]:
        """
        감성 모멘텀 분석 수행

        Args:
            news_data: 뉴스 데이터 목록
            stock_data: 주가 데이터 목록 (선택 사항)
            short_window: 단기 이동평균 기간 (일)
            long_window: 장기 이동평균 기간 (일)

        Returns:
            Dict[str, Any]: 분석 결과
        """
        # 파라미터 업데이트
        if short_window is not None:
            self.short_window = short_window
        if long_window is not None:
            self.long_window = long_window

        # 일별 감성 계산
        daily_sentiment = self.calculate_daily_sentiment(news_data)

        # 데이터가 충분한지 확인
        if len(daily_sentiment) < max(self.short_window, self.long_window):
            logger.warning(f"데이터가 충분하지 않습니다. 최소 {max(self.short_window, self.long_window)}일 필요")
            return {
                "success": False,
                "message": f"데이터가 충분하지 않습니다. 최소 {max(self.short_window, self.long_window)}일 필요",
                "data": daily_sentiment.to_dict('records')
            }

        # 이동평균 계산
        daily_sentiment = self.calculate_sentiment_moving_averages(daily_sentiment)

        # 모멘텀 계산
        daily_sentiment = self.calculate_sentiment_momentum(daily_sentiment)

        # 주가 데이터 결합 (있는 경우)
        if stock_data:
            stock_df = pd.DataFrame(stock_data)
            stock_df['date'] = pd.to_datetime(stock_df['date'])
            stock_df['date_str'] = stock_df['date'].dt.strftime('%Y-%m-%d')

            # 주가 변동 계산
            stock_df['price_change'] = stock_df['close'].pct_change() * 100
            stock_df['price_change_next_day'] = stock_df['price_change'].shift(-1)

            # 감성 데이터와 주가 데이터 결합
            combined_df = pd.merge(
                daily_sentiment,
                stock_df[['date_str', 'close', 'price_change', 'price_change_next_day']],
                on='date_str',
                how='left'
            )

            # 모멘텀 방향별 주가 변동 분석
            momentum_impact_df = combined_df.groupby('momentum_direction').agg({
                'price_change': 'mean',
                'price_change_next_day': 'mean',
                'date_str': 'count'
            })

            # DataFrame을 딕셔너리로 변환
            momentum_impact = {}
            for direction in momentum_impact_df.index:
                momentum_impact[direction] = {
                    'price_change': float(momentum_impact_df.loc[direction, 'price_change']),
                    'price_change_next_day': float(momentum_impact_df.loc[direction, 'price_change_next_day']),
                    'count': int(momentum_impact_df.loc[direction, 'date_str'])
                }

            # 변곡점에서의 주가 변동 분석
            turning_points = combined_df[combined_df['momentum_turning_point']]

            if not turning_points.empty:
                turning_point_impact = {
                    'price_change': float(turning_points['price_change'].mean()),
                    'price_change_next_day': float(turning_points['price_change_next_day'].mean()),
                    'count': len(turning_points)
                }
            else:
                turning_point_impact = {}

            # 모멘텀과 주가 변동 간의 상관관계
            correlation = combined_df['sentiment_momentum'].corr(combined_df['price_change_next_day'])

            # 결과 저장
            result = {
                "success": True,
                "daily_sentiment": daily_sentiment.to_dict('records'),
                "momentum_impact": momentum_impact,
                "turning_point_impact": turning_point_impact,
                "correlation": correlation,
                "combined_data": combined_df.to_dict('records')
            }
        else:
            # 주가 데이터 없이 감성 모멘텀만 분석
            result = {
                "success": True,
                "daily_sentiment": daily_sentiment.to_dict('records')
            }

        return result

    def generate_momentum_charts(self, symbol: str, analysis_result: Dict[str, Any]) -> None:
        """
        감성 모멘텀 차트 생성

        Args:
            symbol: 주식 심볼
            analysis_result: 분석 결과
        """
        if not analysis_result.get("success", False):
            logger.warning("분석 결과가 없어 차트를 생성할 수 없습니다.")
            return

        # 데이터프레임 변환
        if "combined_data" in analysis_result:
            df = pd.DataFrame(analysis_result["combined_data"])
        else:
            df = pd.DataFrame(analysis_result["daily_sentiment"])

        # 날짜 형식 변환
        df['date'] = pd.to_datetime(df['date_str'])

        # 1. 감성 모멘텀 차트
        self._generate_momentum_line_chart(symbol, df)

        # 2. 모멘텀 히트맵 차트
        self._generate_momentum_heatmap(symbol, df)

        # 3. 주가 데이터가 있는 경우 모멘텀-주가 비교 차트
        if "close" in df.columns:
            self._generate_momentum_price_chart(symbol, df)

    def _generate_momentum_line_chart(self, symbol: str, df: pd.DataFrame) -> None:
        """
        감성 모멘텀 라인 차트 생성

        Args:
            symbol: 주식 심볼
            df: 분석 데이터
        """
        plt.figure(figsize=(12, 6))

        # 감성 점수 및 이동평균 플롯
        plt.plot(df['date'], df['avg_sentiment'], 'o-', alpha=0.5, label='Daily Sentiment')
        plt.plot(df['date'], df[f'sentiment_ma_{self.short_window}d'], 'g-',
                label=f'{self.short_window}-day MA')
        plt.plot(df['date'], df[f'sentiment_ma_{self.long_window}d'], 'r-',
                label=f'{self.long_window}-day MA')

        # 모멘텀 플롯
        plt.plot(df['date'], df['sentiment_momentum'], 'b-', label='Momentum')

        # 변곡점 표시
        turning_points = df[df['momentum_turning_point']]
        plt.scatter(turning_points['date'], turning_points['sentiment_momentum'],
                   color='purple', s=100, marker='*', label='Turning Points')

        # 0선 표시
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)

        # 차트 설정
        plt.title(f'{symbol} Sentiment Momentum Analysis', fontsize=14)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Sentiment Score / Momentum', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)

        # x축 날짜 포맷 설정
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(df)//10)))
        plt.gcf().autofmt_xdate()

        # 저장
        file_path = os.path.join(self.results_dir, f"{symbol}_sentiment_momentum_line.png")
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"감성 모멘텀 라인 차트가 저장되었습니다: {file_path}")

    def _generate_momentum_heatmap(self, symbol: str, df: pd.DataFrame) -> None:
        """
        감성 모멘텀 히트맵 차트 생성

        Args:
            symbol: 주식 심볼
            df: 분석 데이터
        """
        # 날짜 및 감성 모멘텀 데이터 준비
        dates = df['date_str'].tolist()
        momentum_values = df['sentiment_momentum'].tolist()

        # 데이터 재구성
        data = []
        for i, date in enumerate(dates):
            data.append([date, "Momentum", momentum_values[i]])

        # 데이터프레임 변환
        heatmap_df = pd.DataFrame(data, columns=['Date', 'Metric', 'Value'])
        heatmap_df = heatmap_df.pivot(index='Metric', columns='Date', values='Value')

        # 커스텀 컬러맵 생성 (빨강-흰색-초록)
        cmap = LinearSegmentedColormap.from_list('RdWhGr', ['red', 'white', 'green'])

        # 히트맵 생성
        plt.figure(figsize=(14, 3))
        sns.heatmap(heatmap_df, cmap=cmap, center=0, annot=False,
                   cbar_kws={'label': 'Momentum Value'})

        # 차트 설정
        plt.title(f'{symbol} Sentiment Momentum Heatmap', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # 저장
        file_path = os.path.join(self.results_dir, f"{symbol}_sentiment_momentum_heatmap.png")
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"감성 모멘텀 히트맵 차트가 저장되었습니다: {file_path}")

    def _generate_momentum_price_chart(self, symbol: str, df: pd.DataFrame) -> None:
        """
        감성 모멘텀과 주가 비교 차트 생성

        Args:
            symbol: 주식 심볼
            df: 분석 데이터
        """
        # 주가 데이터가 있는지 확인
        if 'close' not in df.columns:
            return

        # 두 개의 y축을 가진 차트 생성
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

        # 상단 차트: 주가
        ax1.plot(df['date'], df['close'], 'b-', label='Stock Price')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.set_title(f'{symbol} Stock Price vs Sentiment Momentum', fontsize=14)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)

        # 하단 차트: 감성 모멘텀
        ax2.plot(df['date'], df['sentiment_momentum'], 'g-', label='Sentiment Momentum')
        ax2.axhline(y=0, color='r', linestyle='-', alpha=0.3)

        # 변곡점 표시
        turning_points = df[df['momentum_turning_point']]
        ax2.scatter(turning_points['date'], turning_points['sentiment_momentum'],
                   color='purple', s=100, marker='*', label='Turning Points')

        # 모멘텀 방향에 따른 배경색 설정
        for i in range(len(df)-1):
            if df.iloc[i]['momentum_direction'] == 'improving':
                ax2.axvspan(df.iloc[i]['date'], df.iloc[i+1]['date'], alpha=0.2, color='green')
            elif df.iloc[i]['momentum_direction'] == 'deteriorating':
                ax2.axvspan(df.iloc[i]['date'], df.iloc[i+1]['date'], alpha=0.2, color='red')

        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Momentum', fontsize=12)
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)

        # x축 날짜 포맷 설정
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax2.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(df)//10)))
        fig.autofmt_xdate()

        plt.tight_layout()

        # 저장
        file_path = os.path.join(self.results_dir, f"{symbol}_price_vs_momentum.png")
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"주가-모멘텀 비교 차트가 저장되었습니다: {file_path}")

    def generate_momentum_summary(self, symbol: str, analysis_result: Dict[str, Any]) -> str:
        """
        감성 모멘텀 분석 요약 생성

        Args:
            symbol: 주식 심볼
            analysis_result: 분석 결과

        Returns:
            str: 분석 요약 문자열
        """
        if not analysis_result.get("success", False):
            return "분석 결과가 없습니다."

        summary = [f"# {symbol} 감성 모멘텀 분석 요약"]

        # 기본 정보
        daily_sentiment = pd.DataFrame(analysis_result.get("daily_sentiment", []))
        if not daily_sentiment.empty:
            summary.append(f"\n## 기본 정보")
            summary.append(f"- 분석 기간: {daily_sentiment['date_str'].min()} ~ {daily_sentiment['date_str'].max()}")
            summary.append(f"- 데이터 포인트: {len(daily_sentiment)}개")
            summary.append(f"- 평균 감성 점수: {daily_sentiment['avg_sentiment'].mean():.4f}")

        # 모멘텀 방향별 주가 영향
        if "momentum_impact" in analysis_result:
            summary.append(f"\n## 모멘텀 방향별 주가 영향")
            momentum_impact = analysis_result["momentum_impact"]

            for direction, impact in momentum_impact.items():
                count = impact.get("count", 0)
                if count > 0:
                    same_day = impact.get("price_change", 0)
                    next_day = impact.get("price_change_next_day", 0)
                    summary.append(f"\n### {direction.capitalize()} 모멘텀 ({count}일)")
                    summary.append(f"- 당일 평균 주가 변동: {same_day:.4f}%")
                    summary.append(f"- 다음날 평균 주가 변동: {next_day:.4f}%")

        # 변곡점 영향
        if "turning_point_impact" in analysis_result and analysis_result["turning_point_impact"]:
            summary.append(f"\n## 모멘텀 변곡점 영향")
            turning_point = analysis_result["turning_point_impact"]
            count = turning_point.get("count", 0)

            if count > 0:
                same_day = turning_point.get("price_change", 0)
                next_day = turning_point.get("price_change_next_day", 0)
                summary.append(f"- 변곡점 수: {count}개")
                summary.append(f"- 당일 평균 주가 변동: {same_day:.4f}%")
                summary.append(f"- 다음날 평균 주가 변동: {next_day:.4f}%")

        # 상관관계
        if "correlation" in analysis_result:
            summary.append(f"\n## 모멘텀-주가 상관관계")
            correlation = analysis_result["correlation"]
            summary.append(f"- 모멘텀과 다음날 주가 변동의 상관계수: {correlation:.4f}")

            if correlation > 0.5:
                summary.append(f"- 강한 양의 상관관계: 모멘텀 증가 시 주가 상승 가능성 높음")
            elif correlation > 0.3:
                summary.append(f"- 중간 정도의 양의 상관관계: 모멘텀 증가 시 주가 상승 경향")
            elif correlation > 0:
                summary.append(f"- 약한 양의 상관관계: 모멘텀과 주가 간 약한 연관성")
            elif correlation > -0.3:
                summary.append(f"- 약한 음의 상관관계: 모멘텀과 주가 간 약한 역의 연관성")
            elif correlation > -0.5:
                summary.append(f"- 중간 정도의 음의 상관관계: 모멘텀 증가 시 주가 하락 경향")
            else:
                summary.append(f"- 강한 음의 상관관계: 모멘텀 증가 시 주가 하락 가능성 높음")

        return "\n".join(summary)

if __name__ == "__main__":
    # 테스트 코드
    analyzer = SentimentMomentumAnalyzer()
    print("감성 모멘텀 분석기가 성공적으로 로드되었습니다.")
