package scheduler

import (
	"context"
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/Ling0727-ai/go-buct-course-backend/config"
	"github.com/Ling0727-ai/go-buct-course-backend/models"
	"github.com/Ling0727-ai/go-buct-course-backend/models/AssignmentStatus"
	"github.com/Ling0727-ai/go-buct-course-backend/models/CourseData"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// ──────────────────────────────────────────────
//  处理到期提醒
// ──────────────────────────────────────────────

// processDueReminders 查找并发送所有到期的定时提醒
// 对应 Python _process_due_reminders_impl
func processDueReminders() error {
	client, err := models.ConnectToDB()
	if err != nil {
		return err
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	col := client.Database("REDACTED_MONGO_USER").Collection(RemindersCollection)
	now := time.Now()

	// 查询到期未发送的提醒，limit 50，对应 Python .limit(50)
	cursor, err := col.Find(ctx, bson.M{
		"status":         "scheduled",
		"scheduled_time": bson.M{"$lte": now},
	}, options.Find().SetLimit(50))
	if err != nil {
		return err
	}
	defer cursor.Close(ctx)

	var reminders []ScheduledReminder
	if err = cursor.All(ctx, &reminders); err != nil {
		return err
	}
	if len(reminders) == 0 {
		return nil
	}

	log.Printf("[scheduler] 发现 %d 个到期提醒需要发送", len(reminders))

	var sent, failed, cancelled, skipped int

	for _, r := range reminders {
		// 原子抢占：将 scheduled → processing，防止并发重复发送
		// 对应 Python claim_result = update_one({status:scheduled}, {status:processing})
		claimRes, err := col.UpdateOne(ctx,
			bson.M{"_id": r.ID, "status": "scheduled"},
			bson.M{"$set": bson.M{"status": "processing", "updated_at": now}},
		)
		if err != nil || claimRes.MatchedCount == 0 {
			skipped++
			continue
		}

		if r.Email == "" || r.Message == "" {
			col.UpdateOne(ctx, bson.M{"_id": r.ID},
				bson.M{"$set": bson.M{"status": "failed", "error": "missing email or message", "updated_at": now}})
			failed++
			continue
		}

		// 发送前检查作业/待办是否已完成或已删除，对应 Python should_skip 判断
		if skip, reason := shouldSkipReminder(r); skip {
			col.UpdateOne(ctx, bson.M{"_id": r.ID},
				bson.M{"$set": bson.M{"status": "cancelled", "cancel_reason": reason, "updated_at": now}})
			log.Printf("[scheduler] 提醒已取消（%s）: %s", reason, r.TargetID)
			cancelled++
			continue
		}

		// 发送邮件，对应 Python send_webhook_notification(email_config, message)
		sendErr := config.Mail.SendMail(r.Email, "北化课程提醒", r.Message)
		if sendErr == nil {
			sentAt := now
			col.UpdateOne(ctx, bson.M{"_id": r.ID},
				bson.M{"$set": bson.M{"status": "sent", "sent_at": sentAt, "updated_at": now}})
			log.Printf("[scheduler] ✅ 提醒邮件已发送: %s (类型: %s)", r.Email, r.Type)
			sent++
		} else {
			col.UpdateOne(ctx, bson.M{"_id": r.ID},
				bson.M{"$set": bson.M{"status": "failed", "error": sendErr.Error(), "updated_at": now}})
			log.Printf("[scheduler] ❌ 提醒邮件发送失败: %s, err: %v", r.Email, sendErr)
			failed++
		}
	}

	log.Printf("[scheduler] 提醒处理完成: ✅发送 %d, ❌失败 %d, 🚫取消 %d, ⏭️跳过 %d",
		sent, failed, cancelled, skipped)
	return nil
}

// shouldSkipReminder 检查提醒是否应该跳过（作业已完成/已删除，待办已完成/已删除）
// 对应 Python should_skip 判断逻辑
func shouldSkipReminder(r ScheduledReminder) (bool, string) {
	if r.TargetID == "" || r.UserID == "" {
		return false, ""
	}

	statusRepo := AssignmentStatus.Repository

	switch r.Type {
	case "assignment":
		// 检查完成状态
		completed, _ := statusRepo.IsCompleted(r.UserID, r.TargetID)
		if completed {
			return true, "assignment completed"
		}
		deleted, _ := statusRepo.IsDeleted(r.UserID, r.TargetID)
		if deleted {
			return true, "assignment deleted"
		}
	}
	// todo 类型的检查留给后续 Todo 模型完善后补充
	return false, ""
}

// ──────────────────────────────────────────────
//  自动创建提醒
// ──────────────────────────────────────────────

// checkAndCreateAutoReminders 检查即将到期的作业并自动创建提醒
// 对应 Python _check_and_create_auto_reminders
func checkAndCreateAutoReminders() error {
	client, err := models.ConnectToDB()
	if err != nil {
		return err
	}

	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	now := time.Now()
	checkEnd := now.Add(24 * time.Hour) // DDL 前 24 小时内触发提醒

	log.Println("[scheduler] 开始检查即将到期的作业（DDL前24小时内自动提醒）")

	// 遍历所有用户
	userCol := client.Database("REDACTED_MONGO_USER").Collection("users")
	cursor, err := userCol.Find(ctx, bson.M{}, options.Find().SetProjection(
		bson.M{"_id": 1, "email": 1, "username": 1},
	))
	if err != nil {
		return err
	}
	defer cursor.Close(ctx)

	remCol := client.Database("REDACTED_MONGO_USER").Collection(RemindersCollection)
	courseRepo := CourseData.Repository
	statusRepo := AssignmentStatus.Repository

	var totalReminders int

	for cursor.Next(ctx) {
		var user struct {
			ID       string `bson:"_id"`
			Email    string `bson:"email"`
			Username string `bson:"username"`
		}
		if err = cursor.Decode(&user); err != nil {
			continue
		}
		if user.Email == "" {
			continue
		}

		// 获取该用户所有课程数据
		tasks, err := courseRepo.GetCourseDataByUserID(user.ID)
		if err != nil || len(tasks) == 0 {
			continue
		}

		// 获取已完成/已删除的 task_id 集合
		completedIDs := toSet(statusRepo.GetCompletedIDs(user.ID))
		deletedIDs := toSet(statusRepo.GetDeletedIDs(user.ID))

		for _, task := range tasks {
			// 跳过已完成/已删除
			if completedIDs[task.TaskID] || deletedIDs[task.TaskID] {
				continue
			}
			if task.Deadline == "" {
				continue
			}

			// 解析截止时间，对应 Python 多格式解析逻辑
			deadlineTime, err := parseDeadline(task.Deadline)
			if err != nil {
				continue
			}

			// 检查是否在未来 24 小时内到期
			if deadlineTime.Before(now) || deadlineTime.After(checkEnd) {
				continue
			}

			// 检查是否已经为这个作业创建过自动提醒（scheduled 或 sent），对应 Python existing_reminder 查询
			existCount, _ := remCol.CountDocuments(ctx, bson.M{
				"user_id":      user.ID,
				"target_id":    task.TaskID,
				"type":         "assignment",
				"auto_created": true,
				"status":       bson.M{"$in": bson.A{"scheduled", "sent"}},
			})
			if existCount > 0 {
				continue
			}

			// 构建提醒消息，对应 Python message 模板
			message := buildReminderMessage(task, deadlineTime, now)

			reminder := bson.M{
				"user_id":        user.ID,
				"type":           "assignment",
				"target_id":      task.TaskID,
				"email":          user.Email,
				"message":        message,
				"scheduled_time": now, // 立即发送
				"status":         "scheduled",
				"auto_created":   true,
				"created_at":     now,
				"updated_at":     now,
			}

			if _, err = remCol.InsertOne(ctx, reminder); err != nil {
				if !mongo.IsDuplicateKeyError(err) {
					log.Printf("[scheduler] 创建自动提醒失败: %v", err)
				}
				continue
			}

			totalReminders++
			log.Printf("[scheduler] ✅ 为用户 %s 创建自动提醒: %s - %s (截止: %s)",
				user.Username, task.Subject, task.Title,
				deadlineTime.Format("2006-01-02 15:04"))
		}
	}

	log.Printf("[scheduler] 自动提醒检查完成，共创建 %d 个新提醒", totalReminders)
	return cursor.Err()
}

// parseDeadline 解析多种格式的截止时间字符串，对应 Python 的多格式解析
func parseDeadline(s string) (time.Time, error) {
	s = strings.TrimSpace(s)
	formats := []string{
		"2006-01-02 15:04:05",
		"2006-01-02 15:04",
		"2006年01月02日 15:04:05",
		"2006-01-02T15:04:05",
		"2006-01-02T15:04:05Z",
	}
	for _, layout := range formats {
		if t, err := time.ParseInLocation(layout, strings.TrimSuffix(s, "Z"), time.Local); err == nil {
			return t, nil
		}
	}
	return time.Time{}, fmt.Errorf("无法解析时间: %s", s)
}

// buildReminderMessage 构建提醒邮件正文，对应 Python message 模板
func buildReminderMessage(task *CourseData.CourseData, deadline, now time.Time) string {
	taskType := "作业"
	if task.Type == "test" {
		taskType = "测试"
	}

	timeLeft := deadline.Sub(now)
	hours := int(timeLeft.Hours())
	var timeLeftStr string
	switch {
	case hours < 1:
		timeLeftStr = "不到1小时"
	case hours < 24:
		timeLeftStr = fmt.Sprintf("约%d小时", hours)
	default:
		days := hours / 24
		remain := hours % 24
		if remain > 0 {
			timeLeftStr = fmt.Sprintf("约%d天%d小时", days, remain)
		} else {
			timeLeftStr = fmt.Sprintf("约%d天", days)
		}
	}

	return fmt.Sprintf("⏰ 自动提醒：%s即将截止\n\n科目: %s\n标题: %s\n截止时间: %s\n剩余时间: %s\n\n请及时完成！",
		taskType,
		task.Subject,
		task.Title,
		deadline.Format("2006年01月02日 15:04:05"),
		timeLeftStr,
	)
}

// toSet 将字符串切片转为 set，忽略错误返回
func toSet(ids []string, _ error) map[string]bool {
	m := make(map[string]bool, len(ids))
	for _, id := range ids {
		m[id] = true
	}
	return m
}

// objectIDToString 将 primitive.ObjectID 转为字符串（兼容旧数据）
func objectIDToString(v interface{}) string {
	switch id := v.(type) {
	case primitive.ObjectID:
		return id.Hex()
	case string:
		return id
	}
	return fmt.Sprintf("%v", v)
}
