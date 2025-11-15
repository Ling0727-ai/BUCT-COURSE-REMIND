"""
定时任务调度器
负责定时刷新用户的课程数据，并处理定时提醒
"""

import logging
import threading
import time

from bson import ObjectId

from .model import get_beijing_time

logger = logging.getLogger(__name__)

# 新增：定时提醒集合名
REMINDERS_COLLECTION = 'scheduled_reminders'

class CourseDataScheduler:
    """课程数据定时刷新调度器"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.refresh_interval = 12 * 60 * 60  # 12小时，单位：秒
        # 处理提醒的检查间隔（秒）
        self.reminder_check_interval = 5
        self._last_reminder_check = 0
        # 自动提醒检查间隔（秒）- 每小时检查一次
        self.auto_reminder_check_interval = 3600  # 1小时
        self._last_auto_reminder_check = 0

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

                # 每秒循环一次，并周期性处理到期提醒和自动提醒
                for i in range(3600):  # 3600秒 = 1小时
                    if not self.running:
                        break

                    # 每 self.reminder_check_interval 秒检查一次到期提醒
                    try:
                        if i % self.reminder_check_interval == 0:
                            self._process_due_reminders()
                    except Exception as e:
                        logger.error(f"处理到期提醒时异常: {e}")

                    # 每小时检查一次需要自动提醒的作业
                    try:
                        if i % self.auto_reminder_check_interval == 0:
                            self._check_and_create_auto_reminders()
                    except Exception as e:
                        logger.error(f"检查自动提醒时异常: {e}")

                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"调度器运行异常: {e}")
                time.sleep(60)  # 出错后等候1分钟再继续

    def _get_users_need_refresh(self):
        """
        获取需要刷新数据的用户列表
        """
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
        """
        刷新指定用户的数据
        """
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

    def _process_due_reminders(self):
        """处理到期的定时提醒（发送邮件等）"""
        try:
            from . import mongo
            from .notification_services import send_webhook_notification
            now = get_beijing_time()

            # 查询到期未发送的提醒
            due_cursor = mongo.db[REMINDERS_COLLECTION].find({
                'status': 'scheduled',
                'scheduled_time': {'$lte': now}
            }).limit(50)

            for reminder in due_cursor:
                try:
                    email = reminder.get('email')
                    message = reminder.get('message', '')
                    reminder_type = reminder.get('type', '')
                    target_id = reminder.get('target_id', '')
                    user_id = reminder.get('user_id')

                    if not email or not message:
                        # 不完整，标记失败
                        mongo.db[REMINDERS_COLLECTION].update_one(
                            {'_id': reminder['_id']},
                            {'$set': {'status': 'failed', 'updated_at': now, 'error': 'missing email or message'}}
                        )
                        continue

                    # 在发送前检查作业/待办是否已完成或已删除
                    should_skip = False
                    skip_reason = ''

                    if reminder_type == 'assignment' and target_id and user_id:
                        from .assignment_status import get_assignment_status_manager
                        status_manager = get_assignment_status_manager()

                        # 检查是否已完成
                        completed_ids = set(
                            str(aid) for aid in status_manager.get_completed_assignment_ids(str(user_id)))
                        if target_id in completed_ids:
                            should_skip = True
                            skip_reason = 'assignment completed'

                        # 检查是否已删除
                        if not should_skip:
                            deleted_ids = set(
                                str(aid) for aid in status_manager.get_deleted_assignment_ids(str(user_id)))
                            if target_id in deleted_ids:
                                should_skip = True
                                skip_reason = 'assignment deleted'

                    elif reminder_type == 'todo' and target_id and user_id:
                        from .model import Todo
                        todo_model = Todo(mongo.db)
                        existing_todo = todo_model.get_todo_by_id(target_id, str(user_id))

                        if not existing_todo:
                            should_skip = True
                            skip_reason = 'todo not found'
                        elif existing_todo.get('completed'):
                            should_skip = True
                            skip_reason = 'todo completed'
                        elif existing_todo.get('deleted'):
                            should_skip = True
                            skip_reason = 'todo deleted'

                    if should_skip:
                        # 标记为已取消，不发送
                        mongo.db[REMINDERS_COLLECTION].update_one(
                            {'_id': reminder['_id']},
                            {'$set': {'status': 'cancelled', 'updated_at': now, 'cancel_reason': skip_reason}}
                        )
                        logger.info(f"定时提醒已取消（{skip_reason}）: {target_id}")
                        continue

                    # 发送提醒
                    email_config = {
                        'type': 'email',
                        'enabled': True,
                        'config': {'to_email': email}
                    }
                    sent = send_webhook_notification(email_config, message)
                    new_status = 'sent' if sent else 'failed'
                    mongo.db[REMINDERS_COLLECTION].update_one(
                        {'_id': reminder['_id']},
                        {'$set': {'status': new_status, 'updated_at': now, 'sent_at': now if sent else None}}
                    )
                    logger.info(f"定时提醒{'已发送' if sent else '发送失败'} 到 {email}")
                except Exception as e:
                    logger.error(f"处理单条提醒失败: {e}")
                    mongo.db[REMINDERS_COLLECTION].update_one(
                        {'_id': reminder.get('_id')},
                        {'$set': {'status': 'failed', 'updated_at': now, 'error': str(e)}}
                    )
        except Exception as e:
            logger.error(f"查询或发送定时提醒失败: {e}")

    def _check_and_create_auto_reminders(self):
        """检查即将到期的作业，自动创建截止一天前的提醒"""
        try:
            from datetime import datetime, timedelta
            from . import mongo
            from bson import ObjectId

            now = get_beijing_time()
            # 计算24-48小时后的时间范围（即明天这个时间）
            tomorrow_start = now + timedelta(hours=23)
            tomorrow_end = now + timedelta(hours=25)

            logger.info(
                f"开始检查即将到期的作业（{tomorrow_start.strftime('%Y-%m-%d %H:%M')} - {tomorrow_end.strftime('%Y-%m-%d %H:%M')}）")

            # 获取所有用户
            users = mongo.db.users.find({}, {'_id': 1, 'email': 1})

            reminder_count = 0
            for user in users:
                try:
                    user_id = user['_id']
                    user_email = user.get('email')

                    if not user_email:
                        continue  # 跳过没有邮箱的用户

                    # 获取该用户的课程数据
                    from .course_data import get_course_data_manager
                    course_data_mgr = get_course_data_manager()
                    tasks = course_data_mgr.get_user_course_data(str(user_id))

                    # 获取已完成和已删除的作业ID
                    from .assignment_status import get_assignment_status_manager
                    status_manager = get_assignment_status_manager()
                    completed_ids = set(str(aid) for aid in status_manager.get_completed_assignment_ids(str(user_id)))
                    deleted_ids = set(str(aid) for aid in status_manager.get_deleted_assignment_ids(str(user_id)))

                    for task in tasks:
                        task_id = task.get('task_id')
                        deadline_str = task.get('deadline', '')

                        # 跳过已完成或已删除的作业
                        if task_id in completed_ids or task_id in deleted_ids:
                            continue

                        if not deadline_str:
                            continue

                        # 解析截止时间
                        try:
                            if 'T' in deadline_str:
                                if 'Z' in deadline_str or '+' in deadline_str:
                                    deadline_dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                                    # 转换为北京时间（naive）
                                    deadline_dt = deadline_dt.replace(tzinfo=None) + timedelta(hours=8)
                                else:
                                    deadline_dt = datetime.fromisoformat(deadline_str)
                            elif '年' in deadline_str:
                                # 中文格式：2025年11月15日 23:59:00
                                deadline_dt = datetime.strptime(deadline_str, '%Y年%m月%d日 %H:%M:%S')
                            else:
                                continue
                        except Exception as e:
                            logger.debug(f"无法解析截止时间: {deadline_str}, 错误: {e}")
                            continue

                        # 检查是否在明天的范围内
                        if tomorrow_start <= deadline_dt <= tomorrow_end:
                            # 检查是否已经为这个作业创建过自动提醒
                            existing_reminder = mongo.db[REMINDERS_COLLECTION].find_one({
                                'user_id': user_id,
                                'target_id': task_id,
                                'type': 'assignment',
                                'auto_created': True,
                                'status': {'$in': ['scheduled', 'sent']}
                            })

                            if existing_reminder:
                                continue  # 已经创建过提醒，跳过

                            # 创建自动提醒（设置为立即发送）
                            subject = task.get('subject', '未知科目')
                            title = task.get('title', '未知作业')
                            task_type = task.get('type', 'homework')
                            assignment_type = '作业' if task_type == 'homework' else '测试'

                            deadline_display = deadline_dt.strftime('%Y年%m月%d日 %H:%M:%S')

                            message = f"""⏰ 自动提醒：{assignment_type}即将截止

科目: {subject}
标题: {title}
截止时间: {deadline_display}
剩余时间: 约24小时

请及时完成！"""

                            reminder_doc = {
                                'user_id': user_id,
                                'type': 'assignment',
                                'target_id': task_id,
                                'email': user_email,
                                'message': message,
                                'scheduled_time': now,  # 立即发送
                                'status': 'scheduled',
                                'auto_created': True,  # 标记为自动创建
                                'created_at': now,
                                'updated_at': now
                            }

                            mongo.db[REMINDERS_COLLECTION].insert_one(reminder_doc)
                            reminder_count += 1
                            logger.info(f"为用户 {user_id} 的作业 {title} 创建自动提醒（截止: {deadline_display}）")

                except Exception as e:
                    logger.error(f"处理用户 {user.get('_id')} 的自动提醒时失败: {e}")

            if reminder_count > 0:
                logger.info(f"自动提醒检查完成，共创建 {reminder_count} 个提醒")
            else:
                logger.debug("自动提醒检查完成，没有需要提醒的作业")

        except Exception as e:
            logger.error(f"检查自动提醒时发生异常: {e}")
            import traceback
            traceback.print_exc()

# 全局调度器实例
_scheduler_instance = None
_scheduler_lock = threading.Lock()

def get_scheduler():
    """
    获取调度器单例
    """
    global _scheduler_instance
    with _scheduler_lock:
        if _scheduler_instance is None:
            _scheduler_instance = CourseDataScheduler()
        return _scheduler_instance

def init_scheduler():
    """
    初始化并启动调度器
    """
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler

def stop_scheduler():
    """
    停止调度器
    """
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.stop()