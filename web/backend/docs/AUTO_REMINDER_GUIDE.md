# 自动提醒功能使用指南

## 快速开始

### 1. 确保系统正常运行

```bash
# 启动后端服务
cd web/backend
python app.py
```

系统启动后，调度器会自动初始化并开始工作。

### 2. 配置邮箱服务

在 `web/backend/.env` 文件中配置：

```bash
MAIL_SMTP_SERVER=smtp.163.com
MAIL_SMTP_PORT=465
MAIL_SENDER=your_email@163.com
MAIL_PASSWORD=your_auth_code
```

**注意**:

- 使用163邮箱需要使用授权码而非登录密码
- 授权码获取: 邮箱设置 → POP3/SMTP/IMAP → 开启服务 → 获取授权码

### 3. 用户设置

用户需要完成以下设置才能收到自动提醒：

1. **注册账号并设置邮箱**
    - 在注册页面填写邮箱地址
    - 完成邮箱验证

2. **配置教务系统账号**
    - 进入设置页面
    - 填写学号和教务系统密码
    - 系统将用此账号获取作业数据

## 工作原理

```
用户登录 
   ↓
系统自动刷新作业数据（12小时一次）
   ↓
调度器检查即将到期的作业（每小时一次）
   ↓
发现23-25小时后到期的作业
   ↓
创建自动提醒记录
   ↓
提醒处理器发送邮件（每5秒检查一次）
   ↓
用户收到邮件提醒
```

## 测试功能

### 方法1: 使用测试脚本

```bash
cd web/backend
python test_auto_reminder.py
```

这个脚本会：

- 显示调度器配置信息
- 统计用户和提醒记录
- 允许手动触发一次检查
- 检查邮件配置

### 方法2: 查看日志

```bash
# 查看实时日志
tail -f logs/app.log

# 搜索自动提醒相关日志
grep "自动提醒" logs/app.log
grep "自动检测" logs/app.log
```

关键日志示例：

```
2025-11-17 10:00:00 - 开始检查即将到期的作业
2025-11-17 10:00:05 - 为用户 xxx 的作业 xxx 创建自动提醒
2025-11-17 10:00:10 - 自动提醒检查完成，共创建 3 个提醒
2025-11-17 10:00:15 - 定时提醒已发送 到 user@example.com
```

### 方法3: 直接查询数据库

```javascript
// 连接MongoDB
use buct_course_remind

// 查看所有自动创建的提醒
db.scheduled_reminders.find({ auto_created: true }).pretty()

// 查看待发送的提醒
db.scheduled_reminders.find({ status: 'scheduled' }).pretty()

// 查看今天创建的提醒
db.scheduled_reminders.find({
    auto_created: true,
    created_at: {
        $gte: new Date(new Date().setHours(0,0,0,0))
    }
}).count()

// 统计各状态的提醒数量
db.scheduled_reminders.aggregate([
    { $match: { auto_created: true } },
    { $group: { _id: '$status', count: { $sum: 1 } } }
])
```

## 常见问题

### Q1: 为什么没有收到提醒邮件？

**检查清单**:

- [ ] 邮箱配置是否正确 (`.env` 文件)
- [ ] 用户是否设置了邮箱
- [ ] 用户是否配置了教务系统账号
- [ ] 是否有作业在23-25小时后到期
- [ ] 作业是否被标记为已完成或已删除
- [ ] 调度器是否正常运行

**排查步骤**:

```bash
# 1. 运行测试脚本
python test_auto_reminder.py

# 2. 查看最近的提醒记录
# 如果有记录但状态是failed，查看error字段

# 3. 检查邮件配置
python -c "import os; print('Password set:', bool(os.getenv('MAIL_PASSWORD')))"
```

### Q2: 收到了重复的提醒

这种情况不应该发生，系统有去重机制。如果出现：

1. 检查 `scheduled_reminders` 集合中是否有重复记录
2. 查看日志中是否有异常
3. 联系开发者报告bug

### Q3: 提醒时间不准确

系统使用北京时间（UTC+8）:

- 服务器时区应该正确设置
- 如果在国外部署，可能需要调整时区

### Q4: 如何关闭自动提醒？

当前版本不支持关闭，但可以：

1. 不设置邮箱（不会发送）
2. 不配置教务系统账号（不会获取作业）
3. 标记作业为已完成（不会提醒该作业）

## 性能说明

### 资源占用

- **内存**: 约20-50MB (取决于用户数量)
- **CPU**: 极低，只在检查时短暂使用
- **网络**: 发送邮件时使用，流量很小

### 并发处理

- 用户之间间隔2秒处理，避免过载
- 每次最多处理50条提醒
- 如果用户很多，可能需要调整配置

### 扩展性

当前配置适合：

- 用户数: 1-1000
- 作业数: 1-10000
- 每小时提醒: 1-100

如需支持更大规模，考虑：

- 使用消息队列 (RabbitMQ/Redis)
- 使用异步任务框架 (Celery)
- 增加调度器实例

## 高级配置

### 修改检查间隔

编辑 `app/scheduler.py`:

```python
class CourseDataScheduler:
    def __init__(self):
        # 修改为2小时检查一次
        self.auto_reminder_check_interval = 7200  # 秒
```

### 修改时间范围

编辑 `app/scheduler.py` 中的 `_check_and_create_auto_reminders` 方法:

```python
# 检查48小时后到期的作业
tomorrow_start = now + timedelta(hours=47)
tomorrow_end = now + timedelta(hours=49)
```

### 自定义邮件内容

编辑 `app/scheduler.py`:

```python
message = f"""⏰ 自动提醒：{assignment_type}即将截止

科目: {subject}
标题: {title}
截止时间: {deadline_display}
剩余时间: 约24小时

[在这里添加自定义内容]

请及时完成！"""
```

## 监控建议

### 日常监控

1. 每天检查提醒发送情况
2. 关注failed状态的提醒
3. 定期清理历史记录

### 告警设置

建议设置以下告警：

- 连续3次检查失败
- failed提醒超过10条
- 邮件发送失败率超过10%

### 数据备份

定期备份 `scheduled_reminders` 集合：

```bash
mongodump --db buct_course_remind --collection scheduled_reminders
```

## 更新日志

- **v3.4.2** (2025-11-17)
    - 初次实现自动提醒功能
    - 支持DDL前24小时提醒
    - 智能过滤已完成/已删除作业
    - 每小时自动检查

## 技术支持

如遇到问题，请提供以下信息：

1. 系统版本
2. 错误日志
3. 提醒记录ID
4. 复现步骤

GitHub Issues: https://github.com/Ling0727-ai/BUCT-course-remind/issues

