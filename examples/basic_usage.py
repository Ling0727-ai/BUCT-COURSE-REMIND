#!/usr/bin/env python3
"""
基本使用示例
演示如何使用buct-course库进行登录和基本操作
"""

from buct_course import BUCTAuth, CourseUtils, TestUtils

def demonstrate_basic_usage():
    """演示基本使用"""
    print("=== BUCT Course API 基本使用示例 ===\n")
    
    # 1. 创建认证实例
    auth = BUCTAuth()
    print("1. 创建认证实例成功")
    
    # 2. 登录（这里使用模拟数据，实际使用时需要真实凭据）
    username = input("请输入用户名: ") or "test_user"
    password = input("请输入密码: ") or "test_pass"
    
    try:
        if auth.login(username, password):
            print("2. 登录成功")
            session = auth.get_session()
            
            # 3. 使用课程工具
            course_utils = CourseUtils(session)
            print("3. 课程工具初始化成功")
            
            # 4. 使用测试工具
            test_utils = TestUtils(session)
            print("4. 测试工具初始化成功")
            
            print("\n=== 功能就绪 ===")
            print("现在可以使用以下功能:")
            print("- course_utils.get_pending_tasks() - 获取待办任务")
            print("- test_utils.get_test_categories() - 获取测试分类")
            print("- test_utils.get_available_tests(cate_id) - 获取可用测试")
            
        else:
            print("2. 登录失败 - 请检查用户名和密码")
            
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    demonstrate_basic_usage()