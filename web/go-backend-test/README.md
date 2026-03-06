# BUCT Course Remind - Go Backend

这是一个基于 Go 和 Gin 框架的后端服务，采用模块化架构设计。

## 项目结构

```
go-backend/
├── main.go                 # 主入口文件
├── go.mod                  # Go module 文件
├── go.sum                  # Go dependencies 文件
├── README.md              # 本文档
├── .gitignore             # Git 忽略文件
├── app/                   # 应用初始化和启动逻辑
│   └── app.go
├── config/                # 配置管理模块
│   └── config.go
├── router/                # 路由管理模块
│   └── router.go
├── middleware/            # 中间件模块
│   └── middleware.go
├── models/                # 数据模型
│   └── models.go
├── api/                   # API层
│   └── handlers/
│       └── handlers.go
└── utils/                 # 工具函数
    └── response.go
```

## 模块说明

### 1. **app** - 应用初始化

- 创建Gin路由器实例
- 应用全局中间件
- 管理应用启动逻辑

### 2. **config** - 配置管理

- 加载环境变量配置
- 管理应用配置参数（端口、环境等）

### 3. **router** - 路由管理

- 统一管理所有API路由
- 支持路由分组
- 清晰的路由层次结构

### 4. **middleware** - 中间件

- 日志中间件（LoggingMiddleware）
- CORS跨域中间件（CORSMiddleware）
- 恢复中间件（RecoveryMiddleware）

### 5. **models** - 数据模型

- 用户模型 (User)
- 课程模型 (Course)
- 统一的API响应结构 (APIResponse)
- 错误响应结构 (ErrorResponse)

### 6. **api/handlers** - 请求处理器

- 处理所有HTTP请求
- 业务逻辑实现
- 用户管理处理函数
- 课程管理处理函数

### 7. **utils** - 工具函数

- 统一响应工具函数
- 简化的错误处理响应

## 前提条件

- Go 1.25 或更高版本
- Gin Web Framework v1.11.0

## 快速开始

### 1. 安装依赖

```bash
go mod download
```

### 2. 运行应用

```bash
go run main.go
```

应用将在 `http://localhost:8080` 启动。

### 3. 构建二进制文件

```bash
go build -o go-backend.exe
```

## API 路由

### 健康检查

- `GET /health` - 检查服务器健康状态

### API v1

#### Ping

- `GET /api/v1/ping` - 简单的 Ping 测试

#### 用户管理 (`/api/v1/users`)

- `GET /api/v1/users` - 获取所有用户
- `GET /api/v1/users/:id` - 获取指定用户
- `POST /api/v1/users` - 创建新用户
- `PUT /api/v1/users/:id` - 更新用户信息
- `DELETE /api/v1/users/:id` - 删除用户

#### 课程管理 (`/api/v1/courses`)

- `GET /api/v1/courses` - 获取所有课程
- `GET /api/v1/courses/:id` - 获取指定课程
- `POST /api/v1/courses` - 创建新课程

## 环境变量

| 变量     | 说明    | 默认值           |
|--------|-------|---------------|
| `PORT` | 服务器端口 | `:8080`       |
| `ENV`  | 运行环境  | `development` |

## 依赖

- **gin-gonic/gin** (v1.11.0) - Go Web 框架

## 开发指南

### 添加新路由

1. 在 `api/handlers/handlers.go` 中添加处理函数
2. 在 `router/router.go` 中定义路由

```go
// 在handlers.go中
func NewHandler(c *gin.Context) {
    c.JSON(http.StatusOK, gin.H{"message": "ok"})
}

// 在router.go中
v1.GET("/new", handlers.NewHandler)
```

### 添加新中间件

在 `middleware/middleware.go` 中创建新的中间件函数，然后在 `app/app.go` 中应用。

### 使用响应工具函数

```go
// 成功响应
utils.SuccessResponseOK(c, "获取成功", data)

// 错误响应
utils.ErrorResponseBadRequest(c, "参数错误")
utils.ErrorResponseNotFound(c, "资源不存在")
utils.ErrorResponseServerError(c, "服务器内部错误")
```

## 项目扩展建议

1. **数据库层** - 添加 MongoDB 或 PostgreSQL 支持
    - 创建 `db/` 目录管理数据库连接
    - 创建 `repository/` 目录实现数据访问层

2. **业务逻辑层** - 提取业务逻辑
    - 创建 `service/` 目录实现业务逻辑

3. **认证授权** - 实现JWT认证
    - 创建 `auth/` 目录处理认证逻辑

4. **验证层** - 数据验证
    - 创建 `validators/` 目录处理数据验证

5. **日志系统** - 更强大的日志
    - 集成 `logrus` 或 `zap` 日志库

6. **错误处理** - 统一的错误处理
    - 创建 `errors/` 目录定义自定义错误类型

## 许可证

MIT License

## 贡献

欢迎提交 PR 和 Issue！



