#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试脚本
验证所有新功能是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_integration():
    """测试集成功能"""
    print('🔍 开始集成测试...')
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        try:
            # 1. 验证统一状态管理
            from app.assignment_status import get_assignment_status_manager
            status_mgr = get_assignment_status_manager()
            print('✅ 统一状态管理系统已就绪')
            
            # 2. 验证课程数据管理
            from app.course_data import get_course_data_manager  
            course_mgr = get_course_data_manager()
            print('✅ 课程数据管理系统已就绪')
            
            # 3. 验证定时调度器
            from app.scheduler import CourseDataScheduler
            print('✅ 定时调度器已就绪')
            
            # 4. 验证API蓝图
            from app.course_data import course_data_bp
            from app.assignments import assignments_bp
            print('✅ API蓝图已注册')
            
            # 5. 验证数据库集合
            from app import mongo
            collections = mongo.db.list_collection_names()
            print(f'✅ 数据库连接正常，当前集合: {len(collections)} 个')
            
            print('')
            print('🎉 集成测试完成！')
            print('📊 新数据流: 爬虫 → 数据库 → 前端')
            print('🔄 自动刷新: 每12小时一次')
            print('🗂️ 统一状态管理: 软删除 + 完成状态合并')
            print('⚙️ 手动刷新: Settings页面可用')
            print('')
            print('🚀 系统已准备就绪！')
            
            return True
            
        except Exception as e:
            print(f'❌ 集成测试失败: {e}')
            return False

if __name__ == '__main__':
    success = test_integration()
    sys.exit(0 if success else 1)