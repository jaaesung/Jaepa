"""
뉴스 크롤링 모든 API 테스트 일괄 실행 스크립트

각 API 테스트를 순서대로 실행하고 전체 결과를 보고합니다.
"""
import sys
import os
import unittest
import time
import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import json

# 테스트 결과 저장을 위한 디렉터리 생성
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# API 테스트 순서 (의존성 순서대로 나열)
API_TEST_ORDER = [
    "rss",
    "finnhub",
    "newsdata",
    "sentiment",
    "combiner",
    "integrator_api",
    "integrator"
]

def run_all_api_tests(verbose=False, save_results=False):
    """
    모든 API 테스트를 순서대로 실행
    
    Args:
        verbose: 자세한 출력 여부
        save_results: 결과 저장 여부
    
    Returns:
        dict: 각 API 테스트 결과 요약
    """
    start_time = time.time()
    results = {}
    
    print(f"\n{'='*80}")
    print(f"시작: 모든 API 테스트 일괄 실행")
    print(f"{'='*80}")
    
    # 각 API 테스트 실행
    for api in API_TEST_ORDER:
        print(f"\n\n{'#'*80}")
        print(f"실행: {api} API 테스트")
        print(f"{'#'*80}\n")
        
        # run_crawling_tests.py 스크립트 호출
        cmd = [sys.executable, "run_crawling_tests.py", f"--api={api}"]
        
        if verbose:
            cmd.append("--verbose")
        
        if save_results:
            cmd.append("--save")
        
        # 테스트 실행
        proc = subprocess.run(
            cmd, 
            cwd=os.path.dirname(__file__),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # 성공 여부 저장
        results[api] = {
            "success": proc.returncode == 0,
            "output": proc.stdout,
            "errors": proc.stderr
        }
        
        # 결과 출력
        print(f"\n{api} API 테스트 결과: {'성공' if proc.returncode == 0 else '실패'}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 전체 결과 요약
    print(f"\n\n{'='*80}")
    print(f"모든 API 테스트 완료 (총 소요 시간: {total_time:.2f}초)")
    print(f"{'='*80}")
    
    print("\n테스트 결과 요약:")
    for api in API_TEST_ORDER:
        status = "✅ 성공" if results[api]["success"] else "❌ 실패"
        print(f" - {api}: {status}")
    
    # 실패한 테스트가 있는지 확인
    failed_tests = [api for api in API_TEST_ORDER if not results[api]["success"]]
    
    if failed_tests:
        print(f"\n실패한 테스트: {', '.join(failed_tests)}")
    else:
        print("\n모든 테스트가 성공적으로 완료되었습니다!")
    
    # 상세 결과 저장
    if save_results:
        save_all_test_results(results, total_time)
    
    return results

def save_all_test_results(results, total_time):
    """
    모든 테스트 결과를 파일로 저장
    
    Args:
        results: 테스트 결과
        total_time: 총 실행 시간
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"all_api_tests_results_{timestamp}.txt"
    filepath = RESULTS_DIR / filename
    
    with open(filepath, "w") as f:
        f.write(f"모든 API 테스트 결과 요약\n")
        f.write(f"날짜 및 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"총 실행 시간: {total_time:.2f}초\n")
        f.write(f"{'='*80}\n\n")
        
        for api in API_TEST_ORDER:
            status = "성공" if results[api]["success"] else "실패"
            f.write(f"{api} API 테스트: {status}\n")
            
            # 각 테스트의 주요 출력 저장
            output_lines = results[api]["output"].split("\n")
            summary_start = False
            
            for line in output_lines:
                if "테스트 결과 요약:" in line:
                    summary_start = True
                    f.write(f"  {line}\n")
                elif summary_start and line.strip() and not "=" in line:
                    f.write(f"  {line}\n")
                elif summary_start and "=" in line:
                    summary_start = False
            
            f.write("\n")
        
        # 실패한 테스트가 있는지 확인
        failed_tests = [api for api in API_TEST_ORDER if not results[api]["success"]]
        
        if failed_tests:
            f.write(f"\n실패한 테스트: {', '.join(failed_tests)}\n")
            
            # 실패한 테스트의 에러 출력 저장
            f.write("\n상세 오류 정보:\n")
            for api in failed_tests:
                f.write(f"\n-- {api} API 테스트 오류 --\n")
                f.write(results[api]["errors"])
                f.write("\n")
        else:
            f.write("\n모든 테스트가 성공적으로 완료되었습니다!\n")
    
    print(f"\n통합 테스트 결과가 저장되었습니다: {filepath}")
    
    # JSON 형식으로도 저장
    json_filename = f"all_api_tests_results_{timestamp}.json"
    json_filepath = RESULTS_DIR / json_filename
    
    # 결과 객체 생성
    json_results = {
        "timestamp": datetime.now().isoformat(),
        "total_time": total_time,
        "results": {}
    }
    
    for api in API_TEST_ORDER:
        json_results["results"][api] = {
            "success": results[api]["success"]
        }
    
    # JSON 파일 저장
    with open(json_filepath, "w") as f:
        json.dump(json_results, f, indent=2)

def main():
    """메인 함수: 명령줄 인수 처리 및 테스트 실행"""
    parser = argparse.ArgumentParser(description="JaePa 프로젝트 모든 API 테스트 일괄 실행 스크립트")
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
    
    # 모든 API 테스트 실행
    results = run_all_api_tests(args.verbose, args.save)
    
    # 종료 코드 설정: 모든 테스트 성공 시 0, 그렇지 않으면 1
    all_success = all(results[api]["success"] for api in API_TEST_ORDER)
    sys.exit(0 if all_success else 1)

if __name__ == "__main__":
    main()
