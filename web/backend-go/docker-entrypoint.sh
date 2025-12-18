#!/bin/sh
set -e

echo "=========================================="
echo "  BUCT Course Remind - Go Backend"
echo "=========================================="
echo ""

# MongoDB 连接由 docker-compose depends_on 和健康检查保证
# 简单等待几秒确保网络就绪
if [ -n "$MONGO_URI" ]; then
    echo "MongoDB URI configured, waiting 3 seconds for network..."
    sleep 3
fi

echo ""
echo "Starting Go backend server..."
echo "Port: ${PORT:-5000}"
echo ""

# 启动应用
exec ./main
