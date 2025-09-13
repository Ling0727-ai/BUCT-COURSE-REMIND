"""
U校园API客户端 - 主要的网络请求和业务逻辑
"""

import requests
import json
from typing import Dict, Any, Optional

# 处理导入问题 - 支持直接运行和作为包导入
try:
    # 作为包导入
    from .aes_crypto import encrypt
    from .exceptions import ULoginError, UNetworkError, UApiError
except ImportError:
    # 直接运行时导入
    from aes_crypto import encrypt
    from exceptions import ULoginError, UNetworkError, UApiError

class UClient:
    """U校园API客户端"""
    
    BASE_URL = "https://u.unipus.cn"
    LOGIN_URL = f"https://sso.unipus.cn/sso/0.1/sso/cip/login"
    
    def __init__(self, timeout: int = 30):
        """
        初始化U校园客户端
        
        Args:
            timeout: 请求超时时间（秒）
        """
        self.session = requests.Session()
        self.timeout = timeout
        self._is_logged_in = False
        
        # 设置默认请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/json;charset=UTF-8',
        })
    
    def login(self, username: str, password: str, school_id: str = "") -> bool:
        """
        登录U校园
        
        Args:
            username: 用户名
            password: 密码
            school_id: 学校ID（可选）
            
        Returns:
            bool: 登录是否成功
            
        Raises:
            ULoginError: 登录失败时抛出
            UNetworkError: 网络错误时抛出
        """
        try:
            # 加密用户名和密码
            encrypted_username = encrypt(username)
            encrypted_password = encrypt(password)
            
            # 构建登录数据
            login_data = {
                "service": "https://u.unipus.cn/user/comm/login?school_id=",
                "username": encrypted_username,
                "password": encrypted_password,
                "captcha": "",
                "rememberMe": "on",
                "captchaCode": ""
            }

            
            # 发送登录请求
            response = self.session.post(
                self.LOGIN_URL,
                data=json.dumps(login_data),
                timeout=self.timeout
            )
            
            # 检查响应状态
            if response.status_code != 200:
                raise ULoginError(f"登录失败，状态码: {response.status_code}", response.status_code)
            
            # 解析响应数据
            try:
                result = response.json()
            except json.JSONDecodeError as e:
                raise UApiError(f"响应数据格式错误: {e}")
                
            # 检查登录是否成功 - u校园API返回code为"0"表示成功
            if result.get("code") != "0":
                raise ULoginError(result.get("msg", "登录失败"))
            
            self._is_logged_in = True
            return True
            
        except requests.exceptions.Timeout:
            raise UNetworkError("登录请求超时")
        except requests.exceptions.ConnectionError:
            raise UNetworkError("网络连接错误")
        except requests.exceptions.RequestException as e:
            raise UNetworkError(f"网络请求错误: {str(e)}")
        except json.JSONDecodeError:
            raise UApiError("响应数据格式错误")
    
    def get_courses(self) -> Dict[str, Any]:
        """获取课程列表"""
        if not self._is_logged_in:
            raise ULoginError("请先登录")
        
        # 实现获取课程列表的逻辑
        # TODO: 实现具体的API调用
        return {"courses": []}
    
    def get_assignments(self, course_id: str) -> Dict[str, Any]:
        """获取课程作业"""
        if not self._is_logged_in:
            raise ULoginError("请先登录")
        
        # TODO: 实现获取作业的逻辑
        return {"assignments": []}
    
    def logout(self):
        """注销登录"""
        self.session = requests.Session()
        self._is_logged_in = False
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self._is_logged_in
    
    def get_session(self) -> requests.Session:
        """获取当前会话"""
        if not self._is_logged_in:
            raise ULoginError("请先登录")
        return self.session