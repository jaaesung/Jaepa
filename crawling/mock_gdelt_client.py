#!/usr/bin/env python3
"""
모의 GDELT 클라이언트

이 모듈은 테스트용 모의 GDELT 데이터를 생성합니다.
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

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
    
    def search_news(self, query: str, max_records: int = 250) -> List[Dict[str, Any]]:
        """
        모의 뉴스 검색
        
        Args:
            query: 검색어
            max_records: 최대 검색 결과 수
            
        Returns:
            List[Dict[str, Any]]: 모의 뉴스 검색 결과
        """
        # 검색어에서 회사 심볼 추출
        symbol = None
        for s in self.company_names:
            if s in query or self.company_names[s] in query:
                symbol = s
                break
        
        if not symbol:
            # 일반 검색어인 경우 일반 뉴스 생성
            return self._generate_general_news(query, max_records)
        else:
            # 회사 관련 뉴스 생성
            return self._generate_company_news(symbol, max_records)
    
    def _generate_general_news(self, query: str, count: int) -> List[Dict[str, Any]]:
        """
        일반 검색어에 대한 모의 뉴스 생성
        
        Args:
            query: 검색어
            count: 생성할 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 모의 뉴스 목록
        """
        # 뉴스 제목 템플릿
        news_templates = [
            f"Latest News on {query}",
            f"Breaking: New Developments in {query}",
            f"Experts Discuss {query} Trends",
            f"Analysis: The Future of {query}",
            f"Report: {query} Market Overview",
            f"{query} Update: What You Need to Know",
            f"Special Report: {query} in Focus",
            f"Weekly Roundup: {query} News",
            f"Opinion: The Impact of {query}",
            f"Feature: Understanding {query}"
        ]
        
        # 결과 저장
        result = []
        
        # 뉴스 생성
        for i in range(min(count, len(news_templates))):
            # 랜덤 날짜 생성 (최근 7일 이내)
            days_ago = random.randint(0, 7)
            news_date = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            # 감성 점수 생성 (-1.0 ~ 1.0)
            sentiment_score = (random.random() * 2) - 1
            
            # 뉴스 생성
            news = {
                "title": news_templates[i],
                "snippet": f"This is a mock news article about {query}.",
                "url": f"https://example.com/news/{i}",
                "seendate": int(news_date.timestamp() * 1000),
                "domain": "example.com",
                "language": "English",
                "tone": sentiment_score
            }
            
            result.append(news)
        
        return result
    
    def _generate_company_news(self, symbol: str, count: int) -> List[Dict[str, Any]]:
        """
        회사 관련 모의 뉴스 생성
        
        Args:
            symbol: 주식 심볼 (예: AAPL)
            count: 생성할 뉴스 수
            
        Returns:
            List[Dict[str, Any]]: 모의 뉴스 목록
        """
        company_name = self.company_names.get(symbol, symbol)
        
        # 뉴스 제목 템플릿
        news_templates = [
            f"{company_name} Reports Strong Quarterly Earnings",
            f"{company_name} Announces New Product Line",
            f"{company_name} CEO Discusses Future Growth Strategy",
            f"{company_name} Expands into New Markets",
            f"{company_name} Stock Rises on Positive Analyst Ratings",
            f"{company_name} Partners with Major Tech Company",
            f"{company_name} Faces Regulatory Challenges",
            f"{company_name} Invests in AI and Machine Learning",
            f"{company_name} Restructures Operations",
            f"Investors Optimistic About {company_name}'s Future"
        ]
        
        # 결과 저장
        result = []
        
        # 뉴스 생성
        for i in range(min(count, len(news_templates))):
            # 랜덤 날짜 생성 (최근 7일 이내)
            days_ago = random.randint(0, 7)
            news_date = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            # 감성 점수 생성 (-1.0 ~ 1.0)
            sentiment_score = (random.random() * 2) - 1
            
            # 뉴스 생성
            news = {
                "title": news_templates[i],
                "snippet": f"This is a mock news article about {company_name}.",
                "url": f"https://example.com/news/{symbol.lower()}/{i}",
                "seendate": int(news_date.timestamp() * 1000),
                "domain": "example.com",
                "language": "English",
                "tone": sentiment_score
            }
            
            result.append(news)
        
        return result
    
    def search_financial_news(self,
                             keywords: Union[str, List[str]],
                             symbols: Optional[List[str]] = None,
                             max_records: int = 250) -> List[Dict[str, Any]]:
        """
        모의 금융 뉴스 검색
        
        Args:
            keywords: 검색 키워드 (문자열 또는 목록)
            symbols: 주식 심볼 목록 (예: ["AAPL", "MSFT"])
            max_records: 최대 검색 결과 수
            
        Returns:
            List[Dict[str, Any]]: 모의 뉴스 목록
        """
        # 키워드 처리
        if isinstance(keywords, list):
            keyword = " ".join(keywords)
        else:
            keyword = keywords
        
        # 심볼이 있는 경우 해당 심볼의 뉴스 생성
        if symbols and len(symbols) > 0:
            symbol = symbols[0]
            articles = self._generate_company_news(symbol, max_records)
        else:
            # 심볼이 없는 경우 일반 금융 뉴스 생성
            articles = self._generate_general_news(keyword, max_records)
        
        # 결과 정규화
        normalized_articles = []
        for article in articles:
            # 날짜 변환
            published_date = datetime.fromtimestamp(article.get("seendate", 0)/1000.0).isoformat()
            
            # 관련 심볼 추출
            related_symbols = []
            if symbols:
                for symbol in symbols:
                    related_symbols.append(symbol)
            
            # 정규화된 기사 데이터
            normalized = {
                "title": article.get("title", ""),
                "content": article.get("snippet", ""),
                "summary": article.get("snippet", ""),
                "url": article.get("url", ""),
                "published_date": published_date,
                "source": article.get("domain", ""),
                "source_type": "gdelt",
                "crawled_date": datetime.now().isoformat(),
                "related_symbols": related_symbols,
                "language": article.get("language", ""),
                "sentiment": {
                    "score": float(article.get("tone", 0)),
                    "positive": max(0, float(article.get("tone", 0))),
                    "negative": max(0, -float(article.get("tone", 0))),
                    "neutral": 1.0 - abs(float(article.get("tone", 0)))
                }
            }
            
            normalized_articles.append(normalized)
        
        return normalized_articles
    
    def get_news_by_symbol(self, symbol: str, max_records: int = 100) -> List[Dict[str, Any]]:
        """
        특정 주식 심볼에 대한 모의 뉴스 검색
        
        Args:
            symbol: 주식 심볼 (예: AAPL)
            max_records: 최대 검색 결과 수
            
        Returns:
            List[Dict[str, Any]]: 모의 뉴스 목록
        """
        # 검색 키워드 구성
        keywords = [symbol]
        if symbol in self.company_names:
            keywords.append(self.company_names[symbol])
        
        return self.search_financial_news(
            keywords=keywords,
            symbols=[symbol],
            max_records=max_records
        )
    
    def get_historical_news_by_symbol(self, symbol: str, max_records: int = 250) -> List[Dict[str, Any]]:
        """
        특정 주식 심볼에 대한 과거 모의 뉴스 검색
        
        Args:
            symbol: 주식 심볼 (예: AAPL)
            max_records: 최대 검색 결과 수
            
        Returns:
            List[Dict[str, Any]]: 모의 뉴스 목록
        """
        return self.get_news_by_symbol(symbol, max_records)
    
    def get_news_sentiment_trends(self, symbol: str, interval: str = 'day') -> Dict[str, Any]:
        """
        모의 감성 트렌드 분석
        
        Args:
            symbol: 주식 심볼 (예: AAPL)
            interval: 시간 간격 ('hour', 'day', 'week', 'month')
            
        Returns:
            Dict[str, Any]: 모의 감성 트렌드 분석 결과
        """
        # 뉴스 수집
        articles = self.get_news_by_symbol(symbol, max_records=50)
        
        if not articles:
            return {
                "symbol": symbol,
                "period": f"{(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
                "interval": interval,
                "trends": [],
                "summary": {
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "average_score": 0,
                    "article_count": 0
                }
            }
        
        # 트렌드 생성
        trends = []
        for i in range(10):  # 10일간의 트렌드 생성
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            # 랜덤 감성 점수 생성
            sentiment_score = (random.random() * 2) - 1
            
            trends.append({
                "interval": date,
                "sentiment": {
                    "positive": max(0, sentiment_score),
                    "negative": max(0, -sentiment_score),
                    "neutral": 1.0 - abs(sentiment_score),
                    "score": sentiment_score
                },
                "article_count": random.randint(1, 5)
            })
        
        # 전체 기간 요약
        summary = {
            "positive": sum(t["sentiment"]["positive"] for t in trends) / len(trends),
            "negative": sum(t["sentiment"]["negative"] for t in trends) / len(trends),
            "neutral": sum(t["sentiment"]["neutral"] for t in trends) / len(trends),
            "average_score": sum(t["sentiment"]["score"] for t in trends) / len(trends),
            "article_count": sum(t["article_count"] for t in trends)
        }
        
        return {
            "symbol": symbol,
            "period": f"{(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
            "interval": interval,
            "trends": trends,
            "summary": summary
        }
    
    def analyze_sentiment_stock_correlation(self,
                                          symbol: str,
                                          stock_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        모의 감성-주가 상관관계 분석
        
        Args:
            symbol: 주식 심볼 (예: AAPL)
            stock_data: 주가 데이터 (외부에서 제공하는 경우)
            
        Returns:
            Dict[str, Any]: 모의 감성-주가 상관관계 분석 결과
        """
        # 감성 트렌드 가져오기
        sentiment_data = self.get_news_sentiment_trends(symbol, interval='day')
        
        if not sentiment_data['trends']:
            return {
                "symbol": symbol,
                "period": f"{(datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
                "correlation": {
                    "same_day": 0,
                    "next_day": 0,
                    "next_3_days": 0,
                    "next_week": 0
                },
                "sentiment_impact": [],
                "data_points": 0
            }
        
        # 모의 상관관계 생성
        correlation = {
            "same_day": random.uniform(-0.5, 0.5),
            "next_day": random.uniform(-0.5, 0.5),
            "next_3_days": random.uniform(-0.5, 0.5),
            "next_week": random.uniform(-0.5, 0.5)
        }
        
        # 모의 감성 영향 생성
        sentiment_impact = []
        for group in ['very_negative', 'negative', 'neutral', 'positive', 'very_positive']:
            impact = {
                "sentiment_group": group,
                "count": random.randint(5, 20),
                "avg_price_change": {
                    "same_day": random.uniform(-2.0, 2.0),
                    "next_day": random.uniform(-2.0, 2.0),
                    "next_3_days": random.uniform(-3.0, 3.0),
                    "next_week": random.uniform(-5.0, 5.0)
                }
            }
            sentiment_impact.append(impact)
        
        return {
            "symbol": symbol,
            "period": f"{(datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
            "correlation": correlation,
            "sentiment_impact": sentiment_impact,
            "data_points": random.randint(30, 90)
        }
