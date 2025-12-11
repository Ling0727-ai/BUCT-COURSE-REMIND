# 作业DDL前24小时自动提醒功能说明

## 功能概述

系统会自动检测即将到期的作业和测试，并在截止时间前24小时自动发送邮件提醒给用户，无需手动设置。

## 功能特点

### 1. 自动检测

- **检查频率**: 每小时检查一次
- **时间范围**: 检测23-25小时后到期的作业（允许±1小时的时间误差）
- **检测对象**: 所有已登录且设置了邮箱的用户

### 2. 智能过滤

系统会自动过滤以下情况，避免不必要的提醒：

- ✅ 已完成的作业/测试
- ✅ 已删除的作业/测试（在回收站中）
- ✅ 已经创建过提醒的作业（避免重复提醒）

### 3. 提醒内容

自动发送的邮件包含以下信息：

```
⏰ 自动提醒：作业即将截止

科目: [科目名称]
标题: [作业标题]
截止时间: [具体日期时间]
剩余时间: 约24小时

请及时完成！
```

## 技术实现

### 调度器配置

- **文件**: `app/scheduler.py`
- **类**: `CourseDataScheduler`
- **检查间隔**: 3600秒（1小时）

### 核心方法

```python
def _check_and_create_auto_reminders(self):
    """
    检查即将到期的作业，自动创建截止一天前的提醒
    
    工作流程：
    1. 计算24小时后的时间范围（23-25小时）
    2. 遍历所有用户
    3. 获取用户的课程数据
    4. 筛选在时间范围内的作业
    5. 过滤已完成/已删除/已提醒的作业
    6. 创建提醒记录，状态为'scheduled'
    7. 等待提醒处理器发送邮件
    """
```

### 数据库结构

提醒记录存储在 `scheduled_reminders` 集合中：

```javascript
{
    user_id: ObjectId,           // 用户ID
    type: 'assignment',          // 类型：作业提醒
    target_id: String,           // 作业ID
    email: String,               // 收件人邮箱
    message: String,             // 提醒内容
    scheduled_time: DateTime,    // 计划发送时间
    status: String,              // 状态：scheduled/sent/failed/cancelled
    auto_created: true,          // 标记为自动创建
    created_at: DateTime,        // 创建时间
    updated_at: DateTime         // 更新时间
}
```

### 提醒处理流程

```
1. 检查阶段（每小时）
   ↓
2. 创建提醒记录（status: scheduled）
   ↓
3. 处理阶段（每5秒）
   ↓
4. 检查作业状态（是否完成/删除）
   ↓
5. 发送邮件
   ↓
6. 更新状态（sent/failed/cancelled）
```

## 状态说明

| 状态          | 说明            |
|-------------|---------------|
| `scheduled` | 已创建，等待发送      |
| `sent`      | 已成功发送         |
| `failed`    | 发送失败          |
| `cancelled` | 已取消（作业已完成/删除） |

## 配置要求

### 邮箱配置

在 `.env` 文件中配置邮件服务器：

```bash
MAIL_SMTP_SERVER=smtp.163.com
MAIL_SMTP_PORT=465
MAIL_SENDER=your_email@163.com
MAIL_PASSWORD=your_auth_code
```

### 用户要求

- 用户必须已注册并设置邮箱
- 用户必须已配置学号和教务系统密码（用于获取作业数据）

## 日志监控

### 关键日志

```bash
# 检查开始
开始检查即将到期的作业（2025-11-17 10:00 - 2025-11-17 12:00）

# 创建提醒
为用户 [user_id] 的作业 [作业标题] 创建自动提醒（截止: 2025-11-18 10:00:00）

# 检查完成
自动提醒检查完成，共创建 5 个提醒

# 发送成功
定时提醒已发送 到 user@example.com

# 取消发送
定时提醒已取消（assignment completed）: [task_id]
```

## 故障排查

### 没有收到提醒邮件

1. 检查邮箱配置是否正确
2. 检查用户是否设置了邮箱
3. 检查调度器是否正常运行
4. 查看日志文件中的错误信息
5. 检查作业是否在23-25小时范围内
6. 确认作业没有被标记为已完成或已删除

### 收到重复提醒

- 系统会自动检查是否已创建提醒，正常情况下不会重复
- 如果出现重复，检查 `scheduled_reminders` 集合中的记录

### 提醒时间不准确

- 系统使用北京时间（UTC+8）
- 检查服务器时区设置
- 检查作业截止时间解析是否正确

## 手动测试

### 测试自动提醒功能

```python
from app import create_app
from app.scheduler import get_scheduler

app = create_app()
with app.app_context():
    scheduler = get_scheduler()
    scheduler._check_and_create_auto_reminders()
```

### 查看待发送的提醒

```python
from app import mongo
reminders = list(mongo.db.scheduled_reminders.find({
    'status': 'scheduled',
    'auto_created': True
}))
print(f"待发送提醒数量: {len(reminders)}")
```

## 性能优化

### 当前优化

- 使用索引加速查询（user_id, target_id, status）
- 批量处理，每次最多处理50条提醒
- 用户之间间隔2秒，避免服务器过载

### 建议索引

```javascript
// MongoDB 索引建议
db.scheduled_reminders.createIndex({ user_id: 1, target_id: 1, type: 1 })
db.scheduled_reminders.createIndex({ status: 1, scheduled_time: 1 })
db.scheduled_reminders.createIndex({ auto_created: 1, created_at: -1 })
```

## 未来改进

- [ ] 支持用户自定义提醒时间（如提前2天、3天等）
- [ ] 支持多次提醒（如提前3天、1天、1小时）
- [ ] 支持其他通知方式（微信、短信等）
- [ ] 提供提醒历史记录查询界面
- [ ] 支持用户关闭自动提醒功能

## 相关文件

- `app/scheduler.py` - 调度器核心代码
- `app/notification_services.py` - 邮件发送服务
- `app/assignment_status.py` - 作业状态管理
- `app/course_data.py` - 课程数据管理
- `app/__init__.py` - 调度器初始化

