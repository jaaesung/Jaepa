"""
크롤링 기능 개선 통합 스크립트

개선된 모듈을 원래 모듈과 통합하는 스크립트입니다.
이 스크립트는 백업을 만들고 개선된 모듈을 적용합니다.
"""
import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('integrate_improvements.log', 'w')
    ]
)
logger = logging.getLogger(__name__)

# 프로젝트 폴더 설정
project_dir = Path(__file__).parent
tests_dir = project_dir.parent / 'tests' / 'crawling'

# 백업 폴더 설정
backup_dir = project_dir / 'backup' / datetime.now().strftime('%Y%m%d_%H%M%S')


def create_backup():
    """
    원래 파일의 백업 생성
    """
    logger.info(f"백업 디렉토리 생성: {backup_dir}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 원본 모듈 백업
    files_to_backup = [
        'news_sources_enhanced.py',
        'news_integrator.py'
    ]
    
    for file in files_to_backup:
        source_path = project_dir / file
        if source_path.exists():
            dest_path = backup_dir / file
            shutil.copy2(source_path, dest_path)
            logger.info(f"파일 백업 완료: {file}")
        else:
            logger.warning(f"백업할 파일을 찾을 수 없음: {file}")
    
    # 테스트 파일 백업
    test_backup_dir = backup_dir / 'tests'
    test_backup_dir.mkdir(exist_ok=True)
    
    test_files_to_backup = [
        'test_finnhub_api.py',
        'test_newsdata_api.py',
        'test_news_integrator.py',
        'test_news_integrator_api.py'
    ]
    
    for file in test_files_to_backup:
        source_path = tests_dir / file
        if source_path.exists():
            dest_path = test_backup_dir / file
            shutil.copy2(source_path, dest_path)
            logger.info(f"테스트 파일 백업 완료: {file}")
        else:
            logger.warning(f"백업할 테스트 파일을 찾을 수 없음: {file}")
    
    logger.info("모든 파일 백업 완료")


def integrate_modules():
    """
    개선된 모듈을 원래 모듈과 통합
    """
    # 모듈 통합
    modules_to_integrate = [
        ('news_sources_enhanced_improved.py', 'news_sources_enhanced.py'),
        ('news_integrator_improved.py', 'news_integrator.py')
    ]
    
    for source, dest in modules_to_integrate:
        source_path = project_dir / source
        dest_path = project_dir / dest
        
        if source_path.exists():
            shutil.copy2(source_path, dest_path)
            logger.info(f"모듈 통합 완료: {source} -> {dest}")
        else:
            logger.error(f"통합할 개선된 모듈을 찾을 수 없음: {source}")
    
    # 테스트 파일 통합
    test_modules_to_integrate = [
        ('test_finnhub_api_improved.py', 'test_finnhub_api.py'),
        ('test_newsdata_api_improved.py', 'test_newsdata_api.py'),
        ('test_news_integrator_improved.py', 'test_news_integrator.py')
    ]
    
    for source, dest in test_modules_to_integrate:
        source_path = tests_dir / source
        dest_path = tests_dir / dest
        
        if source_path.exists():
            shutil.copy2(source_path, dest_path)
            logger.info(f"테스트 모듈 통합 완료: {source} -> {dest}")
        else:
            logger.error(f"통합할 개선된 테스트 모듈을 찾을 수 없음: {source}")
    
    logger.info("모든 모듈 통합 완료")


def verify_integration():
    """
    통합 결과 검증
    """
    # 모듈 존재 확인
    modules_to_check = [
        'news_sources_enhanced.py',
        'news_integrator.py'
    ]
    
    for module in modules_to_check:
        module_path = project_dir / module
        if not module_path.exists():
            logger.error(f"통합된 모듈이 존재하지 않음: {module}")
            return False
    
    # 테스트 파일 존재 확인
    test_modules_to_check = [
        'test_finnhub_api.py',
        'test_newsdata_api.py',
        'test_news_integrator.py'
    ]
    
    for module in test_modules_to_check:
        module_path = tests_dir / module
        if not module_path.exists():
            logger.error(f"통합된 테스트 모듈이 존재하지 않음: {module}")
            return False
    
    logger.info("모든 통합 검증 완료")
    return True


def run_tests():
    """
    개선된 테스트 실행
    """
    logger.info("개선된 테스트 실행 중...")
    
    test_script = tests_dir / 'run_crawling_tests.py'
    if not test_script.exists():
        logger.error(f"테스트 실행 스크립트를 찾을 수 없음: {test_script}")
        return False
    
    try:
        # 테스트 실행
        import subprocess
        
        # 개별 API 테스트 실행
        apis = ['rss', 'finnhub', 'newsdata', 'sentiment', 'integrator']
        for api in apis:
            logger.info(f"{api} API 테스트 실행 중...")
            result = subprocess.run(
                [sys.executable, str(test_script), f"--api={api}"],
                cwd=str(tests_dir),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"{api} API 테스트 성공")
            else:
                logger.error(f"{api} API 테스트 실패: {result.stderr}")
        
        # 전체 통합 테스트 실행
        logger.info("전체 통합 테스트 실행 중...")
        result = subprocess.run(
            [sys.executable, str(tests_dir / 'run_all_tests.py')],
            cwd=str(tests_dir),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("전체 통합 테스트 성공")
            return True
        else:
            logger.error(f"전체 통합 테스트 실패: {result.stderr}")
            return False
        
    except Exception as e:
        logger.error(f"테스트 실행 중 오류 발생: {str(e)}")
        return False


def main():
    """
    메인 함수
    """
    logger.info("크롤링 기능 개선 통합 스크립트 시작")
    
    try:
        # 백업 생성
        create_backup()
        
        # 모듈 통합
        integrate_modules()
        
        # 통합 검증
        if not verify_integration():
            logger.error("통합 검증 실패, 롤백 필요")
            return
        
        # 테스트 실행
        if not run_tests():
            logger.warning("일부 테스트 실패, 수동 확인 필요")
        
        logger.info("크롤링 기능 개선 통합 완료")
        
    except Exception as e:
        logger.error(f"통합 중 예상치 못한 오류 발생: {str(e)}")


if __name__ == "__main__":
    main()
