# -*- coding: utf-8 -*-
"""
定时清理任务模块

负责执行各种定时清理任务，包括：
1. 清理过期的已完成作业记录
2. 清理过期的验证码
3. 清理旧的日志记录
"""

import threading
import time
from datetime import datetime, timedelta
from flask import current_app
from . import mongo
from .model import CompletedAssignment

class CleanupTasks:
    """定时清理任务类"""
    
    def __init__(self, app=None):
        self.app = app
        self.cleanup_thread = None
        self.running = False
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化应用"""
        self.app = app
        
        # 在应用启动时启动清理任务
        with app.app_context():
            self.start_cleanup_tasks()
    
    def start_cleanup_tasks(self):
        """启动定时清理任务"""
        if self.running:
            return
        
        self.running = True
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self.cleanup_thread.start()
        
        if current_app:
            current_app.logger.info("定时清理任务已启动")
    
    def stop_cleanup_tasks(self):
        """停止定时清理任务"""
        self.running = False
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
        
        if current_app:
            current_app.logger.info("定时清理任务已停止")
    
    def _cleanup_worker(self):
        """清理任务工作线程"""
        while self.running:
            try:
                with self.app.app_context():
                    self._run_cleanup_tasks()
            except Exception as e:
                if current_app:
                    current_app.logger.error(f"清理任务执行失败: {str(e)}")
            
            # 每30分钟执行一次清理任务
            time.sleep(1800)  # 30分钟 = 1800秒
    
    def _run_cleanup_tasks(self):
        """执行所有清理任务"""
        try:
            # 1. 清理过期的已完成作业记录
            self._cleanup_expired_completed_assignments()
            
            # 2. 清理过期的验证码
            self._cleanup_expired_verification_codes()
            
            # 3. 清理旧的日志记录（保留30天）
            self._cleanup_old_logs()
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"执行清理任务时发生错误: {str(e)}")
    
    def _cleanup_expired_completed_assignments(self):
        """清理过期的已完成作业记录"""
        try:
            completed_model = CompletedAssignment(mongo.db)
            deleted_count = completed_model.cleanup_expired()
            
            if deleted_count > 0 and current_app:
                current_app.logger.info(f"清理了 {deleted_count} 条过期的已完成作业记录")
                
        except Exception as e:
            if current_app:
                current_app.logger.error(f"清理过期已完成作业记录失败: {str(e)}")
    
    def _cleanup_expired_verification_codes(self):
        """清理过期的验证码"""
        try:
            # 删除1小时前的验证码
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            result = mongo.db.verification_codes.delete_many({
                'expires_at': {'$lt': cutoff_time}
            })
            
            if result.deleted_count > 0 and current_app:
                current_app.logger.info(f"清理了 {result.deleted_count} 条过期的验证码")
                
        except Exception as e:
            if current_app:
                current_app.logger.error(f"清理过期验证码失败: {str(e)}")
    
    def _cleanup_old_logs(self):
        """清理旧的日志记录"""
        try:
            # 删除30天前的日志
            cutoff_time = datetime.now() - timedelta(days=30)
            
            result = mongo.db.webhook_logs.delete_many({
                'created_at': {'$lt': cutoff_time}
            })
            
            if result.deleted_count > 0 and current_app:
                current_app.logger.info(f"清理了 {result.deleted_count} 条旧的日志记录")
                
        except Exception as e:
            if current_app:
                current_app.logger.error(f"清理旧日志记录失败: {str(e)}")

# 全局清理任务实例
cleanup_tasks = CleanupTasks()

def init_cleanup_tasks(app):
    """初始化清理任务"""
    cleanup_tasks.init_app(app)
    return cleanup_tasks