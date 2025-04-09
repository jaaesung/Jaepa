"""
뉴스 크롤링 테스트 실행 스크립트

API별로 테스트를 분리하여, 특정 API 테스트만 실행하거나 모든 테스트를 실행할 수 있습니다.
"""
import sys
import os
import unittest
import time
import argparse
from datetime import datetime
from pathlib import Path

# 테스트 결과 저장을 위한 디렉터리 생성
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

def run_tests(api_type=None, verbose=False):
    """
    지정된 API의 테스트 또는 모든 테스트 실행
    
    Args:
        api_type: API 유형 (rss, finnhub, newsdata, sentiment, combiner, integrator, all)
        verbose: 자세한 출력 여부
    
    Returns:
        unittest.TestResult: 테스트 결과
    """
    # 테스트 디스커버리에 필요한 시작 디렉터리
    start_dir = os.path.dirname(__file__)
    
    # 테스트 로더 생성
    loader = unittest.TestLoader()
    
    # API 유형에 따른 패턴 설정
    if api_type == "rss":
        pattern = "test_rss_crawler_api.py"
    elif api_type == "finnhub":
        pattern = "test_finnhub_api.py"
    elif api_type == "newsdata":
        pattern = "test_newsdata_api.py"
    elif api_type == "sentiment":
        pattern = "test_sentiment_analysis_api.py"
    elif api_type == "combiner":
        pattern = "test_news_combiner_api.py"
    elif api_type == "integrator_api":
        pattern = "test_news_integrator_api.py"
    elif api_type == "integrator":
        pattern = "test_news_integrator.py"
    else:
        # 모든 테스트 실행
        pattern = "test_*.py"
    
    # 테스트 케이스 발견
    test_suite = loader.discover(start_dir=start_dir, pattern=pattern)
    
    # 테스트 러너 설정
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    
    # 테스트 실행 및 결과 반환
    print(f"\n{'='*60}")
    print(f"테스트 시작: {api_type or '모든 크롤링'} API 테스트")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = runner.run(test_suite)
    end_time = time.time()
    
    # 결과 요약 출력
    print(f"\n{'='*60}")
    print("테스트 결과 요약:")
    print(f"실행된 테스트 수: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    print(f"실행 시간: {end_time - start_time:.2f}초")
    print(f"{'='*60}\n")
    
    # 실패한 테스트 출력
    if result.failures:
        print("\n실패한 테스트:")
        for test, error in result.failures:
            print(f" - {test}")
    
    # 오류가 발생한 테스트 출력
    if result.errors:
        print("\n오류가 발생한 테스트:")
        for test, error in result.errors:
            print(f" - {test}")
    
    return result

def save_test_results(result, api_type=None):
    """
    테스트 결과를 파일로 저장
    
    Args:
        result: unittest.TestResult 객체
        api_type: API 유형
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"crawling_test_results_{api_type or 'all'}_{timestamp}.txt"
    filepath = RESULTS_DIR / filename
    
    with open(filepath, "w") as f:
        f.write(f"크롤링 테스트 결과: {api_type or '모든'} API 테스트\n")
        f.write(f"날짜 및 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n\n")
        
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
    parser = argparse.ArgumentParser(description="JaePa 프로젝트 크롤링 테스트 실행 스크립트")
    parser.add_argument(
        "--api", 
        choices=["rss", "finnhub", "newsdata", "sentiment", "combiner", "integrator_api", "integrator", "all"],
        default="all",
        help="실행할 API 테스트 유형 (기본값: all)"
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
        "--collect-only", 
        action="store_true",
        help="테스트 실행 없이 수집만 수행"
    )
    
    args = parser.parse_args()
    
    # API 유형 설정
    api_type = None if args.api == "all" else args.api
    
    # 테스트 케이스 수집만 하는 경우
    if args.collect_only:
        loader = unittest.TestLoader()
        start_dir = os.path.dirname(__file__)
        pattern = "test_*.py" if api_type is None else f"test_{api_type}*.py"
        test_suite = loader.discover(start_dir=start_dir, pattern=pattern)
        
        print(f"\n{'='*60}")
        print(f"수집된 테스트 케이스: {api_type or '모든 크롤링'} API")
        print(f"{'='*60}")
        
        for test in test_suite:
            for test_case in test:
                for test_method in test_case:
                    print(f" - {test_method.id()}")
        
        print(f"\n총 테스트 케이스 수: {test_suite.countTestCases()}")
        return
    
    # 테스트 실행
    result = run_tests(api_type, args.verbose)
    
    # 결과 저장
    if args.save:
        save_test_results(result, args.api)
    
    # 종료 코드 설정: 모든 테스트 성공 시 0, 그렇지 않으면 1
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()
