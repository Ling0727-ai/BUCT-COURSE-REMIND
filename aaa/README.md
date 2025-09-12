# 作业管理系统 - 部署指南

## 🚀 快速部署

### 1. 准备工作

确保你的服务器已安装：
- Docker (≥ 20.0)
- Docker Compose (≥ 2.0)

```bash
# 检查版本
docker --version
docker-compose --version
```

### 2. 项目文件结构

创建项目目录并放置以下文件：

```
assignment-manager/
├── app.py                 # Flask主应用
├── db_interface.py        # 数据库接口
├── scraper.py            # 你的抓取脚本
├── requirements.txt       # Python依赖
├── Dockerfile            # Docker构建文件
├── docker-compose.yml    # Docker编排文件
├── docker-entrypoint.sh  # 容器启动脚本
├── nginx.conf           # Nginx配置
├── data/                # 数据持久化目录
├── logs/                # 日志目录
└── frontend/            # 前端静态文件
    ├── index.html
    └── settings.html
```

### 3. 替换你的抓取脚本

将 `scraper.py` 替换为你自己的抓取脚本，确保：

1. **导入数据库接口**：
```python
from db_interface import save_assignment, save_test
```

2. **使用正确的保存函数**：
```python
# 保存作业
save_assignment(
    subject="数字电子技术",
    title="第一次作业", 
    due_date_str="2025年9月21日 23:59:00",
    publisher="李香玲",
    content="作业内容描述"
)

# 保存测试
save_test(
    title="期中考试",
    start_time_str="2025年9月22日 14:00:00",
    end_time_str="2025年9月22日 16:00:00",
    allowed_attempts=1,
    time_limit=120
)
```

### 4. 启动服务

```bash
# 克隆或创建项目目录
mkdir assignment-manager
cd assignment-manager

# 放置所有文件后，启动服务
docker-compose up -d
```

### 5. 访问系统

- **前端界面**: http://your-server:80
- **API接口**: http://your-server:80/api
- **默认账户**: admin / admin123

## ⚙️ 配置说明

### 环境变量

在 `docker-compose.yml` 中可以配置：

```yaml
environment:
  - SECRET_KEY=your-secret-key-change-this
  - DATABASE_URL=sqlite:///data/assignments.db
  - FLASK_ENV=production
  - PORT=5000
```

### 数据库配置

**SQLite (默认)**:
```yaml
environment:
  - DATABASE_URL=sqlite:///data/assignments.db
```

**PostgreSQL (推荐生产环境)**:
```yaml
environment:
  - DATABASE_URL=postgresql://user:password@postgres:5432/assignments
```

### 抓取频率设置

通过前端设置页面可以配置：
- 默认60分钟执行一次
- 可在运行时动态调整
- 支持立即手动刷新

## 🔧 API接口文档

### 认证相关

```bash
# 登录
POST /api/auth/login
{
    "username": "admin",
    "password": "admin123"
}

# 登出
POST /api/auth/logout

# 检查登录状态
GET /api/auth/status
```

### 作业相关

```bash
# 获取作业列表
GET /api/assignments

# 手动刷新数据
POST /api/assignments/refresh
```

### 设置相关

```bash
# 获取设置
GET /api/settings

# 保存设置
POST /api/settings
{
    "username": "your_username",
    "password": "your_password",
    "serverUrl": "http://localhost:5000",
    "scrape_interval": "30",
    "webhooks": [...]
}

# 测试Webhook
POST /api/webhook/test
{
    "webhook": {
        "type": "telegram",
        "config": {...}
    }
}
```

### 系统监控

```bash
# 健康检查
GET /api/health

# 统计信息
GET /api/stats
```

## 📝 Webhook配置示例

### 邮件通知
```json
{
    "type": "email",
    "enabled": true,
    "config": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": "587",
        "email": "your@gmail.com",
        "password": "your_app_password",
        "to_email": "recipient@gmail.com"
    }
}
```

### Telegram机器人
```json
{
    "type": "telegram",
    "enabled": true,
    "config": {
        "bot_token": "your_bot_token",
        "chat_id": "your_chat_id"
    }
}
```

### 自定义Webhook
```json
{
    "type": "webhook",
    "enabled": true,
    "config": {
        "url": "https://your-webhook-url.com",
        "method": "POST",
        "headers": "{\"Content-Type\": \"application/json\"}",
        "template": "{\"text\": \"{{message}}\"}"
    }
}
```

## 🛠️ 维护操作

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f assignment-manager
docker-compose logs -f nginx
```

### 备份数据
```bash
# 备份SQLite数据库
docker-compose exec assignment-manager cp /app/data/assignments.db /app/data/assignments_backup.db

# 或直接复制宿主机文件
cp ./data/assignments.db ./data/assignments_backup_$(date +%Y%m%d).db
```

### 更新系统
```bash
# 停止服务
docker-compose down

# 重新构建
docker-compose build --no-cache

# 启动服务
docker-compose up -d
```

### 重置系统
```bash
# 完全重置（会删除所有数据）
docker-compose down -v
rm -rf data/*
docker-compose up -d
```

## 🔒 安全建议

1. **修改默认密码**: 首次登录后立即修改admin密码
2. **设置强密钥**: 更改 `SECRET_KEY` 环境变量
3. **启用HTTPS**: 配置SSL证书，取消nginx.conf中的HTTPS注释
4. **防火墙设置**: 只开放必要端口（80, 443）
5. **定期备份**: 设置定时备份数据库任务