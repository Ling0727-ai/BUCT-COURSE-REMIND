# app.py
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
import requests
import threading
import time
import schedule
import subprocess
import logging
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///assignments.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy(app)
CORS(app, supports_credentials=True)

# 数据库模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    publisher = db.Column(db.String(100))
    type = db.Column(db.String(50), default='作业')  # 作业 or 测试
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    allowed_attempts = db.Column(db.Integer, default=1)
    time_limit = db.Column(db.Integer)  # 分钟
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WebhookLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    webhook_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20))  # success, failed
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 装饰器：需要登录
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '未登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

# 登录相关API
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['username'] = user.username
        logger.info(f"用户 {username} 登录成功")
        return jsonify({
            'message': '登录成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin
            }
        })
    else:
        logger.warning(f"用户 {username} 登录失败")
        return jsonify({'error': '用户名或密码错误'}), 401

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    username = session.get('username')
    session.clear()
    logger.info(f"用户 {username} 已登出")
    return jsonify({'message': '登出成功'})

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return jsonify({
            'authenticated': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin
            }
        })
    return jsonify({'authenticated': False})

# 作业相关API
@app.route('/api/assignments', methods=['GET'])
@login_required
def get_assignments():
    assignments = Assignment.query.order_by(Assignment.due_date.asc()).all()
    tests = Test.query.order_by(Test.start_time.asc()).all()
    
    result = []
    
    # 添加作业
    for assignment in assignments:
        result.append({
            'id': assignment.id,
            'subject': assignment.subject,
            'title': assignment.title,
            'content': assignment.content or '',
            'dueDate': assignment.due_date.isoformat(),
            'publisher': assignment.publisher,
            'type': assignment.type,
            'completed': False  # 可以后续扩展完成状态
        })
    
    # 添加测试
    for test in tests:
        result.append({
            'id': f"test_{test.id}",
            'subject': '在线测试',
            'title': test.title,
            'content': f"允许测试次数: {test.allowed_attempts}, 限制用时: {test.time_limit}分钟",
            'dueDate': test.end_time.isoformat(),
            'publisher': '系统',
            'type': '测试',
            'completed': False
        })
    
    return jsonify(result)

@app.route('/api/assignments/refresh', methods=['POST'])
@login_required
def refresh_assignments():
    try:
        # 执行Python抓取脚本
        result = subprocess.run(['python', 'scraper.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("作业数据刷新成功")
            return jsonify({'message': '数据刷新成功', 'output': result.stdout})
        else:
            logger.error(f"作业数据刷新失败: {result.stderr}")
            return jsonify({'error': '数据刷新失败', 'details': result.stderr}), 500
            
    except subprocess.TimeoutExpired:
        logger.error("作业数据刷新超时")
        return jsonify({'error': '数据刷新超时'}), 500
    except Exception as e:
        logger.error(f"作业数据刷新异常: {str(e)}")
        return jsonify({'error': '数据刷新失败', 'details': str(e)}), 500

# 设置相关API
@app.route('/api/settings', methods=['GET'])
@login_required
def get_settings():
    settings = {}
    
    # 获取所有设置
    db_settings = Settings.query.all()
    for setting in db_settings:
        if setting.key == 'webhooks':
            settings[setting.key] = json.loads(setting.value) if setting.value else []
        else:
            settings[setting.key] = setting.value
    
    # 默认值
    if 'serverUrl' not in settings:
        settings['serverUrl'] = 'http://localhost:5000'
    if 'webhooks' not in settings:
        settings['webhooks'] = []
    if 'scrape_interval' not in settings:
        settings['scrape_interval'] = '60'  # 默认60分钟
    
    return jsonify(settings)

@app.route('/api/settings', methods=['POST'])
@login_required
def save_settings():
    data = request.get_json()
    
    try:
        # 保存各种设置
        for key, value in data.items():
            if key == 'password' and value:
                # 不保存明文密码，这里应该是用于更新登录密码
                continue
                
            setting = Settings.query.filter_by(key=key).first()
            if not setting:
                setting = Settings(key=key)
                
            if key == 'webhooks':
                setting.value = json.dumps(value)
            else:
                setting.value = str(value)
                
            db.session.merge(setting)
        
        db.session.commit()
        
        # 如果更新了抓取间隔，重新安排定时任务
        if 'scrape_interval' in data:
            setup_scheduler(int(data['scrape_interval']))
        
        logger.info("设置保存成功")
        return jsonify({'message': '设置保存成功'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"设置保存失败: {str(e)}")
        return jsonify({'error': '设置保存失败', 'details': str(e)}), 500

# Webhook相关功能
def send_webhook_notification(webhook_config, message):
    try:
        webhook_type = webhook_config.get('type')
        config = webhook_config.get('config', {})
        
        if webhook_type == 'email':
            success = send_email_notification(config, message)
        elif webhook_type == 'telegram':
            success = send_telegram_notification(config, message)
        elif webhook_type == 'discord':
            success = send_discord_notification(config, message)
        elif webhook_type == 'slack':
            success = send_slack_notification(config, message)
        elif webhook_type == 'webhook':
            success = send_custom_webhook(config, message)
        else:
            success = False
            
        # 记录日志
        log = WebhookLog(
            webhook_type=webhook_type,
            message=message,
            status='success' if success else 'failed'
        )
        db.session.add(log)
        db.session.commit()
        
        return success
        
    except Exception as e:
        logger.error(f"发送通知失败: {str(e)}")
        return False

def send_email_notification(config, message):
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = config.get('email')
        msg['To'] = config.get('to_email')
        msg['Subject'] = "作业提醒通知"
        
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(config.get('smtp_server'), int(config.get('smtp_port')))
        server.starttls()
        server.login(config.get('email'), config.get('password'))
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
        return False

def send_telegram_notification(config, message):
    try:
        bot_token = config.get('bot_token')
        chat_id = config.get('chat_id')
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Telegram发送失败: {str(e)}")
        return False

def send_discord_notification(config, message):
    try:
        webhook_url = config.get('webhook_url')
        data = {'content': message}
        
        response = requests.post(webhook_url, json=data, timeout=10)
        return response.status_code == 204
        
    except Exception as e:
        logger.error(f"Discord发送失败: {str(e)}")
        return False

def send_slack_notification(config, message):
    try:
        webhook_url = config.get('webhook_url')
        data = {'text': message}
        
        response = requests.post(webhook_url, json=data, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Slack发送失败: {str(e)}")
        return False

def send_custom_webhook(config, message):
    try:
        url = config.get('url')
        method = config.get('method', 'POST').upper()
        headers = json.loads(config.get('headers', '{}'))
        template = config.get('template', '{"message": "{{message}}"}')
        
        # 替换模板中的变量
        payload = template.replace('{{message}}', message)
        data = json.loads(payload)
        
        if method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == 'GET':
            response = requests.get(url, params=data, headers=headers, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers, timeout=10)
        else:
            return False
            
        return 200 <= response.status_code < 300
        
    except Exception as e:
        logger.error(f"自定义Webhook发送失败: {str(e)}")
        return False

@app.route('/api/webhook/test', methods=['POST'])
@login_required
def test_webhook():
    data = request.get_json()
    webhook_config = data.get('webhook')
    
    if not webhook_config:
        return jsonify({'error': 'Webhook配置不能为空'}), 400
    
    test_message = "这是一条测试消息 - 作业管理系统"
    success = send_webhook_notification(webhook_config, test_message)
    
    if success:
        return jsonify({'message': '测试消息发送成功'})
    else:
        return jsonify({'error': '测试消息发送失败'}), 500

# 健康检查
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# 统计信息
@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    total_assignments = Assignment.query.count()
    total_tests = Test.query.count()
    
    # 计算紧急和即将到期的作业
    now = datetime.utcnow()
    urgent_assignments = Assignment.query.filter(
        Assignment.due_date <= now + timedelta(days=2)
    ).count()
    
    return jsonify({
        'total_assignments': total_assignments,
        'total_tests': total_tests,
        'urgent_assignments': urgent_assignments,
        'total_items': total_assignments + total_tests
    })

# 定时任务相关
def scrape_assignments():
    """定时执行抓取任务"""
    try:
        logger.info("开始执行定时抓取任务")
        result = subprocess.run(['python', 'scraper.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("定时抓取任务成功")
            
            # 检查是否有新的紧急作业，发送通知
            check_and_send_notifications()
        else:
            logger.error(f"定时抓取任务失败: {result.stderr}")
            
    except Exception as e:
        logger.error(f"定时抓取任务异常: {str(e)}")

def check_and_send_notifications():
    """检查并发送通知"""
    try:
        # 获取Webhook配置
        webhook_setting = Settings.query.filter_by(key='webhooks').first()
        if not webhook_setting or not webhook_setting.value:
            return
            
        webhooks = json.loads(webhook_setting.value)
        active_webhooks = [w for w in webhooks if w.get('enabled', False)]
        
        if not active_webhooks:
            return
        
        # 获取紧急作业
        now = datetime.utcnow()
        urgent_assignments = Assignment.query.filter(
            Assignment.due_date <= now + timedelta(days=1),
            Assignment.due_date > now
        ).all()
        
        for assignment in urgent_assignments:
            message = f"⚠️ 紧急提醒\n\n科目: {assignment.subject}\n作业: {assignment.title}\n截止时间: {assignment.due_date.strftime('%Y-%m-%d %H:%M:%S')}\n发布者: {assignment.publisher}"
            
            for webhook in active_webhooks:
                send_webhook_notification(webhook, message)
                
    except Exception as e:
        logger.error(f"检查通知失败: {str(e)}")

def setup_scheduler(interval_minutes=60):
    """设置定时任务"""
    schedule.clear()
    schedule.every(interval_minutes).minutes.do(scrape_assignments)
    logger.info(f"定时任务已设置，间隔: {interval_minutes}分钟")

def run_scheduler():
    """运行定时任务调度器"""
    while True:
        schedule.run_pending()
        time.sleep(1)

# 初始化数据库和默认数据
def init_db():
    with app.app_context():
        db.create_all()
        
        # 创建默认管理员账户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            logger.info("默认管理员账户已创建 (admin/admin123)")

if __name__ == '__main__':
    init_db()
    
    # 获取抓取间隔设置
    with app.app_context():
        interval_setting = Settings.query.filter_by(key='scrape_interval').first()
        interval = int(interval_setting.value) if interval_setting and interval_setting.value else 60
        setup_scheduler(interval)
    
    # 在后台启动定时任务
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    )