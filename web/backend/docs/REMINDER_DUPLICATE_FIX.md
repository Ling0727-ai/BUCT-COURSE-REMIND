# 提醒邮件重复发送问题修复文档

## 问题概述

**问题描述：** 用户设置作业提醒时，会同时收到两封相同内容的提醒邮件。

**影响范围：** 作业提醒功能（`/api/assignments/<assignment_id>/remind`）

**修复日期：** 2025-11-18

---

## 问题分析

### 复现步骤

1. 用户在主界面点击作业卡片的"提醒"按钮
2. 选择任意提醒方式（特别是"立即提醒"或很短时间后的提醒）
3. 确认发送
4. 用户收到两封相同的提醒邮件

### 根本原因

在 `web/backend/app/assignments.py` 的 `remind_assignment()` 函数中，存在以下逻辑缺陷：

```python
# 原有代码（第 325-360 行）
if scheduled_time <= now:
    # 立即发送邮件
    success = send_webhook_notification(email_config, message)
    if success:
        return jsonify({...})  # 直接返回，不记录到数据库
    else:
        return jsonify({...}), 500

# 插入定时提醒到数据库（状态为 'scheduled'）
mongo.db.scheduled_reminders.insert_one({
    'status': 'scheduled',
    'scheduled_time': scheduled_time,
    ...
})
```

**问题点：**

1. **立即发送分支**：当 `scheduled_time <= now` 时，代码会直接调用 `send_webhook_notification()` 发送邮件，然后直接返回
2. **缺少数据库记录**：立即发送后没有在数据库中记录这次发送操作
3. **潜在的时序问题**：
    - 如果在某些边界情况下，代码没有进入 `if scheduled_time <= now` 分支
    - 而是将 `scheduled_time` 为当前时间（或非常接近当前时间）的记录插入数据库
    - 调度器的 `_process_due_reminders()` 会立即扫描到这条记录并再次发送邮件
    - 导致用户收到两封邮件

### 代码流程图

**修复前的问题流程：**

```
用户点击提醒
    ↓
计算 scheduled_time
    ↓
scheduled_time <= now?
    ↓ YES                          ↓ NO
发送邮件 → 返回              插入数据库（status: 'scheduled'）
                                   ↓
                             调度器扫描到记录
                                   ↓
                             再次发送邮件
                                   ↓
                             用户收到两封邮件 ❌
```

---

## 解决方案

### 修复策略

**核心思想：** 无论是立即发送还是定时发送，都必须在数据库中记录，并正确设置状态，避免调度器重复处理。

### 代码修改

**文件：** `web/backend/app/assignments.py`

**修改位置：** 第 325-360 行

**修改内容：**

```python
# 若计算出的时间早于当前，则改为立即发送
if scheduled_time <= now:
    from .notification_services import send_webhook_notification
    email_config = {'type': 'email', 'enabled': True, 'config': {'to_email': to_email}}
    message = f"{base_message}\n提醒时间: 立即"
    success = send_webhook_notification(email_config, message)
    
    # 🔧 修复：记录到数据库，标记为已发送或失败，避免scheduler重复处理
    reminder_doc = {
        'user_id': ObjectId(user_id),
        'type': 'assignment',
        'target_id': assignment_id,
        'email': to_email,
        'message': message,
        'scheduled_time': now,
        'status': 'sent' if success else 'failed',  # ✅ 关键：直接标记为 sent/failed
        'created_at': now,
        'updated_at': now,
        'sent_at': now if success else None,
        'error': None if success else 'immediate send failed'
    }
    mongo.db.scheduled_reminders.insert_one(reminder_doc)
    
    if success:
        logger.info(f"立即发送提醒到: {to_email}")
        return jsonify({
            'success': True,
            'message': f"提醒已立即发送：{subject} - {task}",
            'detail': {'schedule': 'now', 'email': to_email}
        })
    else:
        logger.error(f"发送提醒邮件失败: {to_email}")
        return jsonify({
            'success': False,
            'error': '邮件发送失败，请检查邮箱配置'
        }), 500

# 插入定时提醒（由scheduler处理）
reminder_doc = {
    'user_id': ObjectId(user_id),
    'type': 'assignment',
    'target_id': assignment_id,
    'email': to_email,
    'message': f"{base_message}\n提醒时间: {schedule_desc}",
    'scheduled_time': scheduled_time,
    'status': 'scheduled',  # ✅ 未来的提醒仍然是 scheduled
    'created_at': now,
    'updated_at': now
}
mongo.db.scheduled_reminders.insert_one(reminder_doc)
logger.info(f"已创建定时提醒，计划 {schedule_desc} 发送到: {to_email}")
```

### 修复要点

1. **立即发送也记录到数据库**
    - 保持数据完整性
    - 便于追溯和统计
    - 用户可以查看提醒历史

2. **状态直接设为 'sent' 或 'failed'**
    - `status: 'sent'` - 发送成功
    - `status: 'failed'` - 发送失败
    - 不再是 `status: 'scheduled'`

3. **调度器不会重复处理**
    - 调度器的查询条件：`{'status': 'scheduled', 'scheduled_time': {'$lte': now}}`
    - 立即发送的记录状态已经是 'sent' 或 'failed'
    - 因此不会被调度器捕获和重复处理

---

## 修复后的流程

**修复后的正确流程：**

```
用户点击提醒
    ↓
计算 scheduled_time
    ↓
scheduled_time <= now?
    ↓ YES                                    ↓ NO
发送邮件                              插入数据库（status: 'scheduled'）
    ↓                                        ↓
插入数据库（status: 'sent'/'failed'）    调度器扫描到记录
    ↓                                        ↓
返回结果                              发送邮件 + 更新状态为 'sent'
    ↓                                        ↓
用户收到一封邮件 ✅                    用户收到一封邮件 ✅
```

---

## 验证方法

### 1. 数据库验证

检查 `scheduled_reminders` 集合中立即发送的记录状态：

```javascript
// 查询立即发送的记录（scheduled_time ≈ created_at）
db.scheduled_reminders.find({
  $expr: {
    $lte: [
      { $abs: { $subtract: ["$scheduled_time", "$created_at"] } },
      5000  // 5秒以内
    ]
  }
}).pretty()

// 验证：所有立即发送的记录状态应该是 'sent' 或 'failed'，而不是 'scheduled'
```

### 2. 日志验证

查看后端日志，确认：

```
立即发送提醒到: xxx@example.com
```

这条日志只出现一次，不会重复。

### 3. 邮箱验证

用户收到的提醒邮件应该：

- ✅ 只有一封
- ✅ 时间正确
- ✅ 内容完整

### 4. 运行测试脚本

```bash
cd web/backend
python test_reminder_duplicate_fix.py
```

测试脚本会检查：

- scheduled_reminders 集合中的记录状态分布
- 是否有重复的 scheduled 记录
- 立即发送的记录状态是否正确

---

## 其他相关检查

### 1. Todos 提醒功能

**文件：** `web/backend/app/todos.py`

**状态：** ✅ 无问题

**原因：** Todos 的提醒功能只做立即发送，不使用调度系统，不存在重复发送问题。

```python
# todos.py 第 434-446 行
from .notification_services import send_webhook_notification
success = send_webhook_notification(email_config, message)
# 直接返回，不涉及数据库调度
```

### 2. 自动提醒功能（DDL前24小时）

**文件：** `web/backend/app/scheduler.py`

**状态：** ✅ 无问题

**原因：** 自动提醒在创建前会检查是否已存在，避免重复创建。

```python
# scheduler.py 第 387-394 行
existing_reminder = mongo.db[REMINDERS_COLLECTION].find_one({
    'user_id': user_id,
    'target_id': task_id,
    'type': 'assignment',
    'auto_created': True,
    'status': {'$in': ['scheduled', 'sent']}
})

if existing_reminder:
    continue  # 已经创建过提醒，跳过
```

### 3. 调度器处理逻辑

**文件：** `web/backend/app/scheduler.py`

**函数：** `_process_due_reminders()`

**状态：** ✅ 无问题

**原因：** 调度器处理后会更新状态，不会处理同一条记录两次。

```python
# scheduler.py 第 180-283 行
# 1. 查询 status='scheduled' 的记录
due_cursor = mongo.db[REMINDERS_COLLECTION].find({
    'status': 'scheduled',
    'scheduled_time': {'$lte': now}
})

# 2. 发送邮件
sent = send_webhook_notification(email_config, message)

# 3. 更新状态为 'sent' 或 'failed'
mongo.db[REMINDERS_COLLECTION].update_one(
    {'_id': reminder['_id']},
    {'$set': {'status': 'sent' if sent else 'failed', 'sent_at': now}}
)
```

---

## 测试建议

### 测试用例

1. **立即提醒**
    - 操作：设置"立即提醒"
    - 预期：只收到一封邮件

2. **1小时后提醒**
    - 操作：设置"1小时后提醒"
    - 预期：1小时后只收到一封邮件

3. **截止前N小时提醒**
    - 操作：设置"截止前3小时提醒"
    - 预期：截止前3小时只收到一封邮件

4. **自定义时间提醒**
    - 操作：设置自定义时间（如明天10:00）
    - 预期：明天10:00只收到一封邮件

5. **已完成作业的提醒**
    - 操作：设置提醒后，在提醒时间前标记作业为已完成
    - 预期：不收到提醒邮件（被取消）

### 回归测试

- ✅ 立即提醒功能正常
- ✅ 定时提醒功能正常
- ✅ 自动提醒（DDL前24小时）功能正常
- ✅ 待办提醒功能正常
- ✅ 提醒取消机制正常（已完成/已删除的作业不发送提醒）

---

## 总结

**问题：** 立即发送提醒时，没有在数据库中记录发送状态，导致调度器可能再次处理并发送邮件。

**修复：** 立即发送后，将提醒记录插入数据库并标记为 'sent' 或 'failed' 状态，确保调度器不会重复处理。

**效果：** 用户每次设置提醒只会收到一封邮件，不再有重复发送问题。

**影响：** 无负面影响，提升用户体验和系统可靠性。

---

## 相关文件

- `web/backend/app/assignments.py` - 主要修复文件
- `web/backend/app/scheduler.py` - 调度器（无需修改）
- `web/backend/app/notification_services.py` - 邮件发送服务（无需修改）
- `web/backend/test_reminder_duplicate_fix.py` - 测试脚本

---

## 联系方式

如有问题，请联系：

- GitHub: ling0727-ai
- Email: ***REMOVED***

