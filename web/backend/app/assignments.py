"""
作业管理模块
提供作业的CRUD操作和状态管理
使用统一的状态管理系统
"""

from flask import Blueprint, request, jsonify, session
from bson import ObjectId
from datetime import datetime, timedelta
import logging
from . import mongo
from .auth import login_required

# 创建蓝图
assignments_bp = Blueprint('assignments', __name__, url_prefix='/api/assignments')

# 配置日志
logger = logging.getLogger(__name__)

def get_scraper_instance():
    """获取scraper实例"""
    try:
        # 导入新版scraper
        from .scraper import get_scraper
        return get_scraper()
    except ImportError as e:
        logger.error(f"导入scraper失败: {e}")
        return None
    except Exception as e:
        logger.error(f"获取scraper实例失败: {e}")
        return None

@assignments_bp.route('/standard', methods=['GET'])
@login_required
def get_standard_assignments():
    """获取标准作业列表（从数据库获取）"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        logger.info(f"用户 {user_id} 请求获取作业列表")
        
        # 从数据库获取数据
        from .course_data import get_course_data_manager
        course_data_mgr = get_course_data_manager()
        tasks = course_data_mgr.get_user_course_data(user_id)
        
        # 获取作业状态信息
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        completed_ids = status_manager.get_completed_assignment_ids(user_id)
        deleted_ids = status_manager.get_deleted_assignment_ids(user_id)
        completed_set = set(str(aid) for aid in completed_ids)
        deleted_set = set(str(aid) for aid in deleted_ids)
        
        # 转换数据格式（过滤掉已删除的任务）
        formatted_tasks = []
        homework_count = 0
        test_count = 0
        
        for task in tasks:
            task_id = task.get('task_id')
            task_type = task.get('type', 'homework')
            
            # 跳过已删除的任务
            if task_id in deleted_set:
                continue
            
            formatted_task = {
                'id': task_id,
                'subject': task.get('subject', ''),
                'type': task_type,
                'details': {
                    'task': task.get('title', ''),
                    'deadline': task.get('deadline', ''),
                    'url': task.get('url', ''),
                    'can_submit': True,
                    'is_group': False,
                    'details_content': task.get('details', '')
                },
                'completed': task_id in completed_set,
                'has_tasks': True,
                'tasks_count': 1
            }
            formatted_tasks.append(formatted_task)
            
            if task_type == 'homework':
                homework_count += 1
            else:
                test_count += 1
        
        stats = {
            'homework_count': homework_count,
            'tests_count': test_count,
            'total_count': len(formatted_tasks)
        }
        
        logger.info(f"从数据库为用户 {user_id} 返回 {len(formatted_tasks)} 个作业/测试项目")
        
        return jsonify({
            'success': True,
            'tasks': formatted_tasks,
            'total': len(formatted_tasks),
            'stats': stats,
            'source': 'database'
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
        
        # 从前端请求中获取作业信息
        data = request.get_json() or {}
        assignment_title = data.get('title', '未知作业')
        assignment_subject = data.get('subject', '未知科目')
        
        # 使用统一状态管理标记为已完成
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        result = status_manager.mark_completed(user_id, assignment_id, assignment_title, assignment_subject)
        
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
        
        # 使用统一状态管理撤销完成状态
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        result = status_manager.restore_assignment(user_id, assignment_id)
        
        if result:
            logger.info(f"作业 {assignment_id} 撤销完成成功")
            return jsonify({'success': True, 'message': '已撤销完成状态'})
        else:
            return jsonify({'success': False, 'error': '撤销失败，可能未完成'}), 400
            
    except Exception as e:
        logger.error(f"撤销作业完成失败: {str(e)}")
        return jsonify({'success': False, 'error': '撤销失败'}), 500

@assignments_bp.route('/<assignment_id>/remind', methods=['POST'])
@login_required
def remind_assignment(assignment_id):
    """提醒作业/测试"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        logger.info(f"用户 {user_id} 提醒作业: {assignment_id}")
        
        # 从前端请求中获取作业信息
        data = request.get_json() or {}
        subject = data.get('subject', '作业')
        task = data.get('title', '任务')
        deadline = data.get('deadline', '')
        assignment_type = '作业' if 'homework' in assignment_id else '测试'
        
        # 格式化截止时间显示
        deadline_display = deadline
        if deadline and deadline != '':
            try:
                from datetime import datetime
                if 'T' in deadline:
                    # ISO格式转换为中文格式
                    dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                    deadline_display = dt.strftime('%Y年%m月%d日 %H:%M:%S')
            except ValueError:
                pass  # 保持原格式
        
        # 记录提醒日志
        logger.info(f"提醒{assignment_type}: {subject} - {task}, 截止时间: {deadline_display}")
        
        return jsonify({
            'success': True,
            'message': f"已设置{assignment_type}提醒: {subject} - {task}" + (f"，截止时间: {deadline_display}" if deadline_display else ""),
            'assignment': {
                'subject': subject,
                'task': task,
                'deadline': deadline_display,
                'type': assignment_type
            }
        })
        
    except Exception as e:
        logger.error(f"提醒作业失败: {str(e)}")
        return jsonify({'success': False, 'error': '提醒失败'}), 500

@assignments_bp.route('/enhanced', methods=['GET'])
@login_required
def get_enhanced_assignments():
    """获取增强作业列表（从数据库获取）"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        logger.info(f"用户 {user_id} 请求获取增强作业列表")
        
        # 从数据库获取数据
        from .course_data import get_course_data_manager
        course_data_mgr = get_course_data_manager()
        tasks = course_data_mgr.get_user_course_data(user_id)
        
        # 获取作业状态信息
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        completed_ids = status_manager.get_completed_assignment_ids(user_id)
        deleted_ids = status_manager.get_deleted_assignment_ids(user_id)
        completed_set = set(str(aid) for aid in completed_ids)
        deleted_set = set(str(aid) for aid in deleted_ids)
        
        # 处理增强数据（过滤掉已删除的任务）
        enhanced_assignments = []
        homework_count = 0
        test_count = 0
        
        for task in tasks:
            task_id = task.get('task_id')
            task_type = task.get('type', 'homework')
            
            # 跳过已删除的任务
            if task_id in deleted_set:
                continue
            
            enhanced_assignment = {
                'id': task_id,
                'subject': task.get('subject', ''),
                'type': task_type,
                'title': task.get('title', ''),
                'deadline': task.get('deadline', ''),
                'url': task.get('url', ''),
                'can_submit': True,
                'is_group': False,
                'details_content': task.get('details', ''),
                'completed': task_id in completed_set,
                'has_detailed_tasks': bool(task.get('details', '').strip()),
                'tasks_count': 1
            }
            enhanced_assignments.append(enhanced_assignment)
            
            if task_type == 'homework':
                homework_count += 1
            else:
                test_count += 1
        
        stats = {
            'homework_count': homework_count,
            'tests_count': test_count,
            'total_count': len(enhanced_assignments)
        }
        
        logger.info(f"从数据库返回 {len(enhanced_assignments)} 个增强作业/测试项目")
        
        return jsonify({
            'success': True,
            'assignments': enhanced_assignments,
            'total': len(enhanced_assignments),
            'statistics': stats,
            'query_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'database'
        })
        
    except Exception as e:
        logger.error(f"获取增强作业列表失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取增强作业列表失败'}), 500

@assignments_bp.route('/completed', methods=['GET'])
@login_required
def get_completed_assignments():
    """获取已完成的作业ID列表"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        # 获取已完成的作业ID列表
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        completed_ids = status_manager.get_completed_assignment_ids(user_id)
        
        return jsonify({
            'success': True,
            'completed_assignments': [str(aid) for aid in completed_ids]
        })
        
    except Exception as e:
        logger.error(f"获取已完成作业列表失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取已完成作业列表失败'}), 500

@assignments_bp.route('/<assignment_id>/delete', methods=['POST'])
@login_required
def delete_assignment(assignment_id):
    """软删除作业（移至回收站）"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        logger.info(f"用户 {user_id} 删除作业 {assignment_id}")
        
        # 从前端请求中获取作业信息
        data = request.get_json() or {}
        assignment_title = data.get('title', '未知作业')
        assignment_subject = data.get('subject', '未知科目')
        assignment_type = data.get('type', 'homework')  # 获取作业类型
        
        # 使用统一状态管理标记为已删除
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        result = status_manager.mark_deleted(user_id, assignment_id, assignment_title, assignment_subject, assignment_type)
        
        if result.upserted_id or result.matched_count > 0:
            logger.info(f"作业 {assignment_id} 标记删除成功")
            return jsonify({'success': True, 'message': '作业已移至回收站'})
        else:
            return jsonify({'success': False, 'error': '删除失败'}), 500
            
    except Exception as e:
        logger.error(f"删除作业失败: {str(e)}")
        return jsonify({'success': False, 'error': '删除作业失败'}), 500

@assignments_bp.route('/<assignment_id>/restore', methods=['POST'])
@login_required
def restore_assignment(assignment_id):
    """恢复已删除的作业"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        logger.info(f"用户 {user_id} 恢复作业 {assignment_id}")
        
        # 使用统一状态管理恢复作业
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        result = status_manager.restore_assignment(user_id, assignment_id)
        
        if result.deleted_count > 0:
            logger.info(f"作业 {assignment_id} 恢复成功")
            return jsonify({'success': True, 'message': '作业已恢复'})
        else:
            return jsonify({'success': False, 'error': '恢复失败，作业不存在'}), 404
            
    except Exception as e:
        logger.error(f"恢复作业失败: {str(e)}")
        return jsonify({'success': False, 'error': '恢复作业失败'}), 500

@assignments_bp.route('/<assignment_id>/permanent-delete', methods=['DELETE'])
@login_required
def permanent_delete_assignment(assignment_id):
    """永久删除作业"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        logger.info(f"用户 {user_id} 永久删除作业 {assignment_id}")
        
        # 永久删除作业状态记录
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        result = status_manager.restore_assignment(user_id, assignment_id)  # 删除状态记录
        
        logger.info(f"作业 {assignment_id} 永久删除成功")
        return jsonify({'success': True, 'message': '作业已永久删除'})
            
    except Exception as e:
        logger.error(f"永久删除作业失败: {str(e)}")
        return jsonify({'success': False, 'error': '永久删除作业失败'}), 500

@assignments_bp.route('/deleted', methods=['GET'])
@login_required
def get_deleted_assignments():
    """获取已删除的作业列表"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        # 获取已删除的作业列表
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        deleted_assignments = status_manager.get_user_assignment_status(user_id, 'deleted')
        
        # 转换ObjectId为字符串
        for assignment in deleted_assignments:
            assignment['_id'] = str(assignment['_id'])
            assignment['user_id'] = str(assignment['user_id'])
            if assignment.get('status_time'):
                assignment['delete_time'] = assignment['status_time'].isoformat()
            if assignment.get('updated_at'):
                assignment['updated_at'] = assignment['updated_at'].isoformat()
        
        return jsonify({
            'success': True,
            'deleted_assignments': deleted_assignments,
            'count': len(deleted_assignments)
        })
        
    except Exception as e:
        logger.error(f"获取已删除作业列表失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取已删除作业列表失败'}), 500

@assignments_bp.route('/clear-deleted', methods=['DELETE'])
@login_required
def clear_deleted_assignments():
    """清空已删除的作业"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        # 清空已删除的作业
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        deleted_count = status_manager.clear_user_status(user_id, 'deleted')
        
        logger.info(f"用户 {user_id} 清空已删除作业，共删除 {deleted_count} 条")
        
        return jsonify({
            'success': True,
            'message': f'已清空 {deleted_count} 个已删除的作业',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        logger.error(f"清空已删除作业失败: {str(e)}")
        return jsonify({'success': False, 'error': '清空已删除作业失败'}), 500

@assignments_bp.route('/stats', methods=['GET'])
@login_required
def get_assignments_stats():
    """获取作业统计信息（从数据库获取）"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        # 从数据库获取数据
        from .course_data import get_course_data_manager
        course_data_mgr = get_course_data_manager()
        tasks = course_data_mgr.get_user_course_data(user_id)
        
        # 获取作业状态信息
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        completed_ids = status_manager.get_completed_assignment_ids(user_id)
        deleted_ids = status_manager.get_deleted_assignment_ids(user_id)
        completed_set = set(str(aid) for aid in completed_ids)
        deleted_set = set(str(aid) for aid in deleted_ids)
        
        # 统计各种状态（排除已删除的任务）
        now = datetime.now()
        active_tasks = [task for task in tasks if task.get('task_id') not in deleted_set]
        total = len(active_tasks)
        completed = 0
        urgent = 0
        soon = 0
        
        # 统计所有活跃任务
        for task in active_tasks:
            task_id = task.get('task_id')
            deadline = task.get('deadline', '')
            
            if task_id in completed_set:
                completed += 1
                continue
                
            # 检查截止日期
            if deadline:
                try:
                    # 尝试解析多种时间格式
                    if 'T' in deadline:
                        # ISO格式
                        due_date = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                    elif '年' in deadline and '月' in deadline and '日' in deadline:
                        # 中文格式：2025年9月23日 23:59:00
                        due_date = datetime.strptime(deadline, '%Y年%m月%d日 %H:%M:%S')
                    else:
                        # 其他格式，跳过
                        continue
                    
                    days_until_due = (due_date - now).days
                    
                    if days_until_due <= 2:
                        urgent += 1
                    elif days_until_due <= 7:
                        soon += 1
                except (ValueError, TypeError):
                    pass
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'completed': completed,
                'urgent': urgent,
                'soon': soon,
                'remaining': total - completed
            },
            'source': 'database'
        })
        
    except Exception as e:
        logger.error(f"获取作业统计失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取统计信息失败'}), 500