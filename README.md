# BUCT课程提醒系统

一个基于 Flask + MongoDB + Vue.js 的课程作业提醒系统，支持自动获取教务系统信息并发送通知。

## 功能特性

- 🔐 用户注册登录系统
- 📚 学生信息管理（学号、外部系统密码）
- 📧 邮箱验证码验证
- 🔔 多种通知方式（邮件、Telegram、Discord等）
- ⚙️ 灵活的系统设置
- 📱 响应式前端界面

## 数据库结构

### 用户表 (users)
```json
{
    "_id": "ObjectId",
    "username": "用户名",
    "password_hash": "加密后的登录密码", 
    "email": "邮箱地址",
    "student_id": "学号",
    "s_password": "外部网站密码",
    "is_admin": false,
    "created_at": "创建时间",
    "updated_at": "更新时间"
}
```

## 项目结构

```
BUCT-couse-remind/
├── web/
│   ├── backend/           # Flask后端
│   │   ├── app/          # 应用模块
│   │   │   ├── __init__.py
│   │   │   ├── model.py   # 数据库模型
│   │   │   ├── auth.py    # 认证相关
│   │   │   ├── settings.py # 设置管理
│   │   │   └── ...
│   │   ├── config.py      # 配置文件
│   │   ├── app.py         # 应用入口
│   │   └── requirements.txt
│   └── fronted/           # Vue.js前端
│       └── src/
│           ├── views/     # 页面组件
│           │   ├── Register.vue  # 注册页面
│           │   ├── Settings.vue  # 设置页面
│           │   └── ...
│           └── ...
└── README.md
```

## 安装和运行

### 后端设置

1. 进入后端目录：
```bash
cd web/backend
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填入正确的配置信息
```

4. 启动后端服务：
```bash
python app.py
```

### 前端设置

1. 进入前端目录：
```bash
cd web/fronted
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run serve
```

## API接口

### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/status` - 获取登录状态
- `GET /api/auth/user-info` - 获取用户信息
- `POST /api/auth/update-student-info` - 更新学生信息
- `POST /api/auth/send-verification-code` - 发送验证码
- `POST /api/auth/verify-code` - 验证验证码

### 设置相关
- `GET /api/settings` - 获取系统设置
- `POST /api/settings` - 保存系统设置

## 主要功能

### 1. 用户注册
- 支持用户名、邮箱、密码注册
- 可选填写学号和外部系统密码
- 邮箱验证码验证
- 密码强度检测

### 2. 学生信息管理
- 在设置页面可以配置学号和外部系统密码
- 用于自动登录教务系统获取作业信息
- 密码安全存储

### 3. 通知系统
- 支持多种通知方式：邮件、Telegram、Discord、Slack等
- 可配置多个通知渠道
- 支持测试通知功能

### 4. 系统设置
- 服务器地址配置
- Webhook通知配置
- 用户个人信息管理

## 环境要求

- Python 3.8+
- MongoDB 4.0+
- Node.js 14+
- Vue.js 3.x

## 配置说明

### 邮件配置
在 `.env` 文件中配置邮件服务器信息：
```
MAIL_SMTP_SERVER=smtp.163.com
MAIL_SMTP_PORT=465
MAIL_SENDER=your_email@163.com
MAIL_PASSWORD=your_auth_code
```

### MongoDB配置
```
MONGO_URI=mongodb://localhost:27017/buct_course_remind
```

## 开发说明

### 后端开发
- 使用 Flask 框架
- MongoDB 作为数据库
- 支持 CORS 跨域请求
- 使用 session 进行用户认证

### 前端开发
- 使用 Vue.js 3 + Composition API
- 响应式设计，支持移动端
- 使用 Vue Router 进行路由管理
- 现代化的 UI 设计

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## TODO list
-  [ ] 添加已删除框
-  [ ] 添加webhook功能
-  [ ] 完善首页作业/测试排序
-  [ ] 添加网站标志
-  [ ] 完善提醒功能

## 许可证

MIT License
