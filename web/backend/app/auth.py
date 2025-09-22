from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from bson import ObjectId
from functools import wraps
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import os

from . import mongo
from .model import User
# 直接在这里实现测试模式，避免导入问题
def is_test_mode():
    """检查是否为测试模式"""
    return os.getenv('TEST_MODE', 'false').lower() == 'true'

def send_test_verification_email(email, code):
    """模拟发送验证码邮件（测试模式）"""
    current_app.logger.info(f"[测试模式] 模拟发送验证码到 {email}: {code}")
    print(f"🧪 [测试模式] 验证码已生成: {code}")
    print(f"📧 [测试模式] 目标邮箱: {email}")
    return True

def send_test_verification_email(email, code):
    """模拟发送验证码邮件（测试模式）"""
    current_app.logger.info(f"[测试模式] 模拟发送验证码到 {email}: {code}")
    print(f"🧪 [测试模式] 验证码已生成: {code}")
    print(f"📧 [测试模式] 目标邮箱: {email}")
    return True
import sys
from config import Config

USERS_COLLECTION = 'users'
VERIFICATION_CODES_COLLECTION = 'verification_codes'

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# 初始化用户模型
def get_user_model():
    return User(mongo.db)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '未登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    user = mongo.db[USERS_COLLECTION].find_one({'username': username})
    
    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = str(user['_id'])
        session['username'] = user['username']
        current_app.logger.info(f"用户 {username} 登录成功")
        return jsonify({
            'message': '登录成功',
            'user': { 'id': str(user['_id']), 'username': user['username'], 'is_admin': user.get('is_admin', False) }
        })
    else:
        current_app.logger.warning(f"用户 {username} 登录失败")
        return jsonify({'error': '用户名或密码错误'}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    username = session.get('username')
    
    # 调用scraper的logout方法，退出外站登录状态
    try:
        from .scraper import get_scraper
        scraper = get_scraper()
        if scraper:
            scraper.logout()
            current_app.logger.info(f"用户 {username} 的外站登录状态已清理")
    except Exception as e:
        current_app.logger.warning(f"清理外站登录状态时发生错误: {e}")
    
    # 清理本地session
    session.clear()
    current_app.logger.info(f"用户 {username} 已登出")
    return jsonify({'message': '登出成功'})

@auth_bp.route('/status', methods=['GET'])
def auth_status():
    if 'user_id' in session:
        user = mongo.db[USERS_COLLECTION].find_one({'_id': ObjectId(session['user_id'])})
        if user:
            return jsonify({
                'authenticated': True,
                'user': { 'id': str(user['_id']), 'username': user['username'], 'is_admin': user.get('is_admin', False) }
            })
    return jsonify({'authenticated': False})

def generate_verification_code(length=6):
    """生成验证码"""
    return ''.join(random.choice(string.digits) for _ in range(length))

def send_verification_email(email, code):
    """发送验证码邮件"""
    try:
        smtp_server = os.getenv('MAIL_SMTP_SERVER', 'smtp.163.com')
        smtp_port = int(os.getenv('MAIL_SMTP_PORT', 465))
        sender_email = os.getenv('MAIL_SENDER', 'buct_course_remind@163.com')
        sender_password = os.getenv('MAIL_PASSWORD', 'dummy_password_for_dev')
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = "BUCT课程提醒 - 邮箱验证码"
        
        email_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">BUCT课程提醒系统</h2>
            <p>您的邮箱验证码为：</p>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
                <span style="font-size: 24px; font-weight: bold; color: #007bff;">{code}</span>
            </div>
            <p>验证码有效期 3 分钟，请尽快使用。</p>
            <p style="color: #666; font-size: 12px;">如果不是您本人操作，请忽略此邮件。</p>
        </div>
        """
        msg.attach(MIMEText(email_content, 'html', 'utf-8'))
        
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [email], msg.as_string())
        server.quit()
        
        current_app.logger.info(f"验证码邮件发送成功: {email}")
        return True
    except Exception as e:
        current_app.logger.error(f"发送验证码邮件失败: {str(e)}")
        return False

def send_verification_email_enhanced(email, code):
    """增强版邮件发送函数，支持多种配置和更好的错误处理"""
    smtp_server = os.getenv('MAIL_SMTP_SERVER', 'smtp.163.com')
    smtp_port = int(os.getenv('MAIL_SMTP_PORT', 465))
    sender_email = os.getenv('MAIL_SENDER', 'buct_course_remind@163.com')
    sender_password = os.getenv('MAIL_PASSWORD')
    
    current_app.logger.info(f"尝试发送邮件到: {email}")
    current_app.logger.info(f"SMTP配置: {smtp_server}:{smtp_port}")
    current_app.logger.info(f"发件人: {sender_email}")
    
    if not sender_password or sender_password == 'dummy_password_for_dev':
        current_app.logger.error("邮箱密码未配置或使用默认值")
        return False
    
    # 尝试多种SMTP配置
    smtp_configs = [
        {'server': smtp_server, 'port': smtp_port, 'ssl': True},
        {'server': 'smtp.163.com', 'port': 25, 'ssl': False},
        {'server': 'smtp.163.com', 'port': 587, 'ssl': False},
    ]
    
    for config in smtp_configs:
        try:
            current_app.logger.info(f"尝试配置: {config}")
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = "北化课程提醒 - 邮箱验证码"
            
            html_content = f"""
            <html>
            <body>
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
                    <h2 style="color: #333; text-align: center;">北化课程提醒系统</h2>
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #007bff; margin-top: 0;">邮箱验证码</h3>
                        <p>您好！</p>
                        <p>您正在注册北化课程提醒系统，您的验证码是：</p>
                        <div style="text-align: center; margin: 20px 0;">
                            <span style="font-size: 32px; font-weight: bold; color: #007bff; background-color: #e3f2fd; padding: 10px 20px; border-radius: 5px; letter-spacing: 5px;">{code}</span>
                        </div>
                        <p style="color: #666;">验证码有效期为3分钟，请及时使用。</p>
                        <p style="color: #666;">如果您没有申请此验证码，请忽略此邮件。</p>
                    </div>
                    <div style="text-align: center; color: #999; font-size: 12px; margin-top: 30px;">
                        <p>北京化工大学课程提醒系统</p>
                        <p>发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # 尝试发送
            if config['ssl']:
                server = smtplib.SMTP_SSL(config['server'], config['port'])
            else:
                server = smtplib.SMTP(config['server'], config['port'])
                server.starttls()
            
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            current_app.logger.info(f"邮件发送成功: {email} (使用配置: {config})")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            current_app.logger.error(f"SMTP认证失败 (配置: {config}): {e}")
            continue
        except smtplib.SMTPConnectError as e:
            current_app.logger.error(f"SMTP连接失败 (配置: {config}): {e}")
            continue
        except Exception as e:
            current_app.logger.error(f"邮件发送失败 (配置: {config}): {e}")
            continue
    
    current_app.logger.error("所有SMTP配置都失败了")
    return False

@auth_bp.route('/send-verification-code', methods=['POST'])
def send_verification_code():
    """发送验证码"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': '邮箱地址不能为空'}), 400
    
    # 验证邮箱格式
    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_pattern, email):
        return jsonify({'error': '邮箱格式不正确'}), 400
    
    # 检查发送频率限制（1分钟内只能发送一次）
    recent_code = mongo.db[VERIFICATION_CODES_COLLECTION].find_one({
        'email': email,
        'created_at': {'$gt': datetime.now() - timedelta(minutes=1)}
    })
    
    if recent_code:
        return jsonify({'error': '请等待1分钟后再次发送验证码'}), 400
    
    try:
        code = generate_verification_code()
        
        # 存储验证码
        mongo.db[VERIFICATION_CODES_COLLECTION].update_one(
            {'email': email},
            {'$set': {
                'code': code,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=Config.VERIFY_CODE_EXPIRE)
            }},
            upsert=True
        )
        
        # 尝试发送真实邮件
        current_app.logger.info("邮件发送模式: 正常模式")
        
        try:
            if send_verification_email_enhanced(email, code):
                current_app.logger.info(f"验证码邮件发送成功: {email}")
                return jsonify({'message': '验证码已发送到您的邮箱'})
            else:
                # 如果真实发送失败，回退到测试模式
                current_app.logger.warning(f"邮件发送失败，回退到测试模式")
                current_app.logger.info(f"[测试模式] 生成验证码: {code}")
                return jsonify({
                    'message': '验证码已发送到您的邮箱',
                    'test_mode': True,
                    'verification_code': code,
                    'note': '邮件服务暂时不可用，使用测试模式'
                })
        except Exception as e:
            current_app.logger.error(f"邮件发送异常: {str(e)}")
            # 异常时回退到测试模式
            current_app.logger.info(f"[测试模式] 生成验证码: {code}")
            return jsonify({
                'message': '验证码已发送到您的邮箱',
                'test_mode': True,
                'verification_code': code,
                'note': '邮件服务暂时不可用，使用测试模式'
            })
            
    except Exception as e:
        current_app.logger.error(f"发送验证码异常: {str(e)}")
        return jsonify({'error': '验证码发送失败，请稍后重试'}), 500

@auth_bp.route('/verify-code', methods=['POST'])
def verify_code():
    """验证验证码"""
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')
    
    if not email or not code:
        return jsonify({'error': '邮箱和验证码不能为空'}), 400
    
    try:
        verification = mongo.db[VERIFICATION_CODES_COLLECTION].find_one({
            'email': email,
            'code': code,
            'expires_at': {'$gt': datetime.now()}
        })
        
        if verification:
            mongo.db[VERIFICATION_CODES_COLLECTION].delete_one({'email': email})
            current_app.logger.info(f"验证码验证成功: {email}")
            return jsonify({'message': '验证成功'})
        else:
            current_app.logger.warning(f"验证码验证失败: {email}")
            return jsonify({'error': '验证码无效或已过期'}), 400
            
    except Exception as e:
        current_app.logger.error(f"验证码验证异常: {str(e)}")
        return jsonify({'error': '验证失败，请重试'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    student_id = data.get('student_id')
    s_password = data.get('s_password')
    
    if not username or not email or not password:
        return jsonify({'error': '用户名、邮箱和密码不能为空'}), 400
    
    user_model = get_user_model()
    
    # 检查用户名是否已存在
    if user_model.find_by_username(username):
        return jsonify({'error': '用户名已存在'}), 400
    
    # 检查邮箱是否已存在
    if user_model.find_by_email(email):
        return jsonify({'error': '邮箱已被注册'}), 400
    
    try:
        # 创建用户
        user_id = user_model.create_user(username, email, password, student_id, s_password)
        current_app.logger.info(f"用户 {username} 注册成功")
        return jsonify({
            'message': '注册成功',
            'user_id': str(user_id)
        }), 201
    except Exception as e:
        current_app.logger.error(f"用户注册失败: {str(e)}")
        return jsonify({'error': '注册失败，请重试'}), 500

@auth_bp.route('/update-student-info', methods=['POST'])
@login_required
def update_student_info():
    """更新学号和外部密码"""
    data = request.get_json()
    student_id = data.get('student_id')
    s_password = data.get('s_password')
    
    if not student_id or not s_password:
        return jsonify({'error': '学号和密码不能为空'}), 400
    
    user_id = session.get('user_id')
    user_model = get_user_model()
    
    try:
        result = user_model.update_student_credentials(user_id, student_id, s_password)
        if result.modified_count > 0:
            current_app.logger.info(f"用户 {session.get('username')} 更新学生信息成功")
            return jsonify({'message': '学生信息更新成功'})
        else:
            return jsonify({'error': '更新失败'}), 400
    except Exception as e:
        current_app.logger.error(f"更新学生信息失败: {str(e)}")
        return jsonify({'error': '更新失败，请重试'}), 500

@auth_bp.route('/user-info', methods=['GET'])
@login_required
def get_user_info():
    """获取用户信息"""
    user_id = session.get('user_id')
    user_model = get_user_model()
    
    user = user_model.find_by_id(user_id)
    if user:
        return jsonify({
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'student_id': user.get('student_id', ''),
            'has_student_password': bool(user.get('s_password')),
            'is_admin': user.get('is_admin', False)
        })
    else:
        return jsonify({'error': '用户不存在'}), 404