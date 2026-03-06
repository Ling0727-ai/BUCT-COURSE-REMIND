# DDL自动邮件提醒功能故障排查指南（服务器端）

## 🔍 快速诊断步骤

### 1️⃣ 检查日志文件

```bash
# 进入后端目录
cd /path/to/BUCT-course-remind/web/backend

# 查看最新日志
tail -n 100 logs/app.log

# 实时监控日志
tail -f logs/app.log

# 搜索自动提醒相关日志
grep "自动提醒" logs/app.log | tail -n 20
grep "邮件发送" logs/app.log | tail -n 20
```

**关键日志标识：**

- `🔔 开始检查即将到期的作业` - 调度器正在工作
- `✅ 为用户 xxx 创建自动提醒` - 成功创建提醒
- `✅ 邮件发送成功` - 邮件发送成功
- `❌ 邮箱密码未配置` - 邮件配置问题
- `❌ SMTP认证失败` - 邮箱认证问题
- `🚫 提醒已取消` - 作业已完成或删除

### 2️⃣ 测试邮件配置

```bash
# 运行邮件配置测试脚本
python test_email_config.py
```

这个脚本会：

- ✅ 显示当前邮件配置
- ✅ 检查密码是否已配置
- ✅ 尝试发送测试邮件
- ✅ 显示详细的错误信息

### 3️⃣ 检查环境变量

```bash
# 查看.env文件配置
cat .env | grep MAIL_

# 应该看到以下配置：
# MAIL_SMTP_SERVER=smtp.163.com
# MAIL_SMTP_PORT=465
# MAIL_SENDER=buct_course_remind@163.com
# MAIL_PASSWORD=你的授权码
```

**⚠️ 重要：** `MAIL_PASSWORD` 必须是163邮箱的**授权码**，不是登录密码！

### 4️⃣ 检查MongoDB数据

```bash
# 连接MongoDB
mongo mongodb://REDACTED_MONGO_USER:REDACTED_MONGO_PASSWORD@localhost:27017/buct-course --authSource admin

# 或使用Docker
docker exec -it mongodb mongo -u REDACTED_MONGO_USER -p REDACTED_MONGO_PASSWORD --authSource admin buct-course
```

在MongoDB中执行：

```javascript
// 检查有邮箱的用户数量
db.users.count({email: {$exists: true, $ne: null, $ne: ''}})

// 查看提醒记录统计
db.scheduled_reminders.aggregate([
  {$group: {_id: "$status", count: {$sum: 1}}}
])

// 查看最近的自动提醒
db.scheduled_reminders.find({auto_created: true}).sort({created_at: -1}).limit(5).pretty()

// 查看失败的提醒
db.scheduled_reminders.find({status: 'failed'}).sort({created_at: -1}).limit(5).pretty()
```

## 🐛 常见问题和解决方案

### ❌ 问题1: 邮件配置错误

**症状：** 日志显示 `❌ 邮箱密码未配置` 或 `❌ SMTP认证失败`

**原因：**

- MAIL_PASSWORD未设置或设置为默认值
- 使用了登录密码而不是授权码
- 授权码过期或被重置

**解决方案：**

1. 登录163邮箱网页版
2. 进入 设置 → POP3/SMTP/IMAP
3. 开启SMTP服务
4. 获取新的授权码
5. 更新.env文件中的MAIL_PASSWORD
6. 重启服务：`docker-compose restart backend`

### ❌ 问题2: 调度器未运行

**症状：** 日志中没有 `🔔 开始检查即将到期的作业` 的记录

**检查方法：**

```bash
# 查看日志是否有调度器启动信息
grep "调度器已启动" logs/app.log
```

**解决方案：**

```bash
# 重启后端服务
docker-compose restart backend

# 查看容器日志
docker-compose logs -f backend
```

### ❌ 问题3: 没有符合条件的作业

**症状：** 日志显示 `🆕 新创建提醒: 0 个`

**可能原因：**

- 用户没有设置邮箱
- 用户没有配置教务系统账号
- 没有即将到期（23-25小时后）的作业
- 作业都已完成或已删除

**检查方法：**
查看日志中的统计信息：

```
📊 自动提醒检查完成统计:
  👥 检查用户: X 个
  📧 有邮箱: X 个
  📚 有作业: X 个
  🎯 在时间范围内: X 个
```

**解决方案：**

1. 确保用户已设置邮箱（在设置页面）
2. 确保用户已配置学号和教务系统密码
3. 检查作业截止时间是否在24小时后

### ❌ 问题4: 网络连接问题

**症状：** 日志显示超时或连接被拒绝

**解决方案：**

```bash
# 测试能否连接到SMTP服务器
telnet smtp.163.com 465
# 或
nc -zv smtp.163.com 465

# 如果连接失败，检查防火墙规则
iptables -L -n | grep 465

# 检查DNS解析
nslookup smtp.163.com
```

### ❌ 问题5: 邮件被标记为垃圾邮件

**症状：** 发送成功但用户收不到邮件

**检查方法：**

- 让用户检查垃圾邮件箱
- 检查邮件主题是否被过滤

**解决方案：**

1. 建议用户将发件人添加到通讯录
2. 从垃圾邮件中标记为"非垃圾邮件"

## 📊 查看运行状态

### 实时监控

创建监控脚本 `monitor_reminders.sh`：

```bash
#!/bin/bash
echo "=========================================="
echo "DDL自动提醒功能监控"
echo "=========================================="
echo ""

echo "📋 最近1小时的自动提醒检查:"
grep "开始检查即将到期的作业" logs/app.log | tail -n 5
echo ""

echo "✅ 最近成功发送的邮件:"
grep "邮件发送成功" logs/app.log | tail -n 10
echo ""

echo "❌ 最近发送失败的邮件:"
grep "邮件发送失败" logs/app.log | tail -n 10
echo ""

echo "📊 数据库统计:"
docker exec -i mongodb mongo -u REDACTED_MONGO_USER -p REDACTED_MONGO_PASSWORD --authSource admin buct-course --quiet <<EOF
print("待发送提醒: " + db.scheduled_reminders.count({status: 'scheduled'}));
print("已发送提醒: " + db.scheduled_reminders.count({status: 'sent', auto_created: true}));
print("发送失败: " + db.scheduled_reminders.count({status: 'failed', auto_created: true}));
print("已取消提醒: " + db.scheduled_reminders.count({status: 'cancelled', auto_created: true}));
EOF
echo ""

echo "=========================================="
```

使用方法：

```bash
chmod +x monitor_reminders.sh
./monitor_reminders.sh
```

## 🔧 手动触发提醒检查

如果需要立即检查并发送提醒（不等待1小时的定时检查）：

```python
# 进入Python环境
python

# 执行以下代码
from app import create_app
from app.scheduler import get_scheduler

app = create_app()
with app.app_context():
    scheduler = get_scheduler()
    
    # 手动触发自动提醒检查
    print("触发自动提醒检查...")
    scheduler._check_and_create_auto_reminders()
    
    # 手动触发提醒发送
    print("触发提醒发送...")
    scheduler._process_due_reminders()
    
print("完成！")
```

## 📝 改进后的日志说明

更新后的系统会在日志中显示详细的emoji标识：

- 🔔 = 开始检查
- ✅ = 成功
- ❌ = 失败
- ⚠️ = 警告
- 🚫 = 取消
- 📧 = 邮件相关
- 📊 = 统计信息
- 👥 = 用户相关
- 📚 = 作业相关
- 🎯 = 目标作业

这样更容易快速定位问题！

## 🚀 性能优化建议

如果系统用户较多，可以调整检查频率：

编辑 `app/scheduler.py`：

```python
# 修改自动提醒检查间隔（默认3600秒=1小时）
self.auto_reminder_check_interval = 1800  # 改为30分钟

# 修改提醒发送检查间隔（默认5秒）
self.reminder_check_interval = 10  # 改为10秒
```

## 📞 联系支持

如果以上方法都无法解决问题，请：

1. 收集以下信息：
    - logs/app.log 的最后200行
    - .env 文件配置（隐藏密码）
    - test_email_config.py 的输出
    - MongoDB中的提醒记录统计

2. 检查是否有其他错误日志

3. 确认Docker容器是否正常运行：
   ```bash
   docker-compose ps
   docker-compose logs backend | tail -n 100
   ```

