# web/backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
import logging

# Extensions
mongo = PyMongo()
cors = CORS(supports_credentials=True)

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Load config from config.py in the root directory
    app.config.from_object('config.Config')
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize extensions
    mongo.init_app(app)
    cors.init_app(app)

    with app.app_context():
        # Import and register blueprints
        from . import auth, assignments, webhooks, settings, utils, test_routes, health
        
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(assignments.assignments_bp)
        app.register_blueprint(webhooks.webhooks_bp)
        app.register_blueprint(settings.settings_bp)
        app.register_blueprint(utils.utils_bp)
        app.register_blueprint(test_routes.test_bp)
        app.register_blueprint(health.health_bp)

    return app