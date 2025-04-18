"""
기사 처리 모듈

기사 내용 추출, 키워드 추출, 정규화, 중복 제거 등의 기능을 제공합니다.
"""
import asyncio
import logging
import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from core.crawler.interfaces import ArticleProcessorInterface, HttpClientInterface
from core.crawler.exceptions import ParsingException

# 로깅 설정
logger = logging.getLogger(__name__)

# NLTK 리소스 다운로드
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)


class ArticleProcessor(ArticleProcessorInterface):
    """
    기사 처리기
    
    기사 내용 추출, 키워드 추출, 정규화, 중복 제거 등의 기능을 제공합니다.
    """
    
    def __init__(self, http_client: HttpClientInterface):
        """
        ArticleProcessor 초기화
        
        Args:
            http_client: HTTP 클라이언트
        """
        self._http_client = http_client
        self._stop_words = set(stopwords.words('english'))
        self._lemmatizer = WordNetLemmatizer()
        
        # 추가 불용어
        self._stop_words.update([
            'said', 'says', 'say', 'told', 'according', 'reported', 'reuters',
            'bloomberg', 'cnbc', 'wsj', 'wall', 'street', 'journal', 'financial',
            'times', 'ft', 'yahoo', 'finance', 'news', 'article', 'read', 'more'
        ])
    
    async def extract_content(self, url: str, html: Optional[str] = None) -> Dict[str, Any]:
        """
        기사 내용 추출
        
        Args:
            url: 기사 URL
            html: HTML 내용 (None인 경우 URL에서 가져옴)
            
        Returns:
            Dict[str, Any]: 추출된 기사 정보
            
        Raises:
            ParsingException: 내용 추출 실패 시
        """
        try:
            # HTML 가져오기
            if html is None:
                status_code, html = await self._http_client.get_with_retry(url)
                
                if status_code != 200:
                    raise ParsingException(f"Failed to fetch article: HTTP {status_code}", url)
            
            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(html, 'html.parser')
            
            # 제목 추출
            title = self._extract_title(soup)
            
            # 본문 추출
            content = self._extract_main_content(soup)
            
            # 발행일 추출
            published_date = self._extract_published_date(soup)
            
            # 저자 추출
            author = self._extract_author(soup)
            
            # 이미지 URL 추출
            image_url = self._extract_image_url(soup, url)
            
            # 도메인 추출
            domain = urlparse(url).netloc
            
            # 기사 정보 구성
            article = {
                'title': title,
                'url': url,
                'content': content,
                'summary': content[:300] + '...' if len(content) > 300 else content,
                'published_date': published_date,
                'author': author,
                'image_url': image_url,
                'domain': domain,
                'crawled_date': datetime.now().isoformat()
            }
            
            return article
            
        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {str(e)}")
            raise ParsingException(f"Failed to extract content: {str(e)}", url)
    
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        텍스트에서 키워드 추출
        
        Args:
            text: 분석할 텍스트
            max_keywords: 최대 키워드 수
            
        Returns:
            List[str]: 추출된 키워드 목록
        """
        if not text:
            return []
        
        try:
            # 텍스트 전처리
            text = text.lower()
            text = re.sub(r'[^\w\s]', ' ', text)  # 특수문자 제거
            
            # 토큰화
            tokens = word_tokenize(text)
            
            # 불용어 및 짧은 단어 제거
            filtered_tokens = [
                self._lemmatizer.lemmatize(token) for token in tokens
                if token not in self._stop_words and len(token) > 2
            ]
            
            # 빈도수 계산
            word_freq = Counter(filtered_tokens)
            
            # 상위 키워드 추출
            keywords = [word for word, _ in word_freq.most_common(max_keywords)]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Failed to extract keywords: {str(e)}")
            return []
    
    async def normalize_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        기사 정보 정규화
        
        Args:
            article: 원본 기사 정보
            
        Returns:
            Dict[str, Any]: 정규화된 기사 정보
        """
        normalized = article.copy()
        
        # 필수 필드 확인 및 기본값 설정
        if 'title' not in normalized or not normalized['title']:
            normalized['title'] = 'Untitled'
        
        if 'url' not in normalized or not normalized['url']:
            raise ParsingException("Article URL is required")
        
        if 'content' not in normalized or not normalized['content']:
            normalized['content'] = normalized.get('summary', '')
        
        if 'summary' not in normalized or not normalized['summary']:
            content = normalized.get('content', '')
            normalized['summary'] = content[:300] + '...' if len(content) > 300 else content
        
        if 'published_date' not in normalized or not normalized['published_date']:
            normalized['published_date'] = datetime.now().isoformat()
        
        if 'crawled_date' not in normalized:
            normalized['crawled_date'] = datetime.now().isoformat()
        
        if 'source' not in normalized:
            domain = urlparse(normalized['url']).netloc
            normalized['source'] = domain
        
        if 'source_type' not in normalized:
            normalized['source_type'] = 'web'
        
        # 키워드가 없는 경우 추출
        if 'keywords' not in normalized or not normalized['keywords']:
            text_for_keywords = f"{normalized['title']} {normalized['content'][:1000]}"
            normalized['keywords'] = await self.extract_keywords(text_for_keywords)
        
        return normalized
    
    async def deduplicate_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        중복 기사 제거
        
        Args:
            articles: 기사 목록
            
        Returns:
            List[Dict[str, Any]]: 중복이 제거된 기사 목록
        """
        if not articles:
            return []
        
        # URL 기준 중복 제거
        unique_articles = {}
        url_set = set()
        
        for article in articles:
            url = article.get('url', '')
            if not url or url in url_set:
                continue
            
            url_set.add(url)
            unique_articles[url] = article
        
        # 제목 유사도 기준 중복 제거
        title_groups = self._group_by_title_similarity(list(unique_articles.values()))
        
        # 각 그룹에서 가장 좋은 기사 선택
        deduplicated = []
        for group in title_groups:
            if len(group) == 1:
                deduplicated.append(group[0])
            else:
                # 여러 소스에서 온 기사는 통합
                best_article = self._merge_similar_articles(group)
                deduplicated.append(best_article)
        
        return deduplicated
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        HTML에서 제목 추출
        
        Args:
            soup: BeautifulSoup 객체
            
        Returns:
            str: 추출된 제목
        """
        # 메타 태그에서 제목 찾기
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            return meta_title['content'].strip()
        
        # 제목 태그에서 제목 찾기
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        
        # h1 태그에서 제목 찾기
        h1_tag = soup.find('h1')
        if h1_tag and h1_tag.text:
            return h1_tag.text.strip()
        
        return 'Untitled'
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        HTML에서 본문 내용 추출
        
        Args:
            soup: BeautifulSoup 객체
            
        Returns:
            str: 추출된 본문 내용
        """
        # 메타 태그에서 설명 찾기
        meta_desc = soup.find('meta', property='og:description')
        description = meta_desc['content'].strip() if meta_desc and meta_desc.get('content') else ''
        
        # 본문 후보 태그
        content_candidates = []
        
        # article 태그 찾기
        article_tags = soup.find_all('article')
        for tag in article_tags:
            content_candidates.append(tag.get_text(separator=' ', strip=True))
        
        # 본문 관련 클래스/ID 찾기
        content_patterns = [
            'article', 'content', 'story', 'body', 'main', 'text', 'post', 'news'
        ]
        
        for pattern in content_patterns:
            # 클래스로 찾기
            for tag in soup.find_all(class_=re.compile(pattern, re.I)):
                content_candidates.append(tag.get_text(separator=' ', strip=True))
            
            # ID로 찾기
            for tag in soup.find_all(id=re.compile(pattern, re.I)):
                content_candidates.append(tag.get_text(separator=' ', strip=True))
        
        # 가장 긴 내용 선택
        if content_candidates:
            content_candidates.sort(key=len, reverse=True)
            return content_candidates[0]
        
        # 본문을 찾지 못한 경우 p 태그 내용 합치기
        p_tags = soup.find_all('p')
        if p_tags:
            return ' '.join(p.get_text(strip=True) for p in p_tags)
        
        # 아무것도 찾지 못한 경우 body 내용 반환
        body = soup.find('body')
        if body:
            return body.get_text(separator=' ', strip=True)
        
        # 설명이라도 있으면 반환
        if description:
            return description
        
        return ''
    
    def _extract_published_date(self, soup: BeautifulSoup) -> str:
        """
        HTML에서 발행일 추출
        
        Args:
            soup: BeautifulSoup 객체
            
        Returns:
            str: 추출된 발행일 (ISO 형식)
        """
        # 메타 태그에서 발행일 찾기
        for meta_name in ['article:published_time', 'pubdate', 'publishdate', 'date']:
            meta_tag = soup.find('meta', property=meta_name) or soup.find('meta', name=meta_name)
            if meta_tag and meta_tag.get('content'):
                try:
                    # 날짜 형식 변환 시도
                    date_str = meta_tag['content']
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    return date_obj.isoformat()
                except (ValueError, TypeError):
                    pass
        
        # time 태그에서 발행일 찾기
        time_tags = soup.find_all('time')
        for time_tag in time_tags:
            datetime_attr = time_tag.get('datetime')
            if datetime_attr:
                try:
                    date_obj = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                    return date_obj.isoformat()
                except (ValueError, TypeError):
                    pass
        
        # 발행일을 찾지 못한 경우 현재 시간 반환
        return datetime.now().isoformat()
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """
        HTML에서 저자 추출
        
        Args:
            soup: BeautifulSoup 객체
            
        Returns:
            Optional[str]: 추출된 저자 또는 None
        """
        # 메타 태그에서 저자 찾기
        meta_author = soup.find('meta', property='article:author') or soup.find('meta', name='author')
        if meta_author and meta_author.get('content'):
            return meta_author['content'].strip()
        
        # 저자 관련 클래스/ID 찾기
        author_patterns = [
            'author', 'byline', 'writer', 'contributor'
        ]
        
        for pattern in author_patterns:
            # 클래스로 찾기
            for tag in soup.find_all(class_=re.compile(pattern, re.I)):
                text = tag.get_text(strip=True)
                if text and len(text) < 100:  # 저자 이름은 보통 짧음
                    return text
            
            # ID로 찾기
            for tag in soup.find_all(id=re.compile(pattern, re.I)):
                text = tag.get_text(strip=True)
                if text and len(text) < 100:
                    return text
        
        return None
    
    def _extract_image_url(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """
        HTML에서 대표 이미지 URL 추출
        
        Args:
            soup: BeautifulSoup 객체
            base_url: 기준 URL
            
        Returns:
            Optional[str]: 추출된 이미지 URL 또는 None
        """
        # 메타 태그에서 이미지 찾기
        meta_image = soup.find('meta', property='og:image')
        if meta_image and meta_image.get('content'):
            return meta_image['content']
        
        # 기사 내 첫 번째 이미지 찾기
        img_tag = soup.find('img')
        if img_tag and img_tag.get('src'):
            img_url = img_tag['src']
            
            # 상대 경로인 경우 절대 경로로 변환
            if not img_url.startswith(('http://', 'https://')):
                from urllib.parse import urljoin
                img_url = urljoin(base_url, img_url)
            
            return img_url
        
        return None
    
    def _group_by_title_similarity(self, articles: List[Dict[str, Any]], 
                                  threshold: float = 0.85) -> List[List[Dict[str, Any]]]:
        """
        제목 유사도 기준으로 기사 그룹화
        
        Args:
            articles: 기사 목록
            threshold: 유사도 임계값 (0.0 ~ 1.0)
            
        Returns:
            List[List[Dict[str, Any]]]: 그룹화된 기사 목록
        """
        if not articles:
            return []
        
        # 그룹 초기화
        groups = []
        processed = set()
        
        for i, article1 in enumerate(articles):
            if i in processed:
                continue
            
            title1 = article1.get('title', '').lower()
            if not title1:
                continue
            
            # 새 그룹 생성
            group = [article1]
            processed.add(i)
            
            # 유사한 기사 찾기
            for j, article2 in enumerate(articles):
                if j in processed or i == j:
                    continue
                
                title2 = article2.get('title', '').lower()
                if not title2:
                    continue
                
                # 제목 유사도 계산
                similarity = self._calculate_similarity(title1, title2)
                
                if similarity >= threshold:
                    group.append(article2)
                    processed.add(j)
            
            groups.append(group)
        
        return groups
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        텍스트 유사도 계산
        
        Args:
            text1: 첫 번째 텍스트
            text2: 두 번째 텍스트
            
        Returns:
            float: 유사도 (0.0 ~ 1.0)
        """
        # 간단한 자카드 유사도 계산
        set1 = set(text1.split())
        set2 = set(text2.split())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _merge_similar_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        유사한 기사 통합
        
        Args:
            articles: 유사한 기사 목록
            
        Returns:
            Dict[str, Any]: 통합된 기사
        """
        if not articles:
            return {}
        
        if len(articles) == 1:
            return articles[0]
        
        # 가장 최신 기사 선택
        articles.sort(key=lambda x: x.get('published_date', ''), reverse=True)
        base_article = articles[0].copy()
        
        # 소스 및 관련 심볼 통합
        sources = set()
        related_symbols = set()
        keywords = set()
        
        for article in articles:
            # 소스 추가
            source = article.get('source', '')
            if source:
                sources.add(source)
            
            # 관련 심볼 추가
            symbols = article.get('related_symbols', [])
            if symbols:
                related_symbols.update(symbols)
            
            # 키워드 추가
            article_keywords = article.get('keywords', [])
            if article_keywords:
                keywords.update(article_keywords)
        
        # 통합 정보 설정
        base_article['sources'] = list(sources)
        base_article['related_symbols'] = list(related_symbols)
        base_article['keywords'] = list(keywords)[:20]  # 최대 20개 키워드
        
        return base_article
