#!/usr/bin/env python3
"""
FinBERT 감성 분석 모듈

이 모듈은 FinBERT 모델을 사용하여 금융 텍스트의 감성을 분석합니다.
"""
import os
import logging
from typing import Dict, List, Any, Union, Optional
from pathlib import Path

import torch
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
env_path = Path(__file__).parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

class FinBERTSentiment:
    """
    FinBERT 모델을 사용한 금융 텍스트 감성 분석
    
    이 클래스는 FinBERT 모델을 사용하여 금융 뉴스 및 텍스트의 감성을 분석합니다.
    """
    
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        """
        FinBERT 감성 분석기 초기화
        
        Args:
            model_name: 사용할 모델 이름 (기본값: 환경 변수에서 가져옴)
            device: 사용할 장치 ('cuda' 또는 'cpu', 기본값: 자동 감지)
        """
        # 모델 이름 설정
        self.model_name = model_name or os.getenv("FINBERT_MODEL_PATH", "yiyanghkust/finbert-tone")
        
        # 장치 설정 (GPU 또는 CPU)
        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"FinBERT 모델 초기화 중: {self.model_name} (장치: {self.device})")
        
        try:
            # 토크나이저 및 모델 로드
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            
            # 모델을 지정된 장치로 이동
            self.model.to(self.device)
            
            # 레이블 설정
            self.labels = ["negative", "neutral", "positive"]
            
            logger.info("FinBERT 모델 초기화 완료")
        except Exception as e:
            logger.error(f"FinBERT 모델 초기화 실패: {str(e)}")
            raise
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        텍스트의 감성 분석
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            Dict[str, Any]: 감성 분석 결과
        """
        if not text or len(text.strip()) == 0:
            return {
                "label": "neutral",
                "score": 1.0,
                "scores": {
                    "negative": 0.0,
                    "neutral": 1.0,
                    "positive": 0.0
                }
            }
        
        try:
            # 텍스트 전처리 및 토큰화
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 모델 추론
            with torch.no_grad():
                outputs = self.model(**inputs)
                
            # 결과 처리
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            probabilities = probabilities.cpu().numpy()[0]
            
            # 가장 높은 확률의 레이블 찾기
            label_idx = np.argmax(probabilities)
            label = self.labels[label_idx]
            score = probabilities[label_idx]
            
            # 결과 반환
            result = {
                "label": label,
                "score": float(score),
                "scores": {
                    self.labels[i]: float(probabilities[i]) for i in range(len(self.labels))
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"감성 분석 중 오류 발생: {str(e)}")
            return {
                "label": "neutral",
                "score": 1.0,
                "scores": {
                    "negative": 0.0,
                    "neutral": 1.0,
                    "positive": 0.0
                }
            }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        여러 텍스트의 감성 분석
        
        Args:
            texts: 분석할 텍스트 목록
            
        Returns:
            List[Dict[str, Any]]: 감성 분석 결과 목록
        """
        results = []
        
        # 빈 텍스트 목록 처리
        if not texts:
            return results
        
        try:
            # 텍스트 전처리 및 토큰화
            inputs = self.tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 모델 추론
            with torch.no_grad():
                outputs = self.model(**inputs)
                
            # 결과 처리
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            probabilities = probabilities.cpu().numpy()
            
            # 각 텍스트에 대한 결과 생성
            for i, probs in enumerate(probabilities):
                label_idx = np.argmax(probs)
                label = self.labels[label_idx]
                score = probs[label_idx]
                
                result = {
                    "label": label,
                    "score": float(score),
                    "scores": {
                        self.labels[j]: float(probs[j]) for j in range(len(self.labels))
                    }
                }
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"배치 감성 분석 중 오류 발생: {str(e)}")
            
            # 오류 발생 시 중립 결과 반환
            neutral_result = {
                "label": "neutral",
                "score": 1.0,
                "scores": {
                    "negative": 0.0,
                    "neutral": 1.0,
                    "positive": 0.0
                }
            }
            
            return [neutral_result] * len(texts)
    
    def analyze_news(self, news: Dict[str, Any]) -> Dict[str, Any]:
        """
        뉴스 기사의 감성 분석
        
        Args:
            news: 뉴스 기사 데이터
            
        Returns:
            Dict[str, Any]: 감성 분석이 추가된 뉴스 기사 데이터
        """
        # 뉴스 기사 복사
        news_with_sentiment = news.copy()
        
        # 분석할 텍스트 준비
        title = news.get("title", "")
        content = news.get("content", "")
        summary = news.get("summary", "")
        
        # 제목과 내용 또는 요약을 결합하여 분석
        if content:
            text = f"{title}. {content}"
        elif summary:
            text = f"{title}. {summary}"
        else:
            text = title
        
        # 감성 분석 수행
        sentiment = self.analyze(text)
        
        # 결과 추가
        news_with_sentiment["sentiment"] = sentiment
        
        return news_with_sentiment
    
    def analyze_news_batch(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        여러 뉴스 기사의 감성 분석
        
        Args:
            news_list: 뉴스 기사 데이터 목록
            
        Returns:
            List[Dict[str, Any]]: 감성 분석이 추가된 뉴스 기사 데이터 목록
        """
        # 뉴스 기사 복사
        news_with_sentiment = [news.copy() for news in news_list]
        
        # 분석할 텍스트 준비
        texts = []
        for news in news_list:
            title = news.get("title", "")
            content = news.get("content", "")
            summary = news.get("summary", "")
            
            if content:
                text = f"{title}. {content}"
            elif summary:
                text = f"{title}. {summary}"
            else:
                text = title
                
            texts.append(text)
        
        # 감성 분석 수행
        sentiments = self.analyze_batch(texts)
        
        # 결과 추가
        for i, sentiment in enumerate(sentiments):
            news_with_sentiment[i]["sentiment"] = sentiment
        
        return news_with_sentiment


# 테스트 코드
if __name__ == "__main__":
    # FinBERT 감성 분석기 초기화
    finbert = FinBERTSentiment()
    
    # 테스트 텍스트
    test_texts = [
        "The company reported strong earnings, beating analyst expectations.",
        "The stock price fell 10% after the disappointing quarterly results.",
        "The market remained stable throughout the trading session.",
        "Investors are concerned about the company's high debt levels.",
        "The new product launch was a huge success, driving sales growth."
    ]
    
    # 개별 텍스트 분석
    print("\n=== 개별 텍스트 분석 ===")
    for text in test_texts:
        sentiment = finbert.analyze(text)
        print(f"텍스트: {text}")
        print(f"감성: {sentiment['label']} (점수: {sentiment['score']:.4f})")
        print(f"세부 점수: {sentiment['scores']}")
        print()
    
    # 배치 분석
    print("\n=== 배치 분석 ===")
    batch_results = finbert.analyze_batch(test_texts)
    for i, (text, sentiment) in enumerate(zip(test_texts, batch_results)):
        print(f"텍스트 {i+1}: {text}")
        print(f"감성: {sentiment['label']} (점수: {sentiment['score']:.4f})")
        print()
    
    # 뉴스 기사 분석
    print("\n=== 뉴스 기사 분석 ===")
    test_news = {
        "title": "Tech Giant Reports Record Profits",
        "content": "The company announced record-breaking quarterly profits today, exceeding analyst expectations by 20%. The CEO attributed the success to strong sales of their new AI-powered devices and growth in cloud services revenue.",
        "url": "https://example.com/news/tech-profits",
        "published_date": "2023-04-15"
    }
    
    news_with_sentiment = finbert.analyze_news(test_news)
    print(f"뉴스 제목: {news_with_sentiment['title']}")
    print(f"감성: {news_with_sentiment['sentiment']['label']} (점수: {news_with_sentiment['sentiment']['score']:.4f})")
    print(f"세부 점수: {news_with_sentiment['sentiment']['scores']}")
