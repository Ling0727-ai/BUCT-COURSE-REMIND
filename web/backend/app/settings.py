from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import json
from .auth import login_required
from . import mongo

settings_bp = Blueprint('settings', __name__, url_prefix='/api')

SETTINGS_COLLECTION = 'settings'

@settings_bp.route('/settings', methods=['GET'])
@login_required
def get_settings():
    settings = {}
    db_settings = mongo.db[SETTINGS_COLLECTION].find()
    for setting in db_settings:
        if setting['key'] == 'webhooks':
            try:
                settings[setting['key']] = json.loads(setting['value']) if setting.get('value') else []
            except json.JSONDecodeError:
                settings[setting['key']] = []
        else:
            settings[setting['key']] = setting.get('value')
    
    # Default values
    if 'serverUrl' not in settings: settings['serverUrl'] = 'http://localhost:5000'
    if 'webhooks' not in settings: settings['webhooks'] = []
    if 'scrape_interval' not in settings: settings['scrape_interval'] = '60'
    
    return jsonify(settings)

@settings_bp.route('/settings', methods=['POST'])
@login_required
def save_settings():
    data = request.get_json()
    try:
        for key, value in data.items():
            if key == 'password' and not value:
                continue
            
            value_to_save = json.dumps(value) if key == 'webhooks' else str(value)
            
            mongo.db[SETTINGS_COLLECTION].update_one(
                {'key': key},
                {'$set': {'value': value_to_save, 'updated_at': datetime.now()}},
                upsert=True
            )
        
        current_app.logger.info("设置保存成功")
        return jsonify({'message': '设置保存成功'})
    except Exception as e:
        current_app.logger.error(f"设置保存失败: {str(e)}")
        return jsonify({'error': '设置保存失败', 'details': str(e)}), 500