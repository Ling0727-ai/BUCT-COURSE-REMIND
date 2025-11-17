# web/backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
import logging
import threading
import time
from datetime import datetime, timezone

# Extensions
mongo = PyMongo()

# 使用占位，稍后在 create_app 中初始化
cors = CORS()

# 动态 CORS 状态缓存
_current_cors_origins = []
_last_cors_refresh_time = None


def _load_cors_origins(app):
    """从配置或环境中加载最新的 CORS origins 列表"""
    global _current_cors_origins, _last_cors_refresh_time
    origins_raw = app.config.get('CORS_ALLOWED_ORIGINS', '')
    origins = [o.strip() for o in origins_raw.split(',') if o.strip()]
    if not origins:
        origins = ['http://localhost:8080']  # 回退默认
    _current_cors_origins = origins
    _last_cors_refresh_time = datetime.now(timezone.utc)
    app.logger.info(f"CORS 允许来源已刷新: {_current_cors_origins}")
    return origins


def _start_cors_refresh_thread(app):
    """后台线程定期刷新 CORS origins（每 N 小时，根据配置）"""
    interval_hours = app.config.get('CORS_REFRESH_INTERVAL_HOURS', 6)
    interval_seconds = max(1, int(interval_hours)) * 3600

    def _worker():
        while True:
            try:
                time.sleep(interval_seconds)
                with app.app_context():
                    _load_cors_origins(app)
            except Exception as e:
                app.logger.error(f"定时刷新 CORS origins 失败: {e}")

    t = threading.Thread(target=_worker, daemon=True, name='cors_refresh')
    t.start()
    app.logger.info(f"CORS 动态刷新线程已启动，间隔: {interval_hours} 小时")


def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Session配置
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    logging.basicConfig(level=logging.INFO)

    mongo.init_app(app)

    # 初次加载 CORS origins 并初始化 CORS
    origins = _load_cors_origins(app)
    cors.init_app(app, supports_credentials=True, origins=origins,
                  allow_headers=['Content-Type', 'Authorization'],
                  methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    # 启动后台刷新线程
    _start_cors_refresh_thread(app)

    with app.app_context():
        from . import auth, assignments, webhooks, settings, utils, test_routes, health, admin, todos, crypto_routes, course_data
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(assignments.assignments_bp)
        app.register_blueprint(webhooks.webhooks_bp)
        app.register_blueprint(settings.settings_bp)
        app.register_blueprint(utils.utils_bp)
        app.register_blueprint(test_routes.test_bp)
        app.register_blueprint(health.health_bp)
        app.register_blueprint(admin.admin_bp)
        app.register_blueprint(todos.todos_bp)
        app.register_blueprint(crypto_routes.crypto_bp)
        app.register_blueprint(course_data.course_data_bp)

        from .cleanup_tasks import init_cleanup_tasks
        init_cleanup_tasks(app)
        app.logger.info("清理任务已初始化")

        from .scheduler import init_scheduler
        init_scheduler()
        app.logger.info("课程数据定时刷新调度器已初始化")

    return app