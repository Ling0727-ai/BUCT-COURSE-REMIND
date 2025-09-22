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
    """获取标准作业列表（通过新版scraper实时获取）"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        logger.info(f"用户 {user_id} 请求获取作业列表")
        
        # 获取已完成的作业ID列表
        completed_manager = CompletedAssignment(mongo.db)
        completed_ids = completed_manager.get_user_completed(user_id)
        completed_set = set(str(aid) for aid in completed_ids)
        
        # 通过新版scraper获取实时数据
        scraper = get_scraper_instance()
        if not scraper:
            logger.error("scraper实例为None")
            return jsonify({'success': False, 'error': 'scraper初始化失败'}), 500
        
        logger.info(f"scraper实例获取成功: {type(scraper)}")
        
        # 获取待办任务
        result = scraper.get_pending_tasks(user_id)
        
        if not result.get('success'):
            return jsonify({'success': False, 'error': result.get('error', '获取数据失败')}), 500
        
        data = result.get('data', {})
        tasks_list = data.get('tasks', [])
        
        # 转换数据格式
        tasks = []
        
        # 处理统一的任务列表
        for task_data in tasks_list:
            # 根据任务内容生成唯一ID
            subject = task_data.get('subject', '未知科目')
            title = task_data.get('title', '无标题')
            deadline = task_data.get('deadline', '')
            
            # 判断任务类型（根据details字段是否为空）
            task_type = 'homework' if task_data.get('details', '').strip() else 'test'
            
            # 生成任务ID
            task_id = f"{task_type}_{abs(hash(subject + title + deadline))}"
            
            task = {
                'id': task_id,
                'subject': subject,
                'type': task_type,
                'details': {
                    'task': title,
                    'deadline': deadline,
                    'url': task_data.get('url', ''),
                    'can_submit': True,
                    'is_group': False,
                    'details_content': task_data.get('details', '')  # 作业详情内容
                },
                'completed': task_id in completed_set,
                'has_tasks': True,
                'tasks_count': 1
            }
            tasks.append(task)
        
        logger.info(f"返回 {len(tasks)} 个作业/测试项目")
        
        return jsonify({
            'success': True,
            'tasks': tasks,
            'total': len(tasks),
            'stats': data.get('stats', {})
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
        
        # 直接标记为已完成
        completed_manager = CompletedAssignment(mongo.db)
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
    """获取增强作业列表"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        logger.info(f"用户 {user_id} 请求获取增强作业列表")
        
        # 获取已完成的作业ID列表
        completed_manager = CompletedAssignment(mongo.db)
        completed_ids = completed_manager.get_user_completed(user_id)
        completed_set = set(str(aid) for aid in completed_ids)
        
        # 通过新版scraper获取数据
        scraper = get_scraper_instance()
        if not scraper:
            return jsonify({'success': False, 'error': 'scraper初始化失败'}), 500
        
        result = scraper.get_pending_tasks(user_id)
        
        if not result.get('success'):
            return jsonify({'success': False, 'error': result.get('error', '获取数据失败')}), 500
        
        data = result.get('data', {})
        tasks_list = data.get('tasks', [])
        
        # 处理增强数据
        enhanced_assignments = []
        
        # 处理统一的任务列表
        for task_data in tasks_list:
            subject = task_data.get('subject', '未知科目')
            title = task_data.get('title', '无标题')
            deadline = task_data.get('deadline', '')
            details = task_data.get('details', '')
            
            # 判断任务类型
            task_type = 'homework' if details.strip() else 'test'
            
            # 生成任务ID
            task_id = f"{task_type}_{abs(hash(subject + title + deadline))}"
            
            enhanced_assignment = {
                'id': task_id,
                'subject': subject,
                'type': task_type,
                'title': title,
                'deadline': deadline,
                'url': task_data.get('url', ''),
                'can_submit': True,
                'is_group': False,
                'details_content': details,  # 作业详情内容
                'completed': task_id in completed_set,
                'has_detailed_tasks': bool(details.strip()),
                'tasks_count': 1
            }
            enhanced_assignments.append(enhanced_assignment)
        
        logger.info(f"返回 {len(enhanced_assignments)} 个增强作业/测试项目")
        
        return jsonify({
            'success': True,
            'assignments': enhanced_assignments,
            'total': len(enhanced_assignments),
            'statistics': data.get('stats', {}),
            'query_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
        completed_manager = CompletedAssignment(mongo.db)
        completed_ids = completed_manager.get_user_completed(user_id)
        
        return jsonify({
            'success': True,
            'completed_assignments': [str(aid) for aid in completed_ids]
        })
        
    except Exception as e:
        logger.error(f"获取已完成作业列表失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取已完成作业列表失败'}), 500

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
        
        # 通过新版scraper获取实时数据
        scraper = get_scraper_instance()
        if not scraper:
            return jsonify({'success': False, 'error': 'scraper初始化失败'}), 500
        
        result = scraper.get_pending_tasks(user_id)
        
        if not result.get('success'):
            return jsonify({'success': False, 'error': result.get('error', '获取数据失败')}), 500
        
        data = result.get('data', {})
        tasks_list = data.get('tasks', [])
        
        # 统计各种状态
        now = datetime.now()
        total = len(tasks_list)
        completed = 0
        urgent = 0
        soon = 0
        
        # 统计所有任务
        for task_data in tasks_list:
            subject = task_data.get('subject', '未知科目')
            title = task_data.get('title', '无标题')
            deadline = task_data.get('deadline', '')
            details = task_data.get('details', '')
            
            # 判断任务类型
            task_type = 'homework' if details.strip() else 'test'
            
            # 生成任务ID
            task_id = f"{task_type}_{abs(hash(subject + title + deadline))}"
            
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
            }
        })
        
    except Exception as e:
        logger.error(f"获取作业统计失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取统计信息失败'}), 500