import requests

class BUCTAuth:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://course.buct.edu.cn"
    
    def login(self, username, password):
        """登录到北化课程平台"""
        login_url = f"{self.base_url}/meol/loginCheck.do"
        response = self.session.post(login_url, data={
            "IPT_LOGINUSERNAME": username,
            "IPT_LOGINPASSWORD": password
        })
        return response.status_code == 200
    
    def get_session(self):
        """获取登录后的session"""
        return self.session