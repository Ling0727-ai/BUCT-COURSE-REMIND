# web/backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_session import Session
import logging
import os

# Extensions
mongo = PyMongo()
cors = CORS(supports_credentials=True)
sess = Session()

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Load config from config.py in the root directory
    app.config.from_object('config.Config')
    
    # 确保session目录存在
    session_dir = os.path.join(app.instance_path, 'flask_session')
    os.makedirs(session_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.logger.info(f"Flask应用启动，SECRET_KEY已设置: {bool(app.config.get('SECRET_KEY'))}")
    
    # Initialize extensions
    mongo.init_app(app)
    
    # 配置CORS，允许跨域请求携带凭据
    cors.init_app(app, 
                  origins=['http://localhost:3000', 'http://localhost:3033', 'http://127.0.0.1:3000', 'http://127.0.0.1:3033'],
                  supports_credentials=True,
                  allow_headers=['Content-Type', 'Authorization'],
                  methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # 初始化Session
    sess.init_app(app)

    # Import and register blueprints (在app context外部导入避免循环导入)
    from . import auth, assignments, webhooks, settings, utils, test_routes, health
    
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(assignments.assignments_bp)
    app.register_blueprint(webhooks.webhooks_bp)
    app.register_blueprint(settings.settings_bp)
    app.register_blueprint(utils.utils_bp)
    app.register_blueprint(test_routes.test_bp)
    app.register_blueprint(health.health_bp)

    return app