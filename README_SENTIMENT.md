# 제파(JaePa) 감성 분석 모듈

이 모듈은 제파(JaePa) 프로젝트의 감성 분석 기능을 제공합니다. FinBERT 모델을 기반으로 금융 텍스트의 감성을 분석하고, 다양한 개선 및 검증 기능을 제공합니다.

## 주요 기능

- **금융 특화 감성 분석**: FinBERT 모델을 사용하여 금융 도메인에 특화된 감성 분석 제공
- **성능 최적화**: 모델 로딩 지연, 배치 처리 최적화, GPU 메모리 효율적 사용
- **정확도 개선**: 금융 용어 사전, 키워드 가중치, 결과 후처리를 통한 정확도 향상
- **다양한 분석 기능**: 텍스트, 뉴스 기사, 트렌드 분석 등 다양한 분석 기능 제공
- **확장성**: 다양한 모델 지원, 모듈식 설계, 파이프라인 커스터마이징 지원

## 구조

```
core/analyzer/
  ├── __init__.py                    # 패키지 초기화 파일
  ├── sentiment_analyzer_interface.py # 감성 분석기 인터페이스
  ├── sentiment_pipeline.py          # 감성 분석 파이프라인
  ├── finbert_analyzer.py            # FinBERT 감성 분석기
  └── sentiment_enhancer.py          # 감성 분석 결과 개선 및 검증

tests/analyzer/
  ├── __init__.py                    # 테스트 패키지 초기화 파일
  └── test_sentiment.py              # 감성 분석 테스트

examples/
  └── sentiment_analyzer_example.py  # 감성 분석기 사용 예제
```

## 설치

1. 필요한 패키지 설치:

```bash
pip install transformers torch numpy pandas
```

2. 추가 리소스 다운로드 (선택 사항):

```bash
# 금융 용어 사전 및 키워드 가중치 파일 다운로드
mkdir -p resources
curl -o resources/financial_terms.json https://example.com/financial_terms.json
curl -o resources/keyword_weights.json https://example.com/keyword_weights.json
```

## 사용 방법

### 기본 사용법

```python
from core.analyzer import FinBertSentimentAnalyzer

# 감성 분석기 생성
analyzer = FinBertSentimentAnalyzer()

# 텍스트 분석
result = analyzer.analyze("The company reported strong earnings, exceeding analyst expectations.")
print(f"감성: {result['label']}")
print(f"점수: {result['score']}")
print(f"신뢰도: {result['confidence']}")

# 배치 분석
texts = [
    "The company reported strong earnings, exceeding analyst expectations.",
    "The stock price plummeted after the company announced a significant loss.",
    "The market remained stable throughout the trading session."
]
results = analyzer.analyze_batch(texts)
```

### 뉴스 기사 분석

```python
from core.analyzer import FinBertSentimentAnalyzer

# 감성 분석기 생성
analyzer = FinBertSentimentAnalyzer()

# 뉴스 기사 분석
news = {
    "title": "Tech Giant Reports Record Profits",
    "content": "The leading technology company announced record-breaking quarterly profits today, exceeding analyst expectations by 15%."
}
result = analyzer.analyze_news(news)

# 여러 뉴스 기사 분석
news_list = [news1, news2, news3]
results = analyzer.analyze_news_batch(news_list)

# 감성 트렌드 분석
trend = analyzer.get_sentiment_trend(results, interval='day')
```

### 감성 분석 결과 개선

```python
from core.analyzer import FinBertSentimentAnalyzer, SentimentEnhancer

# 감성 분석기 생성
analyzer = FinBertSentimentAnalyzer()

# 감성 개선기 생성
enhancer = SentimentEnhancer(
    financial_terms_path="resources/financial_terms.json",
    keyword_weights_path="resources/keyword_weights.json"
)

# 텍스트 분석
text = "The company's performance was acceptable, but not exceptional."
result = analyzer.analyze(text)

# 결과 개선
enhanced = enhancer.enhance_result(result, text)
```

### 감성 분석 결과 검증

```python
from core.analyzer import FinBertSentimentAnalyzer, SentimentValidator

# 감성 분석기 생성
analyzer = FinBertSentimentAnalyzer()

# 감성 검증기 생성
validator = SentimentValidator(
    analyzer=analyzer,
    confidence_threshold=0.6,
    consistency_threshold=0.5
)

# 뉴스 기사 일관성 검증
article = {
    "title": "Tech Giant Reports Record Profits",
    "content": "The leading technology company announced record-breaking quarterly profits today."
}
validation = validator.validate_consistency(article)

# 여러 기사 검증
articles = [article1, article2, article3]
batch_validation = validator.validate_batch(articles)
```

### 감성 분석 앙상블

```python
from core.analyzer import FinBertSentimentAnalyzer, SentimentEnsemble

# 여러 감성 분석기 생성
analyzer1 = FinBertSentimentAnalyzer(model_name="yiyanghkust/finbert-tone")
analyzer2 = FinBertSentimentAnalyzer(model_name="ProsusAI/finbert")

# 앙상블 생성
ensemble = SentimentEnsemble(
    analyzers=[analyzer1, analyzer2],
    weights=[0.7, 0.3]
)

# 텍스트 분석
result = ensemble.analyze("The company reported strong earnings.")
```

### 파이프라인 커스터마이징

```python
from core.analyzer import (
    SentimentPipeline, TextPreprocessor, ModelInferenceStage, PostProcessorStage,
    FinBertSentimentAnalyzer
)

# 감성 분석기 생성
analyzer = FinBertSentimentAnalyzer(use_pipeline=False)

# 커스텀 파이프라인 구성
preprocessor = TextPreprocessor(
    remove_urls=True,
    remove_html_tags=True,
    financial_terms_path="resources/financial_terms.json"
)

inference_stage = ModelInferenceStage(
    model_callable=analyzer._model_inference
)

postprocessor = PostProcessorStage(
    confidence_threshold=0.7,
    apply_keyword_weights=True,
    keyword_weights_path="resources/keyword_weights.json"
)

pipeline = SentimentPipeline(
    preprocessor=preprocessor,
    inference_stage=inference_stage,
    postprocessor=postprocessor
)

# 파이프라인으로 분석
result = pipeline.process("The company reported strong earnings.")
```

## 예제 실행

```bash
python examples/sentiment_analyzer_example.py
```

## 테스트 실행

```bash
# 모든 테스트 실행
pytest tests/analyzer/

# 특정 테스트 실행
pytest tests/analyzer/test_sentiment.py::TestFinBertSentimentAnalyzer
```

## 성능 최적화

### 모델 로딩 최적화

- **지연 로딩**: 필요할 때만 모델을 로드하여 초기화 시간 단축
- **모델 캐싱**: 한 번 로드한 모델을 재사용하여 메모리 효율성 향상

```python
# 지연 로딩 사용
analyzer = FinBertSentimentAnalyzer(lazy_loading=True)
```

### 배치 처리 최적화

- **동적 배치 크기**: 텍스트 길이와 가용 메모리에 따라 배치 크기 자동 조정
- **병렬 처리**: 여러 텍스트를 동시에 처리하여 처리 속도 향상

```python
# 배치 크기 지정
results = analyzer.analyze_batch(texts, batch_size=16)
```

### GPU 메모리 최적화

- **메모리 효율적 추론**: 필요한 만큼만 GPU 메모리 사용
- **그래디언트 비활성화**: 추론 시 그래디언트 계산 비활성화로 메모리 사용량 감소

```python
# CPU 사용
analyzer = FinBertSentimentAnalyzer(device="cpu")

# GPU 사용
analyzer = FinBertSentimentAnalyzer(device="cuda")
```

## 정확도 개선

### 금융 용어 처리

- **금융 용어 사전**: 금융 특화 용어를 인식하고 적절히 처리
- **용어 정규화**: 동일한 의미의 다양한 표현을 통일된 형태로 변환

### 키워드 가중치

- **감성 키워드 가중치**: 특정 키워드에 가중치를 부여하여 감성 점수 조정
- **도메인 특화 규칙**: 금융 도메인에 특화된 규칙 적용

### 결과 검증

- **신뢰도 점수**: 분석 결과의 신뢰도를 계산하여 제공
- **일관성 검증**: 제목과 내용의 감성 일관성 검증

## 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다.
