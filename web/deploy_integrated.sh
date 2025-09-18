#!/bin/bash

# BUCT课程提醒系统 - 集成版部署脚本

echo "🚀 开始部署BUCT课程提醒系统（集成增强版爬虫）..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p backend/logs
mkdir -p ssl

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "⚠️ 未找到.env文件，复制默认配置..."
    if [ -f ".env.production" ]; then
        cp .env.production .env
    else
        echo "❌ 未找到.env.production文件，请先配置环境变量"
        exit 1
    fi
fi

# 运行集成测试
echo "🧪 运行集成测试..."
cd backend
python test_docker_integration.py
if [ $? -ne 0 ]; then
    echo "❌ 集成测试失败，请检查配置"
    exit 1
fi
cd ..

# 构建并启动服务
echo "📦 构建Docker镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 15

# 检查服务状态
echo "🔍 检查服务状态..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ 部署成功!"
    echo ""
    echo "📊 服务状态:"
    docker-compose ps
    echo ""
    echo "🌐 访问地址:"
    echo "前端应用: http://localhost:3000"
    echo "后端API: http://localhost:5000"
    echo "健康检查: http://localhost:5000/api/health"
    echo "MongoDB: localhost:27017"
    echo ""
    echo "🔧 新增API端点:"
    echo "标准格式数据: http://localhost:5000/api/assignments/standard"
    echo "详细课程信息: http://localhost:5000/api/assignments/detailed"
    echo "刷新数据: POST http://localhost:5000/api/assignments/refresh"
    echo ""
    echo "🎯 集成功能:"
    echo "✅ 增强版爬虫已集成到后端API"
    echo "✅ 支持实时数据查询"
    echo "✅ 支持标准JSON格式输出"
    echo "✅ 支持详细统计信息"
else
    echo "❌ 服务启动失败，请检查日志"
    docker-compose logs
    exit 1
fi