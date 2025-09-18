#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUCT课程提醒系统 - 启动脚本
"""

import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app import create_app
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """主函数"""
    app = create_app()
    
    print("=" * 50)
    print("BUCT课程提醒系统启动中...")
    print("访问地址: http://localhost:5000")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

if __name__ == '__main__':
    main()