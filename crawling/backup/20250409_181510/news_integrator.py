"""
개선된 뉴스 통합 수집기 모듈

개선된 API 접근법 및 오류 처리를 사용하여 RSS 피드와 Finnhub, NewsData.io API에서 수집한 뉴스를 
통합하고 정규화 및 중복 제거를 수행하는 통합 모듈입니다.
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
import time
import random

# 개선된 모듈 가져오기 
from .news_crawler import NewsCrawler, SentimentAnalyzer
from .news_sources_enhanced_improved import NewsSourcesHandler

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
    개선된 뉴스 통합 수집기 클래스
    
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
        self.rss_crawler = NewsCrawler(db_connect=False) if use_rss else None
        self.api_handler = NewsSourcesHandler(db_connect=False) if (use_finnhub or use_newsdata) else None
        
        # 초기화 중 감성 분석기 설정
        if self.rss_crawler:
            self.rss_crawler.initialize_sentiment_analyzer()
        
        # API 키 및 상태 확인
        self.check_api_keys()
        
        # 사용자 에이전트 목록
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        
        logger.info(f"뉴스 통합 수집기 초기화 완료 (RSS: {use_rss}, Finnhub: {use_finnhub}, NewsData.io: {use_newsdata})")
    
    def check_api_keys(self):
        """
        API 키 및 상태 확인
        """
        status = {
            "rss": True,  # RSS는 API 키 필요 없음
            "finnhub": False,
            "newsdata": False
        }
        
        if self.api_handler:
            if self.api_handler.finnhub_api_key and self.api_handler.finnhub_client:
                status["finnhub"] = True
            else:
                logger.warning("Finnhub API 키 또는 클라이언트가 설정되지 않았습니다.")
            
            if self.api_handler.newsdata_api_key:
                status["newsdata"] = True
            else:
                logger.warning("NewsData.io API 키가 설정되지 않았습니다.")
        
        self.api_status = status
        
        return status
    
    def _get_random_user_agent(self) -> str:
        """
        랜덤 사용자 에이전트 반환
        
        Returns:
            str: 사용자 에이전트 문자열
        """
        return random.choice(self.user_agents)
    
    def collect_news(self, keyword: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """
        모든 소스에서 뉴스 수집 및 통합 (개선된 버전)
        
        Args:
            keyword: 검색 키워드
            days: 수집할 기간(일)
            
        Returns:
            List[Dict[str, Any]]: 통합된 뉴스 기사 목록
        """
        all_news = []
        start_time = time.time()
        
        try:
            # 1. API 기반 통합 검색 사용 (모든 API를 한 번에 사용)
            if self.api_handler and (self.use_finnhub or self.use_newsdata) and keyword:
                logger.info(f"API 통합 검색 시작: 키워드 '{keyword}'")
                api_news = self.api_handler.search_news_with_apis(keyword, days)
                logger.info(f"API 통합 검색에서 {len(api_news)}개 기사 수집됨")
                all_news.extend(api_news)
            
            # 2. API 개별 검색 (통합 검색 대신)
            else:
                # 2.1 Finnhub API 사용
                if self.api_handler and self.use_finnhub and self.api_status["finnhub"]:
                    try:
                        if keyword:
                            # 키워드가 있는 경우 주식 심볼로 가정
                            finnhub_news = self.api_handler.get_news_from_finnhub(symbol=keyword, days=days)
                        else:
                            # 키워드가 없는 경우 일반 뉴스 가져오기
                            finnhub_news = self.api_handler.get_news_from_finnhub(days=days)
                        
                        logger.info(f"Finnhub API에서 {len(finnhub_news)}개 기사 수집됨")
                        all_news.extend(finnhub_news)
                    except Exception as e:
                        logger.error(f"Finnhub API 호출 중 오류: {str(e)}")
                
                # 2.2 NewsData.io API 사용
                if self.api_handler and self.use_newsdata and self.api_status["newsdata"]:
                    try:
                        category = "business"  # 비즈니스 카테고리 기본 설정
                        newsdata_news = self.api_handler.get_news_from_newsdata(
                            keyword=keyword, category=category, days=days
                        )
                        logger.info(f"NewsData.io API에서 {len(newsdata_news)}개 기사 수집됨")
                        all_news.extend(newsdata_news)
                    except Exception as e:
                        logger.error(f"NewsData.io API 호출 중 오류: {str(e)}")
            
            # 3. RSS 피드 사용
            if self.use_rss and self.rss_crawler:
                try:
                    if keyword:
                        logger.info(f"RSS 피드에서 '{keyword}' 검색 중...")
                        rss_news = self.rss_crawler.search_news_from_rss(keyword=keyword, days=days)
                    else:
                        logger.info("RSS 피드에서 최신 뉴스 수집 중...")
                        rss_news = self.rss_crawler.get_news_from_rss(count=50)  # 더 많은 기사 수집
                        
                    logger.info(f"RSS 피드에서 {len(rss_news)}개 기사 수집됨")
                    all_news.extend(rss_news)
                except Exception as e:
                    logger.error(f"RSS 피드 수집 중 오류: {str(e)}")
        
        except Exception as e:
            logger.error(f"뉴스 수집 과정에서 예상치 못한 오류 발생: {str(e)}")
        
        # 전체 기사 정규화 및 중복 제거
        logger.info(f"기사 통합 전 총 기사 수: {len(all_news)}")
        
        try:
            # 통합 및 중복 제거
            integrated_news = self._integrate_news(all_news)
            logger.info(f"기사 통합 후 총 기사 수: {len(integrated_news)}")
            
            # 감성 분석 수행 (아직 분석되지 않은 기사에 대해)
            integrated_news = self._ensure_sentiment_analysis(integrated_news)
            
            # MongoDB에 저장
            if self.api_handler:
                try:
                    self.api_handler._save_to_mongodb(integrated_news)
                except Exception as e:
                    logger.error(f"MongoDB 저장 중 오류: {str(e)}")
        
        except Exception as e:
            logger.error(f"기사 통합 및 처리 중 오류: {str(e)}")
            # 에러가 발생해도 수집된 뉴스 반환
            integrated_news = all_news
        
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
                
                elif source_type == "alpha_vantage":
                    # Alpha Vantage 특수 필드
                    normalized["related_symbols"] = article.get("related_symbols", [])
                    normalized["categories"] = article.get("categories", [])
                    normalized["sentiment_info"] = article.get("sentiment_info", None)
                
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
            try:
                deduplicated_articles = self.api_handler._deduplicate_news(normalized_articles)
            except Exception as e:
                logger.error(f"중복 제거 중 오류: {str(e)}")
                deduplicated_articles = normalized_articles
        else:
            # API 핸들러가 없으면 직접 중복 제거 함수 구현 필요 (또는 그냥 통과)
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
        if not articles:
            return []
        
        if not self.rss_crawler or not hasattr(self.rss_crawler, 'sentiment_analyzer'):
            logger.warning("감성 분석기가 초기화되지 않았습니다.")
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
        
        try:
            contents = [article.get("content", "") for article in articles_to_analyze]
            
            # 배치 크기 조정 (메모리 문제 방지)
            batch_size = 10
            all_sentiment_results = []
            
            for i in range(0, len(contents), batch_size):
                batch_contents = contents[i:i+batch_size]
                batch_results = sentiment_analyzer.analyze_batch(batch_contents)
                all_sentiment_results.extend(batch_results)
                
                # 배치 간 짧은 지연
                time.sleep(0.1)
            
            # 분석 결과 적용
            for i, result in enumerate(all_sentiment_results):
                if result:
                    articles[indices_to_analyze[i]]["sentiment"] = result
        
        except Exception as e:
            logger.error(f"감성 분석 중 오류: {str(e)}")
        
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
    keyword = "bitcoin"
    print(f"\n'{keyword}' 키워드로 뉴스 검색 중...")
    news = integrator.collect_news(keyword=keyword, days=3)
    
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
