"""
后台任务处理模块
处理登录后的数据刷新等异步任务
"""

import logging
import threading

from bson import ObjectId
from flask import current_app

logger = logging.getLogger(__name__)

# ── 并发控制 ───────────────────────────────────────────────────────────────
# 每个 user_id 同一时刻最多跑一个刷新线程，防止同一用户多次触发时线程堆积
_refresh_locks: dict[str, threading.Lock] = {}
_refresh_locks_meta = threading.Lock()


def _get_user_lock(user_id: str) -> threading.Lock:
    """获取或创建指定用户的刷新锁"""
    with _refresh_locks_meta:
        if user_id not in _refresh_locks:
            _refresh_locks[user_id] = threading.Lock()
        return _refresh_locks[user_id]
# ──────────────────────────────────────────────────────────────────────────


def refresh_user_data_async(user_id, app_context):
    """
    异步刷新用户数据的后台任务（内部实现，由 start_background_refresh 调用）
    """
    lock = _get_user_lock(user_id)
    # 非阻塞尝试获取锁，拿不到说明该用户已有刷新在跑，直接返回
    if not lock.acquire(blocking=False):
        logger.info(f"用户 {user_id} 已有刷新任务在运行，跳过本次")
        return

    try:
        with app_context:
            try:
                logger.info(f"开始异步刷新用户 {user_id} 的作业数据")

                from . import mongo
                from .scraper import get_scraper
                from .course_data import get_course_data_manager

                user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
                if not user:
                    logger.warning(f"用户 {user_id} 不存在，跳过数据刷新")
                    return

                if not user.get('student_id') or not user.get('s_password'):
                    logger.info(f"用户 {user_id} 未设置学号或密码，跳过数据刷新")
                    return

                scraper = get_scraper()
                if not scraper:
                    logger.error(f"无法获取scraper实例，用户 {user_id} 数据刷新失败")
                    return

                result = scraper.get_pending_tasks(user_id)

                if not result.get('success'):
                    logger.warning(f"用户 {user_id} 异步刷新失败: {result.get('error', '获取数据失败')}")
                    return

                data = result.get('data', {})
                tasks_list = data.get('tasks', [])

                course_data_mgr = get_course_data_manager()
                saved_count = course_data_mgr.save_user_course_data(user_id, tasks_list)

                logger.info(f"用户 {user_id} 异步刷新完成，保存了 {saved_count} 条数据")

            except Exception as e:
                logger.error(f"用户 {user_id} 异步刷新数据失败: {str(e)}", exc_info=True)
    finally:
        lock.release()


def start_background_refresh(user_id):
    """
    启动后台数据刷新任务（每个用户同时只允许一个在运行）
    """
    try:
        from flask import current_app

        try:
            app_context = current_app._get_current_object().app_context()
        except Exception as ctx_error:
            logger.error(f"获取应用上下文失败: {str(ctx_error)}")
            return False

        thread = threading.Thread(
            target=refresh_user_data_async,
            args=(user_id, app_context),
            daemon=True,
            name=f"refresh_data_{user_id}"
        )
        thread.start()
        logger.info(f"已启动用户 {user_id} 的后台数据刷新任务")
        return True

    except Exception as e:
        logger.error(f"启动后台刷新任务失败: {str(e)}", exc_info=True)
        return False
