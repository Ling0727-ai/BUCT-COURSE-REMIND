"""
测试路由 - 用于验证码功能调试
"""

from flask import Blueprint, request, jsonify
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime, timedelta
from . import mongo

test_bp = Blueprint('test', __name__, url_prefix='/api/test')

def generate_test_code():
    """生成测试验证码"""
    return ''.join(random.choices(string.digits, k=6))

@test_bp.route('/send-test-email', methods=['POST'])
def send_test_email():
    """发送测试邮件"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': '邮箱地址不能为空'}), 400
    
    # 邮件配置
    smtp_server = os.getenv('MAIL_SMTP_SERVER', 'smtp.163.com')
    smtp_port = int(os.getenv('MAIL_SMTP_PORT', 465))
    sender_email = os.getenv('MAIL_SENDER', 'buct_course_remind@163.com')
    sender_password = os.getenv('MAIL_PASSWORD', 'dummy_password_for_dev')
    
    # 生成测试验证码
    test_code = generate_test_code()
    
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = "BUCT课程提醒 - 测试验证码"
        
        body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">BUCT课程提醒系统 - 测试</h2>
            <p>这是一封测试邮件，您的测试验证码为：</p>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
                <span style="font-size: 24px; font-weight: bold; color: #007bff;">{test_code}</span>
            </div>
            <p>验证码有效期3分钟，请及时使用。</p>
            <p style="color: #666; font-size: 12px;">这是系统测试邮件。</p>
        </div>
        """
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        # 发送邮件
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        # 存储验证码到数据库
        mongo.db.verification_codes.update_one(
            {'email': email},
            {'$set': {
                'code': test_code,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(minutes=3)
            }},
            upsert=True
        )
        
        return jsonify({
            'message': '测试邮件发送成功',
            'test_code': test_code,  # 仅测试时返回
            'email': email
        })
        
    except Exception as e:
        return jsonify({
            'error': f'邮件发送失败: {str(e)}',
            'config': {
                'smtp_server': smtp_server,
                'smtp_port': smtp_port,
                'sender_email': sender_email,
                'password_set': sender_password != 'dummy_password_for_dev'
            }
        }), 500

@test_bp.route('/verify-test-code', methods=['POST'])
def verify_test_code():
    """验证测试验证码"""
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')
    
    if not email or not code:
        return jsonify({'error': '邮箱和验证码不能为空'}), 400
    
    try:
        # 查找验证码
        verification = mongo.db.verification_codes.find_one({
            'email': email,
            'code': code,
            'expires_at': {'$gt': datetime.now()}
        })
        
        if verification:
            # 删除已使用的验证码
            mongo.db.verification_codes.delete_one({'email': email})
            return jsonify({'message': '验证成功'})
        else:
            return jsonify({'error': '验证码无效或已过期'}), 400
            
    except Exception as e:
        return jsonify({'error': f'验证失败: {str(e)}'}), 500

@test_bp.route('/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    return jsonify({
        'smtp_server': os.getenv('MAIL_SMTP_SERVER', 'smtp.163.com'),
        'smtp_port': int(os.getenv('MAIL_SMTP_PORT', 465)),
        'sender_email': os.getenv('MAIL_SENDER', 'buct_course_remind@163.com'),
        'password_set': os.getenv('MAIL_PASSWORD', 'dummy_password_for_dev') != 'dummy_password_for_dev',
        'mongo_uri': os.getenv('MONGO_URI', 'mongodb://localhost:27017/assignment_manager')
    })