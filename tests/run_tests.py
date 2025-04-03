"""
통합 테스트 실행 스크립트

이 스크립트는 모든 테스트 케이스를 실행하고 결과를 보고합니다.
"""
import sys
import os
import unittest
import time
import argparse
from datetime import datetime

# 테스트 결과 저장을 위한 디렉터리 생성
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_tests(test_type=None, verbose=False):
    """
    지정된 유형의 테스트 또는 모든 테스트 실행
    
    Args:
        test_type: 테스트 유형 (crawling, backend, frontend, stock)
        verbose: 자세한 출력 여부
    
    Returns:
        unittest.TestResult: 테스트 결과
    """
    # 테스트 디스커버리에 필요한 시작 디렉터리
    start_dir = os.path.dirname(__file__)
    
    # 테스트 로더 생성
    loader = unittest.TestLoader()
    
    # 테스트 유형에 따른 패턴 설정
    if test_type == "crawling":
        pattern = "test_*crawler*.py"
        start_dir = os.path.join(start_dir, "crawling")
    elif test_type == "backend":
        pattern = "test_api*.py"
        start_dir = os.path.join(start_dir, "backend")
    elif test_type == "frontend":
        pattern = "test_*.js"
        start_dir = os.path.join(start_dir, "frontend")
    elif test_type == "stock":
        pattern = "test_stock*.py"
        start_dir = os.path.join(start_dir, "stock_crawler")
    else:
        # 모든 테스트 실행
        pattern = "test_*.py"
    
    # 테스트 케이스 발견
    test_suite = loader.discover(start_dir=start_dir, pattern=pattern)
    
    # 테스트 러너 설정
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    
    # 테스트 실행 및 결과 반환
    print(f"\n{'='*40}")
    print(f"테스트 시작: {test_type or '전체'} 테스트")
    print(f"{'='*40}")
    
    start_time = time.time()
    result = runner.run(test_suite)
    end_time = time.time()
    
    # 결과 요약 출력
    print(f"\n{'='*40}")
    print("테스트 결과 요약:")
    print(f"실행된 테스트 수: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    print(f"실행 시간: {end_time - start_time:.2f}초")
    print(f"{'='*40}\n")
    
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

def save_test_results(result, test_type=None):
    """
    테스트 결과를 파일로 저장
    
    Args:
        result: unittest.TestResult 객체
        test_type: 테스트 유형
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{test_type or 'all'}_{timestamp}.txt"
    filepath = os.path.join(RESULTS_DIR, filename)
    
    with open(filepath, "w") as f:
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
        choices=["crawling", "backend", "frontend", "stock", "all"],
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
    
    args = parser.parse_args()
    
    # 테스트 유형 설정
    test_type = None if args.type == "all" else args.type
    
    # 테스트 실행
    result = run_tests(test_type, args.verbose)
    
    # 결과 저장
    if args.save:
        save_test_results(result, args.type)
    
    # 종료 코드 설정: 모든 테스트 성공 시 0, 그렇지 않으면 1
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()
