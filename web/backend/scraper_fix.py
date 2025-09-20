# -*- coding: utf-8 -*-
"""
临时修复scraper.py中缺失的函数
"""

def get_enhanced_details(user_id=None):
    """获取增强格式的课程详情 - 临时实现"""
    try:
        # 返回模拟数据，避免500错误
        return {
            'assignments': [],
            'tests': [],
            'statistics': {
                'total_courses': 0,
                'pending_assignments': 0,
                'pending_tests': 0,
                'available_tests': 0
            },
            'query_time': '2024-01-01T00:00:00Z',
            'standard_format': []
        }
    except Exception as e:
        print(f"获取增强详情失败: {str(e)}")
        return None

def get_standard_format_details(user_id=None):
    """获取标准格式的课程详情 - 临时实现"""
    try:
        # 返回模拟数据，避免500错误
        return []
    except Exception as e:
        print(f"获取标准格式详情失败: {str(e)}")
        return []