"""
뉴스 크롤러 사용 예제

리팩토링된 뉴스 크롤러 모듈의 사용 방법을 보여줍니다.
"""
import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(str(Path(__file__).parents[1]))

from core.crawler.factory import NewsCrawlerFactory
from core.crawler.news_crawler import NewsCrawler


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """메인 함수"""
    try:
        # MongoDB 연결 정보
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('MONGO_DB_NAME', 'jaepa')
        
        # 설정 파일 경로
        config_path = Path(__file__).parents[1] / 'crawling' / 'config.json'
        
        logger.info("Creating crawler components...")
        
        # 크롤러 구성 요소 생성
        components = await NewsCrawlerFactory.create_complete_crawler(
            config_path=str(config_path),
            mongo_uri=mongo_uri,
            db_name=db_name
        )
        
        # 뉴스 크롤러 생성
        crawler = NewsCrawler(
            news_source_manager=components['news_source_manager'],
            article_processor=components['article_processor'],
            article_repository=components['article_repository']
        )
        
        logger.info("Crawler created successfully")
        
        # 최신 뉴스 가져오기
        logger.info("Getting latest news...")
        latest_news = await crawler.get_latest_news(count=5)
        
        logger.info(f"Found {len(latest_news)} latest news")
        for i, article in enumerate(latest_news):
            print(f"\nArticle #{i+1}")
            print(f"Title: {article['title']}")
            print(f"Source: {article['source']}")
            print(f"Date: {article['published_date']}")
            print(f"URL: {article['url']}")
        
        # 키워드로 뉴스 검색
        keyword = "AAPL"
        logger.info(f"Searching news for keyword '{keyword}'...")
        search_results = await crawler.search_news(keyword=keyword, days=7, count=5)
        
        logger.info(f"Found {len(search_results)} news for keyword '{keyword}'")
        for i, article in enumerate(search_results):
            print(f"\nArticle #{i+1}")
            print(f"Title: {article['title']}")
            print(f"Source: {article['source']}")
            print(f"Date: {article['published_date']}")
            print(f"URL: {article['url']}")
            if 'keywords' in article:
                print(f"Keywords: {', '.join(article['keywords'])}")
        
        # 리소스 정리
        await crawler.close()
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")


if __name__ == "__main__":
    # 비동기 이벤트 루프 실행
    asyncio.run(main())
