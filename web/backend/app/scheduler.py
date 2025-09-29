"""
定时任务调度器
负责定时刷新用户的课程数据
"""

import threading
import time
import logging
from datetime import datetime, timedelta
from .model import get_beijing_time

logger = logging.getLogger(__name__)

class CourseDataScheduler:
    """课程数据定时刷新调度器"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.refresh_interval = 12 * 60 * 60  # 12小时，单位：秒
        
    def start(self):
        """启动调度器"""
        if self.running:
            logger.warning("调度器已经在运行中")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("课程数据定时刷新调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("课程数据定时刷新调度器已停止")
    
    def _run_scheduler(self):
        """调度器主循环"""
        while self.running:
            try:
                # 检查需要刷新的用户
                users_to_refresh = self._get_users_need_refresh()
                
                if users_to_refresh:
                    logger.info(f"发现 {len(users_to_refresh)} 个用户需要刷新数据")
                    
                    for user_id in users_to_refresh:
                        if not self.running:
                            break
                        
                        try:
                            self._refresh_user_data(user_id)
                            # 每个用户之间间隔一点时间，避免过载
                            time.sleep(2)
                        except Exception as e:
                            logger.error(f"刷新用户 {user_id} 数据失败: {e}")
                
                # 每小时检查一次
                for _ in range(3600):  # 3600秒 = 1小时
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"调度器运行异常: {e}")
                time.sleep(60)  # 出错后等待1分钟再继续
    
    def _get_users_need_refresh(self):
        """获取需要刷新数据的用户列表"""
        try:
            # 延迟导入避免循环导入
            from . import mongo
            from .course_data import get_course_data_manager
            
            # 获取所有有学号和密码的用户
            users_cursor = mongo.db.users.find(
                {
                    'student_id': {'$exists': True, '$ne': None, '$ne': ''},
                    's_password': {'$exists': True, '$ne': None, '$ne': ''}
                },
                {'_id': 1}
            )
            
            users_need_refresh = []
            current_time = get_beijing_time()
            course_data_mgr = get_course_data_manager()
            
            for user in users_cursor:
                user_id = str(user['_id'])
                
                # 检查最后更新时间
                last_update = course_data_mgr.get_last_update_time(user_id)
                
                if last_update is None:
                    # 从未更新过，需要刷新
                    users_need_refresh.append(user_id)
                else:
                    # 检查是否超过12小时
                    time_diff = current_time - last_update
                    if time_diff.total_seconds() >= self.refresh_interval:
                        users_need_refresh.append(user_id)
            
            return users_need_refresh
            
        except Exception as e:
            logger.error(f"获取需要刷新的用户列表失败: {e}")
            return []
    
    def _refresh_user_data(self, user_id):
        """刷新指定用户的数据"""
        try:
            logger.info(f"开始自动刷新用户 {user_id} 的课程数据")
            
            # 获取scraper实例
            from .scraper import get_scraper
            scraper = get_scraper()
            
            # 获取最新数据
            result = scraper.get_pending_tasks(user_id)
            
            if not result.get('success'):
                logger.error(f"获取用户 {user_id} 数据失败: {result.get('error')}")
                return False
            
            data = result.get('data', {})
            tasks_list = data.get('tasks', [])
            
            # 保存到数据库
            from .course_data import get_course_data_manager
            course_data_mgr = get_course_data_manager()
            saved_count = course_data_mgr.save_user_course_data(user_id, tasks_list)
            
            logger.info(f"用户 {user_id} 自动刷新完成，保存了 {saved_count} 条数据")
            return True
            
        except Exception as e:
            logger.error(f"自动刷新用户 {user_id} 数据失败: {e}")
            return False

# 全局调度器实例
_scheduler_instance = None
_scheduler_lock = threading.Lock()

def get_scheduler():
    """获取调度器单例"""
    global _scheduler_instance
    with _scheduler_lock:
        if _scheduler_instance is None:
            _scheduler_instance = CourseDataScheduler()
        return _scheduler_instance

def init_scheduler():
    """初始化并启动调度器"""
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler

def stop_scheduler():
    """停止调度器"""
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.stop()