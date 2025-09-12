#!/usr/bin/env python3
"""
北化课程提醒系统 - 简化版本（无表情符号）
"""

from buct_course import BUCTAuth, CourseUtils, TestUtils
import datetime

# 配置您的登录信息
USERNAME = "***REMOVED***"
PASSWORD = "***REMOVED***"

def display_welcome():
    """显示欢迎信息"""
    print("北化课程提醒系统")
    print("=" * 60)
    print(f"启动时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def display_tasks(tasks, session):
    """显示待办任务"""
    if tasks["success"]:
        print("待办任务统计:")
        print("-" * 40)
        print(f"作业数量: {tasks['data']['stats']['homework_count']}")
        print(f"测试数量: {tasks['data']['stats']['tests_count']}")
        print(f"总计: {tasks['data']['stats']['total_count']}")
        print("-" * 40)

        # 显示作业详情
        if tasks['data']['homework']:
            print("\n待提交作业:")
            for i, hw in enumerate(tasks['data']['homework'], 1):
                print(f"   {i}. {hw['course_name']}")
                print(f"      课程ID: {hw['lid']}")
                # 使用统一的作业链接格式
                homework_link = f"https://course.buct.edu.cn/meol/jpk/course/layout/newpage/index.jsp?courseId={hw['lid']}"
                print(f"      作业链接: {homework_link}")
                print()
        else:
            print("\n暂无待提交作业")

        # 显示测试详情
        if tasks['data']['tests']:
            print("待提交测试:")
            for i, test in enumerate(tasks['data']['tests'], 1):
                print(f"   {i}. {test['course_name']}")
                print(f"      课程ID: {test['lid']}")

                # 获取该课程的测试详细信息
                try:
                    test_utils = TestUtils(session, test['course_name'])
                    test_result = test_utils.get_tests_by_category(test['lid'], test['course_name'])

                    if test_result["success"] and test_result["data"]["tests"]:
                        available_tests = [t for t in test_result["data"]["tests"] if t.get("can_take_test")]
                        if available_tests:
                            print(f"      可进行测试: {len(available_tests)} 个")
                            for test_info in available_tests[:3]:  # 只显示前3个
                                print(f"          测试: {test_info.get('title', '未命名测试')}")
                                if test_info.get('deadline'):
                                    print(f"          截止: {test_info['deadline']}")
                        else:
                            print("      无可用测试")
                except Exception as e:
                    print(f"      测试详情获取失败: {str(e)[:50]}...")

                # 显示测试链接
                test_link = f"https://course.buct.edu.cn/meol/common/question/test/student/list.jsp?sortColumn=createTime&status=1&tagbug=client&sortDirection=-1&strStyle=lesson19&cateId={test['lid']}&pagingPage=1&pagingNumberPer=7"
                print(f"      测试列表: {test_link}")
                print()
        else:
            print("\n暂无待提交测试")
    else:
        print("获取任务失败")


def display_test_details(test_utils, cate_id="34060", course_name="默认课程"):
    """显示测试详细信息"""
    try:
        print("\n" + "=" * 60)
        print(f"测试详细信息 - {course_name}:")

        result = test_utils.get_tests_by_category(cate_id, course_name)

        if result["success"]:
            print(f"测试统计: 总共 {result['data']['stats']['total_tests']} 个测试")
            print(f"可进行: {result['data']['stats']['available_tests']} 个")
            print(f"已完成: {result['data']['stats']['completed_tests']} 个")

            # 显示测试链接信息
            test_link_info = test_utils.generate_test_link(cate_id, course_name)
            print(f"\n测试链接信息:")
            print(f"  课程: {test_link_info['course_name']}")
            print(f"  分类ID: {test_link_info['cate_id']}")
            print(f"  链接: {test_link_info['url']}...")
            print("-" * 40)

            if result['data']['tests']:
                for test in result['data']['tests']:
                    status = "可进行" if test.get('can_take_test') else "不可进行"
                    course_info = f" ({test.get('course_name', '未知课程')})" if test.get('course_name') else ""
                    print(f"{status} - {test.get('title', '无标题')}{course_info}")
                    if test.get('date'):
                        print(f"   创建日期: {test['date']}")
                    if test.get('deadline'):
                        print(f"   截止时间: {test['deadline']}")
                    if test.get('status_text'):
                        print(f"   状态: {test['status_text']}")
                    if test.get('test_id'):
                        print(f"   测试ID: {test['test_id']}")
                    print()
            else:
                print("暂无测试信息")
        else:
            print("获取测试信息失败")

    except Exception as e:
        print(f"获取测试信息时出错: {e}")


def main():
    display_welcome()

    try:
        # 初始化认证
        auth = BUCTAuth()

        # 登录
        if auth.login(USERNAME, PASSWORD):
            print("登录成功!")
            print()

            # 获取session
            session = auth.get_session()

            # 获取待办任务
            course_utils = CourseUtils(session)
            tasks = course_utils.get_pending_tasks()

            display_tasks(tasks, session)

            print("=" * 60)
            print("任务完成!")
            print(f"完成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        else:
            print("登录失败! 请检查用户名和密码")

    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()