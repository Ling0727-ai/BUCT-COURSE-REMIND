#!/usr/bin/env python3
"""
MongoDB设置脚本 - 创建无认证的测试数据库
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def setup_mongodb():
    """设置MongoDB"""
    print("=== MongoDB设置 ===")
    
    try:
        # 连接到MongoDB（带认证）
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://***REMOVED***:***REMOVED***@localhost:27017/assignment_manager')
        client = MongoClient(mongo_uri)
        
        # 测试连接
        client.admin.command('ping')
        print("✅ MongoDB连接成功")
        
        # 选择数据库
        db = client['assignment_manager']
        
        # 创建测试集合并插入测试数据
        test_collection = db['test']
        test_doc = {'message': 'MongoDB setup successful', 'timestamp': '2024-01-01'}
        result = test_collection.insert_one(test_doc)
        print(f"✅ 测试文档插入成功，ID: {result.inserted_id}")
        
        # 清理测试数据
        test_collection.delete_one({'_id': result.inserted_id})
        print("✅ 测试数据清理完成")
        
        # 创建验证码集合的索引
        verification_codes = db['verification_codes']
        verification_codes.create_index("expires_at", expireAfterSeconds=0)
        print("✅ 验证码集合TTL索引创建成功")
        
        client.close()
        print("✅ MongoDB设置完成")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB设置失败: {e}")
        print("\n可能的解决方案：")
        print("1. 确认MongoDB服务正在运行")
        print("2. 尝试启动MongoDB: net start MongoDB (Windows) 或 sudo systemctl start mongod (Linux)")
        print("3. 检查MongoDB是否配置了认证，如果是请更新连接URI")
        return False

if __name__ == "__main__":
    setup_mongodb()