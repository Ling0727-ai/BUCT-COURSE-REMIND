# -*- coding: utf-8 -*-
"""
数据库模型文档

本文档定义了项目中使用的 MongoDB 数据库的集合（Collections）结构和字段说明。
"""

from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 定义北京时区
BEIJING_TZ = timezone(timedelta(hours=8))

def get_beijing_time():
    """获取北京时间（naive datetime，用于MongoDB存储）"""
    # 获取UTC时间，然后转换为北京时间（不带时区信息）
    utc_now = datetime.utcnow()
    beijing_now = utc_now + timedelta(hours=8)
    return beijing_now

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
        
        # 从环境变量读取自定义ECC密钥（十进制）
        private_key_env = os.getenv('ECC_PRIVATE_KEY')
        public_key_env = os.getenv('ECC_PUBLIC_KEY')
        
        print(f"调试信息：ECC_PRIVATE_KEY={private_key_env}, ECC_PUBLIC_KEY={public_key_env}")
        
        if not private_key_env or not public_key_env:
            print("警告：ECC_PRIVATE_KEY 或 ECC_PUBLIC_KEY 环境变量未设置，使用默认密钥")
            # 使用默认密钥
            private_key_value = 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
            expected_public_key_value = None
        else:
            try:
                private_key_value = int(private_key_env)
                expected_public_key_value = int(public_key_env)
                print(f"成功加载自定义密钥：private_key_value={private_key_value}")
            except ValueError as e:
                print(f"警告：密钥格式错误，使用默认密钥: {e}")
                private_key_value = 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
                expected_public_key_value = None
        
        try:
            self.private_key = ec.derive_private_key(private_key_value, ec.SECP256R1())
            self.public_key = self.private_key.public_key()
            
            # 验证公钥是否匹配（可选验证）
            # 注意：ECC公钥是椭圆曲线上的点，不是单个整数
            # 这里只是记录您提供的公钥值，实际使用从私钥派生的公钥
            self.expected_public_value = expected_public_key_value
            
            print(f"ECC密钥初始化成功，私钥值: {private_key_value}")
            print(f"预期公钥值: {expected_public_key_value}")
            
        except Exception as e:
            # 如果自定义密钥无效，使用备用密钥
            print(f"自定义密钥无效，使用备用密钥: {e}")
            backup_key = 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
            self.private_key = ec.derive_private_key(backup_key, ec.SECP256R1())
            self.public_key = self.private_key.public_key()
            self.expected_public_value = None
    
    def create_user(self, username, email, password, student_id=None, s_password=None):
        """创建新用户"""
        user_data = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'student_id': student_id,
            's_password': self._encrypt_password(s_password) if s_password else None,  # 使用ECC加密存储
            'is_admin': False,
            'created_at': get_beijing_time(),
            'updated_at': get_beijing_time()
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
        update_data['updated_at'] = get_beijing_time()
        return self.db[self.collection].update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
    
    def update_student_credentials(self, user_id, student_id, s_password):
        """更新学号和外部密码"""
        return self.update_user(user_id, {
            'student_id': student_id,
            's_password': self._encrypt_password(s_password) if s_password else None  # 使用ECC加密存储
        })
    
    def get_decrypted_s_password(self, user):
        """获取解密后的学生密码"""
        if not user or 's_password' not in user or not user['s_password']:
            return None
        return self._decrypt_password(user['s_password'])
    
    def _encrypt_password(self, password):
        """使用ECC加密密码"""
        if not password:
            return None
        
        # 生成临时密钥对用于ECDH
        ephemeral_private_key = ec.generate_private_key(ec.SECP256R1())
        ephemeral_public_key = ephemeral_private_key.public_key()
        
        # 执行ECDH密钥交换
        shared_key = ephemeral_private_key.exchange(ec.ECDH(), self.public_key)
        
        # 使用HKDF派生AES密钥
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'password encryption',
        ).derive(shared_key)
        
        # 生成随机IV
        iv = os.urandom(16)
        
        # 使用AES-GCM加密
        cipher = Cipher(algorithms.AES(derived_key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(password.encode('utf-8')) + encryptor.finalize()
        
        # 序列化临时公钥
        ephemeral_public_bytes = ephemeral_public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        
        # 组合所有数据：临时公钥 + IV + 认证标签 + 密文
        encrypted_data = ephemeral_public_bytes + iv + encryptor.tag + ciphertext
        
        # Base64编码返回
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def _decrypt_password(self, encrypted_password):
        """使用ECC解密密码"""
        if not encrypted_password:
            return None
        
        try:
            # Base64解码
            encrypted_data = base64.b64decode(encrypted_password.encode('utf-8'))
            
            # 提取各部分数据
            ephemeral_public_bytes = encrypted_data[:65]  # 未压缩点格式65字节
            iv = encrypted_data[65:81]  # 16字节IV
            tag = encrypted_data[81:97]  # 16字节认证标签
            ciphertext = encrypted_data[97:]  # 剩余为密文
            
            # 重建临时公钥
            ephemeral_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256R1(), ephemeral_public_bytes
            )
            
            # 执行ECDH密钥交换
            shared_key = self.private_key.exchange(ec.ECDH(), ephemeral_public_key)
            
            # 使用HKDF派生AES密钥
            derived_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'password encryption',
            ).derive(shared_key)
            
            # 使用AES-GCM解密
            cipher = Cipher(algorithms.AES(derived_key), modes.GCM(iv, tag))
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext.decode('utf-8')
            
        except Exception as e:
            print(f"解密失败: {e}")
            return None
    
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

# ==============================================================================
# 7. todos (待办事项)
# ==============================================================================
"""
存储用户的待办事项。

{
    "_id": ObjectId("..."),
    "user_id": ObjectId("..."),            // ObjectId, 用户ID
    "title": "完成项目报告",               // String, 待办标题
    "description": "需要完成第三章内容",   // String, 待办描述 (可选)
    "priority": "medium",                  // String, 优先级 ("low", "medium", "high")
    "due_date": ISODate("..."),            // DateTime, 截止日期 (可选)
    "completed": false,                    // Boolean, 是否已完成
    "completed_at": ISODate("..."),        // DateTime, 完成时间 (可选)
    "created_at": ISODate("..."),          // DateTime, 创建时间
    "updated_at": ISODate("...")           // DateTime, 更新时间
}
"""

class Todo:
    """待办事项模型类"""
    
    def __init__(self, mongo_db):
        self.db = mongo_db
        self.collection = 'todos'
        # 创建过期时间索引，MongoDB会自动删除过期的已完成待办
        self.db[self.collection].create_index("expires_at", expireAfterSeconds=0)
    
    def create_todo(self, user_id, title, description=None, priority='medium', due_date=None, estimated_hours=None):
        """创建新的待办事项"""
        todo_data = {
            'user_id': ObjectId(user_id),
            'title': title,
            'description': description,
            'priority': priority,
            'due_date': due_date,
            'estimated_hours': estimated_hours,  # 保存用户输入的预计小时数
            'completed': False,
            'completed_at': None,
            'expires_at': None,  # 完成后12小时过期时间
            'is_deleted': False,  # 是否已删除
            'delete_time': None,  # 删除时间
            'created_at': get_beijing_time(),
            'updated_at': get_beijing_time()
        }
        
        result = self.db[self.collection].insert_one(todo_data)
        return result.inserted_id
    
    def get_user_todos(self, user_id, include_completed=True):
        """获取用户的待办事项列表（不包括已删除的）"""
        query = {
            'user_id': ObjectId(user_id),
            'is_deleted': {'$ne': True}  # 排除已删除的项目
        }
        if not include_completed:
            query['completed'] = False
        
        todos = list(self.db[self.collection].find(query).sort('created_at', -1))
        return todos
    
    def get_todo_by_id(self, todo_id, user_id):
        """根据ID获取待办事项"""
        return self.db[self.collection].find_one({
            '_id': ObjectId(todo_id),
            'user_id': ObjectId(user_id)
        })
    
    def update_todo(self, todo_id, user_id, update_data):
        """更新待办事项"""
        update_data['updated_at'] = datetime.now()
        return self.db[self.collection].update_one(
            {
                '_id': ObjectId(todo_id),
                'user_id': ObjectId(user_id)
            },
            {'$set': update_data}
        )
    
    def mark_completed(self, todo_id, user_id):
        """标记待办事项为已完成，12小时后自动删除"""
        from datetime import timedelta
        completed_at = get_beijing_time()
        expires_at = completed_at + timedelta(hours=12)  # 12小时后过期
        
        return self.update_todo(todo_id, user_id, {
            'completed': True,
            'completed_at': completed_at,
            'expires_at': expires_at
        })
    
    def mark_uncompleted(self, todo_id, user_id):
        """撤销待办事项完成状态"""
        return self.update_todo(todo_id, user_id, {
            'completed': False,
            'completed_at': None,
            'expires_at': None
        })
    
    def delete_todo(self, todo_id, user_id):
        """软删除待办事项（标记为已删除）"""
        delete_time = get_beijing_time()
        return self.update_todo(todo_id, user_id, {
            'is_deleted': True,
            'delete_time': delete_time
        })
    
    def restore_todo(self, todo_id, user_id):
        """恢复已删除的待办事项"""
        return self.update_todo(todo_id, user_id, {
            'is_deleted': False,
            'delete_time': None
        })
    
    def permanent_delete_todo(self, todo_id, user_id):
        """永久删除待办事项"""
        return self.db[self.collection].delete_one({
            '_id': ObjectId(todo_id),
            'user_id': ObjectId(user_id)
        })
    
    def get_deleted_todos(self, user_id):
        """获取用户已删除的待办事项列表"""
        query = {
            'user_id': ObjectId(user_id),
            'is_deleted': True
        }
        todos = list(self.db[self.collection].find(query).sort('delete_time', -1))
        return todos
    
    def clear_deleted_todos(self, user_id):
        """清空用户的已删除待办事项"""
        return self.db[self.collection].delete_many({
            'user_id': ObjectId(user_id),
            'is_deleted': True
        })

# ==============================================================================
# 8. completed_assignments (已完成作业记录)
# ==============================================================================
"""
存储用户标记为已完成的作业记录，12小时后自动清除。

{
    "_id": ObjectId("..."),
    "user_id": ObjectId("..."),            // ObjectId, 用户ID
    "assignment_id": "homework_math_123",  // String, 作业唯一标识
    "assignment_title": "数学作业第一章", // String, 作业标题
    "assignment_subject": "高等数学",      // String, 作业科目
    "completed_at": ISODate("..."),        // DateTime, 完成时间
    "expires_at": ISODate("...")           // DateTime, 过期时间 (完成时间 + 12小时)
}
"""

# ==============================================================================
# 9. deleted_assignments (已删除作业记录)
# ==============================================================================
"""
存储用户删除的作业记录，支持恢复功能。

{
    "_id": ObjectId("..."),
    "user_id": ObjectId("..."),            // ObjectId, 用户ID
    "assignment_id": "homework_math_123",  // String, 作业唯一标识
    "assignment_title": "数学作业第一章", // String, 作业标题
    "assignment_subject": "高等数学",      // String, 作业科目
    "delete_time": ISODate("..."),         // DateTime, 删除时间
    "created_at": ISODate("...")           // DateTime, 记录创建时间
}
"""

class CompletedAssignment:
    """已完成作业模型类"""
    
    def __init__(self, mongo_db):
        self.db = mongo_db
        self.collection = 'completed_assignments'
        # 创建过期时间索引，MongoDB会自动删除过期文档
        self.db[self.collection].create_index("expires_at", expireAfterSeconds=0)
    
    def mark_completed(self, user_id, assignment_id, assignment_title, assignment_subject):
        """标记作业为已完成"""
        from datetime import datetime, timedelta
        
        completed_at = get_beijing_time()
        expires_at = completed_at + timedelta(hours=12)  # 12小时后过期
        
        # 使用 upsert 避免重复记录
        result = self.db[self.collection].update_one(
            {
                'user_id': ObjectId(user_id),
                'assignment_id': assignment_id
            },
            {
                '$set': {
                    'user_id': ObjectId(user_id),
                    'assignment_id': assignment_id,
                    'assignment_title': assignment_title,
                    'assignment_subject': assignment_subject,
                    'completed_at': completed_at,
                    'expires_at': expires_at
                }
            },
            upsert=True
        )
        
        return result
    
    def unmark_completed(self, user_id, assignment_id):
        """取消完成标记"""
        result = self.db[self.collection].delete_one({
            'user_id': ObjectId(user_id),
            'assignment_id': assignment_id
        })
        return result
    
    def get_user_completed(self, user_id):
        """获取用户的所有已完成作业"""
        completed_assignments = list(self.db[self.collection].find({
            'user_id': ObjectId(user_id)
        }))
        
        # 返回assignment_id列表，方便前端使用
        return [item['assignment_id'] for item in completed_assignments]
    
    def is_completed(self, user_id, assignment_id):
        """检查作业是否已完成"""
        result = self.db[self.collection].find_one({
            'user_id': ObjectId(user_id),
            'assignment_id': assignment_id
        })
        return result is not None
    
    def cleanup_expired(self):
        """手动清理过期记录（MongoDB TTL索引会自动处理，这个方法作为备用）"""
        from datetime import datetime
        
        result = self.db[self.collection].delete_many({
            'expires_at': {'$lt': get_beijing_time()}
        })
        return result.deleted_count


class DeletedAssignment:
    """已删除作业模型类"""
    
    def __init__(self, mongo_db):
        self.db = mongo_db
        self.collection = 'deleted_assignments'
    
    def mark_deleted(self, user_id, assignment_id, assignment_title, assignment_subject):
        """标记作业为已删除"""
        delete_time = get_beijing_time()
        
        deleted_data = {
            'user_id': ObjectId(user_id),
            'assignment_id': assignment_id,
            'assignment_title': assignment_title,
            'assignment_subject': assignment_subject,
            'delete_time': delete_time,
            'created_at': delete_time
        }
        
        # 使用 upsert 避免重复记录
        result = self.db[self.collection].update_one(
            {
                'user_id': ObjectId(user_id),
                'assignment_id': assignment_id
            },
            {'$set': deleted_data},
            upsert=True
        )
        
        return result
    
    def restore_assignment(self, user_id, assignment_id):
        """恢复已删除的作业"""
        result = self.db[self.collection].delete_one({
            'user_id': ObjectId(user_id),
            'assignment_id': assignment_id
        })
        
        return result
    
    def permanent_delete_assignment(self, user_id, assignment_id):
        """永久删除作业记录"""
        result = self.db[self.collection].delete_one({
            'user_id': ObjectId(user_id),
            'assignment_id': assignment_id
        })
        
        return result
    
    def get_deleted_assignments(self, user_id):
        """获取用户的已删除作业列表"""
        deleted_assignments = list(self.db[self.collection].find({
            'user_id': ObjectId(user_id)
        }).sort('delete_time', -1))
        
        return deleted_assignments
    
    def clear_deleted_assignments(self, user_id):
        """清空用户的已删除作业"""
        result = self.db[self.collection].delete_many({
            'user_id': ObjectId(user_id)
        })
        
        return result
    
    def is_deleted(self, user_id, assignment_id):
        """检查作业是否已删除"""
        result = self.db[self.collection].find_one({
            'user_id': ObjectId(user_id),
            'assignment_id': assignment_id
        })
        return result is not None