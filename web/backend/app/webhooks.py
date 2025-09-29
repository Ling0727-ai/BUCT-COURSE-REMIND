from flask import Blueprint, request, jsonify
from .auth import login_required
from . import services as services_module

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/api/webhook')

@webhooks_bp.route('/test', methods=['POST'])
@login_required
def test_webhook():
    data = request.get_json()
    webhook_config = data.get('webhook')
    
    if not webhook_config:
        return jsonify({'error': 'Webhook配置不能为空'}), 400
    
    test_message = "这是一条来自BUCT课程提醒系统的测试消息"
    success = services_module.send_webhook_notification(webhook_config, test_message)
    
    if success:
        return jsonify({'message': '测试消息发送成功'})
    else:
        return jsonify({'error': '测试消息发送失败'}), 500