"""
백엔드 앱 모듈 (레거시)

이 모듈은 레거시 코드입니다. 새로운 코드는 backend/main.py를 사용하세요.
"""

import os
import sys
import logging

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 경고 메시지
logger.warning("이 모듈은 레거시 코드입니다. 새로운 코드는 backend/main.py를 사용하세요.")

# 메인 앱 임포트
from backend.main import app

# 서버 실행 (직접 실행 시)
if __name__ == "__main__":
    import uvicorn

    logger.warning("이 모듈은 레거시 코드입니다. 새로운 코드는 backend/main.py를 사용하세요.")
    logger.info("backend/main.py로 리디렉션합니다.")

    # backend/main.py로 리디렉션
    import backend.main

    # 실행
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
