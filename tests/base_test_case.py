import unittest
import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path


class BaseTestCase(unittest.TestCase):
    """
    테스트 베이스 클래스
    
    모든 테스트 클래스가 상속받아 사용할 수 있는 공통 기능 제공
    """
    
    def setUp(self):
        """
        테스트 설정
        
        - 환경 변수 설정
        - 공통 패치 설정
        """
        # 테스트용 환경변수 설정
        self.env_patcher = patch.dict('os.environ', {
            'POLYGON_API_KEY': 'test_key',
            'MONGO_URI': 'mongodb://localhost:27017/',
            'TEST_MODE': 'True'
        })
        self.env_patcher.start()
        
        # 실제 API 호출 방지를 위한 공통 패치
        self.patch_requests = patch('requests.get')
        self.mock_requests = self.patch_requests.start()
    
    def tearDown(self):
        """
        테스트 종료 처리
        
        - 환경 변수 패치 복원
        - 공통 패치 복원
        """
        # 환경변수 패치 복원
        self.env_patcher.stop()
        
        # 공통 패치 복원
        self.patch_requests.stop()
    
    def create_mock_response(self, data, status_code=200, content=None):
        """
        API 응답 모킹용 헬퍼 메서드
        
        Args:
            data: JSON 응답으로 반환할 데이터
            status_code: HTTP 상태 코드
            content: 바이너리 콘텐츠 (있는 경우)
            
        Returns:
            MagicMock: 모의 응답 객체
        """
        mock_response = MagicMock()
        mock_response.json.return_value = data
        mock_response.status_code = status_code
        mock_response.text = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
        
        if content:
            mock_response.content = content
        else:
            mock_response.content = json.dumps(data).encode() if isinstance(data, (dict, list)) else str(data).encode()
            
        return mock_response
    
    def load_fixture(self, filename):
        """
        테스트 픽스처 파일 로드
        
        Args:
            filename: 픽스처 파일 이름
            
        Returns:
            dict: 로드된 JSON 데이터
        """
        fixture_path = Path(__file__).parent / "fixtures" / filename
        
        if not fixture_path.exists():
            self.fail(f"픽스처 파일을 찾을 수 없습니다: {fixture_path}")
            
        with open(fixture_path, 'r', encoding='utf-8') as f:
            return json.load(f)
