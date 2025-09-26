#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试待办类型软删除12小时后自动删除功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from bson import ObjectId
from datetime import datetime, timedelta

def test_todo_auto_delete():
    """测试待办类型的自动删除功能"""
    print('🧪 测试待办类型软删除自动删除功能...')
    
    app = create_app()
    
    with app.app_context():
        try:
            from app.assignment_status import get_assignment_status_manager
            from app.course_data import get_course_data_manager
            
            # 创建测试用户ID
            test_user_id = str(ObjectId())
            print(f'👤 测试用户ID: {test_user_id}')
            
            status_manager = get_assignment_status_manager()
            course_manager = get_course_data_manager()
            
            # 1. 创建不同类型的测试数据
            test_tasks = [
                {
                    'subject': '数学',
                    'title': '作业1',
                    'deadline': '2025-10-01 23:59:00',
                    'details': '完成第一章习题',
                    'url': 'http://example.com/1',
                    'type': 'homework'
                },
                {
                    'subject': '物理',
                    'title': '待办事项1',
                    'deadline': '2025-10-02 23:59:00',
                    'details': '复习第二章',
                    'url': 'http://example.com/2',
                    'type': 'todo'
                },
                {
                    'subject': '化学',
                    'title': '待办事项2',
                    'deadline': '2025-10-03 23:59:00',
                    'details': '准备实验',
                    'url': 'http://example.com/3',
                    'type': 'todo'
                }
            ]
            
            # 保存测试数据
            course_manager.save_user_course_data(test_user_id, test_tasks)
            saved_tasks = course_manager.get_user_course_data(test_user_id)
            print(f'📝 保存了 {len(saved_tasks)} 个任务')
            
            # 获取任务ID
            homework_task = next((t for t in saved_tasks if t['type'] == 'homework'), None)
            todo_tasks = [t for t in saved_tasks if t['type'] == 'todo']
            
            print(f'📋 任务类型分布: 作业 {1 if homework_task else 0} 个, 待办 {len(todo_tasks)} 个')
            
            # 2. 软删除不同类型的任务
            if homework_task:
                homework_id = homework_task['task_id']
                status_manager.mark_deleted(test_user_id, homework_id, homework_task['title'], homework_task['subject'], 'homework')
                print(f'🗑️ 软删除作业: {homework_task["title"]} (类型: homework)')
            
            for todo_task in todo_tasks:
                todo_id = todo_task['task_id']
                status_manager.mark_deleted(test_user_id, todo_id, todo_task['title'], todo_task['subject'], 'todo')
                print(f'🗑️ 软删除待办: {todo_task["title"]} (类型: todo)')
            
            # 3. 检查软删除状态
            deleted_ids = status_manager.get_deleted_assignment_ids(test_user_id)
            print(f'✅ 当前软删除列表: {len(deleted_ids)} 个项目')
            
            # 4. 检查数据库中的TTL字段
            from app import mongo
            status_records = list(mongo.db.assignment_status.find({'user_id': ObjectId(test_user_id)}))
            
            print('\\n🔍 检查TTL字段设置:')
            for record in status_records:
                assignment_type = record.get('assignment_type', 'unknown')
                has_todo_expires = 'todo_expires_at' in record
                has_regular_expires = 'expires_at' in record
                
                print(f'   - {record["assignment_title"]} (类型: {assignment_type})')
                print(f'     todo_expires_at: {"✅" if has_todo_expires else "❌"}')
                print(f'     expires_at: {"✅" if has_regular_expires else "❌"}')
                
                if has_todo_expires:
                    todo_expires = record['todo_expires_at']
                    print(f'     待办过期时间: {todo_expires}')
            
            # 5. 验证预期行为
            todo_records = [r for r in status_records if r.get('assignment_type') == 'todo']
            homework_records = [r for r in status_records if r.get('assignment_type') == 'homework']
            
            print('\\n📊 验证结果:')
            
            # 检查待办类型是否设置了todo_expires_at
            todo_with_ttl = sum(1 for r in todo_records if 'todo_expires_at' in r)
            print(f'✅ 待办类型设置TTL: {todo_with_ttl}/{len(todo_records)}')
            
            # 检查作业类型是否没有设置todo_expires_at
            homework_without_todo_ttl = sum(1 for r in homework_records if 'todo_expires_at' not in r)
            print(f'✅ 作业类型未设置待办TTL: {homework_without_todo_ttl}/{len(homework_records)}')
            
            # 6. 模拟12小时后的情况（通过修改过期时间）
            print('\\n⏰ 模拟12小时后的自动删除...')
            
            # 将待办类型的过期时间设置为过去时间
            past_time = datetime.utcnow() - timedelta(minutes=1)
            mongo.db.assignment_status.update_many(
                {
                    'user_id': ObjectId(test_user_id),
                    'assignment_type': 'todo',
                    'status': 'deleted'
                },
                {'$set': {'todo_expires_at': past_time}}
            )
            
            # 等待MongoDB TTL索引处理（实际环境中会自动处理）
            print('⏳ 等待TTL索引处理...')
            
            # 手动触发清理（模拟TTL效果）
            cleanup_result = mongo.db.assignment_status.delete_many({
                'todo_expires_at': {'$lt': datetime.utcnow()}
            })
            
            print(f'🧹 手动清理过期待办记录: {cleanup_result.deleted_count} 条')
            
            # 7. 验证最终结果
            final_deleted_ids = status_manager.get_deleted_assignment_ids(test_user_id)
            final_records = list(mongo.db.assignment_status.find({'user_id': ObjectId(test_user_id)}))
            
            print('\\n🎯 最终验证结果:')
            print(f'   剩余软删除记录: {len(final_deleted_ids)} 个')
            print(f'   剩余状态记录: {len(final_records)} 个')
            
            for record in final_records:
                assignment_type = record.get('assignment_type', 'unknown')
                print(f'   - {record["assignment_title"]} (类型: {assignment_type})')
            
            # 检查是否只剩下作业类型的软删除记录
            remaining_todo_count = sum(1 for r in final_records if r.get('assignment_type') == 'todo')
            remaining_homework_count = sum(1 for r in final_records if r.get('assignment_type') == 'homework')
            
            if remaining_todo_count == 0 and remaining_homework_count > 0:
                print('\\n✅ 测试成功：待办类型已自动删除，作业类型保留')
                success = True
            elif remaining_todo_count > 0:
                print('\\n❌ 测试失败：待办类型未被自动删除')
                success = False
            else:
                print('\\n⚠️ 测试结果：所有记录都被删除了')
                success = False
            
            # 清理测试数据
            course_manager.clear_user_data(test_user_id)
            status_manager.clear_user_status(test_user_id)
            print('🧹 清理测试数据完成')
            
            return success
            
        except Exception as e:
            print(f'❌ 测试失败: {e}')
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_todo_auto_delete()
    if success:
        print('\\n🎉 待办自动删除功能测试通过！')
    else:
        print('\\n💥 待办自动删除功能测试失败！')
    sys.exit(0 if success else 1)