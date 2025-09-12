#!/usr/bin/env python3
"""
示例使用脚本 - 演示如何使用buct_course库的JSON格式返回
"""

from buct_course import BUCTAuth, CourseUtils, TestUtils
import json

# 配置您的登录信息
USERNAME = "***REMOVED***"
PASSWORD = "***REMOVED***"

def example_course_utils():
    """示例：使用CourseUtils获取待办任务"""
    print("🔍 使用CourseUtils获取待办任务...")
    
    auth = BUCTAuth()
    if auth.login(USERNAME, PASSWORD):
        session = auth.get_session()
        course_utils = CourseUtils(session)
        
        # 获取待办任务（返回JSON格式）
        result = course_utils.get_pending_tasks()
        
        if result["success"]:
            print("✅ 获取成功!")
            print(f"📊 统计信息: {json.dumps(result['data']['stats'], indent=2, ensure_ascii=False)}")
            
            # 打印作业信息
            if result['data']['homework']:
                print("\n📝 待提交作业:")
                for hw in result['data']['homework']:
                    print(f"  课程: {hw['course_name']}")
                    print(f"    ID: {hw['lid']}")
                    print(f"    链接: {hw.get('url', '无')}")
                    print()
            
            # 打印测试信息
            if result['data']['tests']:
                print("📋 待提交测试:")
                for test in result['data']['tests']:
                    print(f"  课程: {test['course_name']}")
                    print(f"    ID: {test['lid']}")
                    print(f"    链接: {test.get('url', '无')}")
                    print()
        else:
            print("❌ 获取失败")
    else:
        print("❌ 登录失败")

def example_test_utils():
    """示例：使用TestUtils获取测试信息"""
    print("\n" + "="*60)
    print("🔍 使用TestUtils获取测试信息...")
    
    auth = BUCTAuth()
    if auth.login(USERNAME, PASSWORD):
        session = auth.get_session()
        test_utils = TestUtils(session)
        
        # 示例分类ID（需要根据实际情况修改）
        cate_id = "34060"
        
        # 获取测试列表（返回JSON格式）
        result = test_utils.get_tests_by_category(cate_id)
        
        if result["success"]:
            print("✅ 获取测试列表成功!")
            print(f"📊 统计信息: {json.dumps(result['data']['stats'], indent=2, ensure_ascii=False)}")
            
            # 打印测试详情
            if result['data']['tests']:
                print("\n🧪 测试列表:")
                for test in result['data']['tests']:
                    status = "✅ 可进行" if test['state'] == 1 else "❌ 不可进行"
                    print(f"  {status} - {test.get('title', '无标题')}")
                    print(f"    创建日期: {test.get('date', '无')}")
                    print(f"    截止时间: {test.get('deadline', '无')}")
                    print(f"    状态文本: {test.get('status_text', '无')}")
                    print(f"    测试类型: {test.get('type', '无')}")
                    print(f"    测试链接: {test.get('test_link', '无')}")
                    print(f"    能否测试: {'是' if test.get('can_take_test', False) else '否'}")
                    print()
        else:
            print("❌ 获取测试列表失败")
    else:
        print("❌ 登录失败")

def example_convenience_functions():
    """示例：使用便捷函数"""
    print("\n" + "="*60)
    print("🔍 使用便捷函数...")
    
    from buct_course import get_pending_tasks, get_tests_by_category
    
    # 使用便捷函数获取待办任务
    result = get_pending_tasks(USERNAME, PASSWORD)
    if result["success"]:
        print("✅ 便捷函数 - 获取待办任务成功!")
        print(f"   作业数量: {result['data']['stats']['homework_count']}")
        print(f"   测试数量: {result['data']['stats']['tests_count']}")
    else:
        print("❌ 便捷函数 - 获取失败")

if __name__ == "__main__":
    print("🚀 buct_course库使用示例")
    print("="*60)
    
    try:
        example_course_utils()
        example_test_utils()
        example_convenience_functions()
        
        print("\n🎉 示例执行完成!")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()