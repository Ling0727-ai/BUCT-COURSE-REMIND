"""
作业状态统一管理模块
合并软删除和完成状态的管理
"""

from bson import ObjectId
from datetime import datetime, timedelta
from .model import get_beijing_time
import logging

logger = logging.getLogger(__name__)

class AssignmentStatus:
    """作业状态统一管理类"""
    
    def __init__(self, mongo_db):
        self.db = mongo_db
        self.collection = 'assignment_status'
        
        # 创建索引
        self.db[self.collection].create_index([("user_id", 1), ("assignment_id", 1)], unique=True)
        self.db[self.collection].create_index("expires_at", expireAfterSeconds=0)  # TTL索引
        self.db[self.collection].create_index([("user_id", 1), ("status", 1)])
        # 为待办类型的软删除项目创建TTL索引，12小时后自动删除
        self.db[self.collection].create_index("todo_expires_at", expireAfterSeconds=0)  # 待办TTL索引
    
    def update_assignment_status(self, user_id, assignment_id, assignment_title, assignment_subject, status, auto_expire_hours=None, assignment_type=None):
        """
        更新作业状态
        
        Args:
            user_id: 用户ID
            assignment_id: 作业唯一标识
            assignment_title: 作业标题
            assignment_subject: 作业科目
            status: 状态 ('completed', 'deleted', 'active', 'permanent_deleted')
            auto_expire_hours: 自动过期小时数，None表示不过期
            assignment_type: 作业类型 ('todo', 'homework', 'test')
        """
        try:
            current_time = get_beijing_time()
            expires_at = None
            todo_expires_at = None
            
            if auto_expire_hours:
                expires_at = current_time + timedelta(hours=auto_expire_hours)
            
            # 如果是待办类型的软删除，设置12小时后自动删除
            if status == 'deleted' and assignment_type == 'todo':
                todo_expires_at = current_time + timedelta(hours=12)
                logger.info(f"待办类型 {assignment_id} 软删除，将在12小时后自动删除")
            
            # 如果状态是active，则删除记录（表示恢复到默认状态）
            if status == 'active':
                result = self.db[self.collection].delete_one({
                    'user_id': ObjectId(user_id),
                    'assignment_id': assignment_id
                })
                logger.info(f"恢复作业 {assignment_id} 到活跃状态，删除状态记录")
                return result
            
            # 更新或插入状态记录
            status_data = {
                'user_id': ObjectId(user_id),
                'assignment_id': assignment_id,
                'assignment_title': assignment_title,
                'assignment_subject': assignment_subject,
                'status': status,
                'status_time': current_time,
                'expires_at': expires_at,
                'assignment_type': assignment_type,
                'forever': 1 if status != 'permanent_deleted' else 0,  # 永久删除标记
                'updated_at': current_time
            }
            
            # 只有待办类型的软删除才设置todo_expires_at
            if todo_expires_at:
                status_data['todo_expires_at'] = todo_expires_at
            
            result = self.db[self.collection].update_one(
                {
                    'user_id': ObjectId(user_id),
                    'assignment_id': assignment_id
                },
                {'$set': status_data},
                upsert=True
            )
            
            logger.info(f"更新作业 {assignment_id} 状态为 {status}")
            return result
            
        except Exception as e:
            logger.error(f"更新作业状态失败: {e}")
            raise e
    
    def mark_completed(self, user_id, assignment_id, assignment_title, assignment_subject):
        """标记作业为已完成（12小时后自动过期）"""
        return self.update_assignment_status(
            user_id, assignment_id, assignment_title, assignment_subject, 
            'completed', auto_expire_hours=12
        )
    
    def mark_deleted(self, user_id, assignment_id, assignment_title, assignment_subject, assignment_type=None):
        """标记作业为已删除（待办类型12小时后自动删除）"""
        return self.update_assignment_status(
            user_id, assignment_id, assignment_title, assignment_subject, 
            'deleted', assignment_type=assignment_type
        )
    
    def restore_assignment(self, user_id, assignment_id):
        """恢复作业到活跃状态"""
        return self.update_assignment_status(
            user_id, assignment_id, '', '', 'active'
        )
    
    def permanent_delete_assignment(self, user_id, assignment_id, assignment_title='', assignment_subject=''):
        """永久删除作业（设置forever=0）"""
        return self.update_assignment_status(
            user_id, assignment_id, assignment_title, assignment_subject, 'permanent_deleted'
        )
    
    def get_user_assignment_status(self, user_id, status=None, include_permanent_deleted=False):
        """
        获取用户的作业状态列表
        
        Args:
            user_id: 用户ID
            status: 状态过滤 ('completed', 'deleted', None表示所有)
            include_permanent_deleted: 是否包含永久删除的项目
        """
        try:
            query = {'user_id': ObjectId(user_id)}
            if status:
                query['status'] = status
            
            # 默认排除永久删除的项目
            if not include_permanent_deleted:
                query['forever'] = {'$ne': 0}
            
            cursor = self.db[self.collection].find(query).sort('status_time', -1)
            return list(cursor)
            
        except Exception as e:
            logger.error(f"获取用户作业状态失败: {e}")
            return []
    
    def get_assignment_status(self, user_id, assignment_id):
        """
        获取单个作业的状态
        
        Returns:
            str: 'completed', 'deleted', 'active'
        """
        try:
            doc = self.db[self.collection].find_one({
                'user_id': ObjectId(user_id),
                'assignment_id': assignment_id
            })
            
            if doc:
                return doc.get('status', 'active')
            return 'active'
            
        except Exception as e:
            logger.error(f"获取作业状态失败: {e}")
            return 'active'
    
    def get_completed_assignment_ids(self, user_id):
        """获取用户已完成的作业ID列表（排除永久删除的）"""
        try:
            cursor = self.db[self.collection].find(
                {
                    'user_id': ObjectId(user_id),
                    'status': 'completed',
                    'forever': {'$ne': 0}
                },
                {'assignment_id': 1}
            )
            
            return [doc['assignment_id'] for doc in cursor]
            
        except Exception as e:
            logger.error(f"获取已完成作业ID列表失败: {e}")
            return []
    
    def get_deleted_assignment_ids(self, user_id):
        """获取用户已删除的作业ID列表（排除永久删除的）"""
        try:
            cursor = self.db[self.collection].find(
                {
                    'user_id': ObjectId(user_id),
                    'status': 'deleted',
                    'forever': {'$ne': 0}
                },
                {'assignment_id': 1}
            )
            
            return [doc['assignment_id'] for doc in cursor]
            
        except Exception as e:
            logger.error(f"获取已删除作业ID列表失败: {e}")
            return []
    
    def is_completed(self, user_id, assignment_id):
        """检查作业是否已完成"""
        return self.get_assignment_status(user_id, assignment_id) == 'completed'
    
    def is_deleted(self, user_id, assignment_id):
        """检查作业是否已删除"""
        return self.get_assignment_status(user_id, assignment_id) == 'deleted'
    
    def clear_user_status(self, user_id, status=None):
        """
        清空用户的状态记录（设置为永久删除而不是物理删除）
        
        Args:
            user_id: 用户ID
            status: 要清空的状态，None表示清空所有
        """
        try:
            query = {
                'user_id': ObjectId(user_id),
                'forever': {'$ne': 0}  # 只处理未永久删除的项目
            }
            if status:
                query['status'] = status
            
            # 设置为永久删除而不是物理删除
            result = self.db[self.collection].update_many(
                query,
                {
                    '$set': {
                        'forever': 0,
                        'status': 'permanent_deleted',
                        'updated_at': get_beijing_time()
                    }
                }
            )
            logger.info(f"永久删除用户 {user_id} 的状态记录 {result.modified_count} 条")
            return result.modified_count
            
        except Exception as e:
            logger.error(f"清空用户状态记录失败: {e}")
            raise e
    
    def clear_user_status_by_ids(self, user_id, assignment_ids):
        """
        根据assignment_id列表清空用户的状态记录
        
        Args:
            user_id: 用户ID
            assignment_ids: 要清空的assignment_id列表
        """
        try:
            if not assignment_ids:
                return 0
                
            query = {
                'user_id': ObjectId(user_id),
                'assignment_id': {'$in': assignment_ids}
            }
            
            result = self.db[self.collection].delete_many(query)
            logger.info(f"清空用户 {user_id} 的指定状态记录 {result.deleted_count} 条")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"清空用户指定状态记录失败: {e}")
            raise e
    
    def cleanup_expired(self):
        """手动清理过期记录（TTL索引会自动处理）"""
        try:
            result = self.db[self.collection].delete_many({
                'expires_at': {'$lt': get_beijing_time()}
            })
            logger.info(f"手动清理过期状态记录 {result.deleted_count} 条")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"清理过期记录失败: {e}")
            return 0
    
    def get_status_stats(self, user_id):
        """获取用户的状态统计"""
        try:
            pipeline = [
                {'$match': {'user_id': ObjectId(user_id)}},
                {'$group': {
                    '_id': '$status',
                    'count': {'$sum': 1}
                }}
            ]
            
            result = list(self.db[self.collection].aggregate(pipeline))
            stats = {'completed': 0, 'deleted': 0, 'total': 0}
            
            for item in result:
                status = item['_id']
                count = item['count']
                if status in stats:
                    stats[status] = count
                stats['total'] += count
            
            return stats
            
        except Exception as e:
            logger.error(f"获取状态统计失败: {e}")
            return {'completed': 0, 'deleted': 0, 'total': 0}

# 全局实例
assignment_status_manager = None

def get_assignment_status_manager():
    """获取作业状态管理器实例"""
    global assignment_status_manager
    if assignment_status_manager is None:
        from . import mongo
        if mongo.db is not None:
            assignment_status_manager = AssignmentStatus(mongo.db)
        else:
            # 如果在应用上下文外调用，返回None或抛出异常
            raise RuntimeError("需要在Flask应用上下文中调用此函数")
    return assignment_status_manager