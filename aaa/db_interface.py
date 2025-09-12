# db_interface.py
"""
数据库接口模块
供scraper.py调用，用于保存抓取到的作业和测试数据
"""
from app import app, db, Assignment, Test
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def save_assignment(subject, title, due_date_str, publisher, content=""):
    """
    保存作业信息到数据库
    
    Args:
        subject: 科目名称
        title: 作业标题
        due_date_str: 截止时间字符串，格式如 "2025年9月21日 23:59:00"
        publisher: 发布者
        content: 作业内容描述
    """
    with app.app_context():
        try:
            # 解析日期格式
            due_date = parse_date(due_date_str)
            if not due_date:
                logger.error(f"无法解析日期格式: {due_date_str}")
                return False
            
            # 检查是否已存在相同作业（根据科目、标题、截止时间判断）
            existing = Assignment.query.filter_by(
                subject=subject,
                title=title,
                due_date=due_date
            ).first()
            
            if existing:
                # 更新现有记录
                existing.publisher = publisher
                existing.content = content
                existing.updated_at = datetime.utcnow()
                logger.info(f"更新作业: {subject} - {title}")
            else:
                # 创建新记录
                assignment = Assignment(
                    subject=subject,
                    title=title,
                    content=content,
                    due_date=due_date,
                    publisher=publisher,
                    type='作业'
                )
                db.session.add(assignment)
                logger.info(f"新增作业: {subject} - {title}")
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"保存作业失败: {str(e)}")
            return False

def save_test(title, start_time_str, end_time_str, allowed_attempts=1, time_limit=None):
    """
    保存测试信息到数据库
    
    Args:
        title: 测试标题
        start_time_str: 开始时间字符串
        end_time_str: 结束时间字符串
        allowed_attempts: 允许测试次数
        time_limit: 限制用时（分钟）
    """
    with app.app_context():
        try:
            # 解析日期格式
            start_time = parse_date(start_time_str)
            end_time = parse_date(end_time_str)
            
            if not start_time or not end_time:
                logger.error(f"无法解析测试时间: {start_time_str} - {end_time_str}")
                return False
            
            # 检查是否已存在相同测试
            existing = Test.query.filter_by(
                title=title,
                start_time=start_time,
                end_time=end_time
            ).first()
            
            if existing:
                # 更新现有记录
                existing.allowed_attempts = allowed_attempts
                existing.time_limit = time_limit
                existing.updated_at = datetime.utcnow()
                logger.info(f"更新测试: {title}")
            else:
                # 创建新记录
                test = Test(
                    title=title,
                    start_time=start_time,
                    end_time=end_time,
                    allowed_attempts=allowed_attempts,
                    time_limit=time_limit
                )
                db.session.add(test)
                logger.info(f"新增测试: {title}")
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"保存测试失败: {str(e)}")
            return False

def parse_date(date_str):
    """
    解析多种日期格式
    """
    if not date_str:
        return None
        
    # 常见的日期格式
    formats = [
        "%Y年%m月%d日 %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y年%m月%d日",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m/%d/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    return None

def clear_old_assignments(days=30):
    """
    清理过期的作业记录
    
    Args:
        days: 保留最近多少天的记录
    """
    with app.app_context():
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # 删除过期作业
            deleted_assignments = Assignment.query.filter(
                Assignment.due_date < cutoff_date
            ).delete()
            
            # 删除过期测试
            deleted_tests = Test.query.filter(
                Test.end_time < cutoff_date
            ).delete()
            
            db.session.commit()
            
            logger.info(f"清理完成: 删除了 {deleted_assignments} 个作业, {deleted_tests} 个测试")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"清理过期记录失败: {str(e)}")
            return False

def get_recent_assignments(days=7):
    """
    获取最近的作业列表
    """
    with app.app_context():
        try:
            cutoff_date = datetime.utcnow() + timedelta(days=days)
            
            assignments = Assignment.query.filter(
                Assignment.due_date >= datetime.utcnow(),
                Assignment.due_date <= cutoff_date
            ).order_by(Assignment.due_date.asc()).all()
            
            tests = Test.query.filter(
                Test.end_time >= datetime.utcnow(),
                Test.end_time <= cutoff_date
            ).order_by(Test.start_time.asc()).all()
            
            return assignments, tests
            
        except Exception as e:
            logger.error(f"获取最近作业失败: {str(e)}")
            return [], []

# 示例用法
if __name__ == "__main__":
    # 测试保存作业
    save_assignment(
        subject="数字电子技术",
        title="第一次作业",
        due_date_str="2025年9月21日 23:59:00",
        publisher="李香玲",
        content="完成第一章习题"
    )
    
    # 测试保存测试
    save_test(
        title="期中考试",
        start_time_str="2025年9月20日 14:00:00",
        end_time_str="2025年9月20日 16:00:00",
        allowed_attempts=1,
        time_limit=120
    )
    
    print("数据保存测试完成")