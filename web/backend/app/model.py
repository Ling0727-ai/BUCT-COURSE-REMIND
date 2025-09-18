# -*- coding: utf-8 -*-
"""
数据库模型文档

本文档定义了项目中使用的 MongoDB 数据库的集合（Collections）结构和字段说明。
"""

from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson import ObjectId

# ==============================================================================
# 1. users (用户信息)
# ==============================================================================
"""
存储系统用户的基本信息、凭证和权限。

{
    "_id": ObjectId("..."),
    "username": "admin",                   // String, 用户名 (唯一)
    "password_hash": "pbkdf2:sha256:...",  // String, 哈希后的登录密码
    "email": "user@example.com",           // String, 邮箱地址
    "student_id": "123456789",             // String, 学号
    "s_password": "encrypted_password",    // String, 加密后的外部网站密码
    "is_admin": false,                     // Boolean, 是否为管理员
    "created_at": ISODate("..."),          // DateTime, 账户创建时间
    "updated_at": ISODate("...")           // DateTime, 账户更新时间
}
"""

class User:
    """用户模型类"""
    
    def __init__(self, mongo_db):
        self.db = mongo_db
        self.collection = 'users'
    
    def create_user(self, username, email, password, student_id=None, s_password=None):
        """创建新用户"""
        user_data = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'student_id': student_id,
            's_password': s_password,  # 注意：实际应用中应该加密存储
            'is_admin': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.db[self.collection].insert_one(user_data)
        return result.inserted_id
    
    def find_by_username(self, username):
        """根据用户名查找用户"""
        return self.db[self.collection].find_one({'username': username})
    
    def find_by_email(self, email):
        """根据邮箱查找用户"""
        return self.db[self.collection].find_one({'email': email})
    
    def find_by_id(self, user_id):
        """根据ID查找用户"""
        return self.db[self.collection].find_one({'_id': ObjectId(user_id)})
    
    def update_user(self, user_id, update_data):
        """更新用户信息"""
        update_data['updated_at'] = datetime.utcnow()
        return self.db[self.collection].update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
    
    def update_student_credentials(self, user_id, student_id, s_password):
        """更新学号和外部密码"""
        return self.update_user(user_id, {
            'student_id': student_id,
            's_password': s_password  # 注意：实际应用中应该加密存储
        })
    
    def verify_password(self, user, password):
        """验证密码"""
        return check_password_hash(user['password_hash'], password)

# ==============================================================================
# 2. assignments (作业信息)
# ==============================================================================
"""
存储从教务系统抓取的作业信息。

{
    "_id": ObjectId("..."),
    "subject": "大学物理",                 // String, 科目名称
    "title": "第五章 课后习题",             // String, 作业标题
    "content": "完成课本P123的练习题1-5",  // String, 作业具体内容
    "due_date": ISODate("..."),            // DateTime, 截止日期
    "publisher": "张老师",                 // String, 发布人
    "type": "作业",                        // String, 类型 (固定为"作业")
    "created_at": ISODate("..."),          // DateTime, 记录创建时间
    "updated_at": ISODate("...")           // DateTime, 记录更新时间
}
"""

# ==============================================================================
# 3. tests (测试信息)
# ==============================================================================
"""
存储从教务系统抓取的在线测试信息。

{
    "_id": ObjectId("..."),
    "title": "期中在线测试",               // String, 测试标题
    "start_time": ISODate("..."),          // DateTime, 测试开始时间
    "end_time": ISODate("..."),            // DateTime, 测试结束时间
    "allowed_attempts": 1,                 // Integer, 允许尝试次数
    "time_limit": 60,                      // Integer, 限制用时 (分钟)
    "created_at": ISODate("..."),          // DateTime, 记录创建时间
    "updated_at": ISODate("...")           // DateTime, 记录更新时间
}
"""

# ==============================================================================
# 4. settings (系统设置)
# ==============================================================================
"""
存储系统的各项可配置参数。采用键值对形式。

{
    "_id": ObjectId("..."),
    "key": "scrape_interval",              // String, 设置项的键 (唯一)
    "value": "60",                         // String, 设置项的值
    "updated_at": ISODate("...")           // DateTime, 更新时间
}

# --- 已知的 key ---
# "scrape_interval": 爬虫执行间隔时间（分钟）
# "webhooks": Webhook配置，value是一个JSON字符串数组
# "serverUrl": 服务器URL地址
"""

# ==============================================================================
# 5. verification_codes (邮箱验证码)
# ==============================================================================
"""
临时存储用于邮箱验证的验证码。

{
    "_id": ObjectId("..."),
    "email": "user@example.com",           // String, 接收验证码的邮箱
    "code": "123456",                      // String, 6位数字验证码
    "created_at": ISODate("..."),          // DateTime, 创建时间
    "expires_at": ISODate("...")           // DateTime, 过期时间
}
"""

# ==============================================================================
# 6. webhook_logs (Webhook发送日志)
# ==============================================================================
"""
记录通过Webhook发送通知的日志，用于排查问题。

{
    "_id": ObjectId("..."),
    "webhook_type": "email",               // String, Webhook类型 (如 "email", "discord")
    "message": "⚠️ 紧急提醒...",          // String, 发送的消息内容
    "status": "success",                   // String, 发送状态 ("success" 或 "failed")
    "created_at": ISODate("...")           // DateTime, 日志创建时间
}
"""