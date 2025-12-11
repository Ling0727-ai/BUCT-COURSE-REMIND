from datetime import datetime, timedelta

from flask import Blueprint, jsonify

from . import mongo
from .auth import login_required

utils_bp = Blueprint('utils', __name__, url_prefix='/api')

ASSIGNMENTS_COLLECTION = 'assignments'
TESTS_COLLECTION = 'tests'


@utils_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点 - Docker容器使用"""
    try:
        # 检查数据库连接
        mongo.db.command('ping')

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@utils_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    total_assignments = mongo.db[ASSIGNMENTS_COLLECTION].count_documents({})
    total_tests = mongo.db[TESTS_COLLECTION].count_documents({})

    now = datetime.now()
    urgent_assignments = mongo.db[ASSIGNMENTS_COLLECTION].count_documents({
        'due_date': {'$lte': now + timedelta(days=2)}
    })

    return jsonify({
        'total_assignments': total_assignments,
        'total_tests': total_tests,
        'urgent_assignments': urgent_assignments,
        'total_items': total_assignments + total_tests
    })
