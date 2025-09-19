import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Config:
    # Flask密钥（用于session等）
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key_for_session_and_jwt_2024'
    
    # Session配置
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'buct_course:'
    SESSION_COOKIE_NAME = 'buct_session'
    SESSION_COOKIE_DOMAIN = None
    SESSION_COOKIE_PATH = '/'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # 开发环境设为False，生产环境应设为True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24小时
    
    # MongoDB连接URI（从环境变量获取，兼容Docker部署）
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/buct-course')

    # 验证码配置
    CAPTCHA_EXPIRE_TIME = 300  # 验证码过期时间（秒）

    MAIL_SMTP_SERVER = os.environ.get('MAIL_SMTP_SERVER', 'smtp.163.com')  # SMTP服务器
    MAIL_SMTP_PORT = int(os.environ.get('MAIL_SMTP_PORT', 465))  # SSL端口
    MAIL_SENDER = os.environ.get('MAIL_SENDER', 'buct_course_remind@163.com')  # 发件邮箱地址
    VERIFY_CODE_EXPIRE = int(os.environ.get('VERIFY_CODE_EXPIRE', 180))  # 验证码有效期（秒）
    
    # 邮箱密码配置（避免重复定义）
    _mail_password = os.environ.get('MAIL_PASSWORD')
    if os.environ.get('FLASK_ENV') == 'production' and not _mail_password:
        print("警告: MAIL_PASSWORD 未设置，邮件功能将不可用")
        MAIL_PASSWORD = 'dummy_password_for_dev'  # 开发环境默认值
    else:
        MAIL_PASSWORD = _mail_password or 'dummy_password_for_dev'  # 开发环境默认值


config = Config()
