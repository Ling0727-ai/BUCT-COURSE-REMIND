#!/bin/bash

echo "🔧 修复API调用并重新部署"
echo "================================"

# 停止现有服务
echo "1. 停止现有服务..."
docker-compose down

# 重新构建前端（因为修改了API调用）
echo "2. 重新构建前端..."
docker-compose build frontend

# 重新启动所有服务
echo "3. 启动所有服务..."
docker-compose up -d

# 等待服务启动
echo "4. 等待服务启动..."
sleep 15

# 检查服务状态
echo "5. 检查服务状态..."
docker-compose ps

# 测试后端健康检查
echo "6. 测试后端连接..."
curl -f http://localhost:5000/api/health || echo "后端健康检查失败"

echo ""
echo "🎉 修复完成！"
echo "================================"
echo "📱 前端页面: http://localhost:3000"
echo "🔧 后端API: http://localhost:5000"
echo "📝 注册页面: http://localhost:3000/register"
echo ""
echo "现在可以测试验证码功能了！"