#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
软删除保护机制测试脚本
验证数据更新时软删除状态的保护逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from bson import ObjectId

def test_soft_delete_protection():
    """测试软删除保护机制"""
    print('🧪 测试软删除保护机制...')
    
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
            
            # 1. 模拟初始数据
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
                },
                {
                    'subject': '化学',
                    'title': '测试1',
                    'deadline': '2025-10-03 23:59:00',
                    'details': '',
                    'url': 'http://example.com/3',
                    'type': 'test'
                }
            ]
            
            # 保存初始数据
            count1 = course_manager.save_user_course_data(test_user_id, initial_tasks)
            print(f'📝 保存初始数据: {count1} 条')
            
            # 获取生成的task_id
            saved_tasks = course_manager.get_user_course_data(test_user_id)
            task_ids = [task['task_id'] for task in saved_tasks]
            print(f'🆔 生成的task_id: {task_ids}')
            
            # 2. 软删除其中一个任务
            deleted_task_id = task_ids[1]  # 删除物理作业
            status_manager.mark_deleted(test_user_id, deleted_task_id, '物理作业2', '物理')
            print(f'🗑️ 软删除任务: {deleted_task_id}')
            
            # 验证软删除状态
            deleted_ids = status_manager.get_deleted_assignment_ids(test_user_id)
            print(f'✅ 当前软删除列表: {deleted_ids}')
            
            # 3. 模拟数据更新 - 删除的任务仍然存在
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
                    'title': '作业2',  # 这个任务仍然存在
                    'deadline': '2025-10-02 23:59:00',
                    'details': '完成第二章习题',
                    'url': 'http://example.com/2',
                    'type': 'homework'
                },
                {
                    'subject': '英语',  # 新增任务
                    'title': '作业3',
                    'deadline': '2025-10-04 23:59:00',
                    'details': '完成第三章习题',
                    'url': 'http://example.com/4',
                    'type': 'homework'
                }
                # 化学测试1 不再存在
            ]
            
            print('\n🔄 执行数据更新...')
            count2 = course_manager.save_user_course_data(test_user_id, updated_tasks)
            print(f'📝 更新后数据: {count2} 条')
            
            # 4. 验证软删除保护机制
            deleted_ids_after = status_manager.get_deleted_assignment_ids(test_user_id)
            print(f'🔍 更新后软删除列表: {deleted_ids_after}')
            
            # 验证结果
            if deleted_task_id in deleted_ids_after:
                print('✅ 软删除状态保护成功：物理作业2仍保持软删除状态')
            else:
                print('❌ 软删除状态保护失败：物理作业2的软删除状态丢失')
            
            # 检查化学测试是否被永久删除
            all_deleted_ids = status_manager.get_deleted_assignment_ids(test_user_id)
            chemistry_task_exists = any('化学' in str(task_id) for task_id in all_deleted_ids)
            
            if not chemistry_task_exists:
                print('✅ 永久删除机制正常：化学测试1已被永久删除')
            else:
                print('❌ 永久删除机制异常：化学测试1仍在软删除列表中')
            
            # 5. 清理测试数据
            course_manager.clear_user_data(test_user_id)
            status_manager.clear_user_status(test_user_id)
            print('🧹 清理测试数据完成')
            
            print('\n🎉 软删除保护机制测试完成！')
            return True
            
        except Exception as e:
            print(f'❌ 测试失败: {e}')
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_soft_delete_protection()
    sys.exit(0 if success else 1)