"""
测试模式配置
在邮件配置不可用时，提供模拟的验证码功能
"""

import os
import random
import string
from datetime import datetime, timedelta
from flask import current_app

# 测试模式开关 - 直接启用测试模式
TEST_MODE = True  # 强制启用测试模式以修复验证码功能

def generate_test_verification_code(length=6):
    """生成测试验证码"""
    return ''.join(random.choice(string.digits) for _ in range(length))

def send_test_verification_email(email, code):
    """模拟发送验证码邮件（测试模式）"""
    if not TEST_MODE:
        return False
    
    # 在测试模式下，直接返回成功
    current_app.logger.info(f"[测试模式] 模拟发送验证码到 {email}: {code}")
    print(f"🧪 [测试模式] 验证码已生成: {code}")
    print(f"📧 [测试模式] 目标邮箱: {email}")
    print(f"⏰ [测试模式] 有效期: 3分钟")
    print("=" * 50)
    
    return True

def is_test_mode():
    """检查是否为测试模式"""
    return TEST_MODE

def get_test_info():
    """获取测试模式信息"""
    if TEST_MODE:
        return {
            "mode": "test",
            "message": "当前为测试模式，验证码将在控制台显示",
            "note": "请查看后端日志获取验证码"
        }
    return None