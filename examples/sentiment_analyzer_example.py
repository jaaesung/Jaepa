"""
감성 분석기 사용 예제

개선된 감성 분석 모듈의 사용 방법을 보여줍니다.
"""
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(str(Path(__file__).parents[1]))

from core.analyzer import (
    FinBertSentimentAnalyzer, SentimentEnhancer, SentimentValidator, SentimentEnsemble
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_text_example():
    """텍스트 감성 분석 예제"""
    logger.info("=== 텍스트 감성 분석 예제 ===")
    
    # 감성 분석기 생성
    analyzer = FinBertSentimentAnalyzer(
        lazy_loading=True,  # 지연 로딩 사용
        use_pipeline=True   # 파이프라인 사용
    )
    
    # 분석할 텍스트
    texts = [
        "The company reported strong earnings, exceeding analyst expectations.",
        "The stock price plummeted after the company announced a significant loss.",
        "The market remained stable throughout the trading session."
    ]
    
    # 개별 텍스트 분석
    logger.info("개별 텍스트 분석:")
    for text in texts:
        result = analyzer.analyze(text)
        logger.info(f"텍스트: {text}")
        logger.info(f"감성: {result['label']}")
        logger.info(f"점수: {result['score']:.4f}")
        logger.info(f"신뢰도: {result['confidence']:.4f}")
        logger.info(f"점수 분포: {json.dumps(result['scores'], indent=2)}")
        logger.info("---")
    
    # 배치 분석
    logger.info("배치 분석:")
    results = analyzer.analyze_batch(texts)
    for i, result in enumerate(results):
        logger.info(f"텍스트 #{i+1}: {texts[i]}")
        logger.info(f"감성: {result['label']}")
        logger.info(f"점수: {result['score']:.4f}")
        logger.info(f"신뢰도: {result['confidence']:.4f}")
        logger.info("---")
    
    # 모델 정보 출력
    model_info = analyzer.get_model_info()
    logger.info(f"모델 정보: {json.dumps(model_info, indent=2)}")


def analyze_news_example():
    """뉴스 기사 감성 분석 예제"""
    logger.info("=== 뉴스 기사 감성 분석 예제 ===")
    
    # 감성 분석기 생성
    analyzer = FinBertSentimentAnalyzer(
        lazy_loading=True,
        use_pipeline=True
    )
    
    # 샘플 뉴스 기사
    news_articles = [
        {
            "title": "Tech Giant Reports Record Profits",
            "content": "The leading technology company announced record-breaking quarterly profits today, exceeding analyst expectations by 15%. The company's stock price surged following the announcement.",
            "published_date": datetime.now().isoformat(),
            "source": "Financial News"
        },
        {
            "title": "Market Downturn Continues",
            "content": "Global markets experienced another day of losses as concerns about inflation and interest rates continue to weigh on investor sentiment. Major indices fell by an average of 2%.",
            "published_date": datetime.now().isoformat(),
            "source": "Market Watch"
        },
        {
            "title": "Central Bank Maintains Interest Rates",
            "content": "The central bank decided to maintain current interest rates at its monthly meeting, citing balanced risks to the economic outlook. Analysts had widely expected this decision.",
            "published_date": datetime.now().isoformat(),
            "source": "Economic Times"
        }
    ]
    
    # 뉴스 기사 분석
    logger.info("뉴스 기사 분석:")
    for article in news_articles:
        result = analyzer.analyze_news(article)
        logger.info(f"제목: {result['title']}")
        logger.info(f"감성: {result['sentiment']['label']}")
        logger.info(f"점수: {result['sentiment']['score']:.4f}")
        logger.info(f"신뢰도: {result['sentiment']['confidence']:.4f}")
        logger.info("---")
    
    # 뉴스 기사 배치 분석
    logger.info("뉴스 기사 배치 분석:")
    results = analyzer.analyze_news_batch(news_articles)
    
    # 감성 트렌드 분석
    logger.info("감성 트렌드 분석:")
    trend = analyzer.get_sentiment_trend(results)
    logger.info(f"평균 감성 점수: {trend['summary']['average_score']:.4f}")
    logger.info(f"긍정 비율: {trend['summary']['positive_ratio']:.2%}")
    logger.info(f"부정 비율: {trend['summary']['negative_ratio']:.2%}")
    logger.info(f"중립 비율: {trend['summary']['neutral_ratio']:.2%}")
    logger.info(f"기사 수: {trend['summary']['article_count']}")


def sentiment_enhancer_example():
    """감성 분석 결과 개선 예제"""
    logger.info("=== 감성 분석 결과 개선 예제 ===")
    
    # 감성 분석기 생성
    analyzer = FinBertSentimentAnalyzer(
        lazy_loading=True,
        use_pipeline=True
    )
    
    # 감성 개선기 생성
    enhancer = SentimentEnhancer()
    
    # 분석할 텍스트
    texts = [
        "The company's performance was acceptable, but not exceptional.",
        "The stock showed a slight increase after the earnings report.",
        "Investors are cautiously optimistic about the company's future prospects."
    ]
    
    # 원본 분석 및 개선
    logger.info("원본 분석 및 개선:")
    for text in texts:
        # 원본 분석
        original = analyzer.analyze(text)
        
        # 결과 개선
        enhanced = enhancer.enhance_result(original, text)
        
        logger.info(f"텍스트: {text}")
        logger.info(f"원본 감성: {original['label']}")
        logger.info(f"원본 점수: {original['score']:.4f}")
        logger.info(f"개선 감성: {enhanced['label']}")
        logger.info(f"개선 점수: {enhanced['score']:.4f}")
        logger.info("---")


def sentiment_validator_example():
    """감성 분석 결과 검증 예제"""
    logger.info("=== 감성 분석 결과 검증 예제 ===")
    
    # 감성 분석기 생성
    analyzer = FinBertSentimentAnalyzer(
        lazy_loading=True,
        use_pipeline=True
    )
    
    # 감성 검증기 생성
    validator = SentimentValidator(
        analyzer=analyzer,
        confidence_threshold=0.6,
        consistency_threshold=0.5
    )
    
    # 샘플 뉴스 기사
    news_articles = [
        {
            "title": "Tech Giant Reports Record Profits",
            "content": "The leading technology company announced record-breaking quarterly profits today, exceeding analyst expectations by 15%. The company's stock price surged following the announcement."
        },
        {
            "title": "Market Downturn Continues",
            "content": "Global markets experienced another day of losses as concerns about inflation and interest rates continue to weigh on investor sentiment. Major indices fell by an average of 2%."
        },
        {
            "title": "Positive Outlook Despite Challenges",
            "content": "The company faced significant challenges this quarter, with revenue declining by 5%. However, cost-cutting measures helped maintain profitability."
        }
    ]
    
    # 일관성 검증
    logger.info("일관성 검증:")
    for article in news_articles:
        result = validator.validate_consistency(article)
        logger.info(f"제목: {article['title']}")
        logger.info(f"일관성 여부: {result['is_consistent']}")
        logger.info(f"신뢰성 여부: {result['is_reliable']}")
        logger.info(f"제목 감성: {result['title_sentiment']}")
        logger.info(f"내용 감성: {result['content_sentiment']}")
        logger.info(f"일관성 점수: {result.get('consistency_score', 0):.4f}")
        logger.info("---")
    
    # 배치 검증
    logger.info("배치 검증:")
    batch_result = validator.validate_batch(news_articles)
    logger.info(f"전체 기사 수: {batch_result['total_articles']}")
    logger.info(f"일관성 있는 기사 수: {batch_result['consistent_count']}")
    logger.info(f"신뢰성 있는 기사 수: {batch_result['reliable_count']}")
    logger.info(f"일관성 비율: {batch_result['consistency_ratio']:.2%}")
    logger.info(f"신뢰성 비율: {batch_result['reliability_ratio']:.2%}")
    logger.info(f"감성 분포: {json.dumps(batch_result['sentiment_distribution'], indent=2)}")


def sentiment_ensemble_example():
    """감성 분석 앙상블 예제"""
    logger.info("=== 감성 분석 앙상블 예제 ===")
    
    # 첫 번째 감성 분석기 생성 (FinBERT)
    analyzer1 = FinBertSentimentAnalyzer(
        model_name="yiyanghkust/finbert-tone",
        lazy_loading=True,
        use_pipeline=True
    )
    
    # 두 번째 감성 분석기 생성 (다른 모델을 사용할 수 있지만, 예제에서는 같은 모델 사용)
    analyzer2 = FinBertSentimentAnalyzer(
        model_name="yiyanghkust/finbert-tone",
        lazy_loading=True,
        use_pipeline=False  # 파이프라인 사용하지 않음
    )
    
    # 앙상블 생성
    ensemble = SentimentEnsemble(
        analyzers=[analyzer1, analyzer2],
        weights=[0.7, 0.3]  # 첫 번째 모델에 더 높은 가중치 부여
    )
    
    # 분석할 텍스트
    texts = [
        "The company reported strong earnings, exceeding analyst expectations.",
        "The stock price plummeted after the company announced a significant loss.",
        "The market remained stable throughout the trading session."
    ]
    
    # 앙상블 분석
    logger.info("앙상블 분석:")
    for text in texts:
        result = ensemble.analyze(text)
        logger.info(f"텍스트: {text}")
        logger.info(f"앙상블 감성: {result['label']}")
        logger.info(f"앙상블 점수: {result['score']:.4f}")
        logger.info(f"앙상블 신뢰도: {result['confidence']:.4f}")
        logger.info(f"모델 감성: {result['metadata']['model_labels']}")
        logger.info(f"모델 신뢰도: {[f'{c:.4f}' for c in result['metadata']['model_confidences']]}")
        logger.info("---")


def main():
    """메인 함수"""
    # 텍스트 감성 분석 예제
    analyze_text_example()
    
    # 뉴스 기사 감성 분석 예제
    analyze_news_example()
    
    # 감성 분석 결과 개선 예제
    sentiment_enhancer_example()
    
    # 감성 분석 결과 검증 예제
    sentiment_validator_example()
    
    # 감성 분석 앙상블 예제
    sentiment_ensemble_example()


if __name__ == "__main__":
    main()
