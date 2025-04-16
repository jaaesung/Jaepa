"""
감성-주가 상관관계 시각화 모듈

뉴스 감성과 주가 변동의 상관관계를 시각화하는 기능을 제공합니다.
"""
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
import calendar
import base64
from io import BytesIO

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from scipy import stats
from dotenv import load_dotenv

from crawling.gdelt_client import GDELTClient
from data.stock_data_store import StockDataStore
from analysis.sentiment_stock_analyzer import SentimentStockAnalyzer

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# 시각화 스타일 설정
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("Set2")

class SentimentStockVisualizer:
    """
    감성-주가 상관관계 시각화 클래스

    뉴스 감성과 주가 변동의 상관관계를 시각화하는 기능을 제공합니다.
    """

    def __init__(self):
        """
        SentimentStockVisualizer 클래스 초기화
        """
        self.gdelt_client = GDELTClient()
        self.stock_store = StockDataStore()
        self.analyzer = SentimentStockAnalyzer()

        # 그래프 스타일 설정
        self.colors = {
            'positive': '#2ecc71',  # 녹색
            'negative': '#e74c3c',  # 빨간색
            'neutral': '#3498db',   # 파란색
            'price': '#f39c12',     # 주황색
            'volume': '#9b59b6',    # 보라색
            'correlation': '#1abc9c' # 청록색
        }

        # 그래프 크기 설정
        self.fig_size = (12, 8)
        self.dpi = 100

    def _fig_to_base64(self, fig):
        """
        Matplotlib 그림을 base64 인코딩된 문자열로 변환

        Args:
            fig: Matplotlib 그림 객체

        Returns:
            str: base64 인코딩된 이미지 문자열
        """
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=self.dpi, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close(fig)
        return img_str

    def plot_sentiment_vs_price(self,
                               symbol: str,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None,
                               return_base64: bool = False) -> Union[plt.Figure, str]:
        """
        감성과 주가 변동 비교 차트

        Args:
            symbol: 주식 심볼 (예: AAPL)
            start_date: 시작 날짜 (기본값: 90일 전)
            end_date: 종료 날짜 (기본값: 현재)
            return_base64: base64 인코딩된 이미지 반환 여부

        Returns:
            Union[plt.Figure, str]: Matplotlib 그림 객체 또는 base64 인코딩된 이미지 문자열
        """
        # 날짜 범위 설정
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=90)

        # 감성 데이터 가져오기
        sentiment_data = self.gdelt_client.get_news_sentiment_trends(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval='day'
        )

        # 주가 데이터 가져오기
        days = (end_date - start_date).days + 10  # 여유있게 가져오기
        stock_data = self.stock_store.get_stock_price(
            symbol=symbol,
            days=days
        )

        # 데이터프레임 생성
        sentiment_df = pd.DataFrame(sentiment_data['trends'])
        stock_df = pd.DataFrame(stock_data)

        if sentiment_df.empty or stock_df.empty:
            logger.warning(f"데이터가 부족하여 그래프를 생성할 수 없습니다: {symbol}")
            fig, ax = plt.subplots(figsize=self.fig_size)
            ax.text(0.5, 0.5, f"데이터가 부족하여 그래프를 생성할 수 없습니다: {symbol}",
                    ha='center', va='center', fontsize=14)

            if return_base64:
                return self._fig_to_base64(fig)
            return fig

        # 날짜 형식 변환
        sentiment_df['date'] = pd.to_datetime(sentiment_df['interval'])
        stock_df['date'] = pd.to_datetime(stock_df['date'])

        # 감성 점수 추출
        sentiment_df['positive'] = sentiment_df['sentiment'].apply(lambda x: x.get('positive', 0))
        sentiment_df['negative'] = sentiment_df['sentiment'].apply(lambda x: x.get('negative', 0))
        sentiment_df['neutral'] = sentiment_df['sentiment'].apply(lambda x: x.get('neutral', 0))
        sentiment_df['score'] = sentiment_df['sentiment'].apply(lambda x: x.get('score', 0))

        # 데이터 병합
        merged_df = pd.merge_asof(
            sentiment_df.sort_values('date'),
            stock_df.sort_values('date'),
            on='date',
            direction='nearest'
        )

        # 그래프 생성
        fig, ax1 = plt.subplots(figsize=self.fig_size)

        # 감성 점수 그래프
        ax1.plot(merged_df['date'], merged_df['score'], color=self.colors['neutral'],
                 label='감성 점수', linewidth=2)
        ax1.fill_between(merged_df['date'], 0, merged_df['score'],
                         where=(merged_df['score'] > 0), color=self.colors['positive'], alpha=0.3)
        ax1.fill_between(merged_df['date'], 0, merged_df['score'],
                         where=(merged_df['score'] < 0), color=self.colors['negative'], alpha=0.3)

        # 감성 점수 축 설정
        ax1.set_xlabel('날짜', fontsize=12)
        ax1.set_ylabel('감성 점수', fontsize=12, color=self.colors['neutral'])
        ax1.tick_params(axis='y', labelcolor=self.colors['neutral'])
        ax1.set_ylim(-1, 1)

        # 주가 그래프 (보조 y축)
        ax2 = ax1.twinx()
        ax2.plot(merged_df['date'], merged_df['close'], color=self.colors['price'],
                 label='주가', linewidth=2)

        # 주가 축 설정
        ax2.set_ylabel('주가 ($)', fontsize=12, color=self.colors['price'])
        ax2.tick_params(axis='y', labelcolor=self.colors['price'])

        # x축 날짜 포맷 설정
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.xticks(rotation=45)

        # 범례 설정
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        # 제목 설정
        company_name = self.gdelt_client.company_names.get(symbol, symbol)
        plt.title(f'{company_name} ({symbol}) 감성 점수와 주가 비교', fontsize=16)

        # 그리드 설정
        ax1.grid(True, alpha=0.3)

        # 상관계수 계산 및 표시
        correlation = merged_df['score'].corr(merged_df['close'])
        ax1.annotate(f'상관계수: {correlation:.2f}',
                     xy=(0.02, 0.02), xycoords='axes fraction',
                     fontsize=12, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

        plt.tight_layout()

        if return_base64:
            return self._fig_to_base64(fig)
        return fig

    def plot_sentiment_trends(self,
                             symbol: str,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             interval: str = 'day',
                             return_base64: bool = False) -> Union[plt.Figure, str]:
        """
        감성 트렌드 시각화

        Args:
            symbol: 주식 심볼 (예: AAPL)
            start_date: 시작 날짜 (기본값: 90일 전)
            end_date: 종료 날짜 (기본값: 현재)
            interval: 시간 간격 ('day', 'week', 'month')
            return_base64: base64 인코딩된 이미지 반환 여부

        Returns:
            Union[plt.Figure, str]: Matplotlib 그림 객체 또는 base64 인코딩된 이미지 문자열
        """
        # 날짜 범위 설정
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            if interval == 'day':
                start_date = end_date - timedelta(days=90)
            elif interval == 'week':
                start_date = end_date - timedelta(days=180)
            else:  # month
                start_date = end_date - timedelta(days=365)

        # 감성 데이터 가져오기
        sentiment_data = self.gdelt_client.get_news_sentiment_trends(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )

        # 뉴스 볼륨 데이터 가져오기
        volume_data = self.gdelt_client.get_news_volume_by_symbol(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )

        # 데이터프레임 생성
        sentiment_df = pd.DataFrame(sentiment_data['trends'])
        volume_df = pd.DataFrame(volume_data['volumes'])

        if sentiment_df.empty:
            logger.warning(f"데이터가 부족하여 그래프를 생성할 수 없습니다: {symbol}")
            fig, ax = plt.subplots(figsize=self.fig_size)
            ax.text(0.5, 0.5, f"데이터가 부족하여 그래프를 생성할 수 없습니다: {symbol}",
                    ha='center', va='center', fontsize=14)

            if return_base64:
                return self._fig_to_base64(fig)
            return fig

        # 날짜 형식 변환
        sentiment_df['date'] = pd.to_datetime(sentiment_df['interval'])

        # 감성 점수 추출
        sentiment_df['positive'] = sentiment_df['sentiment'].apply(lambda x: x.get('positive', 0))
        sentiment_df['negative'] = sentiment_df['sentiment'].apply(lambda x: x.get('negative', 0))
        sentiment_df['neutral'] = sentiment_df['sentiment'].apply(lambda x: x.get('neutral', 0))
        sentiment_df['score'] = sentiment_df['sentiment'].apply(lambda x: x.get('score', 0))

        # 볼륨 데이터 병합
        if not volume_df.empty:
            volume_df['date'] = pd.to_datetime(volume_df['interval'])
            merged_df = pd.merge(sentiment_df, volume_df, left_on='date', right_on='date', how='left')
        else:
            merged_df = sentiment_df.copy()
            merged_df['count'] = 0

        # 그래프 생성
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.fig_size, height_ratios=[3, 1], sharex=True)

        # 감성 구성 요소 그래프 (누적 영역 차트)
        ax1.fill_between(merged_df['date'], 0, merged_df['positive'],
                         label='긍정', color=self.colors['positive'], alpha=0.7)
        ax1.fill_between(merged_df['date'], 0, -merged_df['negative'],
                         label='부정', color=self.colors['negative'], alpha=0.7)
        ax1.fill_between(merged_df['date'], -merged_df['negative'], merged_df['positive'],
                         label='중립', color=self.colors['neutral'], alpha=0.5)

        # 감성 점수 선 그래프
        ax1.plot(merged_df['date'], merged_df['score'], color='black',
                 label='감성 점수', linewidth=2)

        # 감성 축 설정
        ax1.set_ylabel('감성 구성', fontsize=12)
        ax1.set_ylim(-1, 1)
        ax1.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
        ax1.legend(loc='upper left')

        # 뉴스 볼륨 그래프
        ax2.bar(merged_df['date'], merged_df['count'], color=self.colors['volume'],
                label='뉴스 볼륨', alpha=0.7)

        # 볼륨 축 설정
        ax2.set_xlabel('날짜', fontsize=12)
        ax2.set_ylabel('뉴스 볼륨', fontsize=12)
        ax2.legend(loc='upper left')

        # x축 날짜 포맷 설정
        if interval == 'day':
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        elif interval == 'week':
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax2.xaxis.set_major_locator(mdates.MonthLocator())
        else:  # month
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

        plt.xticks(rotation=45)

        # 제목 설정
        company_name = self.gdelt_client.company_names.get(symbol, symbol)
        interval_map = {'day': '일별', 'week': '주별', 'month': '월별'}
        interval_str = interval_map.get(interval, interval)
        plt.suptitle(f'{company_name} ({symbol}) {interval_str} 감성 트렌드 분석', fontsize=16)

        # 그리드 설정
        ax1.grid(True, alpha=0.3)
        ax2.grid(True, alpha=0.3)

        # 요약 통계 표시
        avg_score = sentiment_data['summary']['average_score']
        total_articles = sentiment_data['summary']['article_count']

        stats_text = f'평균 감성 점수: {avg_score:.2f}\n총 뉴스 기사: {total_articles}개'
        ax1.annotate(stats_text, xy=(0.02, 0.02), xycoords='axes fraction',
                     fontsize=10, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

        plt.tight_layout()

        if return_base64:
            return self._fig_to_base64(fig)
        return fig

    def plot_pattern_impact(self,
                           symbol: str,
                           pattern_type: Optional[str] = None,
                           lookback_days: int = 365,
                           return_base64: bool = False) -> Union[plt.Figure, str]:
        """
        특정 패턴의 주가 영향 시각화

        Args:
            symbol: 주식 심볼 (예: AAPL)
            pattern_type: 패턴 유형 (None인 경우 모든 패턴)
            lookback_days: 분석 기간 (일)
            return_base64: base64 인코딩된 이미지 반환 여부

        Returns:
            Union[plt.Figure, str]: Matplotlib 그림 객체 또는 base64 인코딩된 이미지 문자열
        """
        # 패턴 식별
        patterns = self.analyzer.identify_sentiment_patterns(
            symbol=symbol,
            lookback_days=lookback_days
        )

        if not patterns['patterns']:
            logger.warning(f"식별된 패턴이 없습니다: {symbol}")
            fig, ax = plt.subplots(figsize=self.fig_size)
            ax.text(0.5, 0.5, f"식별된 패턴이 없습니다: {symbol}",
                    ha='center', va='center', fontsize=14)

            if return_base64:
                return self._fig_to_base64(fig)
            return fig

        # 특정 패턴 선택 또는 모든 패턴 사용
        if pattern_type:
            selected_patterns = [p for p in patterns['patterns'] if p['pattern_type'] == pattern_type]
            if not selected_patterns:
                logger.warning(f"지정된 패턴 유형이 없습니다: {pattern_type}")
                selected_patterns = patterns['patterns']
        else:
            selected_patterns = patterns['patterns']

        # 그래프 생성
        fig, ax = plt.subplots(figsize=self.fig_size)

        # 패턴별 영향 그래프 (막대 그래프)
        pattern_names = []
        next_day_changes = []
        next_3days_changes = []
        next_week_changes = []
        occurrences = []

        for pattern in selected_patterns:
            pattern_names.append(pattern['description'])
            next_day_changes.append(pattern['avg_price_change']['next_day'])
            next_3days_changes.append(pattern['avg_price_change']['next_3_days'])
            next_week_changes.append(pattern['avg_price_change']['next_week'])
            occurrences.append(pattern['occurrences'])

        # 인덱스 설정
        x = np.arange(len(pattern_names))
        width = 0.25

        # 막대 그래프 그리기
        ax.bar(x - width, next_day_changes, width, label='다음날', color='#3498db')
        ax.bar(x, next_3days_changes, width, label='3일 후', color='#2ecc71')
        ax.bar(x + width, next_week_changes, width, label='1주일 후', color='#e74c3c')

        # 축 설정
        ax.set_xlabel('감성 패턴', fontsize=12)
        ax.set_ylabel('평균 주가 변동 (%)', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(pattern_names, rotation=45, ha='right')

        # 범례 설정
        ax.legend()

        # 제목 설정
        company_name = self.gdelt_client.company_names.get(symbol, symbol)
        plt.title(f'{company_name} ({symbol}) 감성 패턴별 주가 영향', fontsize=16)

        # 그리드 설정
        ax.grid(True, alpha=0.3)

        # 발생 횟수 표시
        for i, occ in enumerate(occurrences):
            ax.annotate(f'{occ}회', xy=(i, 0), xytext=(0, 10 if next_day_changes[i] >= 0 else -25),
                        textcoords='offset points', ha='center', va='center',
                        fontsize=9, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.7))

        plt.tight_layout()

        if return_base64:
            return self._fig_to_base64(fig)
        return fig

    def generate_dashboard_data(self,
                               symbol: str,
                               period_days: int = 90) -> Dict[str, Any]:
        """
        대시보드용 데이터 생성

        Args:
            symbol: 주식 심볼 (예: AAPL)
            period_days: 분석 기간 (일)

        Returns:
            Dict[str, Any]: 대시보드용 데이터
        """
        # 날짜 범위 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        # 인사이트 보고서 생성
        insights = self.analyzer.generate_insight_report(
            symbol=symbol,
            period_days=period_days
        )

        # 그래프 생성
        sentiment_vs_price_chart = self.plot_sentiment_vs_price(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            return_base64=True
        )

        sentiment_trends_chart = self.plot_sentiment_trends(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval='day',
            return_base64=True
        )

        pattern_impact_chart = self.plot_pattern_impact(
            symbol=symbol,
            lookback_days=period_days,
            return_base64=True
        )

        # 대시보드 데이터 구성
        dashboard_data = {
            "symbol": symbol,
            "company_name": insights.get('company_name', symbol),
            "period": insights.get('period', f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"),
            "insights": insights.get('insights', []),
            "correlation": insights.get('correlation', {}),
            "total_news": insights.get('total_news', 0),
            "charts": {
                "sentiment_vs_price": sentiment_vs_price_chart,
                "sentiment_trends": sentiment_trends_chart,
                "pattern_impact": pattern_impact_chart
            },
            "top_entities": insights.get('top_entities', {})
        }

        return dashboard_data

# 테스트 코드
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    visualizer = SentimentStockVisualizer()

    # 애플 감성-주가 비교 차트
    print("애플 감성-주가 비교 차트 생성...")
    fig = visualizer.plot_sentiment_vs_price("AAPL")
    plt.savefig("apple_sentiment_vs_price.png", dpi=100, bbox_inches='tight')
    plt.close(fig)

    # 감성 트렌드 차트
    print("애플 감성 트렌드 차트 생성...")
    fig = visualizer.plot_sentiment_trends("AAPL")
    plt.savefig("apple_sentiment_trends.png", dpi=100, bbox_inches='tight')
    plt.close(fig)

    # 패턴 영향 차트
    print("애플 패턴 영향 차트 생성...")
    fig = visualizer.plot_pattern_impact("AAPL")
    plt.savefig("apple_pattern_impact.png", dpi=100, bbox_inches='tight')
    plt.close(fig)

    # 대시보드 데이터 생성
    print("애플 대시보드 데이터 생성...")
    dashboard_data = visualizer.generate_dashboard_data("AAPL")
    print(f"대시보드 데이터 생성 완료: {len(dashboard_data['insights'])}개 인사이트, {len(dashboard_data['charts'])}개 차트")
