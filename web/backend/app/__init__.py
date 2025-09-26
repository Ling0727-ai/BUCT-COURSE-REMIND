# web/backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
import logging

# Extensions
mongo = PyMongo()
cors = CORS(
    supports_credentials=True,
    origins=['*'],  # 在生产环境中应该设置为具体的域名
    allow_headers=['Content-Type', 'Authorization'],
    methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
)

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Load config from config.py in the root directory
    app.config.from_object('config.Config')
    
    # Session配置 - 生产环境安全设置
    app.config['SESSION_COOKIE_SECURE'] = False  # 如果使用HTTPS则设为True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize extensions
    mongo.init_app(app)
    cors.init_app(app)

    with app.app_context():
        # Import and register blueprints
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
        
        # Initialize cleanup tasks
        from .cleanup_tasks import init_cleanup_tasks
        init_cleanup_tasks(app)
        app.logger.info("清理任务已初始化")
        
        # Initialize scheduler
        from .scheduler import init_scheduler
        init_scheduler()
        app.logger.info("课程数据定时刷新调度器已初始化")

    return app