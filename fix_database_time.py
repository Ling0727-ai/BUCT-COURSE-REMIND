#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复数据库中的时间数据
将UTC时间转换为北京时间
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'web', 'backend'))

from pymongo import MongoClient
from datetime import datetime, timedelta
import json

def fix_database_times():
    """修复数据库中的时间数据"""
    
    # 连接MongoDB
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['course_reminder']
        print("✅ 成功连接到MongoDB")
    except Exception as e:
        print(f"❌ 连接MongoDB失败: {e}")
        return
    
    # 修复todos集合中的时间
    todos_collection = db['todos']
    
    print("\n=== 检查待办事项时间数据 ===")
    
    # 查找所有待办事项
    todos = list(todos_collection.find({}))
    print(f"找到 {len(todos)} 个待办事项")
    
    fixed_count = 0
    
    for todo in todos:
        print(f"\n处理待办: {todo.get('title', 'Unknown')}")
        
        update_fields = {}
        
        # 检查并修复各个时间字段
        time_fields = ['created_at', 'updated_at', 'due_date', 'completed_at']
        
        for field in time_fields:
            if field in todo and todo[field]:
                old_time = todo[field]
                print(f"  {field}: {old_time}")
                
                # 如果时间看起来像UTC时间（比当前北京时间小8小时左右）
                if isinstance(old_time, datetime):
                    # 假设这是UTC时间，转换为北京时间
                    beijing_time = old_time + timedelta(hours=8)
                    update_fields[field] = beijing_time
                    print(f"    修复为: {beijing_time}")
        
        # 更新数据库
        if update_fields:
            result = todos_collection.update_one(
                {'_id': todo['_id']},
                {'$set': update_fields}
            )
            if result.modified_count > 0:
                fixed_count += 1
                print(f"  ✅ 已更新")
            else:
                print(f"  ⚠️ 更新失败")
        else:
            print(f"  ℹ️ 无需更新")
    
    print(f"\n=== 修复完成 ===")
    print(f"总共修复了 {fixed_count} 个待办事项")
    
    # 显示修复后的数据
    print(f"\n=== 修复后的数据示例 ===")
    sample_todos = list(todos_collection.find({}).limit(3))
    for todo in sample_todos:
        print(f"标题: {todo.get('title')}")
        print(f"创建时间: {todo.get('created_at')}")
        print(f"截止时间: {todo.get('due_date')}")
        print("---")

if __name__ == "__main__":
    print("数据库时间修复工具")
    print("此工具将修复数据库中可能错误的UTC时间，转换为北京时间")
    
    confirm = input("\n是否继续？(y/N): ")
    if confirm.lower() == 'y':
        fix_database_times()
    else:
        print("操作已取消")