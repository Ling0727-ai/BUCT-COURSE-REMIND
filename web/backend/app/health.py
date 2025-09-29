"""
健康检查端点
"""

from flask import Blueprint, jsonify
from . import mongo
import os

health_bp = Blueprint('health', __name__, url_prefix='/api')

@health_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        # 检查MongoDB连接
        mongo.db.admin.command('ping')
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # 检查邮件配置
    mail_configured = os.getenv('MAIL_PASSWORD', 'dummy_password_for_dev') != 'dummy_password_for_dev'
    
    health_data = {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "mail_configured": mail_configured,
        "services": {
            "verification_code": "available",
            "user_registration": "available",
            "user_authentication": "available"
        }
    }
    
    status_code = 200 if health_data["status"] == "healthy" else 503
    return jsonify(health_data), status_code