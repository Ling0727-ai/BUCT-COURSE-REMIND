#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实场景测试：验证用户实际看到的数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from bson import ObjectId

def test_real_user_experience():
    """测试用户实际看到的数据"""
    print('🧪 测试真实用户体验...')
    
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
            
            # 1. 保存初始数据
            initial_tasks = [
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
                    'title': '作业2', 
                    'deadline': '2025-10-02 23:59:00',
                    'details': '完成第二章习题',
                    'url': 'http://example.com/2',
                    'type': 'homework'
                }
            ]
            
            course_manager.save_user_course_data(test_user_id, initial_tasks)
            print('📝 保存初始数据完成')
            
            # 2. 用户看到的初始数据
            user_data_before = course_manager.get_user_course_data(test_user_id)
            print(f'👀 用户初始看到 {len(user_data_before)} 个任务:')
            for task in user_data_before:
                print(f'   - {task["subject"]}: {task["title"]}')
            
            # 3. 用户软删除物理作业
            physics_task = next((t for t in user_data_before if t['subject'] == '物理'), None)
            if physics_task:
                physics_task_id = physics_task['task_id']
                status_manager.mark_deleted(test_user_id, physics_task_id, '物理作业2', '物理')
                print(f'🗑️ 用户软删除了: {physics_task["subject"]}: {physics_task["title"]}')
            
            # 4. 用户看到的数据（软删除后）
            user_data_after_delete = course_manager.get_user_course_data(test_user_id)
            print(f'👀 软删除后用户看到 {len(user_data_after_delete)} 个任务:')
            for task in user_data_after_delete:
                print(f'   - {task["subject"]}: {task["title"]}')
            
            # 5. 系统数据更新（物理作业仍然存在）
            updated_tasks = [
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
                    'title': '作业2',  # 这个任务重新出现了！
                    'deadline': '2025-10-02 23:59:00',
                    'details': '完成第二章习题',
                    'url': 'http://example.com/2',
                    'type': 'homework'
                },
                {
                    'subject': '英语',
                    'title': '作业3',
                    'deadline': '2025-10-04 23:59:00',
                    'details': '完成第三章习题',
                    'url': 'http://example.com/4',
                    'type': 'homework'
                }
            ]
            
            print('\\n🔄 系统执行数据更新...')
            course_manager.save_user_course_data(test_user_id, updated_tasks)
            
            # 6. 关键测试：用户看到的最终数据
            user_data_final = course_manager.get_user_course_data(test_user_id)
            print(f'\\n👀 数据更新后用户看到 {len(user_data_final)} 个任务:')
            for task in user_data_final:
                print(f'   - {task["subject"]}: {task["title"]}')
            
            # 7. 验证结果
            physics_visible = any(t['subject'] == '物理' for t in user_data_final)
            
            if physics_visible:
                print('\\n❌ 测试失败：物理作业2重新出现了！用户的删除操作被忽略了')
                print('   问题：软删除状态虽然保存了，但在获取数据时没有被过滤')
            else:
                print('\\n✅ 测试成功：物理作业2没有出现，用户的删除操作得到了保护')
            
            # 8. 检查软删除状态
            deleted_ids = status_manager.get_deleted_assignment_ids(test_user_id)
            print(f'🔍 当前软删除列表: {deleted_ids}')
            
            # 清理测试数据
            course_manager.clear_user_data(test_user_id)
            status_manager.clear_user_status(test_user_id)
            print('🧹 清理测试数据完成')
            
            return not physics_visible
            
        except Exception as e:
            print(f'❌ 测试失败: {e}')
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_real_user_experience()
    if success:
        print('\\n🎉 真实场景测试通过！')
    else:
        print('\\n💥 真实场景测试失败，需要修复过滤逻辑！')
    sys.exit(0 if success else 1)