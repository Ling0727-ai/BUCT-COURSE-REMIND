import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, backend_dir)

try:
    from config import Config
except ImportError:
    # 如果导入失败，使用默认配置
    class Config:
        MAIL_SMTP_SERVER = 'smtp.163.com'
        MAIL_SMTP_PORT = 465
        MAIL_SENDER = 'buct_course_remind@163.com'
        MAIL_PASSWORD = 'dummy_password_for_dev'
        VERIFY_CODE_EXPIRE = 180

from .. import mongo

class VerificationService:
    def __init__(self):
        # 使用 MongoDB 存储验证码
        self.db = mongo.db
        self.smtp_server = Config.MAIL_SMTP_SERVER
        self.smtp_port = Config.MAIL_SMTP_PORT
        self.smtp_username = Config.MAIL_SENDER
        self.smtp_password = Config.MAIL_PASSWORD
        self.verification_codes_collection = 'verification_codes'
        
    def generate_verification_code(self, length: int = 6) -> str:
        """生成验证码"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_email_verification(self, email: str, code: str) -> bool:
        """发送邮箱验证码"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = email
            msg['Subject'] = "BUCT课程提醒 - 邮箱验证码"
            
            body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333;">BUCT课程提醒系统</h2>
                <p>您的邮箱验证码为：</p>
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
                    <span style="font-size: 24px; font-weight: bold; color: #007bff;">{code}</span>
                </div>
                <p>验证码有效期 {Config.VERIFY_CODE_EXPIRE // 60} 分钟，请尽快使用。</p>
                <p style="color: #666; font-size: 12px;">如果不是您本人操作，请忽略此邮件。</p>
            </div>
            """
            
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False
    
    def store_verification_code(self, email: str, code: str, expire_minutes: Optional[int] = None):
        """存储验证码到MongoDB"""
        if expire_minutes is None:
            expire_minutes = Config.VERIFY_CODE_EXPIRE // 60
            
        self.db[self.verification_codes_collection].update_one(
            {'email': email},
            {'$set': {
                'code': code,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(seconds=Config.VERIFY_CODE_EXPIRE)
            }},
            upsert=True
        )
    
    def verify_code(self, email: str, code: str) -> bool:
        """验证验证码"""
        verification = self.db[self.verification_codes_collection].find_one({
            'email': email,
            'code': code,
            'expires_at': {'$gt': datetime.utcnow()}
        })
        
        if verification:
            # 验证成功后删除验证码
            self.db[self.verification_codes_collection].delete_one({'email': email})
            return True
        return False
    
    def check_rate_limit(self, email: str) -> bool:
        """检查发送频率限制（1分钟内只能发送一次）"""
        recent_code = self.db[self.verification_codes_collection].find_one({
            'email': email,
            'created_at': {'$gt': datetime.utcnow() - timedelta(minutes=1)}
        })
        return recent_code is not None
    
    def send_verification_code(self, email: str) -> Dict[str, Any]:
        """发送验证码的主要方法"""
        # 检查发送频率限制
        if self.check_rate_limit(email):
            return {
                "success": False,
                "message": "请等待1分钟后再次发送验证码"
            }
        
        # 生成验证码
        code = self.generate_verification_code()
        
        # 发送邮件
        if self.send_email_verification(email, code):
            # 存储验证码
            self.store_verification_code(email, code)
            
            return {
                "success": True,
                "message": "验证码已发送到您的邮箱"
            }
        else:
            return {
                "success": False,
                "message": "验证码发送失败，请稍后重试"
            }

# 创建全局实例
verification_service = VerificationService()