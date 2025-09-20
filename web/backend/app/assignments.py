"""
作业管理模块
提供作业的CRUD操作和状态管理
"""

from flask import Blueprint, request, jsonify, session
from bson import ObjectId
from datetime import datetime, timedelta
import logging
from . import mongo
from .auth import login_required
from .model import CompletedAssignment

# 创建蓝图
assignments_bp = Blueprint('assignments', __name__, url_prefix='/api/assignments')

# 配置日志
logger = logging.getLogger(__name__)

# 集合名称
ASSIGNMENTS_COLLECTION = 'assignments'
TESTS_COLLECTION = 'tests'

@assignments_bp.route('/standard', methods=['GET'])
@login_required
def get_standard_assignments():
    """获取标准作业列表（作业和测试）"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        logger.info(f"用户 {user_id} 请求获取作业列表")
        
        # 获取已完成的作业ID列表
        completed_manager = CompletedAssignment(mongo.db)
        completed_ids = completed_manager.get_user_completed(user_id)
        completed_set = set(str(aid) for aid in completed_ids)
        
        # 获取作业数据
        assignments = list(mongo.db[ASSIGNMENTS_COLLECTION].find({}).sort('due_date', 1))
        tests = list(mongo.db[TESTS_COLLECTION].find({}).sort('due_date', 1))
        
        # 转换数据格式
        tasks = []
        
        # 处理作业
        for assignment in assignments:
            assignment_id = str(assignment['_id'])
            task = {
                'id': assignment_id,
                'subject': assignment.get('subject', '未知科目'),
                'type': 'homework',
                'details': {
                    'task': assignment.get('title', '无标题'),
                    'deadline': assignment.get('due_date', '').isoformat() if assignment.get('due_date') else '',
                    'url': assignment.get('url', '')
                },
                'completed': assignment_id in completed_set
            }
            tasks.append(task)
        
        # 处理测试
        for test in tests:
            test_id = str(test['_id'])
            task = {
                'id': test_id,
                'subject': test.get('subject', '未知科目'),
                'type': 'test',
                'details': {
                    'task': test.get('title', '无标题'),
                    'deadline': test.get('due_date', '').isoformat() if test.get('due_date') else '',
                    'url': test.get('url', '')
                },
                'completed': test_id in completed_set
            }
            tasks.append(task)
        
        logger.info(f"返回 {len(tasks)} 个作业/测试项目")
        
        return jsonify({
            'success': True,
            'tasks': tasks,
            'total': len(tasks)
        })
        
    except Exception as e:
        logger.error(f"获取作业列表失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取作业列表失败'}), 500

@assignments_bp.route('/<assignment_id>/complete', methods=['POST'])
@login_required
def mark_assignment_complete(assignment_id):
    """标记作业为已完成"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        logger.info(f"用户 {user_id} 标记作业 {assignment_id} 为已完成")
        
        # 验证作业是否存在
        assignment = mongo.db[ASSIGNMENTS_COLLECTION].find_one({'_id': ObjectId(assignment_id)})
        if not assignment:
            # 检查是否是测试
            assignment = mongo.db[TESTS_COLLECTION].find_one({'_id': ObjectId(assignment_id)})
            if not assignment:
                return jsonify({'success': False, 'error': '作业不存在'}), 404
        
        # 标记为已完成
        completed_manager = CompletedAssignment(mongo.db)
        assignment_title = assignment.get('title', '未知作业')
        assignment_subject = assignment.get('subject', '未知科目')
        result = completed_manager.mark_completed(user_id, assignment_id, assignment_title, assignment_subject)
        
        if result:
            logger.info(f"作业 {assignment_id} 标记完成成功")
            return jsonify({'success': True, 'message': '作业已标记为完成'})
        else:
            return jsonify({'success': False, 'error': '标记失败，可能已经完成'}), 400
            
    except Exception as e:
        logger.error(f"标记作业完成失败: {str(e)}")
        return jsonify({'success': False, 'error': '标记完成失败'}), 500

@assignments_bp.route('/<assignment_id>/uncomplete', methods=['POST'])
@login_required
def mark_assignment_uncomplete(assignment_id):
    """撤销作业完成状态"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        logger.info(f"用户 {user_id} 撤销作业 {assignment_id} 的完成状态")
        
        # 撤销完成状态
        completed_manager = CompletedAssignment(mongo.db)
        result = completed_manager.unmark_completed(user_id, assignment_id)
        
        if result:
            logger.info(f"作业 {assignment_id} 撤销完成成功")
            return jsonify({'success': True, 'message': '已撤销完成状态'})
        else:
            return jsonify({'success': False, 'error': '撤销失败，可能未完成'}), 400
            
    except Exception as e:
        logger.error(f"撤销作业完成失败: {str(e)}")
        return jsonify({'success': False, 'error': '撤销失败'}), 500

@assignments_bp.route('/stats', methods=['GET'])
@login_required
def get_assignments_stats():
    """获取作业统计信息"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        # 获取已完成的作业ID列表
        completed_manager = CompletedAssignment(mongo.db)
        completed_ids = completed_manager.get_user_completed(user_id)
        completed_set = set(str(aid) for aid in completed_ids)
        
        # 统计作业和测试
        now = datetime.utcnow()
        
        # 获取所有作业和测试
        assignments = list(mongo.db[ASSIGNMENTS_COLLECTION].find({}))
        tests = list(mongo.db[TESTS_COLLECTION].find({}))
        all_tasks = assignments + tests
        
        # 统计各种状态
        total = len(all_tasks)
        completed = len([task for task in all_tasks if str(task['_id']) in completed_set])
        
        # 紧急任务（2天内到期）
        urgent = 0
        # 即将到期（7天内到期）
        soon = 0
        
        for task in all_tasks:
            if str(task['_id']) in completed_set:
                continue  # 跳过已完成的任务
                
            due_date = task.get('due_date')
            if due_date:
                if isinstance(due_date, str):
                    due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                
                days_until_due = (due_date - now).days
                
                if days_until_due <= 2:
                    urgent += 1
                elif days_until_due <= 7:
                    soon += 1
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'completed': completed,
                'urgent': urgent,
                'soon': soon,
                'remaining': total - completed
            }
        })
        
    except Exception as e:
        logger.error(f"获取作业统计失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取统计信息失败'}), 500