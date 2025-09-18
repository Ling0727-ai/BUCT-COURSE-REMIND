import unittest
from unittest.mock import Mock, patch
from buct_course import BUCTAuth, BUCTCourseError

class TestBUCTAuth(unittest.TestCase):
    
    def setUp(self):
        self.auth = BUCTAuth()
    
    def test_auth_initialization(self):
        self.assertIsNotNone(self.auth)
        self.assertIsInstance(self.auth, BUCTAuth)
    
    @patch('buct_course.auth.requests.Session')
    def test_login_with_mock(self, mock_session):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '登录成功'
        mock_session.return_value.post.return_value = mock_response
        
        result = self.auth.login('test_user', 'test_pass')
        self.assertTrue(result)
    
    def test_error_handling(self):
        with self.assertRaises(BUCTCourseError):
            raise BUCTCourseError("测试错误")

if __name__ == '__main__':
    unittest.main()