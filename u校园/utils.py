"""
工具函数模块 - 提供辅助功能
"""

import re
from typing import Dict, Any, Optional
from datetime import datetime
from .exceptions import UValidationError

def validate_username(username: str) -> bool:
    """
    验证用户名格式
    
    Args:
        username: 用户名
        
    Returns:
        bool: 是否有效
    """
    if not username or not isinstance(username, str):
        return False
    
    # 简单的用户名格式验证（可根据实际需求调整）
    if len(username) < 3 or len(username) > 50:
        return False
    
    # 允许字母、数字、下划线
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False
    
    return True

def validate_password(password: str) -> bool:
    """
    验证密码格式
    
    Args:
        password: 密码
        
    Returns:
        bool: 是否有效
    """
    if not password or not isinstance(password, str):
        return False
    
    # 密码长度要求
    if len(password) < 6 or len(password) > 50:
        return False
    
    return True

def parse_datetime(datetime_str: str) -> Optional[datetime]:
    """
    解析U校园日期时间字符串
    
    Args:
        datetime_str: 日期时间字符串
        
    Returns:
        datetime对象或None
    """
    if not datetime_str:
        return None
    
    try:
        # 尝试解析常见格式
        formats = [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
            '%Y年%m月%d日 %H:%M'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
        
        return None
    except (ValueError, TypeError):
        return None

def format_duration(seconds: int) -> str:
    """
    格式化时间间隔
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化后的时间字符串
    """
    if seconds < 0:
        return "已过期"
    
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    
    if days > 0:
        return f"{days}天{hours}小时"
    elif hours > 0:
        return f"{hours}小时{minutes}分钟"
    else:
        return f"{minutes}分钟"

def sanitize_input(input_str: str, max_length: int = 100) -> str:
    """
    清理用户输入
    
    Args:
        input_str: 输入字符串
        max_length: 最大长度限制
        
    Returns:
        清理后的字符串
    """
    if not input_str:
        return ""
    
    # 去除前后空格
    cleaned = input_str.strip()
    
    # 限制长度
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    # 移除可能的危险字符
    cleaned = re.sub(r'[<>"\'&]', '', cleaned)
    
    return cleaned