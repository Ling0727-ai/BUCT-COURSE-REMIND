# BUCT课程提醒系统

一个基于 Flask / **Go (Gin)** + MongoDB + Vue.js 的课程作业提醒系统，支持自动获取教务系统信息并发送通知。

> 项目现提供 **Python (Flask) 后端** 和 **Go (Gin) 后端** 两个实现，功能完全一致，可按需选用。

## 功能特性

- 🔐 用户注册登录系统（RSA 强制加密传输）
- 📚 学生信息管理（学号、外部系统密码 ECC 加密存储）
- 📧 邮箱验证码验证 + 忘记密码重置
- 🔔 邮件提醒（手动 / 定时 / DDL 前 24h 自动提醒）
- 📝 待办事项管理（含优先级、软删除、回收站）
- ⚙️ 灵活的系统设置
- 📱 响应式前端界面（薄荷主色调）
- 🚀 Go 高性能后端（镜像体积 ~20MB，启动 <1s）

## 更新日志

**2025年9到10月版本更新**：

- v0.0.0 - 初始版本发布，包含用户注册、学生信息管理、设置页面等核心功能。
- v1.0.0 - 完善爬虫库，支持自动化获取作业信息与测试信息。
- v1.1.0 - 增加todo list，规划后续功能开发方向。
- v1.2.0 - 优化前端界面，提升用户体验。
- v2.0.0 - 从实时获取数据改为数据库暂存，提升系统稳定性和性能，增加已完成以及删除标记。
- v2.1.0 - 增加密码强度检测功能，增加前端登录和注册时的表单加密，完善反爬措施，提升账户安全性。
- v2.2.0 - 增加手动刷新按钮，方便用户即时获取最新信息。
- v2.3.0 - 优化数据库结构，提升数据存取效率。
- v2.4.0 - 修复删除时的bug，改为软删除+硬删除双标记,增加回收站，提升系统稳定性。

2025年11月版本更新：

- v3.0.0 - 重构前端样式，改为更加清新的薄荷主色调的配色方案，提升视觉体验；同时优化移动端的使用体验。(2025-11-11)
- v3.1.0 - 初步实现邮箱提醒功能，支持用户通过邮箱接收课程作业提醒。(2025-11-13)
- v3.2.0 - 邮箱自动化提醒功能完善，支持定时发送课程作业提醒邮件（ddl24h前自动发送）。(2025-11-14)
- v3.3.0 - 修复了一系列bug并美化界面，提升系统稳定性和用户体验。(2025-11-15 3:00 AM)
    1. 修复刷新数据库后已经删除的作业/测试重新出现的bug
    2. 修复提醒功能不生效的bug
    3. 修复更新教务系统账号密码不写入数据库的bug
    4. 重构了设置todo的时间设置格式，使其更加自由
    5. 优化了提醒设置界面的时间设置，优化页面样式
    6. 重构表单结构，提升代码可维护性，提升安全性
    7. 修复刷新数据库无弹窗提示的bug
    8. 重构数据生成逻辑，提升系统稳定性
    9. 优化邮箱提醒逻辑，减少不必要的邮件发送（已完成以及已删除标记的）
    10. 删除功能重复的字段
    11. 发现部分作业/测试抓取失败的bug，待修复
- v3.3.1 - 修复作业/测试抓取失败bug（其实是修复我的另一个项目https://github.com/Ling0727-ai/python-buct-course.git）
  （2025-11-15 13:08）
- v3.4.0 - 修复了一系列弹窗失效bug，以及滑动条异常显示问题，提升用户体验。（2025-11-15 16:40）
    1. 修复设置页面双滚动条问题，优化页面滚动体验
    2. 修复作业和测试类型显示统一为"作业"的bug，现可正确区分作业和测试
    3. 修复登录自动刷新异常问题：
        - 修正logout方法缺少user_id参数导致的会话清理失败
        - 消除会话资源泄漏，防止客户端对象累积
        - 增强异常处理和日志追踪机制
    4. 重构待办事项时间设置界面：
        - 改用日期时间选择器设置DDL（截止时间）
        - 添加快捷时间选项（1小时、3小时、6小时、12小时、1天、3天、1周）
        - 参考提醒设置界面的设计，提供更直观的用户体验
        - 移除原有的时长输入方式，改为具体截止日期时间设置
- v3.4.1 - 增加6小时未操作自动登出功能，提升账户安全性。 (2025-11-16)
- v3.4.2 - 完善作业DDL前24小时自动邮件提醒功能。 (2025-11-17)
    1. 自动检测即将到期的作业（截止前23-25小时范围内）
    2. 为每个用户的即将到期作业自动创建提醒
    3. 提醒邮件包含科目、标题、截止时间等详细信息
    4. 智能过滤已完成和已删除的作业，避免重复提醒
    5. 调度器每小时自动检查一次，无需手动干预
    6. 修复重新登录后立即切换页面误触发6小时自动退出的问题
- v3.4.3 - 改进登录和密码找回功能，提升用户体验。 (2025-11-17)
    1. 忘记密码邮件中包含用户名信息，解决用户同时忘记用户名和密码的问题
    2. 支持使用用户名或邮箱登录，提供更灵活的登录方式
    3. 优化登录错误提示，更清晰地指出问题所在
    4. 密码重置页面实时显示用户名提示
- v3.4.4 - 强制加密传输，提升系统安全性。 (2025-11-17)
    1. 移除所有接口的兼容模式，强制要求使用RSA加密传输
    2. 登录、注册、发送验证码、重置密码等接口必须使用加密数据
    3. 未使用加密的请求将被拒绝（返回400错误）
    4. 符合OWASP安全标准，防止中间人攻击和网络嗅探

**2026年3月版本更新**：

- v4.0.0 - 完整 Go (Gin) 后端实现，与 Python 版本功能完全对齐。(2026-03-06)
  1. 使用 Go 1.25 + Gin 重写全部后端接口（63 条路由，覆盖全部 Python 蓝图）
  2. 多阶段 Docker 构建，最终镜像体积 ~20MB（Python 版 ~300MB）
  3. 采用分层架构：handler → service → model/repository
  4. Snowflake 分布式 ID 生成，替代 MongoDB ObjectID
  5. goroutine + time.Ticker 实现调度器，替代 APScheduler
  6. 原生 `net/smtp` 实现多候选 SMTP 自动重试发送
  7. 新增 Docker Compose 一键部署（`docker-compose-go.yml`）

## 项目结构

```
BUCT-course-remind/
├── web/
│   ├── backend/                # Python (Flask) 后端
│   │   ├── app/
│   │   │   ├── auth.py         # 认证、验证码、密码重置
│   │   │   ├── assignments.py  # 作业 CRUD + 状态管理
│   │   │   ├── course_data.py  # 课程数据刷新
│   │   │   ├── todos.py        # 待办事项
│   │   │   ├── scheduler.py    # 定时刷新 + 自动提醒
│   │   │   ├── scraper.py      # 教务系统爬虫
│   │   │   └── ...
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── go-backend-test/        # Go (Gin) 后端
│   │   ├── api/handlers/       # Handler 层（接口定义）
│   │   │   ├── auth.go
│   │   │   ├── assignments.go
│   │   │   ├── todos.go
│   │   │   ├── reminder.go
│   │   │   ├── course_data.go
│   │   │   ├── admin.go
│   │   │   ├── settings.go
│   │   │   └── ...
│   │   ├── services/           # 业务逻辑层
│   │   ├── models/             # 数据层（按集合分包）
│   │   │   ├── User/
│   │   │   ├── CourseData/
│   │   │   ├── AssignmentStatus/
│   │   │   ├── Todo/
│   │   │   └── Reminder/
│   │   ├── scheduler/          # 定时调度器
│   │   ├── scraper/            # 教务系统爬虫
│   │   ├── config/             # 配置 + 邮件
│   │   ├── crypto/             # RSA / AES / ECC 加密
│   │   ├── router/router.go    # 路由注册
│   │   ├── middleware/         # 日志 / CORS / Recovery
│   │   ├── Dockerfile
│   │   └── main.go
│   │
│   ├── fronted/                # Vue.js 前端
│   │   └── src/
│   │       ├── views/
│   │       └── components/
│   │
│   ├── docker-compose.yml      # Python 后端一键部署
│   └── docker-compose-go.yml   # Go 后端一键部署
└── README.md
```

## 安装和运行

### 方式一：Docker 一键部署（推荐）

#### 使用 Go 后端

```bash
cd web

# 复制并编辑环境变量
cp .env.example .env

# 启动（MongoDB + Go后端 + 前端）
docker compose -f docker-compose-go.yml up -d

# 查看日志
docker compose -f docker-compose-go.yml logs -f backend
```

服务启动后访问：

- 前端：`http://localhost:3033`
- Go 后端：`http://localhost:8080`

#### 使用 Python 后端

```bash
cd web
docker compose -f docker-compose.yml up -d
```

服务启动后访问：

- 前端：`http://localhost:3033`
- Python 后端：`http://localhost:5000`

#### 环境变量说明（`.env`）

```dotenv
# MongoDB
MONGO_INITDB_ROOT_USERNAME=REDACTED_MONGO_USER
MONGO_INITDB_ROOT_PASSWORD=REDACTED_MONGO_PASSWORD
MONGO_INITDB_DATABASE=REDACTED_MONGO_USER

# 邮件（必填，否则邮件功能不可用）
MAIL_SMTP_SERVER=smtp.163.com
MAIL_SMTP_PORT=465
MAIL_SENDER=your_email@163.com
MAIL_PASSWORD=your_auth_code        # 邮箱授权码，非登录密码

# JWT 密钥（生产环境务必修改）
SECRET_KEY=change-this-in-production

# 端口（可选，默认值如下）
GO_PORT=8080
FLASK_PORT=5000
FRONTEND_PORT=3033
```

---

### 方式二：本地开发运行

#### Go 后端

```bash
cd web/go-backend-test

# 配置环境变量
cp .env.example .env   # 或直接设置系统环境变量

# 下载依赖
go mod download

# 运行
go run main.go
```

#### Python 后端

```bash
cd web/backend
pip install -r requirements.txt
python app.py
```

#### 前端

```bash
cd web/fronted
npm install
npm run serve
```

---

## API 接口

> Go 后端所有接口统一前缀 `/api/v1`，Python 后端前缀为 `/api`。

### 认证

| 方法   | 路径                             | 说明           |
|------|--------------------------------|--------------|
| POST | `/auth/login`                  | 用户登录（RSA 加密） |
| POST | `/auth/logout`                 | 用户登出         |
| POST | `/auth/register`               | 用户注册（RSA 加密） |
| GET  | `/auth/status`                 | 登录状态检查       |
| GET  | `/auth/user-info`              | 获取当前用户信息     |
| POST | `/auth/update-email`           | 修改邮箱         |
| POST | `/auth/update-student-info`    | 更新学号/教务密码    |
| POST | `/auth/check-email`            | 检查邮箱是否已注册    |
| POST | `/auth/send-verification-code` | 发送邮箱验证码      |
| POST | `/auth/verify-code`            | 校验验证码        |
| POST | `/auth/reset-password`         | 重置密码（RSA 加密） |

### 作业

| 方法     | 路径                                  | 说明        |
|--------|-------------------------------------|-----------|
| GET    | `/assignments`                      | 获取作业列表    |
| GET    | `/assignments/stats`                | 统计信息      |
| GET    | `/assignments/completed`            | 已完成 ID 列表 |
| GET    | `/assignments/deleted`              | 回收站列表     |
| DELETE | `/assignments/clear-deleted`        | 清空回收站     |
| POST   | `/assignments/:id/complete`         | 标记完成      |
| POST   | `/assignments/:id/uncomplete`       | 撤销完成      |
| POST   | `/assignments/:id/delete`           | 软删除       |
| POST   | `/assignments/:id/restore`          | 恢复        |
| DELETE | `/assignments/:id/permanent-delete` | 永久删除      |
| POST   | `/assignments/:id/remind`           | 创建提醒      |

### 课程数据

| 方法   | 路径                     | 说明       |
|------|------------------------|----------|
| POST | `/course-data/refresh` | 手动触发爬虫刷新 |
| GET  | `/course-data/list`    | 获取课程数据列表 |
| GET  | `/course-data/status`  | 查看上次刷新时间 |

### 待办事项

| 方法     | 路径                            | 说明              |
|--------|-------------------------------|-----------------|
| GET    | `/todos`                      | 待办列表            |
| POST   | `/todos`                      | 创建待办            |
| GET    | `/todos/stats`                | 统计              |
| GET    | `/todos/deleted`              | 回收站             |
| DELETE | `/todos/clear-deleted`        | 清空回收站           |
| PUT    | `/todos/:id`                  | 更新              |
| POST   | `/todos/:id/complete`         | 标记完成（12h 后自动删除） |
| POST   | `/todos/:id/uncomplete`       | 撤销完成            |
| POST   | `/todos/:id/remind`           | 发送提醒邮件          |
| POST   | `/todos/:id/delete`           | 软删除             |
| POST   | `/todos/:id/restore`          | 恢复              |
| DELETE | `/todos/:id/permanent-delete` | 永久删除            |

### 提醒

| 方法     | 路径                  | 说明     |
|--------|---------------------|--------|
| GET    | `/reminders`        | 提醒列表   |
| POST   | `/reminders`        | 创建定时提醒 |
| DELETE | `/reminders/:id`    | 删除提醒   |
| POST   | `/reminders/manual` | 立即手动发送 |
| POST   | `/reminders/test`   | 发送测试邮件 |

### 设置 / 其他

| 方法       | 路径                             | 说明                |
|----------|--------------------------------|-------------------|
| GET/POST | `/settings`                    | 系统设置              |
| GET/POST | `/settings/email`              | 邮件通知设置            |
| GET      | `/health`                      | 健康检查（含 DB + 邮件状态） |
| GET      | `/stats`                       | 全局统计              |
| GET/POST | `/crypto/public-key` 等         | RSA/AES 加密接口      |
| POST     | `/admin/cleanup/trigger`       | 管理员手动触发刷新         |
| GET      | `/admin/completed-assignments` | 管理员查看完成记录         |
| GET      | `/admin/system/status`         | 系统状态              |

---

## 架构说明

### Go 后端分层

```
HTTP 请求
  → middleware（日志 / CORS / Recovery）
  → router（URL 分发）
  → handlers（解析请求 + 返回响应）
  → services（跨模型业务逻辑）
  → models/[集合名]/database.go（MongoDB 操作）
```

### 调度器

Go 后端使用 `goroutine + time.Ticker` 实现三个并发定时任务：

| 任务     | 间隔    | 说明                              |
|--------|-------|---------------------------------|
| 课程数据刷新 | 12 小时 | 自动爬取教务系统，更新数据库                  |
| 到期提醒检查 | 5 秒   | 发送 `scheduled_reminders` 中到期的邮件 |
| 自动提醒生成 | 1 小时  | 为 DDL 前 24h 内的作业自动创建提醒          |

### Python vs Go 对比

| 指标          | Python (Flask) | Go (Gin)    |
|-------------|----------------|-------------|
| Docker 镜像大小 | ~300MB         | ~20MB       |
| 容器启动时间      | ~3-5s          | <1s         |
| 并发模型        | 多线程 / gevent   | goroutine   |
| 定时任务        | APScheduler    | time.Ticker |
| 路由前缀        | `/api`         | `/api/v1`   |

---

## 环境要求

| 组件    | Python 版本    | Go 版本        |
|-------|--------------|--------------|
| 后端运行时 | Python 3.8+  | Go 1.21+     |
| 数据库   | MongoDB 4.0+ | MongoDB 4.0+ |
| 前端    | Node.js 14+  | Node.js 14+  |

---

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## TODO list

- [ ] JWT 鉴权中间件完善（当前 handler 内手动判断）
- [ ] Go 后端单元测试覆盖
- [ ] 前端适配 Go 后端 `/api/v1` 前缀
- [ ] Python 后端：生产环境使用 `gunicorn` 启动，避免 Flask reloader 导致调度器重复初始化（`"调度器已经在运行中"` 日志的根因）

## 许可证

MIT License
