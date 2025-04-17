"""
저장소 패키지

데이터 저장 및 조회 기능을 제공하는 저장소 구현체를 포함합니다.
"""

from infrastructure.repository.article_repository import MongoArticleRepository

__all__ = ['MongoArticleRepository']
