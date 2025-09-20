"""
作业管理模块
提供作业的CRUD操作和状态管理
"""

from flask import Blueprint, request, jsonify, session
from bson import ObjectId
from datetime import datetime, timedelta
import logging
import sys
import os
from . import mongo
from .auth import login_required
from .model import CompletedAssignment

# 创建蓝图
assignments_bp = Blueprint('assignments', __name__, url_prefix='/api/assignments')

# 配置日志
logger = logging.getLogger(__name__)

def get_scraper_data(user_id=None):
    """调用scraper获取实时课程数据"""
    try:
        # 添加scraper.py所在目录到Python路径
        scraper_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scraper.py')
        scraper_dir = os.path.dirname(scraper_path)
        
        if scraper_dir not in sys.path:
            sys.path.insert(0, scraper_dir)
        
        # 导入scraper模块
        import scraper
        
        # 获取标准格式的课程数据
        logger.info(f"正在为用户 {user_id} 获取实时课程数据...")
        standard_data = scraper.get_standard_format_details(user_id)
        
        if standard_data:
            logger.info(f"成功获取 {len(standard_data)} 个课程任务")
            return standard_data
        else:
            logger.warning("未获取到课程数据")
            return []
            
    except Exception as e:
        logger.error(f"调用scraper获取数据失败: {str(e)}")
        return []

@assignments_bp.route('/standard', methods=['GET'])
@login_required
def get_standard_assignments():
    """获取标准作业列表（通过scraper实时获取）"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        logger.info(f"用户 {user_id} 请求获取作业列表")
        
        # 获取已完成的作业ID列表
        completed_manager = CompletedAssignment(mongo.db)
        completed_ids = completed_manager.get_user_completed(user_id)
        completed_set = set(str(aid) for aid in completed_ids)
        
        # 通过scraper获取实时数据
        scraper_data = get_scraper_data(user_id)
        
        # 转换数据格式
        tasks = []
        
        for item in scraper_data:
            # 生成唯一ID（基于科目和任务内容）
            task_id = f"{item.get('type', 'unknown')}_{hash(item.get('subject', '') + item.get('details', {}).get('task', ''))}"
            
            task = {
                'id': task_id,
                'subject': item.get('subject', '未知科目'),
                'type': item.get('type', 'homework'),
                'details': {
                    'task': item.get('details', {}).get('task', '无标题'),
                    'deadline': item.get('details', {}).get('deadline', ''),
                    'url': item.get('details', {}).get('url', '')
                },
                'completed': task_id in completed_set
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
        
        # 获取实时数据来验证作业是否存在
        scraper_data = get_scraper_data(user_id)
        
        # 查找对应的作业
        assignment = None
        for item in scraper_data:
            item_id = f"{item.get('type', 'unknown')}_{hash(item.get('subject', '') + item.get('details', {}).get('task', ''))}"
            if item_id == assignment_id:
                assignment = item
                break
        
        if not assignment:
            return jsonify({'success': False, 'error': '作业不存在'}), 404
        
        # 标记为已完成
        completed_manager = CompletedAssignment(mongo.db)
        assignment_title = assignment.get('details', {}).get('task', '未知作业')
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
        
        # 通过scraper获取实时数据
        scraper_data = get_scraper_data(user_id)
        
        # 统计各种状态
        now = datetime.utcnow()
        total = len(scraper_data)
        completed = 0
        urgent = 0
        soon = 0
        
        for item in scraper_data:
            item_id = f"{item.get('type', 'unknown')}_{hash(item.get('subject', '') + item.get('details', {}).get('task', ''))}"
            
            if item_id in completed_set:
                completed += 1
                continue  # 跳过已完成的任务
                
            # 检查截止日期
            deadline_str = item.get('details', {}).get('deadline', '')
            if deadline_str:
                try:
                    if isinstance(deadline_str, str):
                        due_date = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                    else:
                        due_date = deadline_str
                    
                    days_until_due = (due_date - now).days
                    
                    if days_until_due <= 2:
                        urgent += 1
                    elif days_until_due <= 7:
                        soon += 1
                except (ValueError, TypeError):
                    pass  # 忽略无效的日期格式
        
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