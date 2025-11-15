import os
import random
import re
import smtplib
import string
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps

from bson import ObjectId
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from . import mongo
from .model import User
from .rsa_crypto import get_rsa_crypto


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

def auto_refresh_assignments_on_login(user_id):
    """
    登录成功后自动刷新用户的作业数据（异步执行）
    
    Args:
        user_id: 用户ID
        
    Returns:
        dict: 刷新结果 {'success': bool, 'message': str}
    """
    try:
        current_app.logger.info(f"准备为用户 {user_id} 启动后台数据刷新")
        
        # 检查用户是否有学号和密码
        user = mongo.db[USERS_COLLECTION].find_one({'_id': ObjectId(user_id)})
        if not user:
            return {'success': False, 'error': '用户不存在'}
        
        student_id = user.get('student_id')
        s_password = user.get('s_password')
        
        if not student_id or not s_password:
            current_app.logger.info(f"用户 {user_id} 未设置学号或密码，跳过自动刷新")
            return {'success': False, 'error': '未设置学号或密码，请先完善学生信息'}
        
        # 启动后台任务刷新数据
        from .background_tasks import start_background_refresh
        task_started = start_background_refresh(user_id)
        
        if task_started:
            return {
                'success': True,
                'message': '作业数据正在后台更新中...'
            }
        else:
            return {
                'success': False,
                'error': '无法启动数据刷新任务'
            }
        
    except Exception as e:
        error_msg = f"启动自动刷新失败: {str(e)}"
        current_app.logger.error(f"用户 {user_id} {error_msg}")
        return {'success': False, 'error': '数据刷新启动失败，但不影响登录'}

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # 检查是否为加密数据
    encrypted_data = data.get('encrypted_data')
    if encrypted_data:
        # 解密数据
        rsa_crypto = get_rsa_crypto()
        decrypted_data = rsa_crypto.decrypt_data(encrypted_data)
        
        if not decrypted_data:
            return jsonify({'error': '数据解密失败'}), 400
        
        username = decrypted_data.get('username')
        password = decrypted_data.get('password')
    else:
        # 兼容未加密的请求（开发阶段）
        username = data.get('username')
        password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    user = mongo.db[USERS_COLLECTION].find_one({'username': username})
    
    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = str(user['_id'])
        session['username'] = user['username']
        current_app.logger.info(f"用户 {username} 登录成功")
        
        # 登录成功后自动刷新作业数据
        user_id = str(user['_id'])
        refresh_success = auto_refresh_assignments_on_login(user_id)
        
        response_data = {
            'message': '登录成功',
            'user': { 'id': str(user['_id']), 'username': user['username'], 'is_admin': user.get('is_admin', False) }
        }
        
        # 如果数据刷新成功，添加刷新信息到响应中
        if refresh_success.get('success'):
            response_data['data_refresh'] = {
                'success': True,
                'message': refresh_success.get('message', '作业数据已更新'),
                'count': refresh_success.get('count', 0)
            }
        else:
            response_data['data_refresh'] = {
                'success': False,
                'message': refresh_success.get('error', '数据刷新失败，但不影响登录')
            }
        
        return jsonify(response_data)
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
    
    # 检查是否为加密数据
    encrypted_data = data.get('encrypted_data')
    if encrypted_data:
        # 解密数据
        rsa_crypto = get_rsa_crypto()
        decrypted_data = rsa_crypto.decrypt_data(encrypted_data)
        
        if not decrypted_data:
            return jsonify({'error': '数据解密失败'}), 400
        
        username = decrypted_data.get('username')
        email = decrypted_data.get('email')
        password = decrypted_data.get('password')
        student_id = decrypted_data.get('student_id')
        s_password = decrypted_data.get('s_password')
    else:
        # 兼容未加密的请求（开发阶段）
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
    """更新学号和/或外部系统密码（允许部分更新）"""
    data = request.get_json() or {}
    student_id = data.get('student_id', None)
    s_password = data.get('s_password', None)

    # 过滤前端占位的掩码值，防止把仅由“•”组成的占位符写回数据库
    if isinstance(s_password, str):
        masked = True
        for ch in s_password.strip():
            if ch != '•':
                masked = False
                break
        if masked and len(s_password.strip()) > 0:
            s_password = None

    if student_id is None and s_password is None:
        return jsonify({'error': '无可更新的字段'}), 400

    user_id = session.get('user_id')
    user_model = get_user_model()

    try:
        # 允许部分更新
        result = user_model.update_student_info_optional(user_id, student_id=student_id, s_password=s_password)
        if result.modified_count > 0:
            current_app.logger.info(f"用户 {session.get('username')} 更新学生信息成功")
            return jsonify({'message': '学生信息更新成功'})
        else:
            return jsonify({'message': '无变更'}), 200
    except Exception as e:
        current_app.logger.error(f"更新学生信息失败: {str(e)}")
        return jsonify({'error': '更新失败，请重试'}), 500


@auth_bp.route('/update-email', methods=['POST'])
@login_required
def update_email():
    """更新用户邮箱（同时更新账号恢复邮箱和提醒邮箱）"""
    data = request.get_json()
    new_email = data.get('email')

    if not new_email:
        return jsonify({'error': '邮箱地址不能为空'}), 400

    # 验证邮箱格式
    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_pattern, new_email):
        return jsonify({'error': '邮箱格式不正确'}), 400

    user_id = session.get('user_id')
    user_model = get_user_model()

    try:
        # 检查新邮箱是否已被其他用户使用
        existing_user = user_model.find_by_email(new_email)
        if existing_user and str(existing_user['_id']) != user_id:
            return jsonify({'error': '该邮箱已被其他用户使用'}), 400

        # 更新用户邮箱
        result = mongo.db[USERS_COLLECTION].update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'email': new_email, 'updated_at': datetime.now()}}
        )

        if result.modified_count > 0:
            current_app.logger.info(f"用户 {session.get('username')} 邮箱更新成功: {new_email}")
            return jsonify({'message': '邮箱修改成功'})
        else:
            return jsonify({'message': '邮箱未改变'}), 200
    except Exception as e:
        current_app.logger.error(f"更新邮箱失败: {str(e)}")
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
            'student_password_length': int(user.get('s_password_len')) if user.get('s_password_len') is not None else 0,
            'is_admin': user.get('is_admin', False)
        })
    else:
        return jsonify({'error': '用户不存在'}), 404

@auth_bp.route('/check-email', methods=['POST'])
def check_email():
    """检查邮箱是否已注册"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': '邮箱地址不能为空'}), 400
    
    # 验证邮箱格式
    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_pattern, email):
        return jsonify({'error': '邮箱格式不正确'}), 400
    
    try:
        user = mongo.db[USERS_COLLECTION].find_one({'email': email})
        exists = user is not None
        
        current_app.logger.info(f"邮箱检查: {email} - {'存在' if exists else '不存在'}")
        return jsonify({'exists': exists})
        
    except Exception as e:
        current_app.logger.error(f"检查邮箱异常: {str(e)}")
        return jsonify({'error': '检查失败，请重试'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """重置密码"""
    data = request.get_json()
    
    # 检查是否为加密数据
    encrypted_data = data.get('encrypted_data')
    if encrypted_data:
        # 解密数据
        rsa_crypto = get_rsa_crypto()
        decrypted_data = rsa_crypto.decrypt_data(encrypted_data)
        
        if not decrypted_data:
            return jsonify({'error': '数据解密失败'}), 400
        
        email = decrypted_data.get('email')
        new_password = decrypted_data.get('new_password')
    else:
        # 兼容未加密的请求（开发阶段）
        email = data.get('email')
        new_password = data.get('new_password')
    
    if not email or not new_password:
        return jsonify({'error': '邮箱和新密码不能为空'}), 400
    
    # 验证邮箱格式
    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_pattern, email):
        return jsonify({'error': '邮箱格式不正确'}), 400
    
    # 验证密码长度
    if len(new_password) < 6:
        return jsonify({'error': '密码长度至少6位'}), 400
    
    try:
        # 查找用户
        user = mongo.db[USERS_COLLECTION].find_one({'email': email})
        if not user:
            return jsonify({'error': '该邮箱未注册'}), 404
        
        # 更新密码
        new_password_hash = generate_password_hash(new_password)
        result = mongo.db[USERS_COLLECTION].update_one(
            {'email': email},
            {'$set': {
                'password_hash': new_password_hash,
                'updated_at': datetime.now()
            }}
        )
        
        if result.modified_count > 0:
            current_app.logger.info(f"用户 {user['username']} 密码重置成功")
            return jsonify({'message': '密码重置成功'})
        else:
            return jsonify({'error': '密码重置失败'}), 400
            
    except Exception as e:
        current_app.logger.error(f"重置密码异常: {str(e)}")
        return jsonify({'error': '重置失败，请重试'}), 500