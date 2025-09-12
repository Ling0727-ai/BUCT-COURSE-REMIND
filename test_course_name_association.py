#!/usr/bin/env python3
"""
测试课程名称关联功能
"""

from buct_course import TestUtils
import json

# 创建测试实例
test_utils = TestUtils(None, "高等数学")

print("=== 测试课程名称关联功能 ===\n")

# 测试1: 生成包含课程名称的测试链接
print("1. 测试生成包含课程名称的链接:")
link_info = test_utils.generate_test_link("34060", "线性代数")
print(json.dumps(link_info, indent=2, ensure_ascii=False))
print()

# 测试2: 测试默认课程名称
print("2. 测试默认课程名称:")
link_info_default = test_utils.generate_test_link("34061")
print(json.dumps(link_info_default, indent=2, ensure_ascii=False))
print()

# 测试3: 模拟测试数据包含课程名称
print("3. 模拟测试数据包含课程名称:")
test_data = {
    "title": "单元测试1",
    "date": "2024-03-15",
    "deadline": "2024-03-20",
    "status_text": "未开始",
    "type": "平时测验",
    "state": 1,
    "test_id": "12345",
    "can_take_test": True,
    "cate_id": "34060",
    "course_name": "高等数学",
    "order": 0,
    "class_name": "classicLook0"
}
print(json.dumps(test_data, indent=2, ensure_ascii=False))
print()

# 测试4: 展示不同课程的测试链接
print("4. 不同课程的测试链接示例:")
courses_and_categories = [
    ("高等数学", "34060"),
    ("线性代数", "34061"),
    ("概率论", "34062"),
    ("大学物理", "34063")
]

for course_name, cate_id in courses_and_categories:
    link_info = test_utils.generate_test_link(cate_id, course_name)
    print(f"课程: {course_name}")
    print(f"分类ID: {cate_id}")
    print(f"链接: {link_info['url'][:80]}...")
    print()

print("=== 测试完成 ===")