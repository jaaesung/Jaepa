"""
크롤러 유효성 검사 모듈

크롤링 결과의 유효성을 검사하고 품질을 평가하는 기능을 제공합니다.
"""
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import nltk
from nltk.tokenize import sent_tokenize

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# NLTK 데이터 다운로드 (첫 실행 시 필요)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


class CrawlerValidator:
    """
    크롤러 유효성 검사 클래스
    
    크롤링된 기사의 유효성을 검사하고 품질을 평가합니다.
    """
    
    def __init__(self):
        """
        CrawlerValidator 클래스 초기화
        """
        # 유효성 검사 임계값 설정
        self.min_title_length = 10
        self.min_content_length = 200
        self.min_sentence_count = 3
        self.max_date_diff_days = 7
    
    def validate_article(self, article: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        기사 유효성 검사
        
        Args:
            article: 검사할 기사 데이터
            
        Returns:
            Tuple[bool, List[str]]: 유효성 여부와 문제점 목록
        """
        issues = []
        
        # 필수 필드 확인
        required_fields = ["url", "title", "content", "source", "published_date", "crawled_date"]
        for field in required_fields:
            if field not in article or article[field] is None:
                issues.append(f"필수 필드 누락: {field}")
                return False, issues
        
        # 제목 검사
        title_valid, title_issues = self.validate_title(article["title"])
        issues.extend(title_issues)
        
        # 내용 검사
        content_valid, content_issues = self.validate_content(article["content"])
        issues.extend(content_issues)
        
        # 날짜 검사
        date_valid, date_issues = self.validate_dates(article["published_date"], article["crawled_date"])
        issues.extend(date_issues)
        
        # URL 검사
        url_valid, url_issues = self.validate_url(article["url"])
        issues.extend(url_issues)
        
        # 출처 검사
        if not article["source"] or len(article["source"].strip()) == 0:
            issues.append("출처가 비어 있습니다")
        
        # 키워드 검사
        if "keywords" in article and article["keywords"]:
            if not isinstance(article["keywords"], list):
                issues.append("키워드가 리스트 형식이 아닙니다")
            elif len(article["keywords"]) == 0:
                issues.append("키워드가 비어 있습니다")
        
        # 유효성 여부 결정 (심각한 문제가 없으면 유효)
        valid = len(issues) == 0 or all(not issue.startswith("필수 필드") for issue in issues)
        
        return valid, issues
    
    def validate_title(self, title: str) -> Tuple[bool, List[str]]:
        """
        제목 유효성 검사
        
        Args:
            title: 검사할 제목
            
        Returns:
            Tuple[bool, List[str]]: 유효성 여부와 문제점 목록
        """
        issues = []
        
        if not title or len(title.strip()) == 0:
            issues.append("제목이 비어 있습니다")
            return False, issues
        
        if len(title) < self.min_title_length:
            issues.append(f"제목이 너무 짧습니다 ({len(title)} < {self.min_title_length})")
        
        if title.isupper():
            issues.append("제목이 모두 대문자입니다")
        
        if title.islower():
            issues.append("제목이 모두 소문자입니다")
        
        if title.endswith(("...", "…")):
            issues.append("제목이 생략 부호로 끝납니다")
        
        # HTML 태그 포함 여부 검사
        if re.search(r"<[^>]+>", title):
            issues.append("제목에 HTML 태그가 포함되어 있습니다")
        
        return len(issues) == 0, issues
    
    def validate_content(self, content: str) -> Tuple[bool, List[str]]:
        """
        내용 유효성 검사
        
        Args:
            content: 검사할 내용
            
        Returns:
            Tuple[bool, List[str]]: 유효성 여부와 문제점 목록
        """
        issues = []
        
        if not content or len(content.strip()) == 0:
            issues.append("내용이 비어 있습니다")
            return False, issues
        
        if len(content) < self.min_content_length:
            issues.append(f"내용이 너무 짧습니다 ({len(content)} < {self.min_content_length})")
        
        # 문장 수 검사
        sentences = sent_tokenize(content)
        if len(sentences) < self.min_sentence_count:
            issues.append(f"문장 수가 너무 적습니다 ({len(sentences)} < {self.min_sentence_count})")
        
        # HTML 태그 포함 여부 검사
        if re.search(r"<[^>]+>", content):
            issues.append("내용에 HTML 태그가 포함되어 있습니다")
        
        # 중복 공백 검사
        if re.search(r"  +", content):
            issues.append("내용에 중복 공백이 포함되어 있습니다")
        
        # 중복 문장 검사
        sentence_set = set(sentences)
        if len(sentence_set) < len(sentences) * 0.8:  # 20% 이상 중복
            issues.append("내용에 중복 문장이 많이 포함되어 있습니다")
        
        return len(issues) == 0, issues
    
    def validate_dates(self, published_date: str, crawled_date: str) -> Tuple[bool, List[str]]:
        """
        날짜 유효성 검사
        
        Args:
            published_date: 검사할 발행일
            crawled_date: 검사할 수집일
            
        Returns:
            Tuple[bool, List[str]]: 유효성 여부와 문제점 목록
        """
        issues = []
        
        try:
            # ISO 형식 파싱
            pub_date = None
            crawl_date = None
            
            # 발행일 파싱
            try:
                pub_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
            except ValueError:
                issues.append("발행일 형식이 올바르지 않습니다")
            
            # 수집일 파싱
            try:
                crawl_date = datetime.fromisoformat(crawled_date.replace('Z', '+00:00'))
            except ValueError:
                issues.append("수집일 형식이 올바르지 않습니다")
            
            # 날짜 비교
            if pub_date and crawl_date:
                # 발행일이 수집일보다 미래인 경우
                if pub_date > crawl_date:
                    issues.append("발행일이 수집일보다 미래입니다")
                
                # 발행일이 너무 오래된 경우
                date_diff = crawl_date - pub_date
                if date_diff.days > self.max_date_diff_days:
                    issues.append(f"발행일이 너무 오래되었습니다 ({date_diff.days} > {self.max_date_diff_days}일)")
                
                # 수집일이 현재보다 미래인 경우
                if crawl_date > datetime.now():
                    issues.append("수집일이 현재보다 미래입니다")
        
        except Exception as e:
            issues.append(f"날짜 검사 중 오류 발생: {str(e)}")
        
        return len(issues) == 0, issues
    
    def validate_url(self, url: str) -> Tuple[bool, List[str]]:
        """
        URL 유효성 검사
        
        Args:
            url: 검사할 URL
            
        Returns:
            Tuple[bool, List[str]]: 유효성 여부와 문제점 목록
        """
        issues = []
        
        if not url or len(url.strip()) == 0:
            issues.append("URL이 비어 있습니다")
            return False, issues
        
        # URL 형식 검사
        url_pattern = re.compile(
            r'^(https?://)([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(/[^/\s]*)*$'
        )
        if not url_pattern.match(url):
            issues.append("URL 형식이 올바르지 않습니다")
        
        # URL 길이 검사
        if len(url) > 2048:
            issues.append("URL이 너무 깁니다")
        
        return len(issues) == 0, issues
    
    def calculate_quality_score(self, article: Dict[str, Any]) -> float:
        """
        기사 품질 점수 계산
        
        Args:
            article: 검사할 기사 데이터
            
        Returns:
            float: 품질 점수 (0.0 ~ 1.0)
        """
        # 유효성 검사
        valid, issues = self.validate_article(article)
        if not valid:
            return 0.0
        
        # 초기 점수
        score = 1.0
        
        # 문제점에 따른 감점
        for issue in issues:
            if "너무 짧습니다" in issue:
                score -= 0.2
            elif "HTML 태그" in issue:
                score -= 0.1
            elif "중복 공백" in issue:
                score -= 0.05
            elif "중복 문장" in issue:
                score -= 0.2
            elif "형식이 올바르지 않습니다" in issue:
                score -= 0.1
            else:
                score -= 0.05
        
        # 내용 길이에 따른 추가 점수
        content_length = len(article["content"])
        if content_length > 1000:
            score += 0.1
        if content_length > 2000:
            score += 0.1
        
        # 키워드 수에 따른 추가 점수
        if "keywords" in article and isinstance(article["keywords"], list):
            keyword_count = len(article["keywords"])
            if keyword_count >= 5:
                score += 0.05
            if keyword_count >= 10:
                score += 0.05
        
        # 감성 분석 결과가 있는 경우 추가 점수
        if "sentiment" in article and article["sentiment"]:
            score += 0.1
        
        # 점수 범위 제한
        return max(0.0, min(1.0, score))
    
    def validate_batch(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        여러 기사 일괄 검사
        
        Args:
            articles: 검사할 기사 목록
            
        Returns:
            Dict[str, Any]: 검사 결과 요약
        """
        total_count = len(articles)
        valid_count = 0
        invalid_count = 0
        total_score = 0.0
        issues_count = {}
        article_scores = []
        
        for article in articles:
            valid, issues = self.validate_article(article)
            score = self.calculate_quality_score(article)
            
            article_scores.append({
                "url": article.get("url", ""),
                "title": article.get("title", ""),
                "valid": valid,
                "score": score,
                "issues": issues
            })
            
            if valid:
                valid_count += 1
            else:
                invalid_count += 1
            
            total_score += score
            
            # 문제점 통계
            for issue in issues:
                issues_count[issue] = issues_count.get(issue, 0) + 1
        
        # 결과 요약
        avg_score = total_score / total_count if total_count > 0 else 0.0
        valid_rate = (valid_count / total_count) * 100 if total_count > 0 else 0.0
        
        # 가장 흔한 문제점
        common_issues = sorted(issues_count.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_count": total_count,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "valid_rate": valid_rate,
            "avg_score": avg_score,
            "common_issues": common_issues[:5],  # 상위 5개 문제점
            "article_scores": article_scores
        }


if __name__ == "__main__":
    # 간단한 사용 예시
    validator = CrawlerValidator()
    
    # 테스트 기사
    test_article = {
        "url": "https://example.com/news/article123",
        "title": "테스트 기사 제목입니다",
        "content": "이것은 테스트 기사의 내용입니다. 유효성 검사를 테스트하기 위한 내용입니다. 충분한 길이의 내용이 필요합니다.",
        "source": "test_source",
        "published_date": datetime.now().isoformat(),
        "crawled_date": datetime.now().isoformat(),
        "keywords": ["테스트", "유효성", "검사"]
    }
    
    # 유효성 검사
    valid, issues = validator.validate_article(test_article)
    
    print(f"유효성: {valid}")
    if issues:
        print("문제점:")
        for issue in issues:
            print(f"- {issue}")
    
    # 품질 점수 계산
    score = validator.calculate_quality_score(test_article)
    print(f"품질 점수: {score:.2f}")
