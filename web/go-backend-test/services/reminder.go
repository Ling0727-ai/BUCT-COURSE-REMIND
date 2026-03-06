package services

import (
	"fmt"
	"time"

	"github.com/Ling0727-ai/go-buct-course-backend/config"
	"github.com/Ling0727-ai/go-buct-course-backend/models/Reminder"
	"github.com/Ling0727-ai/go-buct-course-backend/models/User"
)

// ──────────────────────────────────────────────
//  手动提醒
// ──────────────────────────────────────────────

// ManualReminderInput 手动触发提醒的输入
type ManualReminderInput struct {
	UserID  string
	Subject string
	Title   string
	DueDate string
	Message string // 若非空则直接使用，否则用上面字段拼装
}

// SendManualReminder 立即向用户注册邮箱发送一次提醒邮件
// 对应 Python POST /webhooks/manual
func SendManualReminder(input *ManualReminderInput) error {
	// 获取用户邮箱
	user, err := User.Repository.GetUserByID(input.UserID)
	if err != nil || user == nil {
		return fmt.Errorf("未找到用户")
	}
	if user.Email == "" {
		return fmt.Errorf("用户未设置邮箱")
	}

	// 构建消息正文
	msg := input.Message
	if msg == "" {
		dueStr := input.DueDate
		if dueStr == "" {
			dueStr = "未知时间"
		}
		msg = fmt.Sprintf("⚠️ 手动提醒\n\n科目: %s\n作业: %s\n截止时间: %s",
			input.Subject, input.Title, dueStr)
	}

	return config.Mail.SendMail(user.Email, "北化课程提醒 - 手动提醒", msg)
}

// ──────────────────────────────────────────────
//  测试邮件
// ──────────────────────────────────────────────

// SendTestEmail 向用户注册邮箱发送测试邮件
// 对应 Python POST /webhooks/test
func SendTestEmail(userID string) (string, error) {
	user, err := User.Repository.GetUserByID(userID)
	if err != nil || user == nil {
		return "", fmt.Errorf("未找到用户")
	}
	if user.Email == "" {
		return "", fmt.Errorf("用户未设置邮箱")
	}

	msg := fmt.Sprintf(
		"🔔 测试提醒\n\n这是一封测试邮件，用于验证邮件通知功能是否正常。\n发送时间: %s",
		time.Now().Format("2006-01-02 15:04:05"),
	)

	return user.Email, config.Mail.SendMail(user.Email, "北化课程提醒 - 测试邮件", msg)
}

// ──────────────────────────────────────────────
//  定时提醒 CRUD
// ──────────────────────────────────────────────

// CreateScheduledReminder 为某条作业/待办创建定时提醒
func CreateScheduledReminder(userID, targetID, reminderType, message string, scheduledAt time.Time) (*Reminder.Reminder, error) {
	user, err := User.Repository.GetUserByID(userID)
	if err != nil || user == nil {
		return nil, fmt.Errorf("未找到用户")
	}
	if user.Email == "" {
		return nil, fmt.Errorf("用户未设置邮箱，无法创建提醒")
	}

	return Reminder.Repository.Create(&Reminder.CreateReminderInput{
		UserID:        userID,
		Email:         user.Email,
		Type:          reminderType,
		TargetID:      targetID,
		Message:       message,
		ScheduledTime: scheduledAt,
	})
}

// GetUserReminders 获取用户提醒列表
func GetUserReminders(userID, status string) ([]*Reminder.Reminder, error) {
	return Reminder.Repository.GetByUserID(userID, status)
}

// DeleteReminder 删除用户自己创建的提醒
func DeleteReminder(reminderID, userID string) error {
	return Reminder.Repository.Delete(reminderID, userID)
}
