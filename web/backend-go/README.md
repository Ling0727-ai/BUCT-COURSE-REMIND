# BUCT课程提醒系统 - Go后端

这是BUCT课程提醒系统的Go语言重构版本后端，使用Gin框架构建，集成了北化课程平台的爬虫功能。

## 技术栈

- **Go 1.21+** - 编程语言
- **Gin** - Web框架
- **MongoDB** - 数据库
- **gin-contrib/sessions** - Session管理
- **gin-contrib/cors** - CORS处理
- **goquery** - HTML解析（用于爬虫）

## 项目结构

```
backend-go/
├── main.go                    # 应用入口
├── go.mod                     # Go模块定义
├── Dockerfile                 # Docker构建文件
├── .env.example               # 环境变量示例
├── docker-entrypoint.sh       # Docker入口脚本
└── internal/
    ├── config/
    │   └── config.go          # 配置管理
    ├── crypto/
    │   └── crypto.go          # RSA/ECC加密工具
    ├── database/
    │   └── mongo.go           # MongoDB连接
    ├── handlers/
    │   ├── auth.go            # 认证处理
    │   ├── assignments.go     # 作业处理
    │   ├── todos.go           # 待办事项处理
    │   ├── reminders.go       # 提醒处理
    │   ├── settings.go        # 设置处理
    │   ├── health.go          # 健康检查
    │   ├── admin.go           # 管理员功能
    │   └── crypto.go          # 加密API
    ├── middleware/
    │   └── auth.go            # 认证中间件
    ├── models/
    │   ├── user.go            # 用户模型
    │   ├── assignment.go      # 作业模型
    │   ├── todo.go            # 待办模型
    │   └── reminder.go        # 提醒模型
    ├── routes/
    │   └── routes.go          # 路由注册
    ├── scheduler/
    │   └── scheduler.go       # 定时任务调度
    ├── scraper/               # 🆕 爬虫模块
    │   ├── auth.go            # BUCT登录认证
    │   ├── lid_utils.go       # 课程LID工具
    │   ├── course_utils.go    # 作业解析工具
    │   ├── test_utils.go      # 测试解析工具
    │   ├── client.go          # 客户端封装
    │   └── types.go           # 数据类型定义
    ├── services/
    │   ├── course_data.go     # 课程数据服务（含爬虫调用）
    │   └── email.go           # 邮件服务
    └── utils/
        ├── time.go            # 时间工具
        ├── random.go          # 随机数生成
        └── password.go        # 密码处理
```

## 爬虫功能

本后端集成了北化课程平台的完整爬虫功能，可以：

- 登录北化课程平台
- 获取待提交作业列表
- 获取作业详情和截止时间
- 获取待进行测试列表
- 自动刷新课程数据

### 爬虫API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/assignments/standard` | GET | 获取作业列表 |
| `/api/assignments/refresh` | POST | 异步刷新作业数据 |
| `/api/assignments/refresh-sync` | POST | 同步刷新作业数据 |

## 快速开始

### 1. 环境准备

确保已安装：
- Go 1.21+
- MongoDB 4.5+

### 2. 配置

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的环境变量。

### 3. 安装依赖

```bash
go mod download
```

### 4. 运行

```bash
go run main.go
```

服务器将在 `http://localhost:5000` 启动。

## Docker部署

### 使用Docker Compose（推荐）

在 `web` 目录下运行：

```bash
docker-compose -f docker-compose-go.yml up -d
```

这将启动：
- Go后端服务 (端口5000)
- MongoDB数据库 (端口27017)
- 前端服务 (端口8080)

### 构建单独镜像

```bash
docker build -t buct-course-remind-go .
```

### 运行容器

```bash
docker run -d \
  --name buct-backend-go \
  -p 5000:5000 \
  -e MONGO_URI=mongodb://host.docker.internal:27017/buct-course \
  -e SECRET_KEY=your_secret_key \
  buct-course-remind-go
```

## API端点

### 认证

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/auth/login | 用户登录 |
| POST | /api/auth/logout | 用户登出 |
| GET | /api/auth/status | 检查登录状态 |
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/send-code | 发送验证码 |
| POST | /api/auth/forgot-password | 忘记密码 |

### 作业

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/assignments/standard | 获取作业列表 |
| POST | /api/assignments/:id/complete | 标记作业完成 |
| POST | /api/assignments/:id/uncomplete | 撤销完成状态 |
| DELETE | /api/assignments/:id | 删除作业 |
| POST | /api/assignments/:id/restore | 恢复作业 |
| POST | /api/assignments/refresh | 刷新作业数据 |

### 待办事项

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/todos/ | 获取待办列表 |
| POST | /api/todos/ | 创建待办 |
| PUT | /api/todos/:id | 更新待办 |
| DELETE | /api/todos/:id | 删除待办 |
| POST | /api/todos/:id/complete | 完成待办 |
| POST | /api/todos/:id/uncomplete | 撤销完成 |

### 设置

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/settings | 获取设置 |
| POST | /api/settings | 保存设置 |
| GET | /api/settings/email | 获取邮箱设置 |
| POST | /api/settings/email | 保存邮箱设置 |

### 健康检查

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /health | 基础健康检查 |
| GET | /api/health/detailed | 详细健康检查 |

### 加密

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/crypto/public-key | 获取RSA公钥 |

## 与Python版本的差异

1. **框架**: Python使用Flask，Go使用Gin
2. **Session**: 使用gin-contrib/sessions替代Flask-Session
3. **数据库驱动**: 使用官方mongo-driver替代flask-pymongo
4. **加密**: 使用Go标准库crypto实现

## 待完成功能

- [ ] 爬虫功能（需要根据具体网站实现）
- [ ] 管理员功能
- [ ] Webhook支持
- [ ] 更多通知渠道

## 开发

### 代码格式化

```bash
go fmt ./...
```

### 运行测试

```bash
go test ./...
```

## 许可证

MIT License
