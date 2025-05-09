import logging
import time
import random
import requests
from typing import Dict, Optional, Tuple, Any

logger = logging.getLogger(__name__)

def make_request_with_retry(url: str, params: Dict = None, headers: Dict = None,
                           max_retries: int = 3, backoff_factor: float = 1.5) -> Tuple[int, Optional[str]]:
    """
    지수 백오프 재시도 로직이 포함된 HTTP 요청

    Args:
        url: 요청 URL
        params: URL 파라미터
        headers: HTTP 헤더
        max_retries: 최대 재시도 횟수
        backoff_factor: 백오프 계수

    Returns:
        Tuple[int, Optional[str]]: 상태 코드와 응답 내용
    """
    if headers is None:
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "application/json, text/html",
            "Accept-Language": "en-US,en;q=0.9"
        }

    retries = 0
    initial_wait_time = 1.0  # 초기 대기 시간 (초)

    while retries < max_retries:
        try:
            # 요청 전 약간의 랜덤 지연 추가 (서버 부하 분산)
            jitter = random.uniform(0, 0.5)
            time.sleep(jitter)
            
            response = requests.get(url, params=params, headers=headers, timeout=15)  # 타임아웃 증가

            if response.status_code == 200:
                return response.status_code, response.text

            elif response.status_code == 429:  # Too Many Requests
                # 레이트 리밋으로 인한 제한, 백오프 후 재시도
                wait_time = initial_wait_time * (backoff_factor ** retries)
                logger.warning(f"레이트 리밋 감지, {wait_time:.2f}초 대기 후 재시도 ({retries+1}/{max_retries}) - URL: {url}")
                time.sleep(wait_time)
                retries += 1
                continue

            # 403 Forbidden - API 키 문제 또는 접근 제한
            elif response.status_code == 403:
                logger.error(f"API 접근 거부 (403 Forbidden): {url}")
                # 접근 거부는 재시도해도 해결되지 않을 가능성이 높음
                return response.status_code, None
            
            # 404 Not Found - 잘못된 URL 또는 삭제된 리소스
            elif response.status_code == 404:
                logger.error(f"리소스를 찾을 수 없음 (404 Not Found): {url}")
                return response.status_code, None

            # 기타 클라이언트 오류
            elif 400 <= response.status_code < 500:
                logger.warning(f"클라이언트 오류 ({response.status_code}): {url}")
                # 대부분의 클라이언트 오류는 재시도해도 해결되지 않을 수 있음
                # 하지만 일부 일시적 오류는 재시도할 가치가 있을 수 있음
                if retries < max_retries - 1:  # 마지막 재시도 전까지는 재시도
                    wait_time = initial_wait_time * (backoff_factor ** retries)
                    logger.warning(f"클라이언트 오류, {wait_time:.2f}초 대기 후 재시도 ({retries+1}/{max_retries})")
                    time.sleep(wait_time)
                    retries += 1
                    continue
                return response.status_code, None

            # 서버 오류는 백오프 후 재시도
            else:
                wait_time = initial_wait_time * (backoff_factor ** retries)
                logger.warning(f"서버 오류 ({response.status_code}), {wait_time:.2f}초 대기 후 재시도 ({retries+1}/{max_retries})")
                time.sleep(wait_time)
                retries += 1
                continue

        except requests.exceptions.Timeout:
            # 타임아웃 발생 시 백오프 후 재시도
            wait_time = initial_wait_time * (backoff_factor ** retries)
            logger.warning(f"요청 타임아웃, {wait_time:.2f}초 대기 후 재시도 ({retries+1}/{max_retries}) - URL: {url}")
            time.sleep(wait_time)
            retries += 1
            continue

        except requests.exceptions.ConnectionError:
            # 연결 오류 발생 시 백오프 후 재시도
            wait_time = initial_wait_time * (backoff_factor ** retries)
            logger.warning(f"연결 오류, {wait_time:.2f}초 대기 후 재시도 ({retries+1}/{max_retries}) - URL: {url}")
            time.sleep(wait_time)
            retries += 1
            continue

        except requests.exceptions.RequestException as e:
            logger.error(f"요청 예외 발생: {str(e)} - URL: {url}")
            # 일반적인 요청 예외는 재시도해볼 가치가 있을 수 있음
            if retries < max_retries - 1:
                wait_time = initial_wait_time * (backoff_factor ** retries)
                logger.warning(f"예외 발생, {wait_time:.2f}초 대기 후 재시도 ({retries+1}/{max_retries})")
                time.sleep(wait_time)
                retries += 1
                continue
            return -1, None

    logger.error(f"최대 재시도 횟수 초과: {url}")
    return -1, None

def get_random_user_agent() -> str:
    """
    랜덤 User-Agent 문자열 반환
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]
    return random.choice(user_agents)
