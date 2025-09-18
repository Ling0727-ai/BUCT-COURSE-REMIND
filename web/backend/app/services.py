import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import current_app
from . import mongo

ASSIGNMENTS_COLLECTION = 'assignments'
WEBHOOK_LOGS_COLLECTION = 'webhook_logs'
SETTINGS_COLLECTION = 'settings'

def check_and_send_notifications():
    """Check for urgent assignments and send notifications."""
    try:
        webhook_setting = mongo.db[SETTINGS_COLLECTION].find_one({'key': 'webhooks'})
        if not webhook_setting or not webhook_setting.get('value'): return

        webhooks = json.loads(webhook_setting['value'])
        active_webhooks = [w for w in webhooks if w.get('enabled', False)]
        if not active_webhooks: return

        now = datetime.utcnow()
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
    """Generic webhook sender."""
    try:
        webhook_type = webhook_config.get('type')
        config = webhook_config.get('config', {})
        
        # ... (implementation for different webhook types) ...
        success = False
        if webhook_type == 'email':
            success = send_email_notification(config, message)
        # Add other types like telegram, discord etc. here
        
        log_data = {
            'webhook_type': webhook_type, 'message': message,
            'status': 'success' if success else 'failed',
            'created_at': datetime.utcnow()
        }
        mongo.db[WEBHOOK_LOGS_COLLECTION].insert_one(log_data)
        return success
    except Exception as e:
        current_app.logger.error(f"发送通知失败: {str(e)}")
        return False

def send_email_notification(config, message):
    """Sends an email notification."""
    try:
        # This requires mail configuration in config.py
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from config import Config
        msg = MIMEMultipart()
        msg['From'] = Config.MAIL_SENDER
        msg['To'] = config.get('to_email') # The recipient is from webhook settings
        msg['Subject'] = "作业提醒通知"
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        server = smtplib.SMTP_SSL(Config.MAIL_SMTP_SERVER, Config.MAIL_SMTP_PORT)
        server.login(Config.MAIL_SENDER, Config.MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        current_app.logger.error(f"邮件发送失败: {str(e)}")
        return False