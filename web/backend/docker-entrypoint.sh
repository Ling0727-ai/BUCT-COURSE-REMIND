#!/bin/bash

# Docker容器启动脚本

set -e

echo "======================================"
echo "作业管理系统启动中..."
echo "======================================"

# 创建必要的目录
mkdir -p /app/data
mkdir -p /app/logs

# 设置权限
chmod 755 /app/data
chmod 755 /app/logs

# 等待数据库（如果使用外部数据库）
if [ ! -z "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgres* ]]; then
    echo "等待PostgreSQL数据库启动..."
    
    # 提取数据库连接信息
    DB_HOST=$(echo $DATABASE_URL | sed 's/.*@\([^:]*\).*/\1/')
    DB_PORT=$(echo $DATABASE_URL | sed 's/.*:\([0-9]*\).*/\1/')
    
    # 等待数据库可用
    for i in {30..0}; do
        if nc -z "$DB_HOST" "$DB_PORT" &> /dev/null; then
            echo "PostgreSQL数据库已就绪!"
            break
        fi
        echo "等待PostgreSQL数据库... ($i)"
        sleep 2
    done
    
    if [ "$i" = 0 ]; then
        echo "错误: PostgreSQL数据库未能及时启动"
        exit 1
    fi
fi

# 数据库初始化已移至主应用(main.py)的启动流程中，此处不再执行。

# 检查scraper.py文件
if [ -f "/app/scraper.py" ]; then
    echo "发现抓取脚本: scraper.py"
    chmod +x /app/scraper.py
else
    echo "警告: 未找到抓取脚本 scraper.py，将使用示例脚本"
fi

# 设置日志
export PYTHONUNBUFFERED=1

echo "======================================"
echo "系统启动完成!"
echo "应用端口: 5000"
echo "默认账户: admin/admin123"
echo "======================================"

# 执行传入的命令
exec "$@"