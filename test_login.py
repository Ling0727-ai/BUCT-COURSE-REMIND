#!/usr/bin/env python3
"""
测试登录功能
"""

from buct_course import BUCTAuth, CourseUtils

# 配置您的登录信息
USERNAME = "***REMOVED***"
PASSWORD = "***REMOVED***"

def test_login():
    """测试登录功能"""
    print("测试登录功能...")
    
    try:
        # 初始化认证
        auth = BUCTAuth()

        # 登录
        if auth.login(USERNAME, PASSWORD):
            print("登录成功!")
            
            # 获取session
            session = auth.get_session()
            
            # 获取待办任务
            course_utils = CourseUtils(session)
            tasks = course_utils.get_pending_tasks()
            
            print(f"任务获取结果: {tasks['success']}")
            if tasks['success']:
                print(f"作业数量: {tasks['data']['stats']['homework_count']}")
                print(f"测试数量: {tasks['data']['stats']['tests_count']}")
                print(f"总计: {tasks['data']['stats']['total_count']}")
                
                if tasks['data']['homework']:
                    print("作业详情:")
                    for hw in tasks['data']['homework']:
                        print(f"  - {hw['course_name']}: lid={hw['lid']}")
                
                if tasks['data']['tests']:
                    print("测试详情:")
                    for test in tasks['data']['tests']:
                        print(f"  - {test['course_name']}: lid={test['lid']}")
            else:
                print(f"获取任务失败: {tasks.get('error', '未知错误')}")
        else:
            print("登录失败!")
            
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login()