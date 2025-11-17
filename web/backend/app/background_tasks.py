"""
后台任务处理模块
处理登录后的数据刷新等异步任务
"""

import logging
import threading

from bson import ObjectId
from flask import current_app

logger = logging.getLogger(__name__)

def refresh_user_data_async(user_id, app_context):
    """
    异步刷新用户数据的后台任务
    
    Args:
        user_id: 用户ID
        app_context: Flask应用上下文
    """
    with app_context:
        try:
            logger.info(f"开始异步刷新用户 {user_id} 的作业数据")
            
            # 导入必要的模块
            from . import mongo
            from .scraper import get_scraper
            from .course_data import get_course_data_manager
            
            # 检查用户是否有学号和密码
            user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if not user:
                logger.warning(f"用户 {user_id} 不存在，跳过数据刷新")
                return
            
            student_id = user.get('student_id')
            s_password = user.get('s_password')
            
            if not student_id or not s_password:
                logger.info(f"用户 {user_id} 未设置学号或密码，跳过数据刷新")
                return
            
            # 获取scraper实例并刷新数据
            scraper = get_scraper()
            if not scraper:
                logger.error(f"无法获取scraper实例，用户 {user_id} 数据刷新失败")
                return

            result = scraper.get_pending_tasks(user_id)
            
            if not result.get('success'):
                error_msg = result.get('error', '获取数据失败')
                logger.warning(f"用户 {user_id} 异步刷新失败: {error_msg}")
                return
            
            data = result.get('data', {})
            tasks_list = data.get('tasks', [])
            
            # 保存到数据库
            course_data_mgr = get_course_data_manager()
            saved_count = course_data_mgr.save_user_course_data(user_id, tasks_list)
            
            stats = data.get('stats', {})
            logger.info(f"用户 {user_id} 异步刷新完成，保存了 {saved_count} 条数据，统计: {stats}")
            
        except Exception as e:
            logger.error(f"用户 {user_id} 异步刷新数据失败: {str(e)}", exc_info=True)

def start_background_refresh(user_id):
    """
    启动后台数据刷新任务
    
    Args:
        user_id: 用户ID
        
    Returns:
        bool: 是否成功启动任务
    """
    try:
        from flask import current_app
        
        # 获取当前应用上下文
        try:
            app_context = current_app._get_current_object().app_context()
        except Exception as ctx_error:
            logger.error(f"获取应用上下文失败: {str(ctx_error)}")
            return False

        # 创建后台线程
        thread = threading.Thread(
            target=refresh_user_data_async,
            args=(user_id, app_context),
            daemon=True,
            name=f"refresh_data_{user_id}"
        )
        
        thread.start()
        logger.info(f"已启动用户 {user_id} 的后台数据刷新任务，线程名: {thread.name}")
        return True
        
    except Exception as e:
        logger.error(f"启动后台刷新任务失败: {str(e)}", exc_info=True)
        return False