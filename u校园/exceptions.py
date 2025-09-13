"""
异常处理模块 - U校园API异常定义
"""

class UError(Exception):
    """U校园基础异常类"""
    pass

class ULoginError(UError):
    """登录异常"""
    def __init__(self, message="登录失败", status_code=None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class UNetworkError(UError):
    """网络异常"""
    def __init__(self, message="网络连接错误"):
        self.message = message
        super().__init__(self.message)

class UApiError(UError):
    """API接口异常"""
    def __init__(self, message="API调用失败", error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class UEncryptionError(UError):
    """加密解密异常"""
    def __init__(self, message="加密解密错误"):
        self.message = message
        super().__init__(self.message)

class UValidationError(UError):
    """数据验证异常"""
    def __init__(self, message="数据验证失败"):
        self.message = message
        super().__init__(self.message)