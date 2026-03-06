# Gin 模块化框架 - 项目结构说明

## 📁 完整项目结构

```
go-backend/
├── main.go                    # ⭐ 应用入口
│
├── app/                       # 应用初始化层
│   └── app.go                 # 应用配置、路由器创建、服务启动
│
├── config/                    # 配置管理层
│   └── config.go              # 环境变量加载、配置定义
│
├── router/                    # 路由管理层
│   └── router.go              # 路由定义、路由分组
│
├── api/                       # API层
│   └── handlers/              # 请求处理器
│       └── handlers.go        # HTTP处理函数
│
├── models/                    # 数据模型层
│   └── models.go              # 业务模型定义
│
├── middleware/                # 中间件层
│   └── middleware.go          # 日志、CORS、恢复等中间件
│
├── utils/                     # 工具函数层
│   └── response.go            # 统一响应处理
│
├── go.mod                     # Go模块定义
├── go.sum                     # 依赖版本锁定
├── .gitignore                 # Git忽略规则
├── README.md                  # 项目README
├── GUIDE.md                   # 使用指南
├── Makefile                   # 构建脚本
└── PROJECT_STRUCTURE.md       # 本文件
```

## 🏗️ 分层架构说明

### Layer 1: 入口层 (Entry Point)

**文件**: `main.go`
**职责**:

- 应用程序的入口点
- 初始化配置和启动应用
- 最小化的业务逻辑

```go
func main() {
cfg := config.LoadConfig()
app.Start(cfg)
}
```

### Layer 2: 应用初始化层 (Application Layer)

**目录**: `app/`
**职责**:

- 创建Gin路由器实例
- 配置全局中间件
- 管理应用生命周期
- 决定哪些中间件应用到哪些路由

```go
func NewRouter(cfg *config.Config) *gin.Engine {
r := gin.New()
r.Use(middleware.LoggingMiddleware())
r.Use(middleware.CORSMiddleware())
router.SetupRoutes(r)
return r
}
```

### Layer 3: 配置层 (Configuration Layer)

**目录**: `config/`
**职责**:

- 加载和管理配置参数
- 读取环境变量
- 提供配置给应用

```go
type Config struct {
Port  string // 服务端口
Env   string // 运行环境
Debug bool   // 调试模式
}
```

### Layer 4: 路由层 (Router Layer)

**目录**: `router/`
**职责**:

- 定义所有API路由
- 组织路由分组
- 映射URL到处理函数

```go
func SetupRoutes(router *gin.Engine) {
v1 := router.Group("/api/v1")
{
users := v1.Group("/users")
users.GET("", handlers.GetUsers)
}
}
```

### Layer 5: 处理层 (Handlers Layer)

**目录**: `api/handlers/`
**职责**:

- 处理HTTP请求
- 验证请求参数
- 调用业务逻辑
- 返回HTTP响应

```go
func GetUsers(c *gin.Context) {
users := []models.User{}
utils.SuccessResponseOK(c, "获取成功", users)
}
```

### Layer 6: 中间件层 (Middleware Layer)

**目录**: `middleware/`
**职责**:

- 日志记录 (LoggingMiddleware)
- 跨域处理 (CORSMiddleware)
- 错误恢复 (RecoveryMiddleware)
- 认证授权 (待扩展)

```go
func LoggingMiddleware() gin.HandlerFunc {
return func (c *gin.Context) {
start := time.Now()
c.Next()
duration := time.Since(start)
// 记录日志
}
}
```

### Layer 7: 数据模型层 (Models Layer)

**目录**: `models/`
**职责**:

- 定义业务数据结构
- 定义API响应格式
- 定义数据验证规则

```go
type User struct {
ID    string `json:"id" binding:"required"`
Name  string `json:"name" binding:"required"`
Email string `json:"email" binding:"required,email"`
}
```

### Layer 8: 工具层 (Utils Layer)

**目录**: `utils/`
**职责**:

- 通用工具函数
- 响应格式化
- 错误处理辅助函数

```go
func SuccessResponseOK(c *gin.Context, msg string, data interface{}) {
c.JSON(200, gin.H{"message": msg, "data": data})
}
```

## 📊 数据流示意图

```
┌─────────────────────────────────────────────────────────┐
│                    Client Request                       │
│            GET /api/v1/users?page=1                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Gin Router (router/)                   │
│         Matches URL to handler function                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│               Middleware Pipeline                       │
│   1. LoggingMiddleware → 2. CORSMiddleware →           │
│   3. RecoveryMiddleware                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Handler Function (api/handlers/)           │
│            GetUsers() - Process Request                 │
│         Parse params, validate input                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│            Business Logic Layer (待扩展)                 │
│         UserService.GetUsers(page, limit)              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│          Data Access Layer (待扩展)                      │
│      UserRepository.FindAll() - Query Database         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   Database (待扩展)                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│          Return Data to Handler                         │
│        models.User[], error                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│      Format Response (utils/response.go)                │
│     SuccessResponseOK() - Build JSON response          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Return Response to Client                  │
│          {code: 200, message: "成功", data: [...]}     │
└─────────────────────────────────────────────────────────┘
```

## 🔄 模块间的依赖关系

```
            main.go
              │
        ┌─────┴─────┐
        ▼           ▼
      config/      app/
                    │
              ┌─────┼─────┐
              ▼     ▼     ▼
          router/  middleware/  models/
              │
              ▼
          api/handlers/
              │
        ┌─────┴─────┐
        ▼           ▼
      models/      utils/
```

## 🚀 工作流程

### 1️⃣ 应用启动

```
main.go
    └─→ config.LoadConfig()          # 加载配置
    └─→ app.Start(cfg)               # 启动应用
        └─→ app.NewRouter(cfg)       # 创建路由器
            └─→ router.SetupRoutes()  # 设置所有路由
            └─→ r.Run(port)           # 启动HTTP服务
```

### 2️⃣ 请求处理

```
Client Request
    └─→ Router 匹配路由
    └─→ Middleware Pipeline
        ├─→ LoggingMiddleware (记录请求)
        ├─→ CORSMiddleware (处理跨域)
        ├─→ RecoveryMiddleware (错误恢复)
    └─→ Handler Function (处理请求)
        └─→ 调用业务逻辑
        └─→ 返回数据
    └─→ utils.SuccessResponse (格式化响应)
    └─→ Return to Client
```

## 📝 文件模板

### 添加新的Handler

```go
// api/handlers/handlers.go
func GetNewResource(c *gin.Context) {
// 1. 解析参数
id := c.Param("id")

// 2. 业务逻辑（暂时返回示例数据）
data := map[string]interface{}{"id": id}

// 3. 返回响应
utils.SuccessResponseOK(c, "获取成功", data)
}
```

### 添加新的Model

```go
// models/models.go
type NewModel struct {
ID   string `json:"id" binding:"required"`
Name string `json:"name" binding:"required"`
}
```

### 添加新的Middleware

```go
// middleware/middleware.go
func CustomMiddleware() gin.HandlerFunc {
return func (c *gin.Context) {
// Before
c.Next()
// After
}
}
```

## 🔌 扩展指南

### 添加数据库层

```
db/
  ├── connection.go      # 数据库连接
  └── migration.go       # 数据库迁移

repository/
  ├── user_repo.go       # 用户数据访问
  └── course_repo.go     # 课程数据访问
```

### 添加业务逻辑层

```
service/
  ├── user_service.go    # 用户业务逻辑
  └── course_service.go  # 课程业务逻辑
```

### 添加认证层

```
auth/
  ├── jwt.go             # JWT认证
  └── middleware.go      # 认证中间件
```

### 添加验证层

```
validators/
  ├── user_validator.go  # 用户验证规则
  └── course_validator.go # 课程验证规则
```

## 📚 相关文件

- **README.md** - 项目概述和快速开始
- **GUIDE.md** - 详细的使用指南
- **Makefile** - 开发工具命令

## ✅ 命名规范

| 项目  | 规范        | 示例                      |
|-----|-----------|-------------------------|
| 包名  | 小写，避免下划线  | `handlers`, `models`    |
| 函数名 | 大写开头驼峰    | `GetUser`, `CreateUser` |
| 变量名 | 小写驼峰      | `userName`, `courseID`  |
| 常量  | 全大写       | `MAX_RETRIES`           |
| 结构体 | 大写驼峰      | `User`, `Course`        |
| 接口  | 大写驼峰+er后缀 | `Reader`, `Writer`      |

---

**最后更新**: 2026年2月23日

