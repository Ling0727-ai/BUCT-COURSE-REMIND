from datetime import datetime

from flask import Blueprint, request, jsonify, current_app

from . import mongo
from .auth import login_required

settings_bp = Blueprint('settings', __name__, url_prefix='/api')

SETTINGS_COLLECTION = 'settings'


@settings_bp.route('/settings', methods=['GET'])
@login_required
def get_settings():
    settings = {}
    db_settings = mongo.db[SETTINGS_COLLECTION].find()
    for setting in db_settings:
        # 只保留notification_email设置，其他设置简化
        if setting['key'] == 'notification_email':
            settings[setting['key']] = setting.get('value', '')
        # 注释掉webhooks相关设置，只保留邮箱提醒
        # elif setting['key'] == 'webhooks':
        #     try:
        #         settings[setting['key']] = json.loads(setting['value']) if setting.get('value') else []
        #     except json.JSONDecodeError:
        #         settings[setting['key']] = []
        else:
            settings[setting['key']] = setting.get('value')

    # 简化默认值，只保留必要的设置
    if 'notification_email' not in settings: settings['notification_email'] = ''
    # 注释掉其他设置，只保留邮箱提醒功能
    # if 'serverUrl' not in settings: settings['serverUrl'] = 'http://localhost:5000'
    # if 'webhooks' not in settings: settings['webhooks'] = []
    # if 'scrape_interval' not in settings: settings['scrape_interval'] = '60'

    return jsonify(settings)


@settings_bp.route('/settings', methods=['POST'])
@login_required
def save_settings():
    data = request.get_json()
    try:
        for key, value in data.items():
            # 只处理notification_email设置，其他设置忽略或注释掉
            if key == 'notification_email':
                value_to_save = str(value)

                mongo.db[SETTINGS_COLLECTION].update_one(
                    {'key': key},
                    {'$set': {'value': value_to_save, 'updated_at': datetime.now()}},
                    upsert=True
                )
            # 注释掉webhooks相关设置保存，只保留邮箱提醒
            # elif key == 'webhooks':
            #     value_to_save = json.dumps(value)
            #     
            #     mongo.db[SETTINGS_COLLECTION].update_one(
            #         {'key': key},
            #         {'$set': {'value': value_to_save, 'updated_at': datetime.now()}},
            #         upsert=True
            #     )
            # 其他设置忽略，只保留邮箱提醒功能
            # else:
            #     if key == 'password' and not value:
            #         continue
            #     
            #     value_to_save = str(value)
            #     
            #     mongo.db[SETTINGS_COLLECTION].update_one(
            #         {'key': key},
            #         {'$set': {'value': value_to_save, 'updated_at': datetime.now()}},
            #         upsert=True
            #     )

        current_app.logger.info("设置保存成功")
        return jsonify({'message': '设置保存成功'})
    except Exception as e:
        current_app.logger.error(f"设置保存失败: {str(e)}")
        return jsonify({'error': '设置保存失败', 'details': str(e)}), 500


# 添加专门的邮箱设置接口，与前端保持一致
@settings_bp.route('/settings/email', methods=['GET'])
@login_required
def get_email_settings():
    """获取邮箱设置"""
    try:
        email_setting = mongo.db[SETTINGS_COLLECTION].find_one({'key': 'notification_email'})
        return jsonify({
            'to_email': email_setting.get('value', '') if email_setting else ''
        })
    except Exception as e:
        current_app.logger.error(f"获取邮箱设置失败: {str(e)}")
        return jsonify({'error': '获取邮箱设置失败', 'details': str(e)}), 500


@settings_bp.route('/settings/email', methods=['POST'])
@login_required
def save_email_settings():
    """保存邮箱设置"""
    data = request.get_json()
    try:
        to_email = data.get('to_email', '')

        # 验证邮箱格式
        if to_email and not '@' in to_email:
            return jsonify({'error': '邮箱格式不正确'}), 400

        mongo.db[SETTINGS_COLLECTION].update_one(
            {'key': 'notification_email'},
            {'$set': {'value': to_email, 'updated_at': datetime.now()}},
            upsert=True
        )

        current_app.logger.info(f"邮箱设置保存成功: {to_email}")
        return jsonify({'message': '邮箱设置保存成功'})
    except Exception as e:
        current_app.logger.error(f"邮箱设置保存失败: {str(e)}")
        return jsonify({'error': '邮箱设置保存失败', 'details': str(e)}), 500
