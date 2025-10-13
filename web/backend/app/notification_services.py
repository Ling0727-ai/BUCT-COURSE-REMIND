import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import current_app
from . import mongo
import requests

ASSIGNMENTS_COLLECTION = 'assignments'
WEBHOOK_LOGS_COLLECTION = 'webhook_logs'
SETTINGS_COLLECTION = 'settings'

def check_and_send_notifications():
    """Check for urgent assignments and send notifications."""
    try:
        webhook_setting = mongo.db[SETTINGS_COLLECTION].find_one({'key': 'webhooks'})
        if not webhook_setting or not webhook_setting.get('value'): return

        webhooks = json.loads(webhook_setting['value'])
        # 只保留启用的邮箱webhook
        active_webhooks = [w for w in webhooks if w.get('enabled', False) and w.get('type') == 'email']
        if not active_webhooks: return

        now = datetime.now()
        urgent_assignments = list(mongo.db[ASSIGNMENTS_COLLECTION].find({
            'due_date': {'$lte': now + timedelta(days=1), '$gt': now}
        }))

        for assignment in urgent_assignments:
            message = f"⚠️ 紧急提醒\n\n科目: {assignment['subject']}\n作业: {assignment['title']}\n截止时间: {assignment['due_date'].strftime('%Y-%m-%d %H:%M:%S')}"
            for webhook in active_webhooks:
                send_webhook_notification(webhook, message)
    except Exception as e:
        current_app.logger.error(f"检查通知失败: {str(e)}")


def send_webhook_notification(webhook_config, message):
    """只发送邮箱webhook通知"""
    try:
        webhook_type = webhook_config.get('type')
        config = webhook_config.get('config', {})
        
        success = False
        # 只处理邮箱类型的webhook
        if webhook_type == 'email':
            success = send_email_notification(config, message)
        else:
            # 其他类型的webhook直接返回成功，但不实际发送
            current_app.logger.info(f"跳过非邮箱webhook类型: {webhook_type}")
            success = True
        
        log_data = {
            'webhook_type': webhook_type, 'message': message,
            'status': 'success' if success else 'failed',
            'created_at': datetime.now()
        }
        mongo.db[WEBHOOK_LOGS_COLLECTION].insert_one(log_data)
        return success
    except Exception as e:
        current_app.logger.error(f"发送通知失败: {str(e)}")
        return False

def send_dingtalk_notification(config, message):
    """发送钉钉机器人通知"""
    try:
        webhook_url = config.get('webhook_url')
        if not webhook_url:
            return False
            
        payload = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        current_app.logger.error(f"钉钉通知发送失败: {str(e)}")
        return False

def send_wechat_notification(config, message):
    """发送企业微信机器人通知"""
    try:
        webhook_url = config.get('webhook_url')
        if not webhook_url:
            return False
            
        payload = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        current_app.logger.error(f"企业微信通知发送失败: {str(e)}")
        return False

def send_discord_notification(config, message):
    """发送Discord通知"""
    try:
        webhook_url = config.get('webhook_url')
        if not webhook_url:
            return False
            
        payload = {
            "content": message
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        current_app.logger.error(f"Discord通知发送失败: {str(e)}")
        return False

def send_slack_notification(config, message):
    """发送Slack通知"""
    try:
        webhook_url = config.get('webhook_url')
        if not webhook_url:
            return False
            
        payload = {
            "text": message
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        current_app.logger.error(f"Slack通知发送失败: {str(e)}")
        return False

def send_custom_webhook(config, message):
    """发送自定义webhook通知"""
    try:
        webhook_url = config.get('webhook_url')
        method = config.get('method', 'POST')
        headers = config.get('headers', {})
        body_template = config.get('body_template', '')
        
        if not webhook_url:
            return False
            
        # 处理消息模板
        if body_template:
            try:
                # 简单的模板替换
                body = body_template.replace('{message}', message)
                # 可以添加更多模板变量替换
                body = body.replace('{timestamp}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            except:
                body = message
        else:
            body = message
            
        if method.upper() == 'POST':
            response = requests.post(webhook_url, data=body, headers=headers, timeout=10)
        else:
            response = requests.get(webhook_url, headers=headers, timeout=10)
            
        response.raise_for_status()
        return True
    except Exception as e:
        current_app.logger.error(f"自定义webhook发送失败: {str(e)}")
        return False

# 导出函数到模块级别
__all__ = ['check_and_send_notifications', 'send_webhook_notification', 
           'send_email_notification']

def send_email_notification(config, message):
    """Sends an email notification."""
    try:
        # This requires mail configuration in config.py
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from .config import Config
        msg = MIMEMultipart()
        msg['From'] = Config.MAIL_SENDER
        msg['To'] = config.get('to_email') # The recipient is from webhook settings
        msg['Subject'] = "作业提醒通知"
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        server = smtplib.SMTP_SSL(Config.MAIL_SMTP_SERVER, Config.MAIL_SMTP_PORT)
        server.login(Config.MAIL_SENDER, Config.MAIL_PASSWORD or "")
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        current_app.logger.error(f"邮件发送失败: {str(e)}")
        return False