"""
定时任务调度器
负责定时刷新用户的课程数据，并处理定时提醒
"""

import logging
import threading
import time

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
                    'student_id': {'$exists': True, '$nin': [None, '']},
                    's_password': {'$exists': True, '$nin': [None, '']}
                },
                {'_id': 1}
            )

            users_need_refresh = []
            current_time = get_beijing_time()
            course_data_mgr = get_course_data_manager()

            try:
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
            finally:
                # 确保cursor被关闭释放资源
                users_cursor.close()

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
            from flask import current_app

            # 获取Flask应用实例
            try:
                app = current_app._get_current_object()
                with app.app_context():
                    self._process_due_reminders_impl()
            except RuntimeError:
                # 如果当前没有应用上下文，创建一个新的
                from . import create_app
                app = create_app()
                with app.app_context():
                    self._process_due_reminders_impl()

        except Exception as e:
            logger.error(f"❌ 查询或发送定时提醒失败: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def _process_due_reminders_impl(self):
        """处理到期的定时提醒（实际实现）"""
        due_cursor = None
        try:
            from . import mongo
            from .notification_services import send_webhook_notification
            now = get_beijing_time()

            # 查询到期未发送的提醒
            due_cursor = mongo.db[REMINDERS_COLLECTION].find({
                'status': 'scheduled',
                'scheduled_time': {'$lte': now}
            }).limit(50)

            due_reminders = list(due_cursor)

            if len(due_reminders) > 0:
                logger.info(f"📬 发现 {len(due_reminders)} 个到期的提醒需要发送")
            else:
                logger.debug("📭 没有到期的提醒需要发送")
                return

            sent_count = 0
            failed_count = 0
            cancelled_count = 0
            skipped_count = 0

            for reminder in due_reminders:
                try:
                    # 使用原子操作抢占提醒，防止并发重复发送
                    # 只有状态仍为 'scheduled' 时才更新为 'processing'
                    claim_result = mongo.db[REMINDERS_COLLECTION].update_one(
                        {'_id': reminder['_id'], 'status': 'scheduled'},
                        {'$set': {'status': 'processing', 'updated_at': now}}
                    )

                    # 如果没有成功抢占（已被其他线程处理），跳过
                    if claim_result.matched_count == 0:
                        logger.debug(f"⏭️ 提醒 {reminder['_id']} 已被其他进程处理，跳过")
                        skipped_count += 1
                        continue

                    email = reminder.get('email')
                    message = reminder.get('message', '')
                    reminder_type = reminder.get('type', '')
                    target_id = reminder.get('target_id', '')
                    user_id = reminder.get('user_id')
                    is_auto = reminder.get('auto_created', False)

                    logger.debug(f"📤 处理提醒: 类型={reminder_type}, 目标={target_id}, 邮箱={email}, 自动={is_auto}")

                    if not email or not message:
                        # 不完整，标记失败
                        logger.warning(f"⚠️ 提醒信息不完整: email={bool(email)}, message={bool(message)}")
                        mongo.db[REMINDERS_COLLECTION].update_one(
                            {'_id': reminder['_id']},
                            {'$set': {'status': 'failed', 'updated_at': now, 'error': 'missing email or message'}}
                        )
                        failed_count += 1
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
                        logger.info(f"🚫 提醒已取消（{skip_reason}）: {target_id}")
                        cancelled_count += 1
                        continue

                    # 发送提醒
                    logger.debug(f"📧 开始发送邮件到 {email}...")
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

                    if sent:
                        sent_count += 1
                        logger.info(f"✅ 提醒邮件已发送到 {email} (类型: {reminder_type})")
                    else:
                        failed_count += 1
                        logger.error(f"❌ 提醒邮件发送失败到 {email} (类型: {reminder_type})")

                except Exception as e:
                    failed_count += 1
                    logger.error(f"❌ 处理单条提醒失败: {type(e).__name__}: {e}")
                    mongo.db[REMINDERS_COLLECTION].update_one(
                        {'_id': reminder.get('_id')},
                        {'$set': {'status': 'failed', 'updated_at': now, 'error': str(e)}}
                    )

            logger.info(
                f"📊 提醒处理完成: ✅成功 {sent_count}, ❌失败 {failed_count}, 🚫取消 {cancelled_count}, ⏭️跳过 {skipped_count}")

        except Exception as e:
            logger.error(f"❌ 处理定时提醒实现时失败: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            # 确保cursor被关闭释放资源
            if due_cursor is not None:
                try:
                    due_cursor.close()
                except:
                    pass

    def _check_and_create_auto_reminders(self):
        """检查即将到期的作业，自动创建截止一天前的提醒"""
        users_cursor = None
        try:
            from datetime import datetime, timedelta
            from . import mongo
            from bson import ObjectId
            # 将导入移到循环外部，避免重复导入开销
            from .course_data import get_course_data_manager
            from .assignment_status import get_assignment_status_manager

            now = get_beijing_time()
            # 检测未来0-24小时内到期的作业（DDL前一天提醒）
            check_start = now
            check_end = now + timedelta(hours=24)

            logger.info("=" * 80)
            logger.info(f"🔔 开始检查即将到期的作业（DDL前24小时内自动提醒一次）")
            logger.info(f"📅 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(
                f"🎯 检测范围: {check_start.strftime('%Y-%m-%d %H:%M')} - {check_end.strftime('%Y-%m-%d %H:%M')}")
            logger.info("=" * 80)

            # 获取所有用户，使用cursor而不是一次性加载到内存
            users_cursor = mongo.db.users.find({}, {'_id': 1, 'email': 1, 'username': 1})

            reminder_count = 0
            users_checked = 0
            users_with_email = 0
            users_with_tasks = 0
            tasks_checked = 0
            tasks_in_range = 0
            tasks_completed = 0
            tasks_deleted = 0
            tasks_already_reminded = 0

            # 在循环外获取管理器实例，避免重复创建
            course_data_mgr = get_course_data_manager()
            status_manager = get_assignment_status_manager()

            # 直接在cursor上迭代，避免一次性加载所有用户到内存
            for user in users_cursor:
                try:
                    users_checked += 1
                    user_id = user['_id']
                    user_email = user.get('email')
                    username = user.get('username', 'Unknown')

                    if not user_email:
                        logger.debug(f"⏭️ 用户 {username} ({user_id}) 没有邮箱，跳过")
                        continue

                    users_with_email += 1
                    logger.debug(f"✅ 检查用户: {username} ({user_email})")

                    # 获取该用户的课程数据
                    tasks = course_data_mgr.get_user_course_data(str(user_id))

                    if not tasks:
                        logger.debug(f"  📭 用户 {username} 没有作业数据")
                        continue

                    users_with_tasks += 1
                    logger.debug(f"  📚 用户 {username} 有 {len(tasks)} 个作业/测试")
                    tasks_checked += len(tasks)

                    # 获取已完成和已删除的作业ID
                    completed_ids = set(str(aid) for aid in status_manager.get_completed_assignment_ids(str(user_id)))
                    deleted_ids = set(str(aid) for aid in status_manager.get_deleted_assignment_ids(str(user_id)))

                    logger.debug(f"  ✓ 已完成: {len(completed_ids)}, 🗑️ 已删除: {len(deleted_ids)}")

                    # 记录前3个作业的deadline用于调试
                    for idx, t in enumerate(tasks[:3]):
                        logger.debug(f"  样本{idx + 1}: deadline='{t.get('deadline', 'N/A')}'")

                    for task in tasks:
                        task_id = task.get('task_id')
                        deadline_str = task.get('deadline', '')

                        # 跳过已完成或已删除的作业
                        if task_id in completed_ids:
                            tasks_completed += 1
                            continue
                        if task_id in deleted_ids:
                            tasks_deleted += 1
                            continue

                        if not deadline_str:
                            logger.debug(f"  ⏭️ {task.get('title', 'Unknown')[:30]}: 没有截止时间")
                            continue

                        # 解析截止时间
                        try:
                            if 'T' in deadline_str:
                                if 'Z' in deadline_str or '+' in deadline_str:
                                    deadline_dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                                    # 转换为北京时间（naive）
                                    deadline_dt = deadline_dt.replace(tzinfo=None) + timedelta(hours=8)
                                    logger.debug(f"  🔄 ISO+TZ: {deadline_str} → {deadline_dt}")
                                else:
                                    deadline_dt = datetime.fromisoformat(deadline_str)
                                    logger.debug(f"  🔄 ISO: {deadline_str} → {deadline_dt}")
                            elif '年' in deadline_str:
                                # 中文格式：2025年11月15日 23:59:00
                                deadline_dt = datetime.strptime(deadline_str, '%Y年%m月%d日 %H:%M:%S')
                                logger.debug(f"  🔄 Chinese: {deadline_str} → {deadline_dt}")
                            else:
                                # 尝试标准格式：YYYY-MM-DD HH:MM:SS
                                try:
                                    deadline_dt = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
                                    logger.debug(f"  🔄 Standard: {deadline_str} → {deadline_dt}")
                                except ValueError:
                                    # 尝试不带秒的格式：YYYY-MM-DD HH:MM
                                    try:
                                        deadline_dt = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M')
                                        logger.debug(f"  🔄 Standard-NoSec: {deadline_str} → {deadline_dt}")
                                    except ValueError:
                                        logger.debug(f"  ⚠️ 无法识别格式: {deadline_str}")
                                        continue
                        except Exception as e:
                            logger.debug(f"  ⚠️ 无法解析截止时间: {deadline_str}, 错误: {e}")
                            continue

                        # 检查是否在检测范围内（未来24小时内，DDL前一天提醒）
                        if check_start <= deadline_dt <= check_end:
                            tasks_in_range += 1
                            subject = task.get('subject', '未知科目')
                            title = task.get('title', '未知作业')

                            logger.debug(
                                f"  🎯 发现即将到期作业: {subject} - {title} (截止: {deadline_dt.strftime('%Y-%m-%d %H:%M')})")

                            # 检查是否已经为这个作业创建过自动提醒
                            # 查询条件：同一用户、同一作业、自动创建、状态为scheduled或sent
                            # 这确保同一作业只提醒一次（即使多次检查也不会重复）
                            existing_reminder = mongo.db[REMINDERS_COLLECTION].find_one({
                                'user_id': user_id,
                                'target_id': task_id,
                                'type': 'assignment',
                                'auto_created': True,
                                'status': {'$in': ['scheduled', 'sent']}  # 已计划或已发送的都跳过
                            })

                            if existing_reminder:
                                tasks_already_reminded += 1
                                logger.debug(f"  ⏭️ 已经创建过提醒，跳过: {title}")
                                continue

                            # 创建自动提醒（设置为立即发送）
                            task_type = task.get('type', 'homework')
                            assignment_type = '作业' if task_type == 'homework' else '测试'

                            deadline_display = deadline_dt.strftime('%Y年%m月%d日 %H:%M:%S')

                            # 计算剩余时间
                            time_left = deadline_dt - now
                            hours_left = int(time_left.total_seconds() / 3600)
                            if hours_left < 1:
                                time_left_str = "不到1小时"
                            elif hours_left < 24:
                                time_left_str = f"约{hours_left}小时"
                            else:
                                days_left = hours_left // 24
                                hours_remain = hours_left % 24
                                if hours_remain > 0:
                                    time_left_str = f"约{days_left}天{hours_remain}小时"
                                else:
                                    time_left_str = f"约{days_left}天"

                            message = f"""⏰ 自动提醒：{assignment_type}即将截止

科目: {subject}
标题: {title}
截止时间: {deadline_display}
剩余时间: {time_left_str}

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
                            logger.info(
                                f"  ✅ 为用户 {username} 创建自动提醒: {subject} - {title} (截止: {deadline_display})")

                except Exception as e:
                    logger.error(f"❌ 处理用户 {user.get('_id')} 的自动提醒时失败: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())

            logger.info("=" * 80)
            logger.info(f"📊 自动提醒检查完成统计:")
            logger.info(f"  👥 检查用户: {users_checked} 个")
            logger.info(f"  📧 有邮箱: {users_with_email} 个")
            logger.info(f"  📚 有作业: {users_with_tasks} 个")
            logger.info(f"  📝 总作业数: {tasks_checked} 个")
            logger.info(f"  🎯 在时间范围内: {tasks_in_range} 个")
            logger.info(f"  ✓ 已完成（跳过）: {tasks_completed} 个")
            logger.info(f"  🗑️ 已删除（跳过）: {tasks_deleted} 个")
            logger.info(f"  🔔 已提醒过（跳过）: {tasks_already_reminded} 个")
            logger.info(f"  🆕 新创建提醒: {reminder_count} 个")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"❌ 检查自动提醒时发生异常: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            # 确保cursor被关闭释放资源
            if users_cursor is not None:
                try:
                    users_cursor.close()
                except:
                    pass


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
