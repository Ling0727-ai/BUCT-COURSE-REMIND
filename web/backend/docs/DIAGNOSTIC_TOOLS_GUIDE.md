# 自动提醒功能诊断工具使用说明

## 工具列表

### 1. manual_check_auto_reminder.py

**用途:** 全面诊断自动提醒功能，检查所有环节

**运行方式:**

```bash
cd web/backend
python manual_check_auto_reminder.py
```

**输出内容:**

- 当前时间和检测时间范围
- 用户统计（总用户数、有邮箱的用户数）
- 每个用户的作业数据
- 符合条件的作业列表
- 手动触发提醒检查
- 尝试发送提醒
- 发送结果统计

**适用场景:**

- 初次配置后验证功能
- 怀疑自动提醒不工作时
- 想查看详细的检查过程

### 2. test_email_sending.py

**用途:** 测试邮件发送功能是否正常

**运行方式:**

```bash
cd web/backend
python test_email_sending.py
```

**交互流程:**

1. 显示当前邮件配置
2. 要求输入测试邮箱地址
3. 发送测试邮件
4. 显示发送结果

**适用场景:**

- 验证邮箱配置是否正确
- 测试SMTP连接
- 检查邮件能否正常送达

### 3. test_auto_reminder.py

**用途:** 查看自动提醒功能的配置和统计信息

**运行方式:**

```bash
cd web/backend
python test_auto_reminder.py
```

**输出内容:**

- 调度器配置（检查间隔等）
- 用户统计
- 提醒记录统计
- 最近的提醒记录
- 可选：手动触发检查
- 邮件配置检查

**适用场景:**

- 快速查看系统状态
- 了解提醒发送情况
- 定期检查功能运行

## 使用流程

### 场景1: 首次配置后验证

```bash
# 步骤1: 测试邮件发送
python test_email_sending.py
# 输入你的邮箱，检查是否收到测试邮件

# 步骤2: 运行完整诊断
python manual_check_auto_reminder.py
# 查看是否有符合条件的作业，是否创建了提醒

# 步骤3: 检查日志
tail -f logs/app.log | grep -E "自动提醒|定时提醒"
```

### 场景2: 怀疑功能不工作

```bash
# 步骤1: 查看状态
python test_auto_reminder.py
# 不选择手动触发，只查看统计信息

# 步骤2: 检查日志
grep "自动提醒" logs/app.log | tail -20
# 查看最近的自动提醒检查记录

# 步骤3: 如果日志很少或没有，运行完整诊断
python manual_check_auto_reminder.py
# 这会手动触发一次完整的检查和发送流程

# 步骤4: 如果仍然失败，测试邮件发送
python test_email_sending.py
```

### 场景3: 定期检查

```bash
# 每天运行一次，查看统计信息
python test_auto_reminder.py

# 或者只查看日志
grep "自动提醒检查完成" logs/app.log | tail -5
```

## 常见输出解读

### 正常输出示例

```
开始检查即将到期的作业（当前时间: 2025-11-17 10:00:00, 检测范围: ...）
共有 10 个用户需要检查
用户 xxx 有 5 个作业/测试
为用户 xxx 的作业 xxx 创建自动提醒（截止: 2025-11-18 10:00:00）
自动提醒检查完成: 检查了 10 个用户（其中 8 个有邮箱），共 50 个作业/测试，创建了 3 个提醒

发现 3 个到期的提醒需要发送
定时提醒已发送到 user@example.com
提醒处理完成: 发送成功 3, 发送失败 0, 已取消 0
```

**说明:** 一切正常，找到了作业，创建了提醒，并且成功发送。

### 异常输出示例1

```
共有 10 个用户需要检查
自动提醒检查完成: 检查了 10 个用户（其中 0 个有邮箱），共 0 个作业/测试，创建了 0 个提醒
```

**问题:** 用户没有设置邮箱，或者没有作业数据

**解决:**

1. 检查用户是否设置了邮箱（Settings页面）
2. 检查是否配置了教务系统账号
3. 手动刷新一次数据库

### 异常输出示例2

```
为用户 xxx 的作业 xxx 创建自动提醒（截止: 2025-11-18 10:00:00）
自动提醒检查完成: 检查了 10 个用户（其中 8 个有邮箱），共 50 个作业/测试，创建了 3 个提醒

发现 3 个到期的提醒需要发送
邮箱密码未配置，无法发送邮件 (MAIL_PASSWORD 未设置)
定时提醒发送失败到 user@example.com
提醒处理完成: 发送成功 0, 发送失败 3, 已取消 0
```

**问题:** 邮箱密码未配置

**解决:** 在 `.env` 文件中配置 `MAIL_PASSWORD`

### 异常输出示例3

```
开始检查即将到期的作业（当前时间: 2025-11-17 10:00:00, 检测范围: ...）
共有 10 个用户需要检查
自动提醒检查完成: 检查了 10 个用户（其中 8 个有邮箱），共 50 个作业/测试，创建了 0 个提醒
```

**问题:** 没有符合条件的作业

**可能原因:**

1. 没有作业在23-25小时后到期
2. 所有符合条件的作业都已完成或删除
3. 已经为这些作业创建过提醒了

**验证:** 运行 `python manual_check_auto_reminder.py` 查看详细信息

## 日志位置

- **应用日志:** `web/backend/logs/app.log`
- **错误日志:** 同上，包含ERROR级别的日志

**查看实时日志:**

```bash
tail -f logs/app.log
```

**搜索特定日志:**

```bash
grep "自动提醒" logs/app.log
grep "邮件发送" logs/app.log
grep ERROR logs/app.log
```

## 数据库查询

### 查看所有自动提醒

```javascript
db.scheduled_reminders.find({ auto_created: true }).pretty()
```

### 查看待发送的提醒

```javascript
db.scheduled_reminders.find({ status: 'scheduled' }).pretty()
```

### 查看发送失败的提醒

```javascript
db.scheduled_reminders.find({ 
    status: 'failed',
    auto_created: true 
}).pretty()
```

### 统计提醒状态

```javascript
db.scheduled_reminders.aggregate([
    { $match: { auto_created: true } },
    { $group: { _id: '$status', count: { $sum: 1 } } }
])
```

### 查看今天的提醒

```javascript
db.scheduled_reminders.find({
    auto_created: true,
    created_at: {
        $gte: new Date(new Date().setHours(0,0,0,0))
    }
}).pretty()
```

## 故障排除快速参考

| 问题        | 可能原因                                        | 解决方案                                    |
|-----------|---------------------------------------------|-----------------------------------------|
| 没有创建提醒    | 1. 没有符合条件的作业<br>2. 用户没有邮箱<br>3. 作业被标记为完成/删除 | 运行 `manual_check_auto_reminder.py` 查看详情 |
| 创建了但没发送   | 1. 邮箱配置错误<br>2. SMTP连接失败                    | 运行 `test_email_sending.py` 测试           |
| 发送失败      | 1. 密码错误<br>2. 端口被封<br>3. 邮箱限制               | 检查 `.env` 配置，查看错误日志                     |
| 日志中没有检查记录 | 1. 调度器未启动<br>2. 刚启动不久（需等1小时）                | 查看启动日志，或手动触发检查                          |

## 注意事项

1. **测试脚本会实际发送邮件**，不要频繁测试以免被判定为垃圾邮件
2. **手动触发检查会创建新的提醒记录**，如果数据库中已有记录，不会重复创建
3. **诊断脚本不会删除任何数据**，可以放心运行
4. **日志文件可能很大**，定期清理或使用 `tail` 命令查看最新内容

## 获取帮助

如果以上工具无法解决问题，请:

1. 保存诊断脚本的完整输出
2. 收集最近1小时的日志
3. 导出相关的数据库记录
4. 在GitHub上创建Issue并附上以上信息

GitHub Issues: https://github.com/Ling0727-ai/BUCT-course-remind/issues

