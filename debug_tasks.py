#!/usr/bin/env python3
"""
调试任务数据结构
"""

from buct_course import BUCTAuth, CourseUtils

# 配置您的登录信息
USERNAME = "***REMOVED***"
PASSWORD = "***REMOVED***"

def debug_tasks():
    """调试任务数据结构"""
    print("调试任务数据结构...")
    
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
            
            print(f"任务获取成功: {tasks['success']}")
            print(f"任务数据结构: {list(tasks.keys())}")
            
            if 'data' in tasks:
                print(f"data 结构: {list(tasks['data'].keys())}")
                
                if 'homework' in tasks['data']:
                    print(f"作业数量: {len(tasks['data']['homework'])}")
                    print(f"作业内容: {[hw['course_name'] for hw in tasks['data']['homework']]}")
                
                if 'tests' in tasks['data']:
                    print(f"测试数量: {len(tasks['data']['tests'])}")
                    print(f"测试内容: {[test['course_name'] for test in tasks['data']['tests']]}")
                
                if 'stats' in tasks['data']:
                    print(f"统计信息: {tasks['data']['stats']}")
                else:
                    print("没有 stats 信息")
            
        else:
            print("登录失败!")
            
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_tasks()