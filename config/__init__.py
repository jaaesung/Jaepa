"""
JaePa 프로젝트 설정 패키지

중앙화된 설정 관리를 위한 패키지입니다.
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 현재 환경
ENV = os.getenv("ENV", "development")

# 환경별 설정 가져오기
if ENV == "production":
    from .environments.production import *
elif ENV == "testing":
    from .environments.testing import *
else:
    from .environments.development import *

from .settings import settings

__all__ = ["settings", "ENV"]
