#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, mongo
from app.model import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        try:
            # 创建索引
            logger.info("创建数据库索引...")
            
            # 用户集合索引
            mongo.db.users.create_index("username", unique=True)
            mongo.db.users.create_index("email", unique=True)
            logger.info("✓ 用户集合索引创建完成")
            
            # 设置集合索引
            mongo.db.settings.create_index("key", unique=True)
            logger.info("✓ 设置集合索引创建完成")
            
            # 验证码集合TTL索引
            mongo.db.verification_codes.create_index("expires_at", expireAfterSeconds=0)
            logger.info("✓ 验证码集合TTL索引创建完成")
            
            # 作业集合索引
            mongo.db.assignments.create_index("due_date")
            mongo.db.assignments.create_index("subject")
            logger.info("✓ 作业集合索引创建完成")
            
            # 创建默认管理员用户（如果不存在）
            user_model = User(mongo.db)
            admin_user = user_model.find_by_username('admin')
            
            if admin_user:
                logger.info("管理员用户 'admin' 已存在，跳过创建。")
            else:
                logger.info("默认管理员用户创建功能已被禁用。")
            
            # 创建默认设置
            default_settings = [
                {'key': 'scrape_interval', 'value': '60'},
                {'key': 'serverUrl', 'value': 'http://localhost:5000'},
                {'key': 'webhooks', 'value': '[]'}
            ]
            
            for setting in default_settings:
                existing = mongo.db.settings.find_one({'key': setting['key']})
                if not existing:
                    mongo.db.settings.insert_one({
                        'key': setting['key'],
                        'value': setting['value'],
                        'updated_at': None
                    })
                    logger.info(f"✓ 创建默认设置: {setting['key']}")
            
            logger.info("数据库初始化完成！")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            return False
    
    return True

if __name__ == '__main__':
    print("=" * 50)
    print("BUCT课程提醒系统 - 数据库初始化")
    print("=" * 50)