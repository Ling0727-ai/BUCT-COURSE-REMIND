import os

from dotenv import load_dotenv

# 加载.env文件
load_dotenv()


class Config:
    # JWT密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key_for_jwt'

    # MongoDB连接URI（从环境变量获取，兼容Docker部署）
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/buct-course')

    # 验证码配置
    CAPTCHA_EXPIRE_TIME = 300  # 验证码过期时间（秒）

    MAIL_SMTP_SERVER = os.environ.get('MAIL_SMTP_SERVER', 'smtp.163.com')  # SMTP服务器
    MAIL_SMTP_PORT = int(os.environ.get('MAIL_SMTP_PORT', 465))  # SSL端口
    MAIL_SENDER = os.environ.get('MAIL_SENDER', 'buct_course_remind@163.com')  # 发件邮箱地址
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # 邮箱授权码
    VERIFY_CODE_EXPIRE = int(os.environ.get('VERIFY_CODE_EXPIRE', 180))  # 验证码有效期（秒）

    # 邮箱配置检查（仅在生产环境要求）
    if os.environ.get('FLASK_ENV') == 'production' and not MAIL_PASSWORD:
        print("警告: MAIL_PASSWORD 未设置，邮件功能将不可用")
        MAIL_PASSWORD = 'dummy_password_for_dev'  # 开发环境默认值
    elif not MAIL_PASSWORD:
        MAIL_PASSWORD = 'dummy_password_for_dev'  # 开发环境默认值

    # CORS 配置
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:8080')  # 逗号分隔
    CORS_REFRESH_INTERVAL_HOURS = int(os.environ.get('CORS_REFRESH_INTERVAL_HOURS', 6))  # 动态刷新间隔（小时）


config = Config()
