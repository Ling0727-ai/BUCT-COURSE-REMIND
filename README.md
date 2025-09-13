# BUCT 课程提醒系统

一个用于北京化工大学课程提醒和作业监控的自动化系统。

## 功能特性

- 📚 自动登录 BUCT 教学平台
- 📊 获取待办作业和测试任务
- 🔔 支持多种通知方式（邮件、Telegram、Discord、Slack、自定义Webhook）
- 🎯 详细的作业和测试信息展示
- 📱 现代化 Web 界面配置
- 🔒 安全的认证机制

## 项目结构

```
BUCT-couse-remind/
├── buct_course/          # BUCT 课程相关模块
│   ├── __init__.py
│   ├── auth.py          # 认证模块
│   ├── course_utils.py  # 课程工具
│   ├── test_utils.py    # 测试工具
│   ├── exceptions.py    # 异常处理
│   └── test_utils.py
├── u校园/               # U校园相关模块
│   ├── __init__.py
│   ├── api_client.py    # API 客户端
│   ├── aes_crypto.py    # AES 加密
│   ├── aes_encrypt.py   # AES 加密工具
│   ├── utils.py         # 工具函数
│   └── exceptions.py    # 异常处理
├── web/                 # Web 界面
│   └── app.py          # Flask 应用
├── deced/               # 文档/配置目录
├── buct_course_test_main.py  # 主测试脚本
├── u校园_test_main.py        # U校园测试脚本
├── readme.txt           # 原始说明文件
├── LICENSE             # MIT 许可证
└── README.md           # 项目说明
```

## 安装使用

### 环境要求

- Python 3.7+
- 所需的 Python 包（见 requirements.txt）

### 快速开始

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd BUCT-couse-remind
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行主程序**
   ```bash
   python buct_course_test_main.py
   ```

4. **配置 Web 界面**
   ```bash
   cd web
   python app.py
   ```
   然后在浏览器中访问 `http://localhost:5000`

## 配置说明

### 基础配置

通过 Web 界面或直接编辑配置文件设置：

- **账号/密码**: BUCT 教学平台登录凭据
- **服务器地址**: 后端服务地址（默认: http://localhost:8080）

### 通知配置

系统支持多种通知方式：

1. **邮件通知**
   - SMTP 服务器配置
   - 发件邮箱和密码
   - 收件邮箱地址

2. **Telegram Bot**
   - Bot Token
   - Chat ID

3. **Discord Webhook**
   - Webhook URL

4. **Slack Webhook**
   - Webhook URL

5. **自定义 Webhook**
   - 自定义 URL 和请求配置

## API 接口

### 主要端点

- `GET /api/health` - 服务健康检查
- `POST /api/settings` - 保存系统设置
- `GET /api/tasks` - 获取待办任务
- `GET /api/tests` - 获取测试信息

## 开发说明

### 模块说明

- **buct_course**: 处理 BUCT 教学平台相关功能
- **u校园**: 处理 U校园平台相关功能
- **web**: 提供 Web 配置界面

### 扩展开发

要添加新的通知方式，请在 `webhookTypes` 配置中添加相应的类型定义。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 免责声明

本项目仅用于学习和研究目的，请遵守学校相关规定，合理使用。

---

**注意**: 使用前请确保您有权访问相关系统，并遵守相关使用条款。