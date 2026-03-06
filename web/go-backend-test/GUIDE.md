# Gin 基础框架使用指南

## 项目概览

这个Gin框架采用**模块化架构**设计，遵循以下设计原则：

- **单一职责** - 每个模块负责一个功能
- **可维护性** - 清晰的代码结构便于维护
- **可扩展性** - 易于添加新功能
- **可测试性** - 各模块相对独立便于测试

## 快速开始

### 1. 启动应用

```bash
cd go-backend
go run main.go
```

应用启动后会显示：

```
[2026-02-23 10:30:45] GET /health - 200 (1.2ms)
服务器启动在 http://localhost:8080 (环境: development)
```

### 2. 测试API

#### 健康检查

```bash
curl http://localhost:8080/health
```

响应：

```json
{
  "status": "ok"
}
```

#### Ping测试

```bash
curl http://localhost:8080/api/v1/ping
```

响应：

```json
{
  "message": "pong"
}
```

#### 创建用户

```bash
curl -X POST http://localhost:8080/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"id":"1","name":"张三","email":"test@example.com"}'
```

## 架构详解

### 分层架构

```
┌─────────────────────────────────────┐
│         Router Layer (路由)         │
│      管理所有HTTP请求路由          │
└──────────────────┬──────────────────┘
                   │
┌──────────────────▼──────────────────┐
│      Handlers Layer (处理器)        │
│     处理请求并调用service层        │
└──────────────────┬──────────────────┘
                   │
┌──────────────────▼──────────────────┐
│      Service Layer (业务逻辑)       │
│   实现具体的业务逻辑（待扩展）      │
└──────────────────┬──────────────────┘
                   │
┌──────────────────▼──────────────────┐
│   Repository Layer (数据访问)       │
│  访问数据库或外部服务（待扩展）     │
└─────────────────────────────────────┘
```

### 模块间依赖关系

```
main.go
  ├── config/      (加载配置)
  └── app/         (应用启动)
      ├── middleware/  (中间件)
      └── router/      (路由配置)
          └── api/handlers/  (请求处理)
              ├── models/        (数据模型)
              └── utils/         (工具函数)
```

## 如何添加新功能

### 场景：添加"作业"管理功能

#### 第1步：定义模型 (`models/models.go`)

```go
// Assignment 作业模型
type Assignment struct {
ID          string    `json:"id"`
Title       string    `json:"title"`
Description string    `json:"description"`
Deadline    time.Time `json:"deadline"`
CourseID    string    `json:"course_id"`
}
```

#### 第2步：创建处理函数 (`api/handlers/handlers.go`)

```go
func GetAssignments(c *gin.Context) {
// 获取所有作业
c.JSON(http.StatusOK, gin.H{"data": []models.Assignment{}})
}

func CreateAssignment(c *gin.Context) {
var assignment models.Assignment
if err := c.ShouldBindJSON(&assignment); err != nil {
utils.ErrorResponseBadRequest(c, err.Error())
return
}
// 创建作业逻辑
utils.SuccessResponseCreated(c, "作业创建成功", assignment)
}
```

#### 第3步：添加路由 (`router/router.go`)

```go
// 在 SetupRoutes 函数中添加
assignmentRoutes := v1.Group("/assignments")
{
assignmentRoutes.GET("", handlers.GetAssignments)
assignmentRoutes.POST("", handlers.CreateAssignment)
// 更多路由...
}
```

#### 第4步：测试

```bash
curl -X POST http://localhost:8080/api/v1/assignments \
  -H "Content-Type: application/json" \
  -d '{"title":"第一次作业","description":"完成练习1-5"}'
```

## 中间件使用

### 已实现的中间件

#### 1. 日志中间件

自动记录每个请求的:

- HTTP方法
- 请求路径
- 响应状态码
- 执行时间

```
[2026-02-23 10:30:45] GET /api/v1/users - 200 (2.5ms)
```

#### 2. CORS中间件

允许跨域请求，配置允许的:

- 请求方法: POST, GET, PUT, DELETE, OPTIONS
- 请求头: Content-Type, Authorization等
- 请求源: 所有来源

#### 3. Recovery中间件

捕获panic防止应用崩溃

### 添加自定义中间件

```go
// 在 middleware/middleware.go 中添加
func AuthMiddleware() gin.HandlerFunc {
return func (c *gin.Context) {
// 检查认证信息
token := c.GetHeader("Authorization")
if token == "" {
c.JSON(http.StatusUnauthorized, gin.H{"error": "未授权"})
c.Abort()
return
}
c.Next()
}
}

// 在 app/app.go 中应用
r.Use(middleware.AuthMiddleware())
```

## 响应处理

### 使用响应工具函数

#### 成功响应

```go
// 200 OK
utils.SuccessResponseOK(c, "获取成功", data)

// 201 Created
utils.SuccessResponseCreated(c, "创建成功", data)

// 自定义成功响应
utils.SuccessResponse(c, http.StatusOK, "自定义消息", data)
```

#### 错误响应

```go
// 400 Bad Request
utils.ErrorResponseBadRequest(c, "参数验证失败")

// 404 Not Found
utils.ErrorResponseNotFound(c, "资源不存在")

// 500 Server Error
utils.ErrorResponseServerError(c, err.Error())

// 自定义错误响应
utils.ErrorResponse(c, http.StatusBadRequest, "请求参数错误", errMessage)
```

## 配置管理

### 环境变量

在系统中设置以下环境变量：

```bash
# Windows (PowerShell)
$env:PORT = ":9090"
$env:ENV = "production"

# Linux/Mac
export PORT=":9090"
export ENV="production"
```

### 动态配置

在 `config/config.go` 中修改：

```go
func LoadConfig() *Config {
// 添加新的配置项
dbHost := os.Getenv("DB_HOST")
if dbHost == "" {
dbHost = "localhost"
}
// ...
}
```

## 项目结构最佳实践

### 命名约定

| 类型  | 约定     | 示例                         |
|-----|--------|----------------------------|
| 包名  | 小写，单数  | `models`, `handlers`       |
| 函数名 | 大写开头驼峰 | `GetUsers`, `CreateCourse` |
| 变量名 | 小写驼峰   | `userName`, `courseID`     |
| 常量  | 大写     | `DEFAULT_PORT`             |

### 文件组织

- 一个包一个目录
- 相关的功能放在同一个包内
- 避免循环导入
- 使用明确的导入路径

## 常见问题

### Q: 如何添加数据库支持？

A: 创建 `db/` 目录和 `repository/` 目录来处理数据库连接和查询。

### Q: 如何实现认证？

A: 创建 `auth/` 目录实现JWT认证，并使用中间件保护路由。

### Q: 如何处理业务逻辑？

A: 创建 `service/` 目录，在handlers中调用service层的方法。

### Q: 如何测试？

A: 在各模块目录下创建 `*_test.go` 文件，使用 `go test` 命令运行测试。

## 下一步

1. ✅ 基础框架搭建完成
2. 📝 计划添加：
    - 数据库支持 (PostgreSQL/MongoDB)
    - 认证授权 (JWT)
    - 业务逻辑层 (Service)
    - 数据验证层 (Validators)
    - 单元测试
    - Docker支持

## 更多资源

- [Gin官方文档](https://gin-gonic.com/)
- [Go官方文档](https://golang.org/doc/)
- [REST API最佳实践](https://restfulapi.net/)

