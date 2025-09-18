#!/usr/bin/env python3
from app import create_app
import threading
import time
import schedule
from datetime import datetime
from werkzeug.security import generate_password_hash
from app.assignments import scrape_assignments_job

app = create_app()

def init_db():
    """Initializes the database and creates a default admin user."""
    with app.app_context():
        from app import mongo
        admin_username = app.config.get('ADMIN_USERNAME', 'admin')
        admin_password = app.config.get('ADMIN_PASSWORD', 'admin123')
        
        if not mongo.db.users.find_one({'username': admin_username}):
            admin_data = {
                'username': admin_username,
                'password_hash': generate_password_hash(admin_password),
                'is_admin': True,
                'created_at': datetime.utcnow()
            }
            mongo.db.users.insert_one(admin_data)
            app.logger.info(f"Default admin user created ({admin_username})")

def setup_scheduler(interval_minutes=60):
    """Sets up the job scheduler."""
    def job_with_context():
        with app.app_context():
            scrape_assignments_job()

    schedule.clear()
    schedule.every(interval_minutes).minutes.do(job_with_context)
    app.logger.info(f"Scheduler set up with {interval_minutes} minute interval.")

def run_scheduler():
    """Runs the scheduler in a loop."""
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    init_db()
    
    with app.app_context():
        from app import mongo
        try:
            interval_setting = mongo.db.settings.find_one({'key': 'scrape_interval'})
            interval = int(interval_setting['value']) if interval_setting and interval_setting.get('value') else 60
        except:
            interval = 60
        setup_scheduler(interval)
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=int(app.config.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )