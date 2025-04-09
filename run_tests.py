#!/usr/bin/env python3
"""
통합 테스트 실행 스크립트

이 스크립트는 프로젝트의 모든 테스트를 실행합니다.
"""
import unittest
import sys
import os
import logging
import argparse
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# 테스트 결과 저장을 위한 디렉토리 생성
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "tests", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_test_environment():
    """
    테스트 환경 설정

    - .env 파일 로드
    - 필요한 환경 변수 확인 및 설정
    """
    # 프로젝트 루트 경로 가져오기
    project_root = Path(__file__).parent

    # .env 파일 로드
    dotenv_path = project_root / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
        logger.info(f".env 파일이 로드되었습니다: {dotenv_path}")
    else:
        logger.warning(f".env 파일을 찾을 수 없습니다: {dotenv_path}")

    # 필요한 환경 변수 확인 및 설정
    if "POLYGON_API_KEY" not in os.environ:
        logger.warning("POLYGON_API_KEY가 설정되지 않았습니다. 테스트용 키를 사용합니다.")
        os.environ["POLYGON_API_KEY"] = "test_api_key"
    else:
        key = os.environ["POLYGON_API_KEY"]
        masked_key = key[:4] + '*' * (len(key) - 4) if len(key) > 4 else '****'
        logger.info(f"POLYGON_API_KEY 설정됨: {masked_key}")

    # 기타 필요한 환경 변수 설정
    os.environ.setdefault("TEST_MODE", "True")

def run_tests(test_type=None, verbose=False):
    """
    지정된 유형의 테스트 또는 모든 테스트 실행

    Args:
        test_type: 테스트 유형 (crawling, backend, frontend, stock, finbert, integration, all)
        verbose: 자세한 출력 여부

    Returns:
        unittest.TestResult: 테스트 결과
    """
    # 테스트 디스커버리에 필요한 시작 디렉토리
    start_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')

    # 테스트 시작 메시지 출력
    test_type_str = test_type if test_type else "전체"
    print(f"\n{'='*40}")
    print(f"테스트 시작: {test_type_str} 테스트")
    print(f"{'='*40}")

    # 테스트 시작 시간 기록
    start_time = time.time()

    # 테스트 로더 생성
    loader = unittest.TestLoader()

    # 테스트 유형에 따른 패턴 설정
    if test_type == "crawling":
        pattern = "test_simple.py"
        start_dir = os.path.join(start_dir, "unit", "crawling")
    elif test_type == "finbert":
        pattern = "test_finbert_polygon.py"
        start_dir = os.path.join(start_dir, "unit", "analysis")
    elif test_type == "sentiment":
        pattern = "test_sentiment*.py"
        start_dir = os.path.join(start_dir, "unit", "analysis")
    elif test_type == "backend":
        pattern = "test_*.py"
        start_dir = os.path.join(start_dir, "unit", "backend")
    elif test_type == "frontend":
        pattern = "test_*.js"
        start_dir = os.path.join(start_dir, "frontend")
    elif test_type == "stock":
        pattern = "test_stock*.py"
        start_dir = os.path.join(start_dir, "unit", "data")
    elif test_type == "integration":
        pattern = "test_news_sentiment_pipeline.py"
        start_dir = os.path.join(start_dir, "integration")
    elif test_type == "analysis":
        pattern = "test_simple.py"
        start_dir = os.path.join(start_dir, "unit", "analysis")
    elif test_type == "data":
        pattern = "test_simple.py"
        start_dir = os.path.join(start_dir, "unit", "data")
    elif test_type == "unit":
        pattern = "test_simple.py"
        start_dir = os.path.join(start_dir, "unit")
    else:
        # 모든 테스트 실행
        pattern = "test_simple.py"

    # 테스트 케이스 발견
    test_suite = loader.discover(start_dir=start_dir, pattern=pattern)

    # 테스트 실행
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(test_suite)

    # 테스트 종료 시간 기록 및 소요 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time

    # 결과 요약 출력
    print(f"\n{'='*40}")
    print(f"테스트 결과 요약:")
    print(f"실행된 테스트 수: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    print(f"실행 시간: {elapsed_time:.2f}초")
    print(f"{'='*40}\n")

    # 실패한 테스트 출력
    if result.failures:
        print("\n실패한 테스트:")
        for test, _ in result.failures:
            print(f" - {test}")

    # 오류가 발생한 테스트 출력
    if result.errors:
        print("\n오류가 발생한 테스트:")
        for test, _ in result.errors:
            print(f" - {test}")

    return result

def save_test_results(result, test_type=None):
    """
    테스트 결과를 파일로 저장

    Args:
        result: 테스트 결과
        test_type: 테스트 유형
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{test_type or 'all'}_{timestamp}.txt"
    filepath = os.path.join(RESULTS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"테스트 결과: {test_type or '전체'} 테스트\n")
        f.write(f"날짜 및 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*40}\n\n")

        f.write(f"실행된 테스트 수: {result.testsRun}\n")
        f.write(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}\n")
        f.write(f"실패: {len(result.failures)}\n")
        f.write(f"오류: {len(result.errors)}\n\n")

        if result.failures:
            f.write("실패한 테스트:\n")
            for test, error in result.failures:
                f.write(f" - {test}\n")
                f.write(f"   오류 메시지: {error}\n\n")

        if result.errors:
            f.write("오류가 발생한 테스트:\n")
            for test, error in result.errors:
                f.write(f" - {test}\n")
                f.write(f"   오류 메시지: {error}\n\n")

    print(f"테스트 결과가 저장되었습니다: {filepath}")

def main():
    """메인 함수: 명령줄 인수 처리 및 테스트 실행"""
    parser = argparse.ArgumentParser(description="JaePa 프로젝트 테스트 실행 스크립트")
    parser.add_argument(
        "--type",
        choices=[
            "crawling", "backend", "frontend", "stock", "finbert", "integration", "all",
            "sentiment", "analysis", "data", "unit"
        ],
        default="all",
        help="실행할 테스트 유형 (기본값: all)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="자세한 테스트 출력"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="테스트 결과를 파일로 저장"
    )
    parser.add_argument(
        "--no-env",
        action="store_true",
        help="환경 변수 설정 건너뛰기"
    )

    args = parser.parse_args()

    # 테스트 환경 설정
    if not args.no_env:
        setup_test_environment()

    # 테스트 유형 설정
    test_type = None if args.type == "all" else args.type

    # 테스트 실행
    result = run_tests(test_type, args.verbose)

    # 결과 저장
    if args.save:
        save_test_results(result, args.type)

    # 종료 코드 반환
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(main())
