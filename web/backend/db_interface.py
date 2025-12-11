# db_interface.py
"""
数据库接口模块
供 scraper.py 独立调用，直接与MongoDB交互
"""
import logging
from datetime import datetime, timedelta

import pymongo

from config import Config

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB 集合名称
ASSIGNMENTS_COLLECTION = 'assignments'
TESTS_COLLECTION = 'tests'


def get_db_connection():
    """获取数据库连接"""
    try:
        client = pymongo.MongoClient(Config.MONGO_URI)
        # The database name is part of the MONGO_URI
        db = client.get_default_database()
        return db
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        return None


def parse_date(date_str):
    """解析多种日期格式"""
    if not date_str: return None
    formats = ["%Y年%m月%d日 %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    logger.warning(f"无法解析日期: {date_str}")
    return None


def save_assignment(subject, title, due_date_str, publisher, content=""):
    """保存作业信息到数据库"""
    db = get_db_connection()
    if not db: return False
    try:
        due_date = parse_date(due_date_str)
        if not due_date: return False

        existing = db[ASSIGNMENTS_COLLECTION].find_one({'subject': subject, 'title': title, 'due_date': due_date})

        if existing:
            db[ASSIGNMENTS_COLLECTION].update_one(
                {'_id': existing['_id']},
                {'$set': {'publisher': publisher, 'content': content, 'updated_at': datetime.now()}}
            )
            logger.info(f"更新作业: {subject} - {title}")
        else:
            assignment_data = {
                'subject': subject, 'title': title, 'content': content, 'due_date': due_date,
                'publisher': publisher, 'type': '作业', 'created_at': datetime.now(), 'updated_at': datetime.now()
            }
            db[ASSIGNMENTS_COLLECTION].insert_one(assignment_data)
            logger.info(f"新增作业: {subject} - {title}")
        return True
    except Exception as e:
        logger.error(f"保存作业失败: {e}")
        return False


def save_test(title, start_time_str, end_time_str, allowed_attempts=1, time_limit=None):
    """保存测试信息到数据库"""
    db = get_db_connection()
    if not db: return False
    try:
        start_time, end_time = parse_date(start_time_str), parse_date(end_time_str)
        if not start_time or not end_time: return False

        existing = db[TESTS_COLLECTION].find_one({'title': title, 'start_time': start_time, 'end_time': end_time})

        if existing:
            db[TESTS_COLLECTION].update_one(
                {'_id': existing['_id']},
                {'$set': {'allowed_attempts': allowed_attempts, 'time_limit': time_limit, 'updated_at': datetime.now()}}
            )
            logger.info(f"更新测试: {title}")
        else:
            test_data = {
                'title': title, 'start_time': start_time, 'end_time': end_time,
                'allowed_attempts': allowed_attempts, 'time_limit': time_limit,
                'created_at': datetime.now(), 'updated_at': datetime.now()
            }
            db[TESTS_COLLECTION].insert_one(test_data)
            logger.info(f"新增测试: {title}")
        return True
    except Exception as e:
        logger.error(f"保存测试失败: {e}")
        return False


def clear_old_assignments(days=30):
    """清理过期的作业记录"""
    db = get_db_connection()
    if not db: return False
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        res_a = db[ASSIGNMENTS_COLLECTION].delete_many({'due_date': {'$lt': cutoff_date}})
        res_t = db[TESTS_COLLECTION].delete_many({'end_time': {'$lt': cutoff_date}})
        logger.info(f"清理完成: 删除了 {res_a.deleted_count} 个作业, {res_t.deleted_count} 个测试")
        return True
    except Exception as e:
        logger.error(f"清理过期记录失败: {e}")
        return False
