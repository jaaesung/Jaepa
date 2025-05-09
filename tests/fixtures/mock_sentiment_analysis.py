#!/usr/bin/env python3
"""
모의 감성-주가 상관관계 분석 스크립트

이 스크립트는 모의 데이터를 사용하여 뉴스 감성과 주가 변동 간의 상관관계를 분석하고 결과를 출력합니다.
"""
import os
import logging
import json
import argparse
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockSentimentAnalyzer:
    """
    모의 감성-주가 상관관계 분석기
    """
    
    def __init__(self):
        """
        MockSentimentAnalyzer 클래스 초기화
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
        
        # 결과 저장 디렉토리
        self.results_dir = os.path.join(os.getcwd(), "results")
        os.makedirs(self.results_dir, exist_ok=True)
    
    def analyze_correlation(self, symbol, **kwargs):
        """
        모의 감성-주가 상관관계 분석
        """
        # 모의 상관관계 생성 (심볼별로 다른 값)
        if symbol == "AAPL":
            correlation = {
                "same_day": 0.25,
                "next_day": -0.15,
                "next_3_days": 0.35,
                "next_week": -0.10
            }
        elif symbol == "MSFT":
            correlation = {
                "same_day": -0.10,
                "next_day": 0.30,
                "next_3_days": 0.20,
                "next_week": 0.15
            }
        else:
            correlation = {
                "same_day": random.uniform(-0.3, 0.3),
                "next_day": random.uniform(-0.3, 0.3),
                "next_3_days": random.uniform(-0.3, 0.3),
                "next_week": random.uniform(-0.3, 0.3)
            }
        
        # 모의 감성 영향 생성
        sentiment_impact = []
        for group in ['very_negative', 'negative', 'neutral', 'positive', 'very_positive']:
            # 심볼별로 다른 패턴 생성
            if symbol == "AAPL":
                # Apple: 긍정적 감성이 주가에 긍정적 영향
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
            elif symbol == "MSFT":
                # Microsoft: 부정적 감성이 단기적으로 주가에 부정적, 장기적으로 긍정적 영향
                impact = {
                    "sentiment_group": group,
                    "count": 12 + (3 * (group == 'positive')),
                    "avg_price_change": {
                        "same_day": (-0.6 if group in ['negative', 'very_negative'] else 0.4) + (-0.3 if group == 'very_negative' else 0),
                        "next_day": (-0.4 if group in ['negative', 'very_negative'] else 0.2) + (-0.2 if group == 'very_negative' else 0),
                        "next_3_days": (0.5 if group in ['negative', 'very_negative'] else -0.3) + (0.3 if group == 'very_negative' else 0),
                        "next_week": (0.9 if group in ['negative', 'very_negative'] else -0.5) + (0.5 if group == 'very_negative' else 0)
                    }
                }
            else:
                # 기타 심볼: 랜덤 패턴
                impact = {
                    "sentiment_group": group,
                    "count": random.randint(8, 15),
                    "avg_price_change": {
                        "same_day": random.uniform(-1.0, 1.0),
                        "next_day": random.uniform(-1.0, 1.0),
                        "next_3_days": random.uniform(-1.5, 1.5),
                        "next_week": random.uniform(-2.0, 2.0)
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
    
    def identify_patterns(self, symbol, **kwargs):
        """
        모의 감성 패턴 식별
        """
        # 심볼별로 다른 패턴 생성
        if symbol == "AAPL":
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
        elif symbol == "MSFT":
            patterns = [
                {
                    "pattern_type": "sentiment_dead_cross",
                    "description": "감성 이동평균 데드 크로스 (단기<장기)",
                    "occurrences": 4,
                    "avg_price_change": {
                        "next_day": -0.5,
                        "next_3_days": -1.0,
                        "next_week": 1.2
                    },
                    "strength": 0.70
                },
                {
                    "pattern_type": "extreme_negative_sentiment",
                    "description": "매우 부정적인 감성",
                    "occurrences": 6,
                    "avg_price_change": {
                        "next_day": -0.8,
                        "next_3_days": -0.5,
                        "next_week": 1.8
                    },
                    "strength": 0.65
                },
                {
                    "pattern_type": "sentiment_volatility",
                    "description": "감성 변동성 증가",
                    "occurrences": 5,
                    "avg_price_change": {
                        "next_day": 0.3,
                        "next_3_days": 0.7,
                        "next_week": 1.1
                    },
                    "strength": 0.50
                }
            ]
        else:
            # 기타 심볼: 기본 패턴
            patterns = [
                {
                    "pattern_type": "positive_sentiment_surge",
                    "description": "급격한 긍정적 감성 증가",
                    "occurrences": random.randint(3, 6),
                    "avg_price_change": {
                        "next_day": random.uniform(0.3, 1.0),
                        "next_3_days": random.uniform(0.5, 1.5),
                        "next_week": random.uniform(1.0, 2.5)
                    },
                    "strength": random.uniform(0.5, 0.8)
                },
                {
                    "pattern_type": "negative_sentiment_surge",
                    "description": "급격한 부정적 감성 증가",
                    "occurrences": random.randint(3, 6),
                    "avg_price_change": {
                        "next_day": random.uniform(-1.0, -0.3),
                        "next_3_days": random.uniform(-1.5, -0.5),
                        "next_week": random.uniform(-2.5, -1.0)
                    },
                    "strength": random.uniform(0.5, 0.8)
                }
            ]
        
        return {
            "symbol": symbol,
            "period": "2025-02-08 to 2025-05-09",
            "patterns": patterns,
            "pattern_count": len(patterns)
        }
    
    def generate_insights(self, symbol, **kwargs):
        """
        모의 인사이트 생성
        """
        # 상관관계 분석
        correlation = self.analyze_correlation(symbol)
        
        # 패턴 식별
        patterns = self.identify_patterns(symbol)
        
        # 인사이트 생성
        insights = []
        
        # 상관관계 인사이트
        corr_data = correlation.get('correlation', {})
        if corr_data:
            max_corr = max(corr_data.items(), key=lambda x: abs(x[1]))
            max_corr_period, max_corr_value = max_corr
            
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
        for pattern in patterns.get('patterns', [])[:2]:  # 상위 2개 패턴만
            insights.append({
                "type": "pattern",
                "title": pattern.get('description'),
                "description": f"{pattern.get('occurrences')}회 발생했으며, 이후 3일간 평균 {pattern.get('avg_price_change', {}).get('next_3_days', 0):.2f}% 변동이 있었습니다.",
                "strength": pattern.get('strength', 0)
            })
        
        # 심볼별 특별 인사이트
        if symbol == "AAPL":
            insights.append({
                "type": "special",
                "title": "Apple 제품 출시 전후 감성 변화",
                "description": "Apple 제품 출시 발표 전 2주간 긍정적 감성이 증가하고, 출시 후 1주일 동안 주가가 평균 2.5% 상승했습니다.",
                "strength": 0.85
            })
        elif symbol == "MSFT":
            insights.append({
                "type": "special",
                "title": "Microsoft의 AI 관련 뉴스 영향",
                "description": "Microsoft의 AI 관련 긍정적 뉴스는 3일 후 주가에 평균 1.8%의 상승 효과가 있었습니다.",
                "strength": 0.80
            })
        
        # 인사이트 강도순 정렬
        insights.sort(key=lambda x: x.get('strength', 0), reverse=True)
        
        return {
            "symbol": symbol,
            "company_name": self.company_names.get(symbol, symbol),
            "period": "2025-02-08 to 2025-05-09",
            "insights": insights,
            "correlation": correlation.get('correlation', {}),
            "patterns": patterns.get('patterns', []),
            "total_news": random.randint(100, 500)
        }
    
    def generate_mock_stock_data(self, symbol, days=90):
        """
        모의 주가 데이터 생성
        """
        # 시작 가격 설정
        base_prices = {
            "AAPL": 180.0,
            "MSFT": 350.0,
            "GOOGL": 140.0,
            "AMZN": 130.0,
            "META": 450.0,
            "TSLA": 180.0,
            "NVDA": 850.0
        }
        
        # 기본 가격 설정
        base_price = base_prices.get(symbol, 100.0)
        
        # 날짜 범위 설정
        end_date = datetime.now()
        
        # 결과 저장
        result = []
        
        # 현재 가격
        current_price = base_price
        
        # 일별 데이터 생성
        for i in range(days, 0, -1):
            date = end_date - timedelta(days=i)
            
            # 주말 건너뛰기
            if date.weekday() >= 5:  # 5: 토요일, 6: 일요일
                continue
            
            # 가격 변동 (-2% ~ +2%)
            change_pct = (random.random() * 4) - 2
            current_price = current_price * (1 + change_pct / 100)
            
            # 일중 변동폭
            daily_range = current_price * 0.02
            
            # 데이터 생성
            data = {
                "date": date.strftime("%Y-%m-%d"),
                "open": round(current_price - (daily_range * random.random() * 0.5), 2),
                "high": round(current_price + (daily_range * random.random()), 2),
                "low": round(current_price - (daily_range * random.random()), 2),
                "close": round(current_price, 2),
                "volume": int(random.random() * 10000000) + 1000000
            }
            
            result.append(data)
        
        return result
    
    def save_correlation_chart(self, symbol, correlation):
        """상관계수 차트 생성 및 저장"""
        # 상관계수 데이터
        corr_data = correlation.get('correlation', {})
        if not corr_data:
            return
        
        # 차트 생성
        plt.figure(figsize=(10, 6))
        
        periods = ['same_day', 'next_day', 'next_3_days', 'next_week']
        period_labels = ['Same Day', 'Next Day', '3 Days Later', '1 Week Later']
        values = [corr_data.get(p, 0) for p in periods]
        
        # 막대 색상 설정 (양수: 파란색, 음수: 빨간색)
        colors = ['blue' if v >= 0 else 'red' for v in values]
        
        plt.bar(period_labels, values, color=colors)
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        plt.title(f'{symbol} News Sentiment and Stock Price Correlation', fontsize=14)
        plt.ylabel('Correlation Coefficient', fontsize=12)
        plt.ylim(-1, 1)
        plt.grid(axis='y', alpha=0.3)
        
        # 결과 저장
        file_path = os.path.join(self.results_dir, f"{symbol}_correlation_chart.png")
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"상관계수 차트가 저장되었습니다: {file_path}")
    
    def save_sentiment_impact_chart(self, symbol, correlation):
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
        period_labels = ['Same Day', 'Next Day', '3 Days Later', '1 Week Later']
        
        # 막대 위치 설정
        x = np.arange(len(sentiment_order))
        width = 0.2
        
        # 각 기간별 막대 그래프
        for i, period in enumerate(periods):
            plt.bar(x + (i - 1.5) * width, impact_df[period], width, label=period_labels[i])
        
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.title(f'{symbol} Sentiment Group Impact on Stock Price', fontsize=14)
        plt.xlabel('Sentiment Group', fontsize=12)
        plt.ylabel('Average Price Change (%)', fontsize=12)
        plt.xticks(x, ['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive'])
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        # 결과 저장
        file_path = os.path.join(self.results_dir, f"{symbol}_sentiment_impact_chart.png")
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"감성 영향 차트가 저장되었습니다: {file_path}")
    
    def save_patterns_chart(self, symbol, patterns):
        """패턴 차트 생성 및 저장"""
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
        
        # 차트 생성
        plt.figure(figsize=(12, 8))
        
        periods = ['next_day', 'next_3_days', 'next_week']
        period_labels = ['Next Day', '3 Days Later', '1 Week Later']
        
        # 막대 위치 설정
        x = np.arange(len(pattern_df))
        width = 0.25
        
        # 각 기간별 막대 그래프
        for i, period in enumerate(periods):
            plt.bar(x + (i - 1) * width, pattern_df[period], width, label=period_labels[i])
        
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.title(f'{symbol} Sentiment Pattern Impact on Stock Price', fontsize=14)
        plt.xlabel('Sentiment Pattern', fontsize=12)
        plt.ylabel('Average Price Change (%)', fontsize=12)
        plt.xticks(x, pattern_df['description'], rotation=45, ha='right')
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        # 결과 저장
        file_path = os.path.join(self.results_dir, f"{symbol}_patterns_chart.png")
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"패턴 차트가 저장되었습니다: {file_path}")
    
    def save_insights_json(self, symbol, insights):
        """인사이트 JSON 저장"""
        if not insights:
            return
        
        # 결과 저장
        file_path = os.path.join(self.results_dir, f"{symbol}_insights.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)
        
        logger.info(f"인사이트 JSON이 저장되었습니다: {file_path}")

def main():
    """메인 함수"""
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description='모의 뉴스 감성과 주가 상관관계 분석')
    parser.add_argument('--symbols', type=str, nargs='+', default=['AAPL', 'MSFT', 'GOOGL'],
                        help='분석할 주식 심볼 목록 (기본값: AAPL MSFT GOOGL)')
    
    args = parser.parse_args()
    
    # 분석기 초기화
    analyzer = MockSentimentAnalyzer()
    
    # 각 심볼 분석
    for symbol in args.symbols:
        logger.info(f"{symbol} 분석 시작...")
        
        # 상관관계 분석
        correlation = analyzer.analyze_correlation(symbol)
        
        # 패턴 식별
        patterns = analyzer.identify_patterns(symbol)
        
        # 인사이트 보고서
        insights = analyzer.generate_insights(symbol)
        
        # 결과 출력
        print(f"\n{symbol} 분석 결과:")
        print(f"기간: {correlation.get('period', '')}")
        print(f"데이터 포인트: {correlation.get('data_points', 0)}")
        
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
        analyzer.save_correlation_chart(symbol, correlation)
        analyzer.save_sentiment_impact_chart(symbol, correlation)
        analyzer.save_patterns_chart(symbol, patterns)
        analyzer.save_insights_json(symbol, insights)
        
        logger.info(f"{symbol} 분석 완료")
    
    print(f"\n분석 결과가 {os.path.abspath(analyzer.results_dir)} 디렉토리에 저장되었습니다.")

if __name__ == "__main__":
    main()
