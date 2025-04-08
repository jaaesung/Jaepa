"""
뉴스 통합 수집기 모듈

RSS 피드와 Finnhub, NewsData.io API에서 수집한 뉴스를 통합하고
정규화 및 중복 제거를 수행하는 통합 모듈입니다.
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import time

from .news_crawler import NewsCrawler
from .news_sources_enhanced import NewsSourcesHandler

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 설정 파일 로드
config_path = Path(__file__).parent / 'config.json'
with open(config_path, 'r') as f:
    CONFIG = json.load(f)


class NewsIntegrator:
    """
    뉴스 통합 수집기 클래스
    
    다양한 소스(RSS, Finnhub, NewsData.io)에서 뉴스를 수집하고
    통합된 형태로 제공합니다.
    """
    
    def __init__(self, use_rss: bool = True, use_finnhub: bool = True, use_newsdata: bool = True):
        """
        NewsIntegrator 클래스 초기화
        
        Args:
            use_rss: RSS 피드 사용 여부
            use_finnhub: Finnhub API 사용 여부
            use_newsdata: NewsData.io API 사용 여부
        """
        self.config = CONFIG
        self.use_rss = use_rss
        self.use_finnhub = use_finnhub
        self.use_newsdata = use_newsdata
        
        # 각 소스별 수집기 초기화
        self.rss_crawler = NewsCrawler() if use_rss else None
        self.api_handler = NewsSourcesHandler() if (use_finnhub or use_newsdata) else None
        
        # 초기화 중 감성 분석기 설정
        if self.rss_crawler:
            self.rss_crawler.initialize_sentiment_analyzer()
        
        logger.info(f"뉴스 통합 수집기 초기화 완료 (RSS: {use_rss}, Finnhub: {use_finnhub}, NewsData.io: {use_newsdata})")
    
    def collect_news(self, keyword: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """
        모든 소스에서 뉴스 수집 및 통합
        
        Args:
            keyword: 검색 키워드
            days: 수집할 기간(일)
            
        Returns:
            List[Dict[str, Any]]: 통합된 뉴스 기사 목록
        """
        all_news = []
        start_time = time.time()
        
        # RSS 피드에서 뉴스 수집
        if self.use_rss and self.rss_crawler:
            if keyword:
                logger.info(f"RSS 피드에서 '{keyword}' 검색 중...")
                rss_news = self.rss_crawler.search_news_from_rss(keyword=keyword, days=days)
            else:
                logger.info("RSS 피드에서 최신 뉴스 수집 중...")
                rss_news = self.rss_crawler.get_news_from_rss(count=50)  # 더 많은 기사 수집
                
            logger.info(f"RSS 피드에서 {len(rss_news)}개 기사 수집됨")
            all_news.extend(rss_news)
        
        # Finnhub 및 NewsData.io API에서 뉴스 수집
        if self.api_handler:
            logger.info(f"API 소스에서 뉴스 수집 중 (키워드: {keyword or '없음'})...")
            api_news = self.api_handler.get_combined_news(keyword=keyword, days=days, save_to_db=False)
            logger.info(f"API 소스에서 {len(api_news)}개 기사 수집됨")
            all_news.extend(api_news)
        
        # 전체 기사 정규화 및 중복 제거
        logger.info(f"기사 통합 전 총 기사 수: {len(all_news)}")
        integrated_news = self._integrate_news(all_news)
        logger.info(f"기사 통합 후 총 기사 수: {len(integrated_news)}")
        
        # 감성 분석 수행 (아직 분석되지 않은 기사에 대해)
        integrated_news = self._ensure_sentiment_analysis(integrated_news)
        
        # MongoDB에 저장
        if self.api_handler:
            self.api_handler._save_to_mongodb(integrated_news)
        
        elapsed_time = time.time() - start_time
        logger.info(f"통합 뉴스 수집 완료 (소요 시간: {elapsed_time:.2f}초)")
        
        return integrated_news
    
    def _integrate_news(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        여러 소스의 뉴스 기사 통합 (정규화 및 중복 제거)
        
        Args:
            articles: 뉴스 기사 목록
            
        Returns:
            List[Dict[str, Any]]: 통합된 뉴스 기사 목록
        """
        if not articles:
            return []
            
        # 기본적인 정규화 (데이터 형식 통일)
        normalized_articles = []
        
        for article in articles:
            try:
                # 소스 정보 확인
                source_type = article.get("source_type", "unknown")
                
                # 공통 스키마로 변환
                normalized = {
                    "title": article.get("title", ""),
                    "content": article.get("content", article.get("summary", "")),
                    "url": article.get("url", ""),
                    "published_date": article.get("published_date", datetime.now().isoformat()),
                    "source": article.get("source", "Unknown"),
                    "source_type": source_type,
                    "crawled_date": article.get("crawled_date", datetime.now().isoformat()),
                    "keywords": article.get("keywords", []),
                    "sentiment": article.get("sentiment", None)
                }
                
                # 소스별 추가 필드 처리
                if source_type == "rss":
                    # RSS 피드 특수 필드
                    normalized["image_url"] = article.get("image_url", None)
                    if "author" in article:
                        normalized["author"] = article.get("author")
                    if "categories" in article:
                        normalized["categories"] = article.get("categories")
                        
                elif source_type == "finnhub":
                    # Finnhub 특수 필드
                    normalized["related_symbols"] = article.get("related_symbols", [])
                    normalized["categories"] = article.get("categories", [])
                    normalized["image_url"] = article.get("image_url", None)
                    
                elif source_type == "newsdata":
                    # NewsData.io 특수 필드
                    normalized["creator"] = article.get("creator", None)
                    normalized["categories"] = article.get("categories", [])
                    normalized["image_url"] = article.get("image_url", None)
                    normalized["country"] = article.get("country", [])
                
                # 소스 정보 (sources 배열)
                if "sources" in article:
                    normalized["sources"] = article["sources"]
                else:
                    normalized["sources"] = [article.get("source", "Unknown")]
                    
                normalized_articles.append(normalized)
                
            except Exception as e:
                logger.error(f"기사 정규화 중 오류: {str(e)}")
        
        # API 핸들러로 중복 제거
        if self.api_handler:
            deduplicated_articles = self.api_handler._deduplicate_news(normalized_articles)
        else:
            # API 핸들러가 없으면 직접 중복 제거 함수 구현 필요
            deduplicated_articles = normalized_articles
            
        return deduplicated_articles
    
    def _ensure_sentiment_analysis(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        감성 분석이 없는 뉴스에 대해 감성 분석 수행
        
        Args:
            articles: 뉴스 기사 목록
            
        Returns:
            List[Dict[str, Any]]: 감성 분석이 완료된 뉴스 기사 목록
        """
        if not self.rss_crawler or not hasattr(self.rss_crawler, 'sentiment_analyzer'):
            return articles
            
        sentiment_analyzer = self.rss_crawler.sentiment_analyzer
        
        # 감성 분석이 필요한 기사 필터링
        articles_to_analyze = []
        indices_to_analyze = []
        
        for i, article in enumerate(articles):
            if not article.get("sentiment"):
                articles_to_analyze.append(article)
                indices_to_analyze.append(i)
        
        if not articles_to_analyze:
            return articles
            
        # 감성 분석 실행
        logger.info(f"{len(articles_to_analyze)}개 기사에 대해 감성 분석 수행 중...")
        contents = [article.get("content", "") for article in articles_to_analyze]
        sentiment_results = sentiment_analyzer.analyze_batch(contents)
        
        # 분석 결과 적용
        for i, result in enumerate(sentiment_results):
            if result:
                articles[indices_to_analyze[i]]["sentiment"] = result
                
        return articles
    
    def close(self):
        """
        자원 정리 및 연결 종료
        """
        if self.rss_crawler:
            self.rss_crawler.close()
            
        if self.api_handler:
            self.api_handler.close()
            
        logger.info("뉴스 통합 수집기 종료")


if __name__ == "__main__":
    # 직접 실행 시 간단한 테스트 코드
    integrator = NewsIntegrator(use_rss=True, use_finnhub=True, use_newsdata=True)
    
    # 통합 뉴스 수집 테스트
    news = integrator.collect_news(keyword="bitcoin", days=3)
    
    # 간단한 통계
    sources = {}
    for article in news:
        src = article.get("source_type", "unknown")
        sources[src] = sources.get(src, 0) + 1
    
    print("\n수집 소스별 기사 수:")
    for src, count in sources.items():
        print(f"- {src}: {count}개")
    
    print(f"\n총 {len(news)}개 기사가 통합 수집되었습니다.")
    
    # 몇 가지 샘플 기사 출력
    print("\n샘플 기사:")
    for i, article in enumerate(news[:3]):
        print(f"\n#{i+1} [{article.get('source_type', 'unknown')}] {article['title']}")
        print(f"- URL: {article['url']}")
        print(f"- 날짜: {article['published_date']}")
        print(f"- 소스: {', '.join(article.get('sources', [article.get('source', 'Unknown')]))}")
        if article.get('sentiment'):
            sentiment = article['sentiment']
            print(f"- 감성: 긍정({sentiment.get('positive', 0):.2f}), "
                  f"중립({sentiment.get('neutral', 0):.2f}), "
                  f"부정({sentiment.get('negative', 0):.2f})")
    
    integrator.close()
