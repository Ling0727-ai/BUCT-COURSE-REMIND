#!/usr/bin/env python3
"""
快速开始示例
使用便捷函数快速操作
"""

from buct_course import get_pending_tasks, get_test_categories

def quick_demo():
    """快速演示"""
    print("=== 快速开始示例 ===\n")
    
    print("这些便捷函数可以快速使用:")
    print("1. get_pending_tasks(username, password) - 获取待办任务")
    print("2. get_test_categories(username, password) - 获取测试分类")
    print("3. get_available_tests(username, password, cate_id) - 获取可用测试")
    print("4. take_test(username, password, test_id) - 开始测试")
    
    print("\n示例用法:")
    print("```python")
    print("from buct_course import get_pending_tasks")
    print("tasks = get_pending_tasks('your_username', 'your_password')")
    print("print(f'待办任务: {tasks}')")
    print("```")

if __name__ == "__main__":
    quick_demo()