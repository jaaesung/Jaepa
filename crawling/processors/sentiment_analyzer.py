"""
감성 분석 모듈

금융 뉴스의 감성을 분석하고 신뢰도를 계산하는 기능을 제공합니다.
"""
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import numpy as np
from sklearn.metrics import precision_recall_fscore_support
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
env_path = Path(__file__).parents[2] / '.env'
load_dotenv(dotenv_path=env_path)


class FinancialSentimentAnalyzer:
    """
    금융 감성 분석 클래스
    
    금융 뉴스와 텍스트의 감성을 분석하고 신뢰도를 계산합니다.
    """
    
    def __init__(self, model_name: str = None):
        """
        FinancialSentimentAnalyzer 클래스 초기화
        
        Args:
            model_name: 사용할 모델 이름 (기본값: 환경 변수에서 가져옴)
        """
        # 모델 이름 설정
        if model_name is None:
            self.model_name = os.getenv("FINBERT_MODEL_PATH", "yiyanghkust/finbert-tone")
        else:
            self.model_name = model_name
        
        self.labels = ["negative", "neutral", "positive"]
        self.confidence_threshold = 0.7  # 높은 신뢰도를 위한 임계값
        
        # 모델 로드
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            
            # GPU 사용 가능 시 GPU로 모델 이동
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            logger.info(f"감성 분석 모델 로드 완료: {self.model_name} (장치: {self.device})")
        except Exception as e:
            logger.error(f"감성 분석 모델 로드 실패: {str(e)}")
            self.tokenizer = None
            self.model = None
    
    def analyze(self, text: str) -> Optional[Dict[str, Any]]:
        """
        텍스트 감성 분석
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            Optional[Dict[str, Any]]: 감성 분석 결과 또는 None (실패 시)
        """
        if not self.model or not self.tokenizer:
            logger.error("감성 분석 모델이 초기화되지 않았습니다.")
            return None
        
        try:
            # 텍스트 전처리
            if not text or len(text.strip()) == 0:
                logger.warning("분석할 텍스트가 비어있습니다.")
                return None
            
            # 텍스트가 너무 길면 첫 부분만 사용
            text_chunk = text[:1024]
            
            # 토큰화
            inputs = self.tokenizer(
                text_chunk,
                return_tensors="pt",
                truncation=True,
                padding=True
            )
            inputs = {key: val.to(self.device) for key, val in inputs.items()}
            
            # 모델 추론
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # 소프트맥스로 클래스별 확률 계산
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
            probabilities = probabilities[0].cpu().numpy()
            
            # 결과 사전 생성
            result = {
                "text_sample": text_chunk[:100] + "...",  # 분석된 텍스트 샘플
                "scores": {
                    self.labels[i]: float(probabilities[i])
                    for i in range(len(self.labels))
                },
                "sentiment": self.labels[np.argmax(probabilities)],  # 가장 높은 감성
                "confidence": float(np.max(probabilities)),  # 신뢰도 (최대 확률)
                "is_reliable": float(np.max(probabilities)) >= self.confidence_threshold  # 신뢰도 임계값 기반 판단
            }
            
            return result
        
        except Exception as e:
            logger.error(f"감성 분석 중 오류: {str(e)}")
            return None
    
    def analyze_batch(self, texts: List[str], batch_size: int = 16) -> List[Optional[Dict[str, Any]]]:
        """
        여러 텍스트 배치 감성 분석
        
        Args:
            texts: 분석할 텍스트 목록
            batch_size: 배치 크기
            
        Returns:
            List[Optional[Dict[str, Any]]]: 각 텍스트의 감성 분석 결과 목록
        """
        if not self.model or not self.tokenizer:
            logger.error("감성 분석 모델이 초기화되지 않았습니다.")
            return [None] * len(texts)
        
        results = []
        
        # 배치 단위로 처리
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_results = []
            
            # 유효한 텍스트만 필터링
            valid_texts = []
            valid_indices = []
            
            for j, text in enumerate(batch_texts):
                if text and len(text.strip()) > 0:
                    # 텍스트가 너무 길면 첫 부분만 사용
                    valid_texts.append(text[:1024])
                    valid_indices.append(j)
                else:
                    batch_results.append(None)
            
            if not valid_texts:
                results.extend(batch_results)
                continue
                
            try:
                # 토큰화
                inputs = self.tokenizer(
                    valid_texts,
                    return_tensors="pt",
                    truncation=True,
                    padding=True
                )
                inputs = {key: val.to(self.device) for key, val in inputs.items()}
                
                # 모델 추론
                with torch.no_grad():
                    outputs = self.model(**inputs)
                
                # 소프트맥스로 클래스별 확률 계산
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
                probabilities = probabilities.cpu().numpy()
                
                # 결과 사전 생성
                for j, (idx, text) in enumerate(zip(valid_indices, valid_texts)):
                    result = {
                        "text_sample": text[:100] + "...",
                        "scores": {
                            self.labels[k]: float(probabilities[j][k])
                            for k in range(len(self.labels))
                        },
                        "sentiment": self.labels[np.argmax(probabilities[j])],
                        "confidence": float(np.max(probabilities[j])),
                        "is_reliable": float(np.max(probabilities[j])) >= self.confidence_threshold
                    }
                    
                    # 원래 인덱스에 결과 배치
                    while len(batch_results) <= idx:
                        batch_results.append(None)
                    batch_results[idx] = result
                
                # 결과 리스트에 추가
                results.extend(batch_results)
                
            except Exception as e:
                logger.error(f"배치 감성 분석 중 오류: {str(e)}")
                # 오류 발생 시 None으로 채움
                results.extend([None] * len(batch_texts))
        
        return results
    
    def analyze_with_context(self, text: str, headline: str = None) -> Optional[Dict[str, Any]]:
        """
        헤드라인과 문맥을 함께 고려한 감성 분석
        
        Args:
            text: 분석할 본문 텍스트
            headline: 헤드라인 텍스트 (선택 사항)
            
        Returns:
            Optional[Dict[str, Any]]: 감성 분석 결과 또는 None (실패 시)
        """
        if not text or len(text.strip()) == 0:
            logger.warning("분석할 텍스트가 비어있습니다.")
            return None
            
        # 헤드라인이 있는 경우 함께 분석
        if headline and len(headline.strip()) > 0:
            # 헤드라인 분석
            headline_result = self.analyze(headline)
            
            # 본문 분석
            content_result = self.analyze(text)
            
            if headline_result and content_result:
                # 헤드라인과 본문의 감성 점수 가중 평균 계산 (헤드라인에 더 높은 가중치)
                headline_weight = 0.6
                content_weight = 0.4
                
                combined_scores = {}
                for label in self.labels:
                    combined_scores[label] = (
                        headline_weight * headline_result["scores"][label] +
                        content_weight * content_result["scores"][label]
                    )
                
                # 가장 높은 감성 및 신뢰도 계산
                sentiment = max(combined_scores, key=combined_scores.get)
                confidence = combined_scores[sentiment]
                
                return {
                    "headline_sentiment": headline_result["sentiment"],
                    "content_sentiment": content_result["sentiment"],
                    "scores": combined_scores,
                    "sentiment": sentiment,
                    "confidence": confidence,
                    "is_reliable": confidence >= self.confidence_threshold
                }
            elif headline_result:
                # 본문 분석 실패 시 헤드라인만 사용
                return headline_result
            elif content_result:
                # 헤드라인 분석 실패 시 본문만 사용
                return content_result
            else:
                return None
        else:
            # 헤드라인이 없는 경우 본문만 분석
            return self.analyze(text)
    
    def validate(self, texts: List[str], ground_truth: List[str]) -> Dict[str, Any]:
        """
        감성 분석 모델 성능 평가
        
        Args:
            texts: 분석할 텍스트 목록
            ground_truth: 실제 레이블 목록 (negative, neutral, positive)
            
        Returns:
            Dict[str, Any]: 성능 평가 결과
        """
        if not all(label in self.labels for label in ground_truth):
            logger.error("유효하지 않은 레이블이 포함되어 있습니다.")
            return {
                "error": "유효하지 않은 레이블이 포함되어 있습니다.",
                "valid_labels": self.labels
            }
        
        # 예측 수행
        predictions = []
        confidences = []
        
        for text in texts:
            result = self.analyze(text)
            if result:
                predictions.append(result["sentiment"])
                confidences.append(result["confidence"])
            else:
                predictions.append("neutral")  # 실패 시 중립으로 기본 설정
                confidences.append(0.0)
        
        # 성능 평가
        precision, recall, f1, _ = precision_recall_fscore_support(
            ground_truth, predictions, labels=self.labels, average=None
        )
        
        # 클래스별 성능
        class_performance = {
            label: {
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1": float(f1[i])
            }
            for i, label in enumerate(self.labels)
        }
        
        # 신뢰도 통계
        confidence_stats = {
            "mean": float(np.mean(confidences)),
            "min": float(np.min(confidences)),
            "max": float(np.max(confidences)),
            "median": float(np.median(confidences))
        }
        
        # 전체 성능
        macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
            ground_truth, predictions, labels=self.labels, average="macro"
        )
        
        overall_performance = {
            "precision": float(macro_precision),
            "recall": float(macro_recall),
            "f1": float(macro_f1),
            "accuracy": float(np.mean(np.array(ground_truth) == np.array(predictions)))
        }
        
        return {
            "overall": overall_performance,
            "class_performance": class_performance,
            "confidence_stats": confidence_stats
        }


class SentimentAnalysisResultValidator:
    """
    감성 분석 결과 검증 클래스
    
    감성 분석 결과의 일관성과 신뢰성을 검증합니다.
    """
    
    def __init__(self, analyzer: FinancialSentimentAnalyzer = None):
        """
        SentimentAnalysisResultValidator 클래스 초기화
        
        Args:
            analyzer: 사용할 감성 분석기 (None인 경우 새로 생성)
        """
        if analyzer:
            self.analyzer = analyzer
        else:
            self.analyzer = FinancialSentimentAnalyzer()
    
    def validate_consistency(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        기사 감성 일관성 검증
        
        Args:
            article: 검증할 기사 데이터
            
        Returns:
            Dict[str, Any]: 검증 결과
        """
        if not article or "title" not in article or "content" not in article:
            return {
                "is_consistent": False,
                "error": "유효하지 않은 기사 데이터"
            }
        
        # 제목과 내용 감성 분석
        title_analysis = self.analyzer.analyze(article["title"])
        content_analysis = self.analyzer.analyze(article["content"])
        
        if not title_analysis or not content_analysis:
            return {
                "is_consistent": False,
                "error": "감성 분석 실패"
            }
        
        # 제목과 내용의 감성이 일치하는지 확인
        is_consistent = title_analysis["sentiment"] == content_analysis["sentiment"]
        
        # 신뢰도 확인
        is_reliable = title_analysis["is_reliable"] and content_analysis["is_reliable"]
        
        return {
            "is_consistent": is_consistent,
            "is_reliable": is_reliable,
            "title_sentiment": title_analysis["sentiment"],
            "content_sentiment": content_analysis["sentiment"],
            "title_confidence": title_analysis["confidence"],
            "content_confidence": content_analysis["confidence"]
        }
    
    def validate_batch(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        여러 기사 감성 일관성 일괄 검증
        
        Args:
            articles: 검증할 기사 데이터 목록
            
        Returns:
            Dict[str, Any]: 검증 결과 요약
        """
        results = []
        consistent_count = 0
        reliable_count = 0
        
        for article in articles:
            result = self.validate_consistency(article)
            results.append(result)
            
            if result.get("is_consistent", False):
                consistent_count += 1
            if result.get("is_reliable", False):
                reliable_count += 1
        
        # 일관성 및 신뢰도 비율 계산
        total = len(articles)
        consistency_ratio = consistent_count / total if total > 0 else 0
        reliability_ratio = reliable_count / total if total > 0 else 0
        
        # 감성 분포 계산
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        for result in results:
            if "content_sentiment" in result:
                sentiment_counts[result["content_sentiment"]] += 1
        
        sentiment_distribution = {
            sentiment: count / total if total > 0 else 0
            for sentiment, count in sentiment_counts.items()
        }
        
        return {
            "total_articles": total,
            "consistent_count": consistent_count,
            "reliable_count": reliable_count,
            "consistency_ratio": consistency_ratio,
            "reliability_ratio": reliability_ratio,
            "sentiment_distribution": sentiment_distribution,
            "detailed_results": results
        }


if __name__ == "__main__":
    # 간단한 사용 예시
    analyzer = FinancialSentimentAnalyzer()
    
    # 테스트 텍스트
    positive_text = "The company reported strong earnings growth, exceeding market expectations. Investors responded positively to the news."
    negative_text = "The stock plummeted after the company announced disappointing quarterly results, falling short of analyst estimates."
    neutral_text = "The market remained steady today as investors await the Federal Reserve's decision on interest rates."
    
    # 감성 분석
    print("긍정 텍스트 분석:")
    print(json.dumps(analyzer.analyze(positive_text), indent=2))
    
    print("\n부정 텍스트 분석:")
    print(json.dumps(analyzer.analyze(negative_text), indent=2))
    
    print("\n중립 텍스트 분석:")
    print(json.dumps(analyzer.analyze(neutral_text), indent=2))
