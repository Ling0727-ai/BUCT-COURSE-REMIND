"""
u校园 (U Campus) API 客户端库

提供北化大学U校园平台的自动化接口，包括登录、课程管理、作业提交等功能。
"""

from .aes_crypto import encrypt, decrypt
from .api_client import UClient
from .exceptions import ULoginError, UNetworkError

__version__ = "1.0.0"
__author__ = "BUCT Course Remind System"
__all__ = ['encrypt', 'decrypt', 'UClient', 'ULoginError', 'UNetworkError']