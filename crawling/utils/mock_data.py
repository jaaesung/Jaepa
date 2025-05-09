#!/usr/bin/env python3
"""
모의 API 응답 데이터

API 테스트 및 개발을 위한 모의 데이터를 제공합니다.
"""
import json
from datetime import datetime, timedelta
import random

# 모의 Finnhub 뉴스 데이터
MOCK_FINNHUB_NEWS = [
    {
        "category": "technology,business",
        "datetime": int((datetime.now() - timedelta(hours=2)).timestamp()),
        "headline": "Apple Announces New iPhone Features at WWDC",
        "id": 1001,
        "image": "https://example.com/images/apple_news.jpg",
        "related": "AAPL",
        "source": "TechCrunch",
        "summary": "Apple unveiled new iPhone features at its annual Worldwide Developers Conference, including enhanced privacy controls and AI capabilities.",
        "url": "https://example.com/news/apple-wwdc-2023"
    },
    {
        "category": "cryptocurrency,finance",
        "datetime": int((datetime.now() - timedelta(hours=4)).timestamp()),
        "headline": "Bitcoin Surges Past $30,000 as Institutional Interest Grows",
        "id": 1002,
        "image": "https://example.com/images/bitcoin_news.jpg",
        "related": "COIN,MSTR",
        "source": "CoinDesk",
        "summary": "Bitcoin has surged past $30,000 as institutional investors continue to show interest in the cryptocurrency market.",
        "url": "https://example.com/news/bitcoin-surges-past-30000"
    },
    {
        "category": "cryptocurrency,technology",
        "datetime": int((datetime.now() - timedelta(hours=6)).timestamp()),
        "headline": "Crypto Firms Embrace AI for Enhanced Security Measures",
        "id": 1003,
        "image": "https://example.com/images/crypto_ai_news.jpg",
        "related": "COIN,NVDA",
        "source": "CoinTelegraph",
        "summary": "Major cryptocurrency firms are increasingly adopting artificial intelligence to enhance their security protocols and detect fraudulent activities.",
        "url": "https://example.com/news/crypto-firms-embrace-ai"
    },
    {
        "category": "finance,markets",
        "datetime": int((datetime.now() - timedelta(hours=8)).timestamp()),
        "headline": "S&P 500 Reaches New All-Time High Amid Economic Recovery",
        "id": 1004,
        "image": "https://example.com/images/sp500_news.jpg",
        "related": "SPY",
        "source": "Bloomberg",
        "summary": "The S&P 500 index reached a new all-time high today as economic recovery continues to strengthen investor confidence.",
        "url": "https://example.com/news/sp500-new-high"
    },
    {
        "category": "technology,business",
        "datetime": int((datetime.now() - timedelta(hours=10)).timestamp()),
        "headline": "Microsoft Expands Cloud Services with New Data Centers",
        "id": 1005,
        "image": "https://example.com/images/microsoft_news.jpg",
        "related": "MSFT",
        "source": "CNBC",
        "summary": "Microsoft announced the expansion of its cloud services with new data centers in Asia and Europe to meet growing demand.",
        "url": "https://example.com/news/microsoft-cloud-expansion"
    }
]

# 모의 NewsData.io 뉴스 데이터
MOCK_NEWSDATA_RESPONSE = {
    "status": "success",
    "totalResults": 3,
    "results": [
        {
            "title": "Bitcoin Mining Becomes More Environmentally Friendly",
            "link": "https://example.com/news/bitcoin-mining-environment",
            "keywords": ["Bitcoin", "Mining", "Environment", "Renewable Energy"],
            "creator": ["John Smith"],
            "video_url": None,
            "description": "Bitcoin mining operations are increasingly turning to renewable energy sources to reduce their environmental impact.",
            "content": "Bitcoin mining operations are increasingly turning to renewable energy sources to reduce their environmental impact. Several major mining companies have announced plans to achieve carbon neutrality by 2025.",
            "pubDate": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "image_url": "https://example.com/images/bitcoin_mining.jpg",
            "source_id": "crypto_news",
            "source_priority": 1,
            "country": ["united states of america"],
            "category": ["business", "technology"],
            "language": "english"
        },
        {
            "title": "Crypto Regulations Tighten Globally as Market Matures",
            "link": "https://example.com/news/crypto-regulations",
            "keywords": ["Cryptocurrency", "Regulations", "Global", "Finance"],
            "creator": ["Jane Doe"],
            "video_url": None,
            "description": "Governments worldwide are implementing stricter regulations on cryptocurrency trading and exchanges.",
            "content": "Governments worldwide are implementing stricter regulations on cryptocurrency trading and exchanges. The move comes as the market continues to mature and attract mainstream investors.",
            "pubDate": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "image_url": "https://example.com/images/crypto_regulations.jpg",
            "source_id": "finance_daily",
            "source_priority": 2,
            "country": ["united kingdom"],
            "category": ["business", "politics"],
            "language": "english"
        },
        {
            "title": "Apple's AI Strategy Focuses on Privacy and On-Device Processing",
            "link": "https://example.com/news/apple-ai-strategy",
            "keywords": ["Apple", "AI", "Privacy", "Technology"],
            "creator": ["Tech Reporter"],
            "video_url": None,
            "description": "Apple's approach to artificial intelligence emphasizes user privacy and on-device processing.",
            "content": "Apple's approach to artificial intelligence emphasizes user privacy and on-device processing. The company's latest AI features process data locally on users' devices rather than in the cloud.",
            "pubDate": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "image_url": "https://example.com/images/apple_ai.jpg",
            "source_id": "tech_news",
            "source_priority": 1,
            "country": ["united states of america"],
            "category": ["technology"],
            "language": "english"
        }
    ],
    "nextPage": None
}

def get_mock_finnhub_news(keyword=None):
    """
    키워드에 따른 모의 Finnhub 뉴스 데이터 반환
    
    Args:
        keyword: 검색 키워드 (None인 경우 모든 뉴스 반환)
        
    Returns:
        List: 모의 뉴스 데이터 목록
    """
    if keyword is None:
        return MOCK_FINNHUB_NEWS
        
    keyword_lower = keyword.lower()
    filtered_news = []
    
    for news in MOCK_FINNHUB_NEWS:
        if (keyword_lower in news.get('headline', '').lower() or 
            keyword_lower in news.get('summary', '').lower() or 
            keyword_lower in news.get('category', '').lower() or
            keyword_lower in news.get('related', '').lower()):
            filtered_news.append(news)
            
    return filtered_news

def get_mock_newsdata_response(keyword=None):
    """
    키워드에 따른 모의 NewsData.io 응답 데이터 반환
    
    Args:
        keyword: 검색 키워드 (None인 경우 모든 뉴스 반환)
        
    Returns:
        Dict: 모의 NewsData.io 응답 데이터
    """
    if keyword is None:
        return MOCK_NEWSDATA_RESPONSE
        
    keyword_lower = keyword.lower()
    filtered_results = []
    
    for news in MOCK_NEWSDATA_RESPONSE['results']:
        if (keyword_lower in news.get('title', '').lower() or 
            keyword_lower in news.get('description', '').lower() or 
            keyword_lower in news.get('content', '').lower() or
            keyword_lower in ' '.join(news.get('keywords', [])).lower()):
            filtered_results.append(news)
            
    response = MOCK_NEWSDATA_RESPONSE.copy()
    response['results'] = filtered_results
    response['totalResults'] = len(filtered_results)
    
    return response

if __name__ == "__main__":
    # 모의 데이터 테스트
    print("Finnhub 모의 데이터 테스트:")
    bitcoin_news = get_mock_finnhub_news("bitcoin")
    print(f"Bitcoin 관련 뉴스: {len(bitcoin_news)}개")
    
    print("\nNewsData.io 모의 데이터 테스트:")
    crypto_news = get_mock_newsdata_response("crypto")
    print(f"Crypto 관련 뉴스: {len(crypto_news['results'])}개")
