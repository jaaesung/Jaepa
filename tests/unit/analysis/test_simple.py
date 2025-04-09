"""
간단한 테스트 모듈
"""
import unittest


class TestSimple(unittest.TestCase):
    """
    간단한 테스트 클래스
    """
    
    def test_simple(self):
        """
        간단한 테스트
        """
        self.assertEqual(1 + 1, 2)


if __name__ == "__main__":
    unittest.main()
