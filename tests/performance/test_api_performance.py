"""
API 성능 테스트

이 모듈은 API 엔드포인트의 성능을 테스트합니다.
"""
import pytest
import time
import statistics
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

# 성능 테스트 설정
BASE_URL = "http://localhost:8000"
REQUEST_COUNT = 100
CONCURRENT_REQUESTS = 10


@pytest.mark.performance
class TestAPIPerformance:
    """
    API 성능 테스트 클래스
    """
    
    @pytest.fixture(autouse=True)
    def setup_test(self, api_client):
        """
        테스트 설정
        
        Args:
            api_client: FastAPI 테스트 클라이언트 fixture
        """
        self.api_client = api_client
        
        # 서버가 실행 중인지 확인
        try:
            response = self.api_client.get("/api/health")
            if response.status_code != 200:
                pytest.skip("API 서버가 실행되지 않았습니다.")
        except Exception:
            pytest.skip("API 서버가 실행되지 않았습니다.")
    
    def measure_response_time(self, endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> float:
        """
        응답 시간 측정
        
        Args:
            endpoint: API 엔드포인트
            method: HTTP 메서드
            data: 요청 데이터
            
        Returns:
            float: 응답 시간 (초)
        """
        start_time = time.time()
        
        if method == "GET":
            response = self.api_client.get(endpoint)
        elif method == "POST":
            response = self.api_client.post(endpoint, json=data)
        elif method == "PUT":
            response = self.api_client.put(endpoint, json=data)
        elif method == "PATCH":
            response = self.api_client.patch(endpoint, json=data)
        elif method == "DELETE":
            response = self.api_client.delete(endpoint)
        else:
            raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
        
        end_time = time.time()
        
        # 응답 확인
        assert 200 <= response.status_code < 500, f"API 호출 실패: {response.status_code} - {response.text}"
        
        return end_time - start_time
    
    async def async_measure_response_time(self, session: aiohttp.ClientSession, endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> float:
        """
        비동기 응답 시간 측정
        
        Args:
            session: aiohttp 세션
            endpoint: API 엔드포인트
            method: HTTP 메서드
            data: 요청 데이터
            
        Returns:
            float: 응답 시간 (초)
        """
        url = f"{BASE_URL}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                async with session.get(url) as response:
                    await response.text()
            elif method == "POST":
                async with session.post(url, json=data) as response:
                    await response.text()
            elif method == "PUT":
                async with session.put(url, json=data) as response:
                    await response.text()
            elif method == "PATCH":
                async with session.patch(url, json=data) as response:
                    await response.text()
            elif method == "DELETE":
                async with session.delete(url) as response:
                    await response.text()
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
            
            end_time = time.time()
            return end_time - start_time
            
        except Exception as e:
            print(f"API 호출 중 오류 발생: {str(e)}")
            return -1
    
    async def run_concurrent_requests(self, endpoint: str, method: str = "GET", data: Dict[str, Any] = None, count: int = 10) -> List[float]:
        """
        동시 요청 실행
        
        Args:
            endpoint: API 엔드포인트
            method: HTTP 메서드
            data: 요청 데이터
            count: 요청 수
            
        Returns:
            List[float]: 응답 시간 목록
        """
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.async_measure_response_time(session, endpoint, method, data)
                for _ in range(count)
            ]
            return await asyncio.gather(*tasks)
    
    def analyze_response_times(self, response_times: List[float]) -> Dict[str, float]:
        """
        응답 시간 분석
        
        Args:
            response_times: 응답 시간 목록
            
        Returns:
            Dict[str, float]: 분석 결과
        """
        # 오류 응답 제외
        valid_times = [t for t in response_times if t > 0]
        
        if not valid_times:
            return {
                "min": 0,
                "max": 0,
                "mean": 0,
                "median": 0,
                "p95": 0,
                "p99": 0,
                "success_rate": 0
            }
        
        # 정렬
        sorted_times = sorted(valid_times)
        
        # 백분위수 계산
        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)
        
        return {
            "min": min(sorted_times),
            "max": max(sorted_times),
            "mean": statistics.mean(sorted_times),
            "median": statistics.median(sorted_times),
            "p95": sorted_times[p95_index - 1] if p95_index > 0 else sorted_times[-1],
            "p99": sorted_times[p99_index - 1] if p99_index > 0 else sorted_times[-1],
            "success_rate": len(valid_times) / len(response_times)
        }
    
    def print_performance_results(self, endpoint: str, results: Dict[str, float]) -> None:
        """
        성능 결과 출력
        
        Args:
            endpoint: API 엔드포인트
            results: 분석 결과
        """
        print(f"\n성능 테스트 결과: {endpoint}")
        print(f"최소 응답 시간: {results['min']:.4f}초")
        print(f"최대 응답 시간: {results['max']:.4f}초")
        print(f"평균 응답 시간: {results['mean']:.4f}초")
        print(f"중앙값 응답 시간: {results['median']:.4f}초")
        print(f"95 백분위수 응답 시간: {results['p95']:.4f}초")
        print(f"99 백분위수 응답 시간: {results['p99']:.4f}초")
        print(f"성공률: {results['success_rate'] * 100:.2f}%")
    
    @pytest.mark.slow
    def test_latest_news_performance(self):
        """
        최신 뉴스 API 성능 테스트
        """
        endpoint = "/api/news/latest"
        
        # 단일 요청 테스트
        response_time = self.measure_response_time(endpoint)
        print(f"\n단일 요청 응답 시간: {response_time:.4f}초")
        
        # 순차적 요청 테스트
        sequential_times = []
        for _ in range(10):
            sequential_times.append(self.measure_response_time(endpoint))
        
        sequential_results = self.analyze_response_times(sequential_times)
        self.print_performance_results(f"{endpoint} (순차적 요청)", sequential_results)
        
        # 동시 요청 테스트
        concurrent_times = asyncio.run(self.run_concurrent_requests(endpoint, count=CONCURRENT_REQUESTS))
        
        concurrent_results = self.analyze_response_times(concurrent_times)
        self.print_performance_results(f"{endpoint} (동시 요청)", concurrent_results)
        
        # 성능 기준 검증
        assert sequential_results["mean"] < 0.5, f"평균 응답 시간이 너무 깁니다: {sequential_results['mean']:.4f}초"
        assert concurrent_results["p95"] < 1.0, f"95 백분위수 응답 시간이 너무 깁니다: {concurrent_results['p95']:.4f}초"
        assert concurrent_results["success_rate"] > 0.95, f"성공률이 너무 낮습니다: {concurrent_results['success_rate'] * 100:.2f}%"
    
    @pytest.mark.slow
    def test_search_news_performance(self):
        """
        뉴스 검색 API 성능 테스트
        """
        endpoint = "/api/news/search?keyword=테스트"
        
        # 단일 요청 테스트
        response_time = self.measure_response_time(endpoint)
        print(f"\n단일 요청 응답 시간: {response_time:.4f}초")
        
        # 순차적 요청 테스트
        sequential_times = []
        for _ in range(10):
            sequential_times.append(self.measure_response_time(endpoint))
        
        sequential_results = self.analyze_response_times(sequential_times)
        self.print_performance_results(f"{endpoint} (순차적 요청)", sequential_results)
        
        # 동시 요청 테스트
        concurrent_times = asyncio.run(self.run_concurrent_requests(endpoint, count=CONCURRENT_REQUESTS))
        
        concurrent_results = self.analyze_response_times(concurrent_times)
        self.print_performance_results(f"{endpoint} (동시 요청)", concurrent_results)
        
        # 성능 기준 검증
        assert sequential_results["mean"] < 0.5, f"평균 응답 시간이 너무 깁니다: {sequential_results['mean']:.4f}초"
        assert concurrent_results["p95"] < 1.0, f"95 백분위수 응답 시간이 너무 깁니다: {concurrent_results['p95']:.4f}초"
        assert concurrent_results["success_rate"] > 0.95, f"성공률이 너무 낮습니다: {concurrent_results['success_rate'] * 100:.2f}%"
    
    @pytest.mark.slow
    def test_news_by_symbol_performance(self):
        """
        심볼별 뉴스 API 성능 테스트
        """
        endpoint = "/api/news/symbol/AAPL"
        
        # 단일 요청 테스트
        response_time = self.measure_response_time(endpoint)
        print(f"\n단일 요청 응답 시간: {response_time:.4f}초")
        
        # 순차적 요청 테스트
        sequential_times = []
        for _ in range(10):
            sequential_times.append(self.measure_response_time(endpoint))
        
        sequential_results = self.analyze_response_times(sequential_times)
        self.print_performance_results(f"{endpoint} (순차적 요청)", sequential_results)
        
        # 동시 요청 테스트
        concurrent_times = asyncio.run(self.run_concurrent_requests(endpoint, count=CONCURRENT_REQUESTS))
        
        concurrent_results = self.analyze_response_times(concurrent_times)
        self.print_performance_results(f"{endpoint} (동시 요청)", concurrent_results)
        
        # 성능 기준 검증
        assert sequential_results["mean"] < 0.5, f"평균 응답 시간이 너무 깁니다: {sequential_results['mean']:.4f}초"
        assert concurrent_results["p95"] < 1.0, f"95 백분위수 응답 시간이 너무 깁니다: {concurrent_results['p95']:.4f}초"
        assert concurrent_results["success_rate"] > 0.95, f"성공률이 너무 낮습니다: {concurrent_results['success_rate'] * 100:.2f}%"
    
    @pytest.mark.slow
    def test_create_news_performance(self):
        """
        뉴스 생성 API 성능 테스트
        """
        endpoint = "/api/news"
        
        # 테스트 데이터 생성
        def create_test_data(index: int) -> Dict[str, Any]:
            return {
                "title": f"성능 테스트 뉴스 {index}",
                "url": f"https://example.com/perf_test_{index}_{int(time.time())}",
                "source": "성능 테스트 소스",
                "published_date": datetime.now().isoformat(),
                "content": f"성능 테스트 뉴스 {index}의 내용입니다.",
                "summary": f"성능 테스트 뉴스 {index}의 요약입니다.",
                "keywords": ["성능", "테스트", f"키워드{index}"],
                "symbols": ["TEST"],
                "categories": ["테스트"]
            }
        
        # 단일 요청 테스트
        response_time = self.measure_response_time(endpoint, method="POST", data=create_test_data(0))
        print(f"\n단일 요청 응답 시간: {response_time:.4f}초")
        
        # 순차적 요청 테스트
        sequential_times = []
        for i in range(10):
            sequential_times.append(self.measure_response_time(endpoint, method="POST", data=create_test_data(i + 1)))
        
        sequential_results = self.analyze_response_times(sequential_times)
        self.print_performance_results(f"{endpoint} (순차적 요청)", sequential_results)
        
        # 동시 요청 테스트
        test_data_list = [create_test_data(i + 11) for i in range(CONCURRENT_REQUESTS)]
        
        async def run_concurrent_create_requests():
            async with aiohttp.ClientSession() as session:
                tasks = [
                    self.async_measure_response_time(session, endpoint, method="POST", data=data)
                    for data in test_data_list
                ]
                return await asyncio.gather(*tasks)
        
        concurrent_times = asyncio.run(run_concurrent_create_requests())
        
        concurrent_results = self.analyze_response_times(concurrent_times)
        self.print_performance_results(f"{endpoint} (동시 요청)", concurrent_results)
        
        # 성능 기준 검증
        assert sequential_results["mean"] < 0.5, f"평균 응답 시간이 너무 깁니다: {sequential_results['mean']:.4f}초"
        assert concurrent_results["p95"] < 1.0, f"95 백분위수 응답 시간이 너무 깁니다: {concurrent_results['p95']:.4f}초"
        assert concurrent_results["success_rate"] > 0.95, f"성공률이 너무 낮습니다: {concurrent_results['success_rate'] * 100:.2f}%"
