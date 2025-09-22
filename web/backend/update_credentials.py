# update_credentials.py
import os
import sys
from pymongo import MongoClient
from urllib.parse import quote_plus
import getpass

# Add backend to path to allow imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def update_credentials():
    """安全地更新 testuser 的教务系统凭证"""
    print("--- 更新 'testuser' 的教务系统凭证 ---")

    try:
        # 获取用户输入
        student_id = input("请输入您的真实学号 (student_id): ")
        s_password = getpass.getpass("请输入您的真实教务系统密码 (s_password, 输入时不会显示): ")

        if not student_id or not s_password:
            print("错误: 学号和密码不能为空。")
            return

        # 连接数据库
        username = quote_plus(os.getenv('MONGO_INITDB_ROOT_USERNAME', 'REDACTED_MONGO_USER'))
        password = quote_plus(os.getenv('MONGO_INITDB_ROOT_PASSWORD', 'REDACTED_MONGO_PASSWORD'))
        host = os.getenv('MONGO_HOST', 'localhost')
        port = os.getenv('MONGO_PORT', '27017')
        db_name = os.getenv('MONGO_INITDB_DATABASE', 'buct-course')
        mongo_uri = f"mongodb://{username}:{password}@{host}:{port}/{db_name}?authSource=admin"

        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client[db_name]

        # 更新 testuser 的凭证
        result = db.users.update_one(
            {'username': 'testuser'},
            {'$set': {
                'student_id': student_id,
                's_password': s_password  # 注意: 在生产环境中，密码应该加密存储
            }}
        )

        if result.matched_count > 0:
            if result.modified_count > 0:
                print("\n✓ 凭证更新成功！")
            else:
                print("\n✓ 凭证与数据库中已存储的相同，未进行修改。")
        else:
            print("\n✗ 错误: 在数据库中未找到 'testuser'。")

        client.close()

    except Exception as e:
        print(f"\n✗ 数据库操作失败: {e}")

if __name__ == "__main__":
    update_credentials()