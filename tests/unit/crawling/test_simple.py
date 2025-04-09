"""
간단한 크롤링 테스트 모듈
"""
import unittest


class TestSimpleCrawling(unittest.TestCase):
    """
    간단한 크롤링 테스트 클래스
    """
    
    def test_simple_crawling(self):
        """
        간단한 크롤링 테스트
        """
        data = {"url": "https://example.com", "content": "Example content"}
        self.assertEqual(data["url"], "https://example.com")


if __name__ == "__main__":
    unittest.main()
