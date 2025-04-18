"""
감성 분석 결과 개선 및 검증 모듈

감성 분석 결과의 정확도를 높이고 신뢰성을 검증하는 기능을 제공합니다.
"""
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from pathlib import Path
from collections import defaultdict

import numpy as np
from dotenv import load_dotenv

from core.analyzer.sentiment_analyzer_interface import SentimentAnalyzerInterface, SentimentAnalysisResult

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
env_path = Path(__file__).parents[2] / '.env'
load_dotenv(dotenv_path=env_path)


class SentimentEnhancer:
    """
    감성 분석 결과 개선 클래스
    
    감성 분석 결과의 정확도를 높이는 다양한 기법을 제공합니다.
    """
    
    def __init__(self, 
                financial_terms_path: Optional[str] = None,
                keyword_weights_path: Optional[str] = None,
                domain_specific_rules_path: Optional[str] = None):
        """
        SentimentEnhancer 초기화
        
        Args:
            financial_terms_path: 금융 용어 사전 파일 경로
            keyword_weights_path: 키워드 가중치 파일 경로
            domain_specific_rules_path: 도메인 특화 규칙 파일 경로
        """
        # 금융 용어 사전 로드
        self.financial_terms = {}
        if financial_terms_path:
            try:
                self._load_financial_terms(financial_terms_path)
                logger.info(f"금융 용어 사전 로드 완료: {len(self.financial_terms)}개 용어")
            except Exception as e:
                logger.error(f"금융 용어 사전 로드 실패: {str(e)}")
        
        # 키워드 가중치 로드
        self.keyword_weights = {}
        if keyword_weights_path:
            try:
                self._load_keyword_weights(keyword_weights_path)
                logger.info(f"키워드 가중치 로드 완료: {len(self.keyword_weights)}개 키워드")
            except Exception as e:
                logger.error(f"키워드 가중치 로드 실패: {str(e)}")
        
        # 도메인 특화 규칙 로드
        self.domain_rules = []
        if domain_specific_rules_path:
            try:
                self._load_domain_rules(domain_specific_rules_path)
                logger.info(f"도메인 특화 규칙 로드 완료: {len(self.domain_rules)}개 규칙")
            except Exception as e:
                logger.error(f"도메인 특화 규칙 로드 실패: {str(e)}")
    
    def enhance_result(self, result: Dict[str, Any], text: str) -> Dict[str, Any]:
        """
        감성 분석 결과 개선
        
        Args:
            result: 원본 감성 분석 결과
            text: 분석된 원본 텍스트
            
        Returns:
            Dict[str, Any]: 개선된 감성 분석 결과
        """
        if not result or not text:
            return result
        
        # 결과 복사
        enhanced = result.copy()
        
        # 키워드 가중치 적용
        enhanced = self._apply_keyword_weights(enhanced, text)
        
        # 도메인 특화 규칙 적용
        enhanced = self._apply_domain_rules(enhanced, text)
        
        # 신뢰도 재계산
        enhanced = self._recalculate_confidence(enhanced)
        
        return enhanced
    
    def enhance_batch(self, results: List[Dict[str, Any]], texts: List[str]) -> List[Dict[str, Any]]:
        """
        여러 감성 분석 결과 개선
        
        Args:
            results: 원본 감성 분석 결과 목록
            texts: 분석된 원본 텍스트 목록
            
        Returns:
            List[Dict[str, Any]]: 개선된 감성 분석 결과 목록
        """
        if not results or not texts or len(results) != len(texts):
            return results
        
        return [self.enhance_result(result, text) for result, text in zip(results, texts)]
    
    def _load_financial_terms(self, file_path: str) -> None:
        """
        금융 용어 사전 로드
        
        Args:
            file_path: 금융 용어 사전 파일 경로
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            self.financial_terms = json.load(f)
    
    def _load_keyword_weights(self, file_path: str) -> None:
        """
        키워드 가중치 로드
        
        Args:
            file_path: 키워드 가중치 파일 경로
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            self.keyword_weights = json.load(f)
    
    def _load_domain_rules(self, file_path: str) -> None:
        """
        도메인 특화 규칙 로드
        
        Args:
            file_path: 도메인 특화 규칙 파일 경로
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            self.domain_rules = json.load(f)
    
    def _apply_keyword_weights(self, result: Dict[str, Any], text: str) -> Dict[str, Any]:
        """
        키워드 가중치 적용
        
        Args:
            result: 감성 분석 결과
            text: 분석된 원본 텍스트
            
        Returns:
            Dict[str, Any]: 가중치가 적용된 감성 분석 결과
        """
        if not self.keyword_weights or not text:
            return result
        
        # 결과 복사
        enhanced = result.copy()
        
        # 점수 복사
        scores = enhanced.get("scores", {}).copy()
        if not scores:
            return enhanced
        
        # 텍스트를 소문자로 변환
        text_lower = text.lower()
        
        # 키워드 가중치 적용
        for keyword, weights in self.keyword_weights.items():
            if keyword.lower() in text_lower:
                for sentiment, weight in weights.items():
                    if sentiment in scores:
                        scores[sentiment] *= weight
        
        # 점수 정규화
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        
        # 가장 높은 점수의 레이블 찾기
        label = max(scores, key=scores.get)
        score = scores[label]
        
        # 결과 업데이트
        enhanced["label"] = label
        enhanced["score"] = score
        enhanced["scores"] = scores
        
        # 메타데이터 추가
        metadata = enhanced.get("metadata", {})
        metadata["enhanced"] = True
        metadata["applied_keywords"] = [
            keyword for keyword in self.keyword_weights
            if keyword.lower() in text_lower
        ]
        enhanced["metadata"] = metadata
        
        return enhanced
    
    def _apply_domain_rules(self, result: Dict[str, Any], text: str) -> Dict[str, Any]:
        """
        도메인 특화 규칙 적용
        
        Args:
            result: 감성 분석 결과
            text: 분석된 원본 텍스트
            
        Returns:
            Dict[str, Any]: 규칙이 적용된 감성 분석 결과
        """
        if not self.domain_rules or not text:
            return result
        
        # 결과 복사
        enhanced = result.copy()
        
        # 텍스트를 소문자로 변환
        text_lower = text.lower()
        
        # 적용된 규칙 추적
        applied_rules = []
        
        # 도메인 규칙 적용
        for rule in self.domain_rules:
            rule_id = rule.get("id", "unknown")
            patterns = rule.get("patterns", [])
            conditions = rule.get("conditions", [])
            actions = rule.get("actions", {})
            
            # 패턴 매칭 확인
            pattern_matched = any(pattern.lower() in text_lower for pattern in patterns)
            
            # 조건 확인
            conditions_met = True
            for condition in conditions:
                field = condition.get("field", "")
                operator = condition.get("operator", "eq")
                value = condition.get("value")
                
                if field and field in enhanced:
                    field_value = enhanced[field]
                    
                    if operator == "eq" and field_value != value:
                        conditions_met = False
                    elif operator == "ne" and field_value == value:
                        conditions_met = False
                    elif operator == "gt" and field_value <= value:
                        conditions_met = False
                    elif operator == "lt" and field_value >= value:
                        conditions_met = False
                    elif operator == "in" and field_value not in value:
                        conditions_met = False
                
                if not conditions_met:
                    break
            
            # 규칙 적용
            if pattern_matched and conditions_met:
                # 레이블 변경
                if "label" in actions:
                    enhanced["label"] = actions["label"]
                
                # 점수 조정
                if "score_adjust" in actions:
                    score_adjustments = actions["score_adjust"]
                    scores = enhanced.get("scores", {}).copy()
                    
                    for sentiment, adjustment in score_adjustments.items():
                        if sentiment in scores:
                            scores[sentiment] *= adjustment
                    
                    # 점수 정규화
                    total = sum(scores.values())
                    if total > 0:
                        scores = {k: v / total for k, v in scores.items()}
                    
                    # 가장 높은 점수의 레이블 찾기
                    label = max(scores, key=scores.get)
                    score = scores[label]
                    
                    enhanced["label"] = label
                    enhanced["score"] = score
                    enhanced["scores"] = scores
                
                # 신뢰도 조정
                if "confidence_adjust" in actions:
                    enhanced["confidence"] = enhanced.get("confidence", 0.0) * actions["confidence_adjust"]
                
                # 적용된 규칙 추가
                applied_rules.append(rule_id)
        
        # 메타데이터 추가
        if applied_rules:
            metadata = enhanced.get("metadata", {})
            metadata["applied_rules"] = applied_rules
            enhanced["metadata"] = metadata
        
        return enhanced
    
    def _recalculate_confidence(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        신뢰도 재계산
        
        Args:
            result: 감성 분석 결과
            
        Returns:
            Dict[str, Any]: 신뢰도가 재계산된 감성 분석 결과
        """
        # 결과 복사
        enhanced = result.copy()
        
        # 점수 확인
        scores = enhanced.get("scores", {})
        if not scores:
            return enhanced
        
        # 레이블 확인
        label = enhanced.get("label", "")
        if not label or label not in scores:
            return enhanced
        
        # 신뢰도 계산
        # 1. 최고 점수와 두 번째 점수의 차이
        sorted_scores = sorted(scores.values(), reverse=True)
        score_diff = sorted_scores[0] - sorted_scores[1] if len(sorted_scores) > 1 else sorted_scores[0]
        
        # 2. 최고 점수의 절대값
        top_score = scores[label]
        
        # 3. 신뢰도 계산 (점수 차이와 최고 점수의 가중 평균)
        confidence = 0.7 * top_score + 0.3 * score_diff
        
        # 신뢰도 업데이트
        enhanced["confidence"] = confidence
        
        return enhanced


class SentimentValidator:
    """
    감성 분석 결과 검증 클래스
    
    감성 분석 결과의 일관성과 신뢰성을 검증합니다.
    """
    
    def __init__(self, 
                analyzer: Optional[SentimentAnalyzerInterface] = None,
                confidence_threshold: float = 0.6,
                consistency_threshold: float = 0.5):
        """
        SentimentValidator 초기화
        
        Args:
            analyzer: 감성 분석기 (None인 경우 검증 시 외부에서 제공)
            confidence_threshold: 신뢰도 임계값
            consistency_threshold: 일관성 임계값
        """
        self.analyzer = analyzer
        self.confidence_threshold = confidence_threshold
        self.consistency_threshold = consistency_threshold
    
    def validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        감성 분석 결과 검증
        
        Args:
            result: 검증할 감성 분석 결과
            
        Returns:
            Dict[str, Any]: 검증 결과
            {
                "is_valid": bool,  # 유효성 여부
                "confidence": float,  # 신뢰도
                "is_reliable": bool,  # 신뢰성 여부
                "issues": List[str]  # 발견된 문제점
            }
        """
        if not result:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "is_reliable": False,
                "issues": ["결과가 비어 있습니다."]
            }
        
        # 검증 결과 초기화
        validation = {
            "is_valid": True,
            "confidence": result.get("confidence", 0.0),
            "is_reliable": False,
            "issues": []
        }
        
        # 필수 필드 확인
        required_fields = ["label", "score", "scores"]
        for field in required_fields:
            if field not in result:
                validation["is_valid"] = False
                validation["issues"].append(f"필수 필드 '{field}'가 없습니다.")
        
        # 유효하지 않은 경우 조기 반환
        if not validation["is_valid"]:
            return validation
        
        # 레이블 확인
        label = result["label"]
        scores = result["scores"]
        
        if label not in scores:
            validation["is_valid"] = False
            validation["issues"].append(f"레이블 '{label}'가 점수에 없습니다.")
            return validation
        
        # 점수 합계 확인
        score_sum = sum(scores.values())
        if abs(score_sum - 1.0) > 0.01:
            validation["issues"].append(f"점수 합계가 1이 아닙니다: {score_sum:.4f}")
        
        # 신뢰도 확인
        confidence = validation["confidence"]
        if confidence < self.confidence_threshold:
            validation["issues"].append(f"신뢰도가 낮습니다: {confidence:.4f} < {self.confidence_threshold:.4f}")
        else:
            validation["is_reliable"] = True
        
        return validation
    
    def validate_consistency(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        기사 감성 일관성 검증
        
        Args:
            article: 검증할 기사 데이터
            
        Returns:
            Dict[str, Any]: 검증 결과
            {
                "is_consistent": bool,  # 일관성 여부
                "is_reliable": bool,  # 신뢰성 여부
                "title_sentiment": str,  # 제목 감성
                "content_sentiment": str,  # 내용 감성
                "title_confidence": float,  # 제목 신뢰도
                "content_confidence": float,  # 내용 신뢰도
                "consistency_score": float  # 일관성 점수
            }
        """
        if not article or "title" not in article:
            return {
                "is_consistent": False,
                "is_reliable": False,
                "error": "유효하지 않은 기사 데이터"
            }
        
        # 제목과 내용 추출
        title = article["title"]
        content = article.get("content", article.get("summary", ""))
        
        if not content:
            return {
                "is_consistent": False,
                "is_reliable": False,
                "error": "내용이 없습니다."
            }
        
        # 감성 분석기 확인
        if not self.analyzer:
            return {
                "is_consistent": False,
                "is_reliable": False,
                "error": "감성 분석기가 설정되지 않았습니다."
            }
        
        # 제목과 내용 감성 분석
        title_analysis = self.analyzer.analyze(title)
        content_analysis = self.analyzer.analyze(content)
        
        # 감성 레이블 및 신뢰도 추출
        title_sentiment = title_analysis.get("label", "neutral")
        content_sentiment = content_analysis.get("label", "neutral")
        title_confidence = title_analysis.get("confidence", 0.0)
        content_confidence = content_analysis.get("confidence", 0.0)
        
        # 일관성 점수 계산
        title_scores = title_analysis.get("scores", {})
        content_scores = content_analysis.get("scores", {})
        
        consistency_score = 0.0
        if title_scores and content_scores:
            # 코사인 유사도 계산
            title_vector = [title_scores.get(label, 0.0) for label in ["positive", "neutral", "negative"]]
            content_vector = [content_scores.get(label, 0.0) for label in ["positive", "neutral", "negative"]]
            
            # 벡터 정규화
            title_norm = np.linalg.norm(title_vector)
            content_norm = np.linalg.norm(content_vector)
            
            if title_norm > 0 and content_norm > 0:
                title_vector = [v / title_norm for v in title_vector]
                content_vector = [v / content_norm for v in content_vector]
                
                # 코사인 유사도
                consistency_score = sum(t * c for t, c in zip(title_vector, content_vector))
        
        # 일관성 및 신뢰도 확인
        is_consistent = consistency_score >= self.consistency_threshold
        is_reliable = title_confidence >= self.confidence_threshold and content_confidence >= self.confidence_threshold
        
        return {
            "is_consistent": is_consistent,
            "is_reliable": is_reliable,
            "title_sentiment": title_sentiment,
            "content_sentiment": content_sentiment,
            "title_confidence": title_confidence,
            "content_confidence": content_confidence,
            "consistency_score": consistency_score
        }
    
    def validate_batch(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        여러 기사의 감성 일관성 검증
        
        Args:
            articles: 검증할 기사 데이터 목록
            
        Returns:
            Dict[str, Any]: 검증 결과
            {
                "total_articles": int,  # 전체 기사 수
                "consistent_count": int,  # 일관성 있는 기사 수
                "reliable_count": int,  # 신뢰성 있는 기사 수
                "consistency_ratio": float,  # 일관성 비율
                "reliability_ratio": float,  # 신뢰성 비율
                "sentiment_distribution": Dict[str, float],  # 감성 분포
                "detailed_results": List[Dict[str, Any]]  # 상세 결과
            }
        """
        if not articles:
            return {
                "total_articles": 0,
                "consistent_count": 0,
                "reliable_count": 0,
                "consistency_ratio": 0.0,
                "reliability_ratio": 0.0,
                "sentiment_distribution": {"positive": 0.0, "neutral": 0.0, "negative": 0.0},
                "detailed_results": []
            }
        
        # 각 기사 검증
        results = []
        consistent_count = 0
        reliable_count = 0
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        
        for article in articles:
            result = self.validate_consistency(article)
            results.append(result)
            
            if result.get("is_consistent", False):
                consistent_count += 1
            
            if result.get("is_reliable", False):
                reliable_count += 1
            
            # 감성 카운트 증가
            content_sentiment = result.get("content_sentiment", "neutral")
            sentiment_counts[content_sentiment] = sentiment_counts.get(content_sentiment, 0) + 1
        
        # 일관성 및 신뢰도 비율 계산
        total = len(articles)
        consistency_ratio = consistent_count / total if total > 0 else 0.0
        reliability_ratio = reliable_count / total if total > 0 else 0.0
        
        # 감성 분포 계산
        sentiment_distribution = {
            sentiment: count / total if total > 0 else 0.0
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


class SentimentEnsemble:
    """
    감성 분석 앙상블 클래스
    
    여러 감성 분석 모델의 결과를 결합하여 더 정확한 결과를 제공합니다.
    """
    
    def __init__(self, analyzers: List[SentimentAnalyzerInterface], weights: Optional[List[float]] = None):
        """
        SentimentEnsemble 초기화
        
        Args:
            analyzers: 감성 분석기 목록
            weights: 각 분석기의 가중치 (None인 경우 동일 가중치)
        """
        self.analyzers = analyzers
        
        # 가중치 설정
        if weights and len(weights) == len(analyzers):
            # 가중치 정규화
            total = sum(weights)
            self.weights = [w / total for w in weights]
        else:
            # 동일 가중치
            self.weights = [1.0 / len(analyzers) for _ in analyzers]
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        텍스트의 감성 분석
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            Dict[str, Any]: 앙상블 감성 분석 결과
        """
        if not text or not self.analyzers:
            return SentimentAnalysisResult.neutral().to_dict()
        
        # 각 분석기로 분석
        results = []
        for analyzer in self.analyzers:
            try:
                result = analyzer.analyze(text)
                results.append(result)
            except Exception as e:
                logger.error(f"분석기 오류: {str(e)}")
        
        # 결과가 없는 경우
        if not results:
            return SentimentAnalysisResult.neutral().to_dict()
        
        # 앙상블 결과 계산
        return self._ensemble_results(results)
    
    def analyze_batch(self, texts: List[str], batch_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        여러 텍스트의 감성 분석
        
        Args:
            texts: 분석할 텍스트 목록
            batch_size: 배치 크기 (None인 경우 자동 결정)
            
        Returns:
            List[Dict[str, Any]]: 앙상블 감성 분석 결과 목록
        """
        if not texts or not self.analyzers:
            return [SentimentAnalysisResult.neutral().to_dict()] * len(texts)
        
        # 각 분석기로 분석
        all_results = []
        for analyzer in self.analyzers:
            try:
                results = analyzer.analyze_batch(texts, batch_size)
                all_results.append(results)
            except Exception as e:
                logger.error(f"분석기 오류: {str(e)}")
                all_results.append([SentimentAnalysisResult.neutral().to_dict()] * len(texts))
        
        # 결과가 없는 경우
        if not all_results:
            return [SentimentAnalysisResult.neutral().to_dict()] * len(texts)
        
        # 앙상블 결과 계산
        ensemble_results = []
        for i in range(len(texts)):
            results = [analyzer_results[i] for analyzer_results in all_results]
            ensemble_results.append(self._ensemble_results(results))
        
        return ensemble_results
    
    def _ensemble_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        여러 감성 분석 결과를 앙상블
        
        Args:
            results: 감성 분석 결과 목록
            
        Returns:
            Dict[str, Any]: 앙상블 감성 분석 결과
        """
        # 레이블 집합 생성
        labels = set()
        for result in results:
            scores = result.get("scores", {})
            labels.update(scores.keys())
        
        # 가중 평균 점수 계산
        ensemble_scores = {label: 0.0 for label in labels}
        
        for i, result in enumerate(results):
            weight = self.weights[i] if i < len(self.weights) else 0.0
            scores = result.get("scores", {})
            
            for label in labels:
                ensemble_scores[label] += weight * scores.get(label, 0.0)
        
        # 점수 정규화
        total = sum(ensemble_scores.values())
        if total > 0:
            ensemble_scores = {k: v / total for k, v in ensemble_scores.items()}
        
        # 가장 높은 점수의 레이블 찾기
        label = max(ensemble_scores, key=ensemble_scores.get)
        score = ensemble_scores[label]
        
        # 신뢰도 계산
        # 1. 최고 점수와 두 번째 점수의 차이
        sorted_scores = sorted(ensemble_scores.values(), reverse=True)
        score_diff = sorted_scores[0] - sorted_scores[1] if len(sorted_scores) > 1 else sorted_scores[0]
        
        # 2. 각 모델의 신뢰도 평균
        model_confidences = [result.get("confidence", 0.0) for result in results]
        avg_confidence = sum(model_confidences) / len(model_confidences) if model_confidences else 0.0
        
        # 3. 최종 신뢰도 계산
        confidence = 0.7 * avg_confidence + 0.3 * score_diff
        
        # 메타데이터 생성
        metadata = {
            "ensemble": True,
            "model_count": len(results),
            "model_labels": [result.get("label", "neutral") for result in results],
            "model_confidences": model_confidences
        }
        
        # 결과 생성
        return {
            "label": label,
            "score": score,
            "scores": ensemble_scores,
            "confidence": confidence,
            "language": results[0].get("language", "en") if results else "en",
            "metadata": metadata
        }
