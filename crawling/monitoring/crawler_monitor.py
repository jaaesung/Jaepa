"""
크롤러 모니터링 모듈

크롤링 작업의 성능과 상태를 모니터링하는 기능을 제공합니다.
"""
import os
import time
import json
import logging
import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import threading
import statistics
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
env_path = Path(__file__).parents[2] / '.env'
load_dotenv(dotenv_path=env_path)


class CrawlerMonitor:
    """
    크롤러 모니터링 클래스
    
    크롤링 작업의 성능, 상태, 오류 등을 모니터링하고 기록합니다.
    """
    
    def __init__(self, db_connect: bool = True):
        """
        CrawlerMonitor 클래스 초기화
        
        Args:
            db_connect: MongoDB 연결 여부 (기본값: True)
        """
        self.stats = {
            "start_time": None,
            "end_time": None,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_articles": 0,
            "request_times": [],
            "errors": [],
            "warnings": [],
            "sources": {}
        }
        
        self.running = False
        self.lock = threading.RLock()
        
        # 로그 디렉토리 설정
        self.log_dir = Path(__file__).parents[2] / "logs" / "crawler"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # MongoDB 연결
        if db_connect:
            mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
            mongo_db_name = os.getenv("MONGO_DB_NAME", "jaepa")
            
            try:
                self.client = MongoClient(mongo_uri)
                self.db = self.client[mongo_db_name]
                self.stats_collection = self.db.crawler_stats
                
                # 인덱스 생성
                self.stats_collection.create_index("start_time")
                self.stats_collection.create_index("source")
                
                logger.info("MongoDB 연결 성공")
            except Exception as e:
                logger.error(f"MongoDB 연결 실패: {str(e)}")
                self.client = None
                self.db = None
                self.stats_collection = None
        else:
            self.client = None
            self.db = None
            self.stats_collection = None
    
    def start_monitoring(self):
        """
        모니터링 시작
        """
        with self.lock:
            self.running = True
            self.stats["start_time"] = datetime.datetime.now()
            self.stats["end_time"] = None
            self.stats["total_requests"] = 0
            self.stats["successful_requests"] = 0
            self.stats["failed_requests"] = 0
            self.stats["total_articles"] = 0
            self.stats["request_times"] = []
            self.stats["errors"] = []
            self.stats["warnings"] = []
            self.stats["sources"] = {}
            
            logger.info("크롤러 모니터링 시작")
    
    def stop_monitoring(self):
        """
        모니터링 종료
        """
        with self.lock:
            if not self.running:
                logger.warning("모니터링이 이미 종료되었습니다.")
                return
            
            self.running = False
            self.stats["end_time"] = datetime.datetime.now()
            
            # 통계 계산
            self.calculate_stats()
            
            # 로그 저장
            self.save_stats()
            
            logger.info("크롤러 모니터링 종료")
    
    def record_request(self, url: str, source: str, success: bool, response_time: float, status_code: Optional[int] = None):
        """
        HTTP 요청 기록
        
        Args:
            url: 요청 URL
            source: 뉴스 소스 이름
            success: 요청 성공 여부
            response_time: 응답 시간(초)
            status_code: HTTP 상태 코드 (선택 사항)
        """
        if not self.running:
            logger.warning("모니터링이 시작되지 않았습니다.")
            return
        
        with self.lock:
            self.stats["total_requests"] += 1
            self.stats["request_times"].append(response_time)
            
            # 소스별 통계
            if source not in self.stats["sources"]:
                self.stats["sources"][source] = {
                    "requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "articles": 0,
                    "request_times": []
                }
            
            self.stats["sources"][source]["requests"] += 1
            self.stats["sources"][source]["request_times"].append(response_time)
            
            if success:
                self.stats["successful_requests"] += 1
                self.stats["sources"][source]["successful_requests"] += 1
            else:
                self.stats["failed_requests"] += 1
                self.stats["sources"][source]["failed_requests"] += 1
                
                # 오류 기록
                error_info = {
                    "url": url,
                    "source": source,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "status_code": status_code
                }
                self.stats["errors"].append(error_info)
    
    def record_article(self, source: str):
        """
        크롤링된 기사 기록
        
        Args:
            source: 뉴스 소스 이름
        """
        if not self.running:
            logger.warning("모니터링이 시작되지 않았습니다.")
            return
        
        with self.lock:
            self.stats["total_articles"] += 1
            
            if source in self.stats["sources"]:
                self.stats["sources"][source]["articles"] += 1
    
    def record_warning(self, message: str, source: Optional[str] = None):
        """
        경고 메시지 기록
        
        Args:
            message: 경고 메시지
            source: 뉴스 소스 이름 (선택 사항)
        """
        if not self.running:
            logger.warning("모니터링이 시작되지 않았습니다.")
            return
        
        with self.lock:
            warning_info = {
                "message": message,
                "source": source,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.stats["warnings"].append(warning_info)
    
    def record_error(self, message: str, url: Optional[str] = None, source: Optional[str] = None):
        """
        오류 메시지 기록
        
        Args:
            message: 오류 메시지
            url: 관련 URL (선택 사항)
            source: 뉴스 소스 이름 (선택 사항)
        """
        if not self.running:
            logger.warning("모니터링이 시작되지 않았습니다.")
            return
        
        with self.lock:
            error_info = {
                "message": message,
                "url": url,
                "source": source,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.stats["errors"].append(error_info)
    
    def calculate_stats(self):
        """
        모니터링 통계 계산
        """
        with self.lock:
            # 전체 통계 계산
            if self.stats["request_times"]:
                self.stats["avg_response_time"] = statistics.mean(self.stats["request_times"])
                self.stats["min_response_time"] = min(self.stats["request_times"])
                self.stats["max_response_time"] = max(self.stats["request_times"])
                
                if len(self.stats["request_times"]) > 1:
                    self.stats["stdev_response_time"] = statistics.stdev(self.stats["request_times"])
                else:
                    self.stats["stdev_response_time"] = 0
            else:
                self.stats["avg_response_time"] = 0
                self.stats["min_response_time"] = 0
                self.stats["max_response_time"] = 0
                self.stats["stdev_response_time"] = 0
            
            # 성공률 계산
            if self.stats["total_requests"] > 0:
                self.stats["success_rate"] = (self.stats["successful_requests"] / self.stats["total_requests"]) * 100
            else:
                self.stats["success_rate"] = 0
            
            # 소스별 통계 계산
            for source, source_stats in self.stats["sources"].items():
                if source_stats["request_times"]:
                    source_stats["avg_response_time"] = statistics.mean(source_stats["request_times"])
                    source_stats["min_response_time"] = min(source_stats["request_times"])
                    source_stats["max_response_time"] = max(source_stats["request_times"])
                    
                    if len(source_stats["request_times"]) > 1:
                        source_stats["stdev_response_time"] = statistics.stdev(source_stats["request_times"])
                    else:
                        source_stats["stdev_response_time"] = 0
                else:
                    source_stats["avg_response_time"] = 0
                    source_stats["min_response_time"] = 0
                    source_stats["max_response_time"] = 0
                    source_stats["stdev_response_time"] = 0
                
                # 소스별 성공률 계산
                if source_stats["requests"] > 0:
                    source_stats["success_rate"] = (source_stats["successful_requests"] / source_stats["requests"]) * 100
                else:
                    source_stats["success_rate"] = 0
    
    def save_stats(self):
        """
        모니터링 통계 저장
        """
        with self.lock:
            # MongoDB에 저장
            if self.stats_collection:
                stats_copy = self.stats.copy()
                
                # datetime 객체 변환
                if stats_copy["start_time"]:
                    stats_copy["start_time"] = stats_copy["start_time"].isoformat()
                if stats_copy["end_time"]:
                    stats_copy["end_time"] = stats_copy["end_time"].isoformat()
                
                try:
                    self.stats_collection.insert_one(stats_copy)
                    logger.info("모니터링 통계가 MongoDB에 저장되었습니다.")
                except Exception as e:
                    logger.error(f"MongoDB 저장 실패: {str(e)}")
            
            # JSON 파일로 저장
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_path = self.log_dir / f"crawler_stats_{timestamp}.json"
            
            stats_copy = self.stats.copy()
            
            # datetime 객체 변환
            if stats_copy["start_time"]:
                stats_copy["start_time"] = stats_copy["start_time"].isoformat()
            if stats_copy["end_time"]:
                stats_copy["end_time"] = stats_copy["end_time"].isoformat()
            
            with open(log_path, 'w') as f:
                json.dump(stats_copy, f, indent=2)
            
            logger.info(f"모니터링 통계가 {log_path}에 저장되었습니다.")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """
        현재 모니터링 통계 가져오기
        
        Returns:
            Dict[str, Any]: 현재 모니터링 통계
        """
        with self.lock:
            stats_copy = self.stats.copy()
            
            # datetime 객체 변환
            if stats_copy["start_time"]:
                stats_copy["start_time"] = stats_copy["start_time"].isoformat()
            if stats_copy["end_time"]:
                stats_copy["end_time"] = stats_copy["end_time"].isoformat()
            
            return stats_copy
    
    def get_historical_stats(self, days: int = 7, source: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        과거 모니터링 통계 가져오기
        
        Args:
            days: 조회할 기간(일)
            source: 뉴스 소스 이름 (선택 사항)
            
        Returns:
            List[Dict[str, Any]]: 과거 모니터링 통계 목록
        """
        if not self.stats_collection:
            logger.warning("MongoDB 연결이 설정되지 않았습니다.")
            return []
        
        # 조회 기간
        start_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        # 쿼리 조건
        query = {"start_time": {"$gte": start_date.isoformat()}}
        if source:
            query["sources." + source] = {"$exists": True}
        
        try:
            # 통계 조회
            results = list(self.stats_collection.find(query).sort("start_time", -1))
            return results
        except Exception as e:
            logger.error(f"통계 조회 실패: {str(e)}")
            return []
    
    def get_status_summary(self) -> Dict[str, Any]:
        """
        모니터링 상태 요약 가져오기
        
        Returns:
            Dict[str, Any]: 모니터링 상태 요약
        """
        with self.lock:
            if not self.running:
                return {
                    "status": "stopped",
                    "message": "모니터링이 실행 중이 아닙니다."
                }
            
            # 현재까지의 통계 계산
            self.calculate_stats()
            
            # 요약 정보
            summary = {
                "status": "running",
                "start_time": self.stats["start_time"].isoformat() if self.stats["start_time"] else None,
                "duration": str(datetime.datetime.now() - self.stats["start_time"]) if self.stats["start_time"] else None,
                "total_requests": self.stats["total_requests"],
                "successful_requests": self.stats["successful_requests"],
                "failed_requests": self.stats["failed_requests"],
                "success_rate": self.stats.get("success_rate", 0),
                "total_articles": self.stats["total_articles"],
                "sources": {}
            }
            
            # 소스별 요약 정보
            for source, source_stats in self.stats["sources"].items():
                summary["sources"][source] = {
                    "requests": source_stats["requests"],
                    "successful_requests": source_stats["successful_requests"],
                    "failed_requests": source_stats["failed_requests"],
                    "success_rate": source_stats.get("success_rate", 0),
                    "articles": source_stats["articles"]
                }
            
            return summary
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        성능 지표 가져오기
        
        Returns:
            Dict[str, Any]: 성능 지표
        """
        with self.lock:
            if not self.running:
                return {
                    "status": "stopped",
                    "message": "모니터링이 실행 중이 아닙니다."
                }
            
            # 현재까지의 통계 계산
            self.calculate_stats()
            
            # 성능 지표
            metrics = {
                "avg_response_time": self.stats.get("avg_response_time", 0),
                "min_response_time": self.stats.get("min_response_time", 0),
                "max_response_time": self.stats.get("max_response_time", 0),
                "stdev_response_time": self.stats.get("stdev_response_time", 0),
                "request_rate": self.stats["total_requests"] / ((datetime.datetime.now() - self.stats["start_time"]).total_seconds() / 60) if self.stats["start_time"] else 0,
                "article_rate": self.stats["total_articles"] / ((datetime.datetime.now() - self.stats["start_time"]).total_seconds() / 60) if self.stats["start_time"] else 0,
                "sources": {}
            }
            
            # 소스별 성능 지표
            for source, source_stats in self.stats["sources"].items():
                metrics["sources"][source] = {
                    "avg_response_time": source_stats.get("avg_response_time", 0),
                    "min_response_time": source_stats.get("min_response_time", 0),
                    "max_response_time": source_stats.get("max_response_time", 0),
                    "stdev_response_time": source_stats.get("stdev_response_time", 0)
                }
            
            return metrics
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        오류 요약 가져오기
        
        Returns:
            Dict[str, Any]: 오류 요약
        """
        with self.lock:
            if not self.running:
                return {
                    "status": "stopped",
                    "message": "모니터링이 실행 중이 아닙니다."
                }
            
            # 오류 요약
            summary = {
                "total_errors": len(self.stats["errors"]),
                "total_warnings": len(self.stats["warnings"]),
                "recent_errors": self.stats["errors"][-10:] if self.stats["errors"] else [],
                "recent_warnings": self.stats["warnings"][-10:] if self.stats["warnings"] else []
            }
            
            return summary
    
    def close(self):
        """
        모니터링 종료 및 리소스 해제
        """
        if self.running:
            self.stop_monitoring()
        
        if self.client:
            self.client.close()
            logger.info("MongoDB 연결 종료")


def get_monitor() -> CrawlerMonitor:
    """
    싱글톤 모니터 인스턴스 가져오기
    
    Returns:
        CrawlerMonitor: 모니터 인스턴스
    """
    if not hasattr(get_monitor, "instance") or get_monitor.instance is None:
        get_monitor.instance = CrawlerMonitor()
    
    return get_monitor.instance


if __name__ == "__main__":
    # 간단한 사용 예시
    monitor = CrawlerMonitor(db_connect=False)
    monitor.start_monitoring()
    
    # 요청 기록 시뮬레이션
    for i in range(10):
        monitor.record_request(
            url=f"https://example.com/article{i}",
            source="reuters",
            success=i % 3 != 0,  # 3의 배수 인덱스는 실패 처리
            response_time=0.5 + (i * 0.1),
            status_code=200 if i % 3 != 0 else 404
        )
        
        if i % 3 != 0:
            monitor.record_article(source="reuters")
        
        time.sleep(0.1)
    
    # 경고 및 오류 기록
    monitor.record_warning("속도 제한에 접근 중", source="reuters")
    monitor.record_error("파싱 오류 발생", url="https://example.com/error", source="reuters")
    
    # 모니터링 종료
    monitor.stop_monitoring()
    
    # 현재 상태 출력
    print(json.dumps(monitor.get_status_summary(), indent=2))
