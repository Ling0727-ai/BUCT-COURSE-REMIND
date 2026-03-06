#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUCT课程提醒系统 - 主应用入口
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
import logging
from logging.handlers import RotatingFileHandler

# 确保logs目录存在
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 配置日志 - 同时输出到文件和控制台
log_file = os.path.join(log_dir, 'app.log')
file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

# 专门为邮件和调度器设置DEBUG级别日志
logging.getLogger('app.notification_services').setLevel(logging.DEBUG)
logging.getLogger('app.scheduler').setLevel(logging.DEBUG)

app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
