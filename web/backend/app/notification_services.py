import json
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from flask import current_app

from . import mongo

ASSIGNMENTS_COLLECTION = 'assignments'
WEBHOOK_LOGS_COLLECTION = 'webhook_logs'
SETTINGS_COLLECTION = 'settings'


def check_and_send_notifications():
    """
    [已弃用] 检查紧急作业并发送通知

    ⚠️ 警告：此函数已被scheduler.py中的自动提醒系统取代。
    直接调用此函数可能导致重复发送邮件。
    建议使用scheduler的auto-reminder功能，它会自动检查并创建提醒，
    且能避免重复发送。

    此函数仅保留用于手动触发测试。
    """
    try:
        current_app.logger.warning("⚠️ check_and_send_notifications() 已弃用，可能导致重复邮件，建议使用auto-reminder")

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
    """Sends an email notification using environment variables.
    Expected config: {'to_email': 'recipient@example.com'}
    Returns True on success, False on failure with error logged.
    """
    try:
        import os
        smtp_server = os.getenv('MAIL_SMTP_SERVER', 'smtp.163.com')
        smtp_port = int(os.getenv('MAIL_SMTP_PORT', 465))
        sender_email = os.getenv('MAIL_SENDER', 'buct_course_remind@163.com')
        sender_password = os.getenv('MAIL_PASSWORD', '')

        # DEBUG: 记录邮件配置（不记录密码）
        current_app.logger.debug(f"邮件配置 - SMTP服务器: {smtp_server}, 端口: {smtp_port}, 发件人: {sender_email}")
        current_app.logger.debug(
            f"邮箱密码已配置: {bool(sender_password and sender_password != 'dummy_password_for_dev')}")

        if not sender_password or sender_password == 'dummy_password_for_dev':
            current_app.logger.error("❌ 邮箱密码未配置，无法发送邮件 (MAIL_PASSWORD 未设置或为默认值)")
            current_app.logger.error("请在.env文件中设置正确的MAIL_PASSWORD（163邮箱授权码）")
            return False

        to_email = (config or {}).get('to_email')
        if not to_email:
            current_app.logger.error("❌ 未指定收件人邮箱 (config.to_email 为空)")
            return False

        current_app.logger.debug(f"准备发送邮件到: {to_email}")
        current_app.logger.debug(f"邮件内容长度: {len(message) if message else 0} 字符")

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = "作业提醒通知"
        msg.attach(MIMEText(message or '', 'plain', 'utf-8'))

        # 多配置尝试：SSL 优先，其次 StartTLS
        smtp_candidates = [
            {'server': smtp_server, 'port': smtp_port, 'ssl': True},
            {'server': smtp_server, 'port': 587, 'ssl': False},
            {'server': smtp_server, 'port': 25, 'ssl': False},
        ]

        last_err = None
        attempt_count = 0
        for conf in smtp_candidates:
            attempt_count += 1
            server = None
            try:
                current_app.logger.debug(
                    f"尝试 #{attempt_count}: 连接到 {conf['server']}:{conf['port']} (SSL={conf['ssl']})")

                if conf['ssl']:
                    server = smtplib.SMTP_SSL(conf['server'], conf['port'], timeout=30)
                else:
                    server = smtplib.SMTP(conf['server'], conf['port'], timeout=30)
                    try:
                        server.starttls()
                        current_app.logger.debug("StartTLS 升级成功")
                    except Exception as e:
                        current_app.logger.debug(f"StartTLS 升级失败或不支持: {e}")

                current_app.logger.debug(f"正在登录邮箱: {sender_email}")
                server.login(sender_email, sender_password)
                current_app.logger.debug("邮箱登录成功")

                current_app.logger.debug("正在发送邮件...")
                server.send_message(msg)
                server.quit()

                current_app.logger.info(
                    f"✅ 邮件发送成功: {to_email} (使用配置: {conf['server']}:{conf['port']}, SSL={conf['ssl']})")
                return True
            except smtplib.SMTPAuthenticationError as e:
                last_err = e
                current_app.logger.error(f"❌ SMTP认证失败 (配置 #{attempt_count}): {e}")
                current_app.logger.error("请检查MAIL_SENDER和MAIL_PASSWORD是否正确（163邮箱需要使用授权码，不是登录密码）")
                try:
                    server.quit()
                except Exception:
                    pass
            except smtplib.SMTPException as e:
                last_err = e
                current_app.logger.warning(f"⚠️ SMTP错误 (配置 #{attempt_count}): {e}，尝试下一个配置")
                try:
                    server.quit()
                except Exception:
                    pass
            except Exception as e:
                last_err = e
                current_app.logger.warning(
                    f"⚠️ 连接失败 (配置 #{attempt_count}): {type(e).__name__}: {e}，尝试下一个配置")
                try:
                    server.quit()
                except Exception:
                    pass

        current_app.logger.error(f"❌ 所有SMTP配置均失败，邮件发送失败: {type(last_err).__name__}: {last_err}")
        return False
    except Exception as e:
        current_app.logger.error(f"❌ 邮件发送过程异常: {type(e).__name__}: {str(e)}")
        import traceback
        current_app.logger.error(f"异常堆栈:\n{traceback.format_exc()}")
        return False
