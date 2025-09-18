# Docker部署指南 - BUCT课程提醒系统

## 快速部署

### 1. 配置邮件服务

编辑 `web/.env` 文件，设置真实的邮箱信息：

```env
# 邮件配置 (必须配置)
MAIL_SMTP_SERVER=smtp.163.com
MAIL_SMTP_PORT=465
MAIL_SENDER=your_email@163.com
MAIL_PASSWORD=your_email_auth_code
```

**重要**：`MAIL_PASSWORD` 应该是邮箱的授权码，不是登录密码。

### 2. 重新部署服务

如果是首次部署：
```bash
cd web
docker-compose up -d --build
```

如果需要重新部署（推荐）：
```bash
cd web
# 停止并删除现有容器和网络
docker-compose down

# 清理数据卷（如果需要全新开始）
docker-compose down -v

# 重新构建并启动
docker-compose up -d --build
```

如果遇到端口占用问题：
```bash
# 停止可能冲突的服务
docker-compose down
# 或者停止本地MongoDB服务
net stop MongoDB

# 然后重新启动
docker-compose up -d --build
```

### 3. 检查服务状态

```bash
# 查看所有服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### 4. 访问应用

- **前端页面**: http://localhost:3000
- **后端API**: http://localhost:5000
- **注册页面**: http://localhost:3000/register
- **健康检查**: http://localhost:5000/api/health

## 验证码功能测试

### 测试步骤

1. 访问注册页面：http://localhost:3000/register
2. 填写用户信息
3. 输入有效邮箱地址
4. 点击"获取验证码"
5. 检查邮箱收到验证码
6. 输入验证码完成注册

### 测试API

```bash
# 发送验证码
curl -X POST http://localhost:5000/api/auth/send-verification-code \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'

# 验证验证码
curl -X POST http://localhost:5000/api/auth/verify-code \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","code":"123456"}'
```

## 服务配置

### MongoDB配置

- **用户名**: REDACTED_MONGO_USER
- **密码**: REDACTED_MONGO_PASSWORD
- **数据库**: buct-course
- **端口**: 27017

### 邮件服务配置

支持的邮件服务商：
- 163邮箱 (默认)
- QQ邮箱
- Gmail
- 其他SMTP服务

### 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| MONGO_INITDB_ROOT_USERNAME | MongoDB用户名 | REDACTED_MONGO_USER |
| MONGO_INITDB_ROOT_PASSWORD | MongoDB密码 | REDACTED_MONGO_PASSWORD |
| MAIL_SMTP_SERVER | SMTP服务器 | smtp.163.com |
| MAIL_SMTP_PORT | SMTP端口 | 465 |
| MAIL_SENDER | 发件邮箱 | 需要配置 |
| MAIL_PASSWORD | 邮箱授权码 | 需要配置 |
| VERIFY_CODE_EXPIRE | 验证码有效期(秒) | 180 |

## 常见问题

### 1. 验证码发送失败

**原因**：邮箱配置不正确

**解决方案**：
1. 检查 `.env` 文件中的邮箱配置
2. 确认使用的是授权码而不是登录密码
3. 检查SMTP服务器和端口设置

### 2. MongoDB连接失败

**原因**：数据库未启动或认证失败

**解决方案**：
```bash
# 重启MongoDB服务
docker-compose restart mongodb

# 查看MongoDB日志
docker-compose logs mongodb
```

### 3. 前端无法访问后端

**原因**：网络配置问题

**解决方案**：
```bash
# 检查网络连接
docker network ls
docker network inspect web_assignment-network
```

### 4. 健康检查失败

**原因**：服务未完全启动

**解决方案**：
```bash
# 检查健康状态
curl http://localhost:5000/api/health

# 重启后端服务
docker-compose restart backend
```

## 维护命令

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 更新服务

```bash
# 重新构建并启动
docker-compose up -d --build

# 仅重新构建后端
docker-compose build backend
docker-compose up -d backend
```

### 查看资源使用

```bash
# 查看容器资源使用情况
docker stats

# 查看磁盘使用
docker system df
```

### 备份数据

```bash
# 备份MongoDB数据
docker exec web_mongodb_1 mongodump --out /backup
docker cp web_mongodb_1:/backup ./mongodb_backup
```

## 生产环境部署

### 1. 安全配置

- 修改默认密码
- 使用HTTPS
- 配置防火墙
- 启用日志监控

### 2. 性能优化

- 配置资源限制
- 启用缓存
- 优化数据库索引
- 配置负载均衡

### 3. 监控配置

- 配置健康检查
- 设置告警规则
- 启用日志收集
- 配置性能监控

## 故障排除

### 查看详细日志

```bash
# 实时查看所有日志
docker-compose logs -f --tail=100

# 查看错误日志
docker-compose logs | grep -i error

# 导出日志到文件
docker-compose logs > deployment.log
```

### 进入容器调试

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入MongoDB容器
docker-compose exec mongodb mongo

# 进入前端容器
docker-compose exec frontend sh
```

### 重置环境

```bash
# 完全重置（删除所有数据）
docker-compose down -v
docker system prune -f
docker-compose up -d --build
```

---

## 技术支持

如果遇到问题，请：

1. 查看日志文件
2. 检查配置文件
3. 参考常见问题解决方案
4. 提供详细的错误信息