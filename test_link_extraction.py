#!/usr/bin/env python3
"""
测试链接提取功能
"""

from buct_course import BUCTAuth, TestUtils
import json

# 配置您的登录信息
USERNAME = "***REMOVED***"
PASSWORD = "***REMOVED***"

def test_link_extraction():
    """测试链接提取功能"""
    print(">> 测试链接提取功能...")
    
    try:
        auth = BUCTAuth()
        if auth.login(USERNAME, PASSWORD):
            session = auth.get_session()
            test_utils = TestUtils(session)
            
            # 测试分类ID
            cate_id = "34060"
            
            # 获取测试列表
            result = test_utils.get_tests_by_category(cate_id)
            
            if result["success"]:
                print("++ 获取测试列表成功!")
                
                # 分析链接提取结果
                tests_with_links = []
                tests_with_ids = []
                
                for test in result["data"]["tests"]:
                    if test.get("test_link"):
                        tests_with_links.append(test)
                    if test.get("test_id"):
                        tests_with_ids.append(test)
                
                print(f"== 总共 {len(result['data']['tests'])} 个测试")
                print(f"== 有ID的测试: {len(tests_with_ids)}")
                
                # 显示有ID的测试详情
                if tests_with_ids:
                    print("\n== 有ID的测试:")
                    for test in tests_with_ids:
                        print(f"  - {test.get('title', '无标题')}")
                        if test.get('test_id'):
                            print(f"    ID: {test['test_id']}")
                        print()
                
                # 显示原始数据（用于调试）
                print("\n== 原始数据示例:")
                if result["data"]["tests"]:
                    sample_test = result["data"]["tests"][0]
                    print(json.dumps(sample_test, indent=2, ensure_ascii=False))
                
            else:
                print("-- 获取测试列表失败")
                print(f"错误: {result.get('error', '未知错误')}")
        else:
            print("-- 登录失败")
            
    except Exception as e:
        print(f"!! 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_link_extraction()