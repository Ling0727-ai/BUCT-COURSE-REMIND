# DDL前24小时自动提醒功能诊断指南

## 问题现象

DDL前一天的作业/测试提醒无法正常运行

## 可能的原因

### 1. 调度器未启动

**检查方法:**

```bash
# 查看日志，搜索调度器启动信息
grep "调度器已启动" logs/app.log
grep "课程数据定时刷新调度器已初始化" logs/app.log
```

**解决方案:**
确保应用正常启动，调度器会自动初始化。

### 2. 没有符合条件的作业

**检查条件:**

- 作业截止时间在 23-25 小时后
- 用户设置了邮箱
- 用户配置了教务系统账号（学号和密码）
- 作业未被标记为已完成或已删除

**检查方法:**

```bash
# 运行诊断脚本
cd web/backend
python manual_check_auto_reminder.py
```

### 3. 邮件配置问题

**检查方法:**

```bash
# 检查环境变量
echo $MAIL_SMTP_SERVER
echo $MAIL_SMTP_PORT
echo $MAIL_SENDER
echo $MAIL_PASSWORD
```

**解决方案:**
确保 `.env` 文件中配置了正确的邮件服务器信息。

### 4. 时区问题

**检查方法:**

```bash
# 查看系统时间
date

# 查看Python时区
python -c "from datetime import datetime; print(datetime.now())"
```

**解决方案:**
确保系统时间正确，代码中使用的是北京时间（UTC+8）。

### 5. 调度器检查间隔太长

**当前配置:**

- 自动提醒检查间隔: 3600秒（1小时）
- 提醒发送检查间隔: 5秒

**说明:**
调度器每小时检查一次是否有新的作业需要提醒。如果刚启动应用，可能需要等待最多1小时才会执行第一次检查。

**解决方案:**
手动触发检查：

```bash
python manual_check_auto_reminder.py
```

## 诊断步骤

### 步骤1: 检查日志

```bash
cd web/backend
tail -f logs/app.log | grep -E "自动提醒|定时提醒|邮件发送"
```

查找以下关键日志:

- `开始检查即将到期的作业` - 检查是否定期执行
- `共有 X 个用户需要检查` - 确认有用户
- `为用户 xxx 的作业 xxx 创建自动提醒` - 确认创建了提醒
- `定时提醒已发送到 xxx` - 确认发送成功

### 步骤2: 运行诊断脚本

```bash
python manual_check_auto_reminder.py
```

这个脚本会:

1. 显示当前时间和检测范围
2. 列出所有用户及其邮箱
3. 检查每个用户的作业数据
4. 显示符合条件的作业
5. 手动触发一次自动提醒检查
6. 尝试发送提醒邮件
7. 显示发送结果

### 步骤3: 检查数据库

```javascript
// 连接MongoDB
use buct_course_remind

// 1. 检查用户配置
db.users.find({
    email: { $exists: true, $ne: null, $ne: '' }
}).count()

// 2. 检查作业数据
db.course_data.find().count()

// 3. 检查提醒记录
db.scheduled_reminders.find({ auto_created: true }).pretty()

// 4. 查看最近的提醒
db.scheduled_reminders.find().sort({ created_at: -1 }).limit(5).pretty()

// 5. 统计提醒状态
db.scheduled_reminders.aggregate([
    { $match: { auto_created: true } },
    { $group: { _id: '$status', count: { $sum: 1 } } }
])
```

### 步骤4: 测试邮件发送

```python
# 创建测试脚本 test_email.py
from app import create_app
from app.notification_services import send_email_notification

app = create_app()
with app.app_context():
    config = {'to_email': 'your_email@example.com'}
    message = "这是一封测试邮件"
    result = send_email_notification(config, message)
    print(f"发送结果: {'成功' if result else '失败'}")
```

运行:

```bash
python test_email.py
```

## 常见问题解答

### Q1: 日志中没有"开始检查即将到期的作业"

**原因:** 调度器可能没有启动或刚启动不久（需要等1小时）

**解决:**

1. 检查应用是否正常运行
2. 查看启动日志是否有"课程数据定时刷新调度器已初始化"
3. 手动运行 `manual_check_auto_reminder.py`

### Q2: 日志显示"没有需要提醒的作业"

**原因:**

- 没有作业在23-25小时后到期
- 用户没有设置邮箱
- 作业被标记为已完成或已删除

**解决:**
运行 `manual_check_auto_reminder.py` 查看详细信息

### Q3: 创建了提醒但没有发送

**原因:**

- 邮件配置错误
- SMTP服务器连接失败
- 邮箱密码不正确（注意：163邮箱需要授权码）

**解决:**

1. 检查 `.env` 文件中的邮件配置
2. 运行 `test_email.py` 测试邮件发送
3. 查看日志中的错误信息

### Q4: 提醒发送失败，状态为failed

**原因:**
查看数据库中的 error 字段

**解决:**

```javascript
// 查看失败原因
db.scheduled_reminders.find({ 
    status: 'failed',
    auto_created: true 
}).forEach(function(doc) {
    print('Email:', doc.email);
    print('Error:', doc.error);
    print('---');
})
```

根据错误信息进行相应处理。

### Q5: 时间解析失败

**原因:** 作业的deadline格式不被支持

**当前支持的格式:**

- ISO格式: `2025-11-18T10:00:00`
- ISO格式（带时区）: `2025-11-18T10:00:00Z`
- 中文格式: `2025年11月18日 10:00:00`

**解决:**
如果有其他格式，需要在代码中添加解析逻辑。

## 手动触发提醒

如果需要立即测试，不想等待1小时:

### 方法1: 使用诊断脚本

```bash
python manual_check_auto_reminder.py
```

### 方法2: 直接调用调度器

```python
from app import create_app
from app.scheduler import get_scheduler

app = create_app()
with app.app_context():
    scheduler = get_scheduler()
    
    # 检查并创建提醒
    scheduler._check_and_create_auto_reminders()
    
    # 发送提醒
    scheduler._process_due_reminders()
```

### 方法3: 修改检查间隔（临时）

编辑 `app/scheduler.py`:

```python
class CourseDataScheduler:
    def __init__(self):
        # 改为5分钟检查一次（仅用于测试）
        self.auto_reminder_check_interval = 300  # 5分钟
```

重启应用后，调度器会每5分钟检查一次。

## 监控建议

### 设置日志监控

```bash
# 持续监控自动提醒相关日志
tail -f logs/app.log | grep -E "自动提醒|定时提醒"

# 监控错误日志
tail -f logs/app.log | grep ERROR
```

### 定期检查数据库

每天检查一次提醒发送情况:

```javascript
// 今天的提醒统计
db.scheduled_reminders.aggregate([
    {
        $match: {
            auto_created: true,
            created_at: {
                $gte: new Date(new Date().setHours(0,0,0,0))
            }
        }
    },
    {
        $group: {
            _id: '$status',
            count: { $sum: 1 }
        }
    }
])
```

### 设置告警

如果有监控系统，可以设置以下告警:

- 连续3小时没有"开始检查即将到期的作业"日志
- failed状态的提醒超过5条
- 邮件发送失败率超过20%

## 联系支持

如果以上方法都无法解决问题，请提供:

1. 诊断脚本的完整输出
2. 最近的应用日志（最近1小时）
3. 数据库中的提醒记录（`db.scheduled_reminders.find().pretty()`）
4. 邮件配置（不要包含密码）

GitHub Issues: https://github.com/Ling0727-ai/BUCT-course-remind/issues

