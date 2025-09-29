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

### 2. 自动化配置部署

我们提供了自动化配置脚本，让部署更简单：

**Windows系统**:
```powershell
# 运行自动化配置脚本
.\setup.ps1
```

**Linux/Mac系统**:
```bash
# 给脚本添加执行权限
chmod +x setup.sh

# 运行自动化配置脚本
./setup.sh
```

或者手动配置：
```bash
# 复制环境变量模板
cp .env.template .env

# 编辑配置文件
nano .env

# 启动服务
docker-compose up --build
```

### 3. 配置文件说明 (.env)

部署前请编辑 `.env` 文件配置以下参数：

```ini
# MongoDB 配置
MONGO_INITDB_ROOT_USERNAME=admin          # MongoDB root用户名
MONGO_INITDB_ROOT_PASSWORD=admin123       # MongoDB root密码
MONGO_INITDB_DATABASE=assignment_manager  # 数据库名称

# Flask 应用配置
SECRET_KEY=your-secret-key-change-this    # Flask密钥，请修改为强密码
MONGO_URI=mongodb://admin:admin123@mongodb:27017/assignment_manager?authSource=admin

# 端口映射配置
FLASK_PORT=5000          # Flask应用端口
MONGO_PORT=27017         # MongoDB端口
NGINX_HTTP_PORT=80       # Nginx HTTP端口
NGINX_HTTPS_PORT=443     # Nginx HTTPS端口

# 管理员账户配置
ADMIN_USERNAME=admin     # 系统管理员用户名
ADMIN_PASSWORD=admin123  # 系统管理员密码
```

### 4. 项目文件结构

```
assignment-manager/
├── app.py                 # Flask主应用
├── db_interface.py        # 数据库接口 (MongoDB)
├── scraper.py            # 你的抓取脚本
├── requirements.txt       # Python依赖
├── Dockerfile            # Docker构建文件
├── docker-compose.yml    # Docker编排文件
├── .env.template         # 环境变量模板
├── setup.ps1            # Windows自动化部署脚本
├── setup.sh             # Linux/Mac自动化部署脚本
├── nginx.conf           # Nginx配置
├── logs/                # 日志目录
└── frontend/            # 前端静态文件
    ├── index.html
    └── settings.html
```

### 5. 替换你的抓取脚本

将 `scraper.py` 替换为你自己的抓取脚本，确保使用MongoDB接口：

```python
from db_interface import save_assignment, save_test

# 保存作业到MongoDB
save_assignment(
    subject="数字电子技术",
    title="第一次作业", 
    due_date_str="2025年9月21日 23:59:00",
    publisher="李香玲",
    content="作业内容描述"
)

# 保存测试到MongoDB
save_test(
    title="期中考试",
    start_time_str="2025年9月22日 14:00:00",
    end_time_str="2025年9月22日 16:00:00",
    allowed_attempts=1,
    time_limit=120
)
```

### 6. 启动服务

```bash
# 使用自动化配置（推荐）
.\setup.ps1

# 或手动启动
docker-compose up --build
```

### 7. 访问系统

- **前端界面**: http://localhost:80 (或你配置的端口)
- **API接口**: http://localhost:80/api
- **默认账户**: 使用你在 .env 中配置的管理员账户

## ⚙️ 配置说明

### 数据库配置

**MongoDB (默认)**:
- 使用Docker容器运行MongoDB 6.0
- 支持数据持久化存储
- 内置认证和权限管理

### 端口映射配置

通过修改 `.env` 文件可以自定义端口映射：

```ini
FLASK_PORT=5000       # 映射Flask应用到宿主机5000端口
MONGO_PORT=27017      # 映射MongoDB到宿主机27017端口
NGINX_HTTP_PORT=80    # HTTP服务端口
NGINX_HTTPS_PORT=443  # HTTPS服务端口
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
