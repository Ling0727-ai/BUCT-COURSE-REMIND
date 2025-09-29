"""
课程数据管理模块
处理从爬虫获取的课程数据的存储和检索
"""

from flask import Blueprint, request, jsonify, session
from bson import ObjectId
from datetime import datetime, timedelta
import logging
from .auth import login_required
from .model import get_beijing_time

# 创建蓝图
course_data_bp = Blueprint('course_data', __name__, url_prefix='/api/course-data')

# 配置日志
logger = logging.getLogger(__name__)

class CourseData:
    """课程数据模型类"""
    
    def __init__(self, mongo_db):
        self.db = mongo_db
        self.collection = 'course_data'
        # 创建索引以提高查询性能
        self.db[self.collection].create_index([("user_id", 1), ("updated_at", -1)])
        self.db[self.collection].create_index([("user_id", 1), ("task_id", 1)], unique=True)
    
    def save_user_course_data(self, user_id, tasks_data):
        """
        智能保存用户的课程数据（保护软删除状态）
        
        Args:
            user_id: 用户ID
            tasks_data: 任务数据列表，格式：
            [
                {
                    'subject': '科目名称',
                    'title': '任务标题',
                    'deadline': '截止时间',
                    'details': '详情内容',
                    'url': '链接',
                    'type': 'homework' 或 'test'
                }
            ]
        """
        try:
            # 获取用户当前的软删除状态
            from .assignment_status import get_assignment_status_manager
            status_manager = get_assignment_status_manager()
            deleted_ids = set(status_manager.get_deleted_assignment_ids(user_id))
            
            logger.info(f"用户 {user_id} 当前有 {len(deleted_ids)} 个软删除项目")
            
            # 生成新数据的task_id集合
            current_time = get_beijing_time()
            new_task_ids = set()
            documents = []
            
            for task in tasks_data:
                # 生成任务唯一ID，优先使用传入的type字段
                task_type = task.get('type', 'homework')
                if task_type not in ['homework', 'test', 'todo']:
                    # 如果没有明确的type或type不在预期范围内，使用原来的逻辑
                    task_type = 'homework' if task.get('details', '').strip() else 'test'
                
                if task_type not in ['homework', 'test', 'todo']:
                    # 如果没有明确的type或type不在预期范围内，使用原来的逻辑
                    task_type = 'homework' if task.get('details', '').strip() else 'test'
                
                task_id = f"{task_type}_{abs(hash(task.get('subject', '') + task.get('title', '') + task.get('deadline', '')))}"
                new_task_ids.add(task_id)
                
                doc = {
                    'user_id': ObjectId(user_id),
                    'task_id': task_id,
                    'subject': task.get('subject', ''),
                    'title': task.get('title', ''),
                    'deadline': task.get('deadline', ''),
                    'details': task.get('details', ''),
                    'url': task.get('url', ''),
                    'type': task_type,
                    'created_at': current_time,
                    'updated_at': current_time
                }
                documents.append(doc)
            
            # 检查软删除项目的处理策略
            deleted_to_remove = deleted_ids - new_task_ids  # 不再存在的软删除项目
            deleted_to_keep = deleted_ids & new_task_ids    # 仍然存在的软删除项目
            
            logger.info(f"软删除项目分析: 保留 {len(deleted_to_keep)} 个, 永久删除 {len(deleted_to_remove)} 个")
            
            # 删除该用户的所有旧数据
            delete_result = self.db[self.collection].delete_many({'user_id': ObjectId(user_id)})
            logger.info(f"删除用户 {user_id} 的旧课程数据 {delete_result.deleted_count} 条")
            
            # 插入新数据，包括软删除的项目（软删除项目会在get_user_course_data中被过滤）
            inserted_count = 0
            if documents:
                insert_result = self.db[self.collection].insert_many(documents)
                inserted_count = len(insert_result.inserted_ids)
                logger.info(f"为用户 {user_id} 插入新课程数据 {inserted_count} 条")
                
                # 记录软删除项目的保护情况
                if deleted_to_keep:
                    logger.info(f"保护了 {len(deleted_to_keep)} 个软删除项目（数据已插入但会在显示时过滤）")
            
            # 处理软删除状态
            if deleted_to_remove:
                # 永久删除不再存在的软删除项目
                removed_count = status_manager.clear_user_status_by_ids(user_id, list(deleted_to_remove))
                logger.info(f"永久删除 {removed_count} 个不再存在的软删除项目")
            
            if deleted_to_keep:
                logger.info(f"保留 {len(deleted_to_keep)} 个仍存在的软删除项目状态")
            
            return inserted_count
            
        except Exception as e:
            logger.error(f"保存用户 {user_id} 课程数据失败: {e}")
            raise e
    
    def get_user_course_data(self, user_id):
        """
        获取用户的课程数据（过滤软删除）
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 课程数据列表（已过滤软删除）
        """
        try:
            cursor = self.db[self.collection].find(
                {'user_id': ObjectId(user_id)}
            ).sort('updated_at', -1)
            
            # 获取软删除的任务ID列表
            from .assignment_status import get_assignment_status_manager
            status_manager = get_assignment_status_manager()
            deleted_ids = set(status_manager.get_deleted_assignment_ids(user_id))
            
            tasks = []
            for doc in cursor:
                task_id = doc.get('task_id')
                
                # 跳过软删除的任务
                if task_id in deleted_ids:
                    continue
                
                task = {
                    'task_id': task_id,
                    'subject': doc.get('subject'),
                    'title': doc.get('title'),
                    'deadline': doc.get('deadline'),
                    'details': doc.get('details'),
                    'url': doc.get('url'),
                    'type': doc.get('type'),
                    'updated_at': doc.get('updated_at')
                }
                tasks.append(task)
            
            logger.info(f"为用户 {user_id} 返回 {len(tasks)} 条课程数据（已过滤软删除）")
            return tasks
            
        except Exception as e:
            logger.error(f"获取用户 {user_id} 课程数据失败: {e}")
            raise e
    
    def get_last_update_time(self, user_id):
        """
        获取用户数据的最后更新时间
        
        Args:
            user_id: 用户ID
            
        Returns:
            datetime: 最后更新时间，如果没有数据则返回None
        """
        try:
            doc = self.db[self.collection].find_one(
                {'user_id': ObjectId(user_id)},
                sort=[('updated_at', -1)]
            )
            
            if doc:
                return doc.get('updated_at')
            return None
            
        except Exception as e:
            logger.error(f"获取用户 {user_id} 最后更新时间失败: {e}")
            return None
    
    def clear_user_data(self, user_id):
        """
        清空用户的课程数据
        
        Args:
            user_id: 用户ID
        """
        try:
            result = self.db[self.collection].delete_many({'user_id': ObjectId(user_id)})
            logger.info(f"清空用户 {user_id} 的课程数据 {result.deleted_count} 条")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"清空用户 {user_id} 课程数据失败: {e}")
            raise e

# 全局实例
course_data_manager = None

def get_course_data_manager():
    """获取课程数据管理器实例"""
    global course_data_manager
    if course_data_manager is None:
        from . import mongo
        if mongo.db is not None:
            course_data_manager = CourseData(mongo.db)
        else:
            # 如果在应用上下文外调用，返回None或抛出异常
            raise RuntimeError("需要在Flask应用上下文中调用此函数")
    return course_data_manager

@course_data_bp.route('/refresh', methods=['POST'])
@login_required
def refresh_course_data():
    """手动刷新用户的课程数据"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        logger.info(f"用户 {user_id} 请求手动刷新课程数据")
        
        # 获取scraper实例
        from .scraper import get_scraper
        scraper = get_scraper()
        
        # 获取最新数据
        result = scraper.get_pending_tasks(user_id)
        
        if not result.get('success'):
            return jsonify({'success': False, 'error': result.get('error', '获取数据失败')}), 500
        
        data = result.get('data', {})
        tasks_list = data.get('tasks', [])
        
        # 保存到数据库
        course_data_mgr = get_course_data_manager()
        saved_count = course_data_mgr.save_user_course_data(user_id, tasks_list)
        
        logger.info(f"用户 {user_id} 手动刷新完成，保存了 {saved_count} 条数据")
        
        return jsonify({
            'success': True,
            'message': f'数据刷新成功，共更新 {saved_count} 条记录',
            'count': saved_count,
            'stats': data.get('stats', {}),
            'updated_at': get_beijing_time().isoformat()
        })
        
    except Exception as e:
        logger.error(f"手动刷新课程数据失败: {str(e)}")
        return jsonify({'success': False, 'error': '刷新数据失败'}), 500

@course_data_bp.route('/list', methods=['GET'])
@login_required
def get_course_data_list():
    """从数据库获取用户的课程数据"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        # 从数据库获取数据
        course_data_mgr = get_course_data_manager()
        tasks = course_data_mgr.get_user_course_data(user_id)
        last_update = course_data_mgr.get_last_update_time(user_id)
        
        # 获取作业状态信息
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        completed_ids = status_manager.get_completed_assignment_ids(user_id)
        deleted_ids = status_manager.get_deleted_assignment_ids(user_id)
        completed_set = set(str(aid) for aid in completed_ids)
        deleted_set = set(str(aid) for aid in deleted_ids)
        
        # 转换数据格式以兼容前端（过滤掉已删除的任务）
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
        
        logger.info(f"从数据库为用户 {user_id} 返回 {len(formatted_tasks)} 条课程数据")
        
        return jsonify({
            'success': True,
            'tasks': formatted_tasks,
            'total': len(formatted_tasks),
            'stats': stats,
            'last_update': last_update.isoformat() if last_update else None,
            'source': 'database'
        })
        
    except Exception as e:
        logger.error(f"获取课程数据列表失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取数据失败'}), 500

@course_data_bp.route('/status', methods=['GET'])
@login_required
def get_data_status():
    """获取数据状态信息"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401
        
        course_data_mgr = get_course_data_manager()
        last_update = course_data_mgr.get_last_update_time(user_id)
        
        # 计算距离下次自动刷新的时间
        next_auto_refresh = None
        hours_until_refresh = None
        
        if last_update:
            next_auto_refresh = last_update + timedelta(hours=12)
            time_diff = next_auto_refresh - get_beijing_time()
            hours_until_refresh = max(0, time_diff.total_seconds() / 3600)
        
        return jsonify({
            'success': True,
            'last_update': last_update.isoformat() if last_update else None,
            'next_auto_refresh': next_auto_refresh.isoformat() if next_auto_refresh else None,
            'hours_until_refresh': round(hours_until_refresh, 1) if hours_until_refresh is not None else None,
            'has_data': last_update is not None
        })
        
    except Exception as e:
        logger.error(f"获取数据状态失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取状态失败'}), 500