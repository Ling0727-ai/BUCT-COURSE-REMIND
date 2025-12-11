# -*- coding: utf-8 -*-
"""
管理员接口模块

提供管理员专用的API接口，包括：
1. 手动触发清理任务
2. 查看系统统计信息
3. 管理已完成作业记录
"""

from datetime import datetime, timedelta

from flask import Blueprint, jsonify, current_app, session

from . import mongo
from .auth import login_required
from .model import CompletedAssignment

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def admin_required(f):
    """管理员权限装饰器"""

    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '未登录'}), 401

        # 查找用户信息
        user = mongo.db.users.find_one({'_id': user_id})
        if not user or not user.get('is_admin', False):
            return jsonify({'error': '需要管理员权限'}), 403

        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


@admin_bp.route('/cleanup/trigger', methods=['POST'])
@login_required
@admin_required
def trigger_cleanup():
    """手动触发清理任务"""
    try:
        from .cleanup_tasks import cleanup_tasks

        # 手动执行清理任务
        with current_app.app_context():
            cleanup_tasks._run_cleanup_tasks()

        current_app.logger.info("管理员手动触发清理任务")
        return jsonify({
            'success': True,
            'message': '清理任务已执行',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f"手动清理任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '清理任务执行失败',
            'details': str(e)
        }), 500


@admin_bp.route('/stats/completed-assignments', methods=['GET'])
@login_required
@admin_required
def get_completed_assignments_stats():
    """获取已完成作业统计信息"""
    try:
        completed_model = CompletedAssignment(mongo.db)

        # 统计信息
        total_completed = mongo.db.completed_assignments.count_documents({})

        # 按用户统计
        user_stats = list(mongo.db.completed_assignments.aggregate([
            {
                '$group': {
                    '_id': '$user_id',
                    'count': {'$sum': 1},
                    'latest_completion': {'$max': '$completed_at'}
                }
            },
            {
                '$lookup': {
                    'from': 'users',
                    'localField': '_id',
                    'foreignField': '_id',
                    'as': 'user_info'
                }
            },
            {
                '$project': {
                    'user_id': '$_id',
                    'username': {'$arrayElemAt': ['$user_info.username', 0]},
                    'completed_count': '$count',
                    'latest_completion': '$latest_completion'
                }
            }
        ]))

        # 今日完成统计
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_completed = mongo.db.completed_assignments.count_documents({
            'completed_at': {'$gte': today_start}
        })

        # 即将过期的记录
        next_hour = datetime.now() + timedelta(hours=1)
        expiring_soon = mongo.db.completed_assignments.count_documents({
            'expires_at': {'$lte': next_hour}
        })

        return jsonify({
            'success': True,
            'stats': {
                'total_completed': total_completed,
                'today_completed': today_completed,
                'expiring_soon': expiring_soon,
                'user_stats': user_stats
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f"获取完成作业统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取统计信息失败',
            'details': str(e)
        }), 500


@admin_bp.route('/completed-assignments', methods=['GET'])
@login_required
@admin_required
def list_completed_assignments():
    """列出所有已完成作业记录"""
    try:
        # 获取查询参数
        from flask import request
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        skip = (page - 1) * limit

        # 查询记录
        records = list(mongo.db.completed_assignments.aggregate([
            {
                '$lookup': {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': '_id',
                    'as': 'user_info'
                }
            },
            {
                '$project': {
                    'assignment_id': 1,
                    'assignment_title': 1,
                    'assignment_subject': 1,
                    'completed_at': 1,
                    'expires_at': 1,
                    'username': {'$arrayElemAt': ['$user_info.username', 0]},
                    'user_email': {'$arrayElemAt': ['$user_info.email', 0]}
                }
            },
            {'$sort': {'completed_at': -1}},
            {'$skip': skip},
            {'$limit': limit}
        ]))

        # 总数
        total_count = mongo.db.completed_assignments.count_documents({})

        return jsonify({
            'success': True,
            'records': records,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f"列出完成作业记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取记录列表失败',
            'details': str(e)
        }), 500


@admin_bp.route('/system/status', methods=['GET'])
@login_required
@admin_required
def get_system_status():
    """获取系统状态信息"""
    try:
        from .cleanup_tasks import cleanup_tasks

        # 数据库统计
        db_stats = {
            'users': mongo.db.users.count_documents({}),
            'completed_assignments': mongo.db.completed_assignments.count_documents({}),
            'verification_codes': mongo.db.verification_codes.count_documents({}),
            'webhook_logs': mongo.db.webhook_logs.count_documents({})
        }

        # 清理任务状态
        cleanup_status = {
            'running': cleanup_tasks.running,
            'thread_alive': cleanup_tasks.cleanup_thread.is_alive() if cleanup_tasks.cleanup_thread else False
        }

        return jsonify({
            'success': True,
            'system_status': {
                'database_stats': db_stats,
                'cleanup_tasks': cleanup_status,
                'server_time': datetime.now().isoformat()
            }
        })

    except Exception as e:
        current_app.logger.error(f"获取系统状态失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取系统状态失败',
            'details': str(e)
        }), 500
