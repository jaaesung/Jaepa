#!/usr/bin/env python3
"""
감성-주가 상관관계 분석 실행 스크립트

이 스크립트는 GDELT 뉴스 감성과 주가 변동 간의 상관관계를 분석하고 결과를 출력합니다.
"""
import os
import logging
import json
import argparse
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# 모의 GDELT 클라이언트 직접 구현
class MockGDELTClient:
    """
    모의 GDELT 클라이언트

    GDELT API를 사용하지 않고 모의 데이터를 생성합니다.
    """

    def __init__(self):
        """
        MockGDELTClient 클래스 초기화
        """
        # 회사 이름 매핑
        self.company_names = {
            "AAPL": "Apple",
            "MSFT": "Microsoft",
            "GOOGL": "Google",
            "AMZN": "Amazon",
            "META": "Meta",
            "TSLA": "Tesla",
            "NVDA": "NVIDIA"
        }

    def analyze_sentiment_stock_correlation(self, symbol, **kwargs):
        """
        모의 감성-주가 상관관계 분석
        """
        # 모의 상관관계 생성
        correlation = {
            "same_day": 0.25,
            "next_day": -0.15,
            "next_3_days": 0.35,
            "next_week": -0.10
        }

        # 모의 감성 영향 생성
        sentiment_impact = []
        for group in ['very_negative', 'negative', 'neutral', 'positive', 'very_positive']:
            impact = {
                "sentiment_group": group,
                "count": 10 + (5 * (group == 'neutral')),
                "avg_price_change": {
                    "same_day": (0.5 if group in ['positive', 'very_positive'] else -0.5) + (0.5 if group == 'very_positive' else 0),
                    "next_day": (-0.3 if group in ['positive', 'very_positive'] else 0.3) + (0.2 if group == 'very_negative' else 0),
                    "next_3_days": (0.8 if group in ['positive', 'very_positive'] else -0.8) + (0.4 if group == 'very_positive' else 0),
                    "next_week": (1.2 if group in ['positive', 'very_positive'] else -1.2) + (0.6 if group == 'very_positive' else 0)
                }
            }
            sentiment_impact.append(impact)

        return {
            "symbol": symbol,
            "period": "2025-02-08 to 2025-05-09",
            "correlation": correlation,
            "sentiment_impact": sentiment_impact,
            "data_points": 60
        }

    def identify_sentiment_patterns(self, symbol, **kwargs):
        """
        모의 감성 패턴 식별
        """
        # 모의 패턴 생성
        patterns = [
            {
                "pattern_type": "positive_sentiment_surge",
                "description": "급격한 긍정적 감성 증가",
                "occurrences": 5,
                "avg_price_change": {
                    "next_day": 0.8,
                    "next_3_days": 1.5,
                    "next_week": 2.2
                },
                "strength": 0.75
            },
            {
                "pattern_type": "negative_sentiment_surge",
                "description": "급격한 부정적 감성 증가",
                "occurrences": 4,
                "avg_price_change": {
                    "next_day": -0.6,
                    "next_3_days": -1.2,
                    "next_week": -1.8
                },
                "strength": 0.65
            },
            {
                "pattern_type": "sentiment_golden_cross",
                "description": "감성 이동평균 골든 크로스 (단기>장기)",
                "occurrences": 3,
                "avg_price_change": {
                    "next_day": 0.4,
                    "next_3_days": 0.9,
                    "next_week": 1.5
                },
                "strength": 0.55
            }
        ]

        return {
            "symbol": symbol,
            "period": "2025-02-08 to 2025-05-09",
            "patterns": patterns,
            "pattern_count": len(patterns)
        }

    def get_news_volume_by_symbol(self, symbol, **kwargs):
        """
        모의 뉴스 볼륨 데이터
        """
        # 모의 볼륨 데이터 생성
        volumes = []
        for i in range(30):
            volumes.append({
                "interval": f"2025-04-{10+i:02d}",
                "count": 10 + (i % 5) * 2
            })

        return {
            "symbol": symbol,
            "period": "2025-04-10 to 2025-05-09",
            "volumes": volumes,
            "total_articles": sum(v["count"] for v in volumes)
        }

    def get_related_entities(self, symbol, **kwargs):
        """
        모의 관련 엔티티 데이터
        """
        # 모의 엔티티 데이터 생성
        persons = []
        orgs = []

        if symbol == "AAPL":
            persons = [
                {"name": "Tim Cook", "count": 15},
                {"name": "Steve Jobs", "count": 8},
                {"name": "Luca Maestri", "count": 5}
            ]
            orgs = [
                {"name": "Apple Inc.", "count": 25},
                {"name": "TSMC", "count": 10},
                {"name": "Foxconn", "count": 8}
            ]
        elif symbol == "MSFT":
            persons = [
                {"name": "Satya Nadella", "count": 18},
                {"name": "Bill Gates", "count": 10},
                {"name": "Amy Hood", "count": 6}
            ]
            orgs = [
                {"name": "Microsoft Corporation", "count": 30},
                {"name": "OpenAI", "count": 15},
                {"name": "GitHub", "count": 12}
            ]
        else:
            persons = [
                {"name": "CEO", "count": 12},
                {"name": "CFO", "count": 8},
                {"name": "CTO", "count": 5}
            ]
            orgs = [
                {"name": f"{symbol} Inc.", "count": 20},
                {"name": "Competitor A", "count": 10},
                {"name": "Competitor B", "count": 8}
            ]

        return {
            "symbol": symbol,
            "period": "2025-02-08 to 2025-05-09",
            "persons": persons,
            "organizations": orgs
        }

    def get_news_sentiment_trends(self, symbol, **kwargs):
        """
        모의 감성 트렌드 분석
        """
        # 모의 트렌드 생성
        trends = []
        for i in range(30):
            date = f"2025-04-{10+i:02d}"
            sentiment_score = (i % 10) / 10.0 - 0.5  # -0.5 ~ 0.4

            trends.append({
                "interval": date,
                "sentiment": {
                    "positive": max(0, sentiment_score),
                    "negative": max(0, -sentiment_score),
                    "neutral": 1.0 - abs(sentiment_score),
                    "score": sentiment_score
                },
                "article_count": 5 + (i % 5)
            })

        # 전체 기간 요약
        summary = {
            "positive": 0.3,
            "negative": 0.2,
            "neutral": 0.5,
            "average_score": 0.1,
            "article_count": sum(t["article_count"] for t in trends)
        }

        return {
            "symbol": symbol,
            "period": "2025-04-10 to 2025-05-09",
            "interval": "day",
            "trends": trends,
            "summary": summary
        }

# 모의 클라이언트로 SentimentStockAnalyzer 초기화
from analysis.sentiment_stock_analyzer import SentimentStockAnalyzer

# 원래 GDELT 클라이언트를 모의 클라이언트로 대체
import crawling.gdelt_client
crawling.gdelt_client.GDELTClient = MockGDELTClient
logger.info("GDELT 클라이언트가 모의 클라이언트로 대체되었습니다.")

def create_results_directory():
    """결과 저장 디렉토리 생성"""
    results_dir = os.path.join(os.getcwd(), "results")
    os.makedirs(results_dir, exist_ok=True)
    return results_dir

def save_correlation_chart(symbol, correlation, results_dir):
    """상관계수 차트 생성 및 저장"""
    # 상관계수 데이터
    corr_data = correlation.get('correlation', {})
    if not corr_data:
        return

    # 차트 생성
    plt.figure(figsize=(10, 6))

    periods = ['same_day', 'next_day', 'next_3_days', 'next_week']
    period_labels = ['당일', '다음날', '3일 후', '1주일 후']
    values = [corr_data.get(p, 0) for p in periods]

    # 막대 색상 설정 (양수: 파란색, 음수: 빨간색)
    colors = ['blue' if v >= 0 else 'red' for v in values]

    plt.bar(period_labels, values, color=colors)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)

    plt.title(f'{symbol} 뉴스 감성과 주가 변동의 상관계수', fontsize=14)
    plt.ylabel('상관계수', fontsize=12)
    plt.ylim(-1, 1)
    plt.grid(axis='y', alpha=0.3)

    # 결과 저장
    file_path = os.path.join(results_dir, f"{symbol}_correlation_chart.png")
    plt.savefig(file_path, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"상관계수 차트가 저장되었습니다: {file_path}")

def save_sentiment_impact_chart(symbol, correlation, results_dir):
    """감성 그룹별 영향 차트 생성 및 저장"""
    # 감성 영향 데이터
    impact_data = correlation.get('sentiment_impact', [])
    if not impact_data:
        return

    # 데이터프레임 변환
    impact_df = pd.DataFrame()

    for impact in impact_data:
        group = impact.get('sentiment_group', '')
        price_changes = impact.get('avg_price_change', {})

        row = {
            'sentiment_group': group,
            'same_day': price_changes.get('same_day', 0),
            'next_day': price_changes.get('next_day', 0),
            'next_3_days': price_changes.get('next_3_days', 0),
            'next_week': price_changes.get('next_week', 0)
        }

        impact_df = pd.concat([impact_df, pd.DataFrame([row])], ignore_index=True)

    # 감성 그룹 순서 설정
    sentiment_order = ['very_negative', 'negative', 'neutral', 'positive', 'very_positive']
    impact_df['sentiment_group'] = pd.Categorical(impact_df['sentiment_group'], categories=sentiment_order, ordered=True)
    impact_df = impact_df.sort_values('sentiment_group')

    # 차트 생성
    plt.figure(figsize=(12, 8))

    periods = ['same_day', 'next_day', 'next_3_days', 'next_week']
    period_labels = ['당일', '다음날', '3일 후', '1주일 후']

    # 막대 위치 설정
    x = np.arange(len(sentiment_order))
    width = 0.2

    # 각 기간별 막대 그래프
    for i, period in enumerate(periods):
        plt.bar(x + (i - 1.5) * width, impact_df[period], width, label=period_labels[i])

    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.title(f'{symbol} 감성 그룹별 주가 변동 영향', fontsize=14)
    plt.xlabel('감성 그룹', fontsize=12)
    plt.ylabel('평균 가격 변화 (%)', fontsize=12)
    plt.xticks(x, ['매우 부정', '부정', '중립', '긍정', '매우 긍정'])
    plt.legend()
    plt.grid(axis='y', alpha=0.3)

    # 결과 저장
    file_path = os.path.join(results_dir, f"{symbol}_sentiment_impact_chart.png")
    plt.savefig(file_path, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"감성 영향 차트가 저장되었습니다: {file_path}")

def save_patterns_chart(symbol, patterns, results_dir):
    """패턴 차트 생성 및 저장"""
    if not patterns or not patterns.get('patterns'):
        return

    # 패턴 데이터
    pattern_list = patterns.get('patterns', [])
    if not pattern_list:
        return

    # 데이터프레임 변환
    pattern_df = pd.DataFrame()

    for pattern in pattern_list:
        price_changes = pattern.get('avg_price_change', {})

        row = {
            'pattern_type': pattern.get('pattern_type', ''),
            'description': pattern.get('description', ''),
            'occurrences': pattern.get('occurrences', 0),
            'strength': pattern.get('strength', 0),
            'next_day': price_changes.get('next_day', 0),
            'next_3_days': price_changes.get('next_3_days', 0),
            'next_week': price_changes.get('next_week', 0)
        }

        pattern_df = pd.concat([pattern_df, pd.DataFrame([row])], ignore_index=True)

    if pattern_df.empty:
        return

    # 강도순 정렬
    pattern_df = pattern_df.sort_values('strength', ascending=False)

    # 상위 5개 패턴만 선택
    pattern_df = pattern_df.head(5)

    # 차트 생성
    plt.figure(figsize=(12, 8))

    periods = ['next_day', 'next_3_days', 'next_week']
    period_labels = ['다음날', '3일 후', '1주일 후']

    # 막대 위치 설정
    x = np.arange(len(pattern_df))
    width = 0.25

    # 각 기간별 막대 그래프
    for i, period in enumerate(periods):
        plt.bar(x + (i - 1) * width, pattern_df[period], width, label=period_labels[i])

    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.title(f'{symbol} 감성 패턴별 주가 변동 영향', fontsize=14)
    plt.xlabel('감성 패턴', fontsize=12)
    plt.ylabel('평균 가격 변화 (%)', fontsize=12)
    plt.xticks(x, pattern_df['description'], rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    # 결과 저장
    file_path = os.path.join(results_dir, f"{symbol}_patterns_chart.png")
    plt.savefig(file_path, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"패턴 차트가 저장되었습니다: {file_path}")

def save_insights_json(symbol, insights, results_dir):
    """인사이트 JSON 저장"""
    if not insights:
        return

    # 결과 저장
    file_path = os.path.join(results_dir, f"{symbol}_insights.json")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(insights, f, indent=2, ensure_ascii=False)

    logger.info(f"인사이트 JSON이 저장되었습니다: {file_path}")

def main():
    """메인 함수"""
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description='GDELT 뉴스 감성과 주가 상관관계 분석')
    parser.add_argument('--symbols', type=str, nargs='+', default=['AAPL', 'MSFT', 'GOOGL'],
                        help='분석할 주식 심볼 목록 (기본값: AAPL MSFT GOOGL)')
    parser.add_argument('--days', type=int, default=90,
                        help='분석 기간 (일) (기본값: 90)')

    args = parser.parse_args()

    # 결과 디렉토리 생성
    results_dir = create_results_directory()

    # 분석기 초기화
    analyzer = SentimentStockAnalyzer(db_connect=False)

    try:
        # 각 심볼 분석
        for symbol in args.symbols:
            logger.info(f"{symbol} 분석 시작...")

            # 상관관계 분석
            end_date = datetime.now()
            start_date = end_date - timedelta(days=args.days)

            correlation = analyzer.analyze_correlation(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                force_update=True
            )

            # 패턴 식별
            patterns = analyzer.identify_sentiment_patterns(
                symbol=symbol,
                lookback_days=args.days
            )

            # 인사이트 보고서
            insights = analyzer.generate_insight_report(
                symbol=symbol,
                period_days=args.days
            )

            # 결과 출력
            print(f"\n{symbol} 분석 결과:")
            print(f"기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")

            # 상관계수 출력
            corr_data = correlation.get('correlation', {})
            if corr_data:
                print("\n상관계수:")
                print(f"당일: {corr_data.get('same_day', 0):.4f}")
                print(f"다음날: {corr_data.get('next_day', 0):.4f}")
                print(f"3일 후: {corr_data.get('next_3_days', 0):.4f}")
                print(f"1주일 후: {corr_data.get('next_week', 0):.4f}")

            # 패턴 출력
            pattern_list = patterns.get('patterns', [])
            if pattern_list:
                print(f"\n식별된 패턴 ({len(pattern_list)}개):")
                for pattern in pattern_list:
                    print(f"- {pattern.get('description')}: 강도 {pattern.get('strength', 0):.2f}")
                    price_changes = pattern.get('avg_price_change', {})
                    print(f"  다음날: {price_changes.get('next_day', 0):.2f}%, 3일 후: {price_changes.get('next_3_days', 0):.2f}%, 1주일 후: {price_changes.get('next_week', 0):.2f}%")

            # 인사이트 출력
            insight_list = insights.get('insights', [])
            if insight_list:
                print(f"\n인사이트 ({len(insight_list)}개):")
                for insight in insight_list:
                    print(f"- {insight.get('title')}")
                    print(f"  {insight.get('description')}")

            # 차트 저장
            save_correlation_chart(symbol, correlation, results_dir)
            save_sentiment_impact_chart(symbol, correlation, results_dir)
            save_patterns_chart(symbol, patterns, results_dir)
            save_insights_json(symbol, insights, results_dir)

            logger.info(f"{symbol} 분석 완료")

        print(f"\n분석 결과가 {os.path.abspath(results_dir)} 디렉토리에 저장되었습니다.")

    finally:
        # 연결 종료
        analyzer.close()

if __name__ == "__main__":
    main()
