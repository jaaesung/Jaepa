#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
테스트 실행 스크립트

이 스크립트는 다양한 유형의 테스트를 실행하는 명령줄 인터페이스를 제공합니다.
"""

import os
import sys
import argparse
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

# 색상 코드
COLORS = {
    "RESET": "\033[0m",
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m"
}


def colorize(text: str, color: str) -> str:
    """
    텍스트에 색상 적용

    Args:
        text: 색상을 적용할 텍스트
        color: 색상 코드 키

    Returns:
        str: 색상이 적용된 텍스트
    """
    return f"{COLORS.get(color, '')}{text}{COLORS['RESET']}"


def print_header(title: str) -> None:
    """
    제목 헤더 출력

    Args:
        title: 제목
    """
    width = 80
    print("\n" + "=" * width)
    print(colorize(f" {title.center(width - 2)} ", "BOLD"))
    print("=" * width + "\n")


def print_section(title: str) -> None:
    """
    섹션 제목 출력

    Args:
        title: 섹션 제목
    """
    print(colorize(f"\n=== {title} ===\n", "CYAN"))


def run_command(command: List[str], env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
    """
    명령 실행

    Args:
        command: 실행할 명령
        env: 환경 변수

    Returns:
        subprocess.CompletedProcess: 실행 결과
    """
    print(colorize(f"실행 명령: {' '.join(command)}", "BLUE"))

    # 환경 변수 설정
    if env:
        env_vars = os.environ.copy()
        env_vars.update(env)
    else:
        env_vars = None

    # 명령 실행
    start_time = time.time()
    result = subprocess.run(
        command,
        env=env_vars,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    elapsed_time = time.time() - start_time

    # 결과 출력
    if result.returncode == 0:
        print(colorize(f"성공 (소요 시간: {elapsed_time:.2f}초)", "GREEN"))
    else:
        print(colorize(f"실패 (소요 시간: {elapsed_time:.2f}초)", "RED"))
        print(colorize("오류:", "RED"))
        print(result.stderr)

    return result


def run_pytest(
    test_path: str,
    markers: Optional[List[str]] = None,
    options: Optional[List[str]] = None,
    env: Optional[Dict[str, str]] = None
) -> bool:
    """
    pytest 실행

    Args:
        test_path: 테스트 경로
        markers: 테스트 마커
        options: pytest 옵션
        env: 환경 변수

    Returns:
        bool: 성공 여부
    """
    command = ["pytest", test_path]

    # 마커 추가
    if markers:
        marker_expr = " or ".join(markers)
        command.extend(["-m", marker_expr])

    # 옵션 추가
    if options:
        command.extend(options)

    # 명령 실행
    result = run_command(command, env)

    return result.returncode == 0


def run_unit_tests(options: Optional[List[str]] = None) -> bool:
    """
    단위 테스트 실행

    Args:
        options: pytest 옵션

    Returns:
        bool: 성공 여부
    """
    print_section("단위 테스트 실행")

    # Jest 단위 테스트 실행
    command = ["npm", "test"]

    if options:
        command.extend(["--", *options])

    result = run_command(command)
    return result.returncode == 0


def run_integration_tests(options: Optional[List[str]] = None) -> bool:
    """
    통합 테스트 실행

    Args:
        options: pytest 옵션

    Returns:
        bool: 성공 여부
    """
    print_section("통합 테스트 실행")

    # Jest 통합 테스트 실행
    if options is None:
        options = []

    # 통합 테스트 패턴 추가
    options.extend(["--testPathPattern", ".*\.integration\.test\.(js|jsx|ts|tsx)$"])

    command = ["npm", "test"]
    if options:
        command.extend(["--", *options])

    result = run_command(command)
    return result.returncode == 0


def run_api_tests(options: Optional[List[str]] = None) -> bool:
    """
    API 테스트 실행

    Args:
        options: pytest 옵션

    Returns:
        bool: 성공 여부
    """
    print_section("API 테스트 실행")
    return run_pytest("tests/api", ["api"], options)


def run_database_tests(options: Optional[List[str]] = None) -> bool:
    """
    데이터베이스 테스트 실행

    Args:
        options: pytest 옵션

    Returns:
        bool: 성공 여부
    """
    print_section("데이터베이스 테스트 실행")
    return run_pytest("tests/database", ["database"], options)


def run_performance_tests(options: Optional[List[str]] = None) -> bool:
    """
    성능 테스트 실행

    Args:
        options: pytest 옵션

    Returns:
        bool: 성공 여부
    """
    print_section("성능 테스트 실행")

    # 성능 테스트는 시간이 오래 걸릴 수 있으므로 기본 타임아웃 증가
    if options is None:
        options = []

    if not any(opt.startswith("--timeout=") for opt in options):
        options.append("--timeout=300")

    return run_pytest("tests/performance", ["performance"], options)


def run_all_tests(options: Optional[List[str]] = None) -> bool:
    """
    모든 테스트 실행

    Args:
        options: pytest 옵션

    Returns:
        bool: 성공 여부
    """
    print_section("모든 테스트 실행")

    # 느린 테스트 제외 옵션
    if options is None:
        options = []

    if not any(opt == "-m" for opt in options):
        options.extend(["-k", "not slow"])

    return run_pytest("tests", None, options)


def run_smoke_tests(options: Optional[List[str]] = None) -> bool:
    """
    스모크 테스트 실행

    Args:
        options: pytest 옵션

    Returns:
        bool: 성공 여부
    """
    print_section("스모크 테스트 실행")
    return run_pytest("tests", ["smoke"], options)


def generate_coverage_report(options: Optional[List[str]] = None) -> bool:
    """
    코드 커버리지 보고서 생성

    Args:
        options: Jest 옵션

    Returns:
        bool: 성공 여부
    """
    print_section("코드 커버리지 보고서 생성")

    # Jest 커버리지 실행
    command = ["npm", "test", "--", "--coverage"]

    if options:
        command.extend(options)

    result = run_command(command)

    if result.returncode == 0:
        print(colorize("커버리지 보고서가 'coverage' 디렉토리에 생성되었습니다.", "GREEN"))

    return result.returncode == 0


def main() -> int:
    """
    메인 함수

    Returns:
        int: 종료 코드
    """
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description="테스트 실행 스크립트")

    parser.add_argument(
        "--type",
        choices=["unit", "integration", "api", "database", "performance", "all", "smoke", "coverage"],
        default="all",
        help="실행할 테스트 유형 (기본값: all)"
    )

    parser.add_argument(
        "--path",
        type=str,
        help="특정 테스트 경로 실행"
    )

    parser.add_argument(
        "--markers",
        type=str,
        help="실행할 테스트 마커 (쉼표로 구분)"
    )

    parser.add_argument(
        "--options",
        type=str,
        help="pytest 옵션 (쉼표로 구분)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="상세 출력 활성화"
    )

    parser.add_argument(
        "--no-capture",
        action="store_true",
        help="출력 캡처 비활성화"
    )

    parser.add_argument(
        "--pdb",
        action="store_true",
        help="실패 시 디버거 실행"
    )

    args = parser.parse_args()

    # 테스트 시작 시간
    start_time = time.time()

    # 헤더 출력
    print_header("JaePa 테스트 실행")

    # pytest 옵션 설정
    options = []

    if args.verbose:
        options.append("-v")

    if args.no_capture:
        options.append("-s")

    if args.pdb:
        options.append("--pdb")

    if args.options:
        options.extend(args.options.split(","))

    # 특정 경로 테스트
    if args.path:
        print_section(f"경로 테스트 실행: {args.path}")

        markers = args.markers.split(",") if args.markers else None
        success = run_pytest(args.path, markers, options)

        elapsed_time = time.time() - start_time
        print(colorize(f"\n총 소요 시간: {elapsed_time:.2f}초", "YELLOW"))

        return 0 if success else 1

    # 테스트 유형별 실행
    success = True

    if args.type == "unit":
        success = run_unit_tests(options)
    elif args.type == "integration":
        success = run_integration_tests(options)
    elif args.type == "api":
        success = run_api_tests(options)
    elif args.type == "database":
        success = run_database_tests(options)
    elif args.type == "performance":
        success = run_performance_tests(options)
    elif args.type == "smoke":
        success = run_smoke_tests(options)
    elif args.type == "coverage":
        success = generate_coverage_report(options)
    else:  # all
        success = run_all_tests(options)

    # 테스트 종료 시간
    elapsed_time = time.time() - start_time

    # 결과 출력
    print("\n" + "=" * 80)
    if success:
        print(colorize(" 테스트 성공 ", "GREEN"))
    else:
        print(colorize(" 테스트 실패 ", "RED"))
    print("=" * 80)

    print(colorize(f"\n총 소요 시간: {elapsed_time:.2f}초", "YELLOW"))

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
