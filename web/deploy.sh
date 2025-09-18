#!/bin/bash

# BUCT课程提醒系统 - Docker部署脚本

set -e

echo "======================================"
echo "🚀 BUCT课程提醒系统 Docker部署"
echo "======================================"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

echo "✅ Docker环境检查通过"

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️ .env文件不存在，创建默认配置..."
    cp .env.example .env 2>/dev/null || echo "请手动创建.env文件"
fi

# 检查邮件配置
if grep -q "your_email_auth_code_here" .env; then
    echo "⚠️ 请在.env文件中配置真实的邮箱信息："
    echo "   MAIL_SENDER=your_email@163.com"
    echo "   MAIL_PASSWORD=your_email_auth_code"
    echo ""
    read -p "是否继续部署？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📋 当前配置："
echo "   MongoDB用户: $(grep MONGO_INITDB_ROOT_USERNAME .env | cut -d'=' -f2)"
echo "   前端端口: $(grep FRONTEND_PORT .env | cut -d'=' -f2)"
echo "   后端端口: $(grep FLASK_PORT .env | cut -d'=' -f2)"
echo "   邮件服务器: $(grep MAIL_SMTP_SERVER .env | cut -d'=' -f2)"

echo ""
echo "🔨 开始部署..."

# 停止现有服务
echo "停止现有服务..."
docker-compose down 2>/dev/null || true

# 构建并启动服务
echo "构建并启动服务..."
docker-compose up -d --build

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态："
docker-compose ps

# 健康检查
echo ""
echo "🏥 健康检查："
for i in {1..30}; do
    if curl -f http://localhost:5000/api/health &>/dev/null; then
        echo "✅ 后端服务健康检查通过"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ 后端服务健康检查失败"
        echo "查看日志: docker-compose logs backend"
    else
        echo "等待后端服务启动... ($i/30)"
        sleep 2
    fi
done

# 显示访问信息
echo ""
echo "======================================"
echo "🎉 部署完成！"
echo "======================================"
echo "📱 前端页面: http://localhost:$(grep FRONTEND_PORT .env | cut -d'=' -f2)"
echo "🔧 后端API: http://localhost:$(grep FLASK_PORT .env | cut -d'=' -f2)"
echo "📝 注册页面: http://localhost:$(grep FRONTEND_PORT .env | cut -d'=' -f2)/register"
echo "🏥 健康检查: http://localhost:$(grep FLASK_PORT .env | cut -d'=' -f2)/api/health"
echo ""
echo "📋 管理命令："
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo ""
echo "🧪 验证码功能测试："
echo "   1. 访问注册页面"
echo "   2. 填写邮箱地址"
echo "   3. 点击获取验证码"
echo "   4. 检查邮箱收到验证码"
echo "======================================"