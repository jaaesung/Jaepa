#!/usr/bin/env python3
"""
감성-주가 상관관계 분석 시스템 테스트 스크립트

GDELT 기반 감성 분석 및 주가 상관관계 분석 시스템을 테스트합니다.
"""
import os
import sys
import logging
import json
from datetime import datetime, timedelta
from pprint import pprint
import matplotlib.pyplot as plt

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from crawling.gdelt_client import GDELTClient
from analysis.sentiment_stock_analyzer import SentimentStockAnalyzer
from analysis.sentiment_stock_visualizer import SentimentStockVisualizer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_gdelt_client():
    """GDELT 클라이언트 테스트"""
    client = GDELTClient()

    # 1. 뉴스 검색 테스트
    print("\n=== 뉴스 검색 테스트 ===")
    news = client.get_news_by_symbol("AAPL", days=3, max_records=3)
    print(f"애플 관련 뉴스: {len(news)}개")
    for article in news:
        print(f"제목: {article.get('title', 'N/A')}")
        print(f"날짜: {article.get('published_date', 'N/A')}")
        print(f"감성 점수: {article.get('sentiment', {}).get('score', 'N/A')}")
        print("---")

    # 2. 과거 뉴스 검색 테스트
    print("\n=== 과거 뉴스 검색 테스트 ===")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    historical_news = client.get_historical_news_by_symbol(
        "AAPL",
        start_date=start_date,
        end_date=end_date,
        max_records=5
    )
    print(f"애플 관련 과거 뉴스: {len(historical_news)}개")
    for article in historical_news[:2]:  # 처음 2개만 출력
        print(f"제목: {article.get('title', 'N/A')}")
        print(f"날짜: {article.get('published_date', 'N/A')}")
        print(f"감성 점수: {article.get('sentiment', {}).get('score', 'N/A')}")
        print("---")

    # 3. 감성 트렌드 테스트
    print("\n=== 감성 트렌드 테스트 ===")
    trends = client.get_news_sentiment_trends(
        "AAPL",
        start_date=start_date,
        end_date=end_date,
        interval='day'
    )
    print(f"감성 트렌드 기간 수: {len(trends.get('trends', []))}개")
    print(f"평균 감성 점수: {trends.get('summary', {}).get('average_score', 'N/A')}")

    # 4. 뉴스 볼륨 테스트
    print("\n=== 뉴스 볼륨 테스트 ===")
    volume = client.get_news_volume_by_symbol(
        "AAPL",
        start_date=start_date,
        end_date=end_date,
        interval='day'
    )
    print(f"뉴스 볼륨 기간 수: {len(volume.get('volumes', []))}개")
    print(f"총 기사 수: {volume.get('total_articles', 'N/A')}개")

    # 5. 관련 엔티티 테스트
    print("\n=== 관련 엔티티 테스트 ===")
    entities = client.get_related_entities(
        "AAPL",
        start_date=start_date,
        end_date=end_date
    )
    print(f"관련 인물: {len(entities.get('persons', []))}명")
    print(f"관련 조직: {len(entities.get('organizations', []))}개")
    print(f"관련 장소: {len(entities.get('locations', []))}개")
    print(f"관련 테마: {len(entities.get('themes', []))}개")

    # 6. 감성-주가 상관관계 테스트
    print("\n=== 감성-주가 상관관계 테스트 ===")
    correlation = client.analyze_sentiment_stock_correlation("AAPL")
    print(f"상관계수:")
    for period, coef in correlation.get('correlation', {}).items():
        print(f"- {period}: {coef:.4f}")

    return {
        "news_count": len(news),
        "historical_news_count": len(historical_news),
        "trends_count": len(trends.get('trends', [])),
        "volumes_count": len(volume.get('volumes', [])),
        "entities_count": sum([
            len(entities.get('persons', [])),
            len(entities.get('organizations', [])),
            len(entities.get('locations', [])),
            len(entities.get('themes', []))
        ]),
        "correlation": correlation.get('correlation', {})
    }

def test_sentiment_analyzer():
    """감성-주가 상관관계 분석기 테스트"""
    analyzer = SentimentStockAnalyzer()

    try:
        # 1. 상관관계 분석 테스트
        print("\n=== 상관관계 분석 테스트 ===")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        correlation = analyzer.analyze_correlation(
            symbol="AAPL",
            start_date=start_date,
            end_date=end_date
        )
        print(f"상관계수:")
        for period, coef in correlation.get('correlation', {}).items():
            print(f"- {period}: {coef:.4f}")
        print(f"데이터 포인트: {correlation.get('data_points', 'N/A')}개")

        # 2. 패턴 식별 테스트
        print("\n=== 패턴 식별 테스트 ===")
        patterns = analyzer.identify_sentiment_patterns("AAPL", lookback_days=180)
        print(f"식별된 패턴: {patterns.get('pattern_count', 0)}개")
        for pattern in patterns.get('patterns', []):
            print(f"- {pattern.get('description', 'N/A')}: 강도 {pattern.get('strength', 'N/A'):.2f}")
            print(f"  발생 횟수: {pattern.get('occurrences', 'N/A')}회")
            print(f"  다음날 평균 변동: {pattern.get('avg_price_change', {}).get('next_day', 'N/A'):.2f}%")

        # 3. 인사이트 보고서 테스트
        print("\n=== 인사이트 보고서 테스트 ===")
        insights = analyzer.generate_insight_report("AAPL", period_days=90)
        print(f"생성된 인사이트: {len(insights.get('insights', []))}개")
        for insight in insights.get('insights', []):
            print(f"- {insight.get('title', 'N/A')}")
            print(f"  {insight.get('description', 'N/A')}")

        return {
            "correlation_data_points": correlation.get('data_points', 0),
            "pattern_count": patterns.get('pattern_count', 0),
            "insight_count": len(insights.get('insights', []))
        }
    finally:
        analyzer.close()

def test_sentiment_visualizer():
    """감성-주가 상관관계 시각화기 테스트"""
    visualizer = SentimentStockVisualizer()

    # 1. 감성-주가 비교 차트 테스트
    print("\n=== 감성-주가 비교 차트 테스트 ===")
    fig1 = visualizer.plot_sentiment_vs_price("AAPL")
    plt.savefig("test_sentiment_vs_price.png", dpi=100, bbox_inches='tight')
    plt.close(fig1)
    print("감성-주가 비교 차트 생성 완료: test_sentiment_vs_price.png")

    # 2. 감성 트렌드 차트 테스트
    print("\n=== 감성 트렌드 차트 테스트 ===")
    fig2 = visualizer.plot_sentiment_trends("AAPL")
    plt.savefig("test_sentiment_trends.png", dpi=100, bbox_inches='tight')
    plt.close(fig2)
    print("감성 트렌드 차트 생성 완료: test_sentiment_trends.png")

    # 3. 패턴 영향 차트 테스트
    print("\n=== 패턴 영향 차트 테스트 ===")
    fig3 = visualizer.plot_pattern_impact("AAPL")
    plt.savefig("test_pattern_impact.png", dpi=100, bbox_inches='tight')
    plt.close(fig3)
    print("패턴 영향 차트 생성 완료: test_pattern_impact.png")

    # 4. 대시보드 데이터 테스트
    print("\n=== 대시보드 데이터 테스트 ===")
    dashboard = visualizer.generate_dashboard_data("AAPL", period_days=90)
    print(f"대시보드 데이터 생성 완료:")
    print(f"- 인사이트: {len(dashboard.get('insights', []))}개")
    print(f"- 차트: {len(dashboard.get('charts', {}))}개")
    print(f"- 상위 엔티티: {sum([len(entities) for entities in dashboard.get('top_entities', {}).values()])}개")

    return {
        "charts_generated": 3,
        "dashboard_insights": len(dashboard.get('insights', [])),
        "dashboard_charts": len(dashboard.get('charts', {}))
    }

if __name__ == "__main__":
    print("\n===== GDELT 기반 감성-주가 상관관계 분석 시스템 테스트 =====\n")

    # 테스트 실행
    try:
        # GDELT 클라이언트 테스트
        gdelt_results = test_gdelt_client()

        # 감성-주가 상관관계 분석기 테스트
        analyzer_results = test_sentiment_analyzer()

        # 감성-주가 상관관계 시각화기 테스트
        visualizer_results = test_sentiment_visualizer()

        # 테스트 결과 요약
        print("\n===== 테스트 결과 요약 =====")
        print(f"GDELT 클라이언트: {gdelt_results['news_count']}개 뉴스, {gdelt_results['trends_count']}개 트렌드, {gdelt_results['entities_count']}개 엔티티")
        print(f"감성 분석기: {analyzer_results['correlation_data_points']}개 데이터 포인트, {analyzer_results['pattern_count']}개 패턴, {analyzer_results['insight_count']}개 인사이트")
        print(f"시각화기: {visualizer_results['charts_generated']}개 차트, {visualizer_results['dashboard_insights']}개 대시보드 인사이트")

        print("\n모든 테스트가 완료되었습니다.")
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {str(e)}")
        raise
