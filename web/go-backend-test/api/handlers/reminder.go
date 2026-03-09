package handlers

import (
	"time"

	"github.com/Ling0727-ai/go-buct-course-backend/services"
	"github.com/Ling0727-ai/go-buct-course-backend/utils"
	"github.com/gin-gonic/gin"
)

// getUserID 从 gin.Context 取 user_id（由 JWT 中间件注入）
func getUserID(c *gin.Context) (string, bool) {
	v, exists := c.Get("user_id")
	if !exists {
		c.JSON(utils.Defaults.Status.Unauthorized, gin.H{"error": utils.Defaults.Auth.NotLoggedIn})
		return "", false
	}
	id, ok := v.(string)
	if !ok || id == "" {
		c.JSON(utils.Defaults.Status.Unauthorized, gin.H{"error": utils.Defaults.Auth.NotLoggedIn})
		return "", false
	}
	return id, true
}

// ManualReminder 手动触发一次提醒邮件
// 对应 Python POST /api/webhooks/manual
func ManualReminder(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	var body struct {
		Subject string `json:"subject"`
		Title   string `json:"title"`
		DueDate string `json:"due_date"`
		Message string `json:"message"` // 若非空则直接使用
	}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Auth.RequestFormatError})
		return
	}

	err := services.SendManualReminder(&services.ManualReminderInput{
		UserID:  userID,
		Subject: body.Subject,
		Title:   body.Title,
		DueDate: body.DueDate,
		Message: body.Message,
	})
	if err != nil {
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{
			"success": false,
			"error":   err.Error(),
		})
		return
	}

	c.JSON(utils.Defaults.Status.OK, gin.H{
		"success": true,
		"message": utils.Defaults.Reminder.SendSuccess,
	})
}

// TestReminder 发送测试邮件，验证邮件配置是否正常
// 对应 Python POST /api/webhooks/test
func TestReminder(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	email, err := services.SendTestEmail(userID)
	if err != nil {
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{
			"success": false,
			"error":   err.Error(),
		})
		return
	}

	c.JSON(utils.Defaults.Status.OK, gin.H{
		"success": true,
		"message": utils.Defaults.Reminder.TestEmailSuccess + email,
	})
}

// CreateReminder 为指定作业/待办创建定时提醒
func CreateReminder(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	var body struct {
		TargetID      string `json:"target_id"      binding:"required"`
		Type          string `json:"type"           binding:"required"` // "assignment" | "todo"
		Message       string `json:"message"        binding:"required"`
		ScheduledTime string `json:"scheduled_time" binding:"required"` // RFC3339 / "2006-01-02 15:04:05"
	}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": err.Error()})
		return
	}

	// 解析时间
	var scheduledAt time.Time
	var parseErr error
	for _, layout := range []string{time.RFC3339, "2006-01-02 15:04:05", "2006-01-02 15:04"} {
		scheduledAt, parseErr = time.ParseInLocation(layout, body.ScheduledTime, time.Local)
		if parseErr == nil {
			break
		}
	}
	if parseErr != nil {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Reminder.TimeInvalid})
		return
	}
	if scheduledAt.Before(time.Now()) {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Reminder.TimePast})
		return
	}

	reminder, err := services.CreateScheduledReminder(
		userID, body.TargetID, body.Type, body.Message, scheduledAt,
	)
	if err != nil {
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(utils.Defaults.Status.Created, gin.H{
		"success": true,
		"data":    reminder,
	})
}

// GetReminders 获取当前用户的提醒列表
func GetReminders(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	status := c.Query("status") // 可选过滤，如 "scheduled"

	reminders, err := services.GetUserReminders(userID, status)
	if err != nil {
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(utils.Defaults.Status.OK, gin.H{
		"success": true,
		"data":    reminders,
		"count":   len(reminders),
	})
}

// DeleteReminder 删除指定提醒（只能删除非自动创建的）
func DeleteReminder(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	reminderID := c.Param("id")
	if reminderID == "" {
		c.JSON(utils.Defaults.Status.BadRequest, gin.H{"error": utils.Defaults.Reminder.MissingID})
		return
	}

	if err := services.DeleteReminder(reminderID, userID); err != nil {
		c.JSON(utils.Defaults.Status.InternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(utils.Defaults.Status.OK, gin.H{
		"success": true,
		"message": utils.Defaults.Reminder.DeleteSuccess,
	})
}
