package handlers

import (
	"net/http"
	"time"

	"github.com/Ling0727-ai/go-buct-course-backend/services"
	"github.com/gin-gonic/gin"
)

// getUserID 从 gin.Context 取 user_id（由 JWT 中间件注入）
func getUserID(c *gin.Context) (string, bool) {
	v, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未登录"})
		return "", false
	}
	id, ok := v.(string)
	if !ok || id == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未登录"})
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
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
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
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "提醒邮件已发送",
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
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "测试邮件已发送到: " + email,
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
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
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
		c.JSON(http.StatusBadRequest, gin.H{"error": "时间格式不正确，请使用 2006-01-02 15:04:05"})
		return
	}
	if scheduledAt.Before(time.Now()) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "提醒时间不能早于当前时间"})
		return
	}

	reminder, err := services.CreateScheduledReminder(
		userID, body.TargetID, body.Type, body.Message, scheduledAt,
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
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
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
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
		c.JSON(http.StatusBadRequest, gin.H{"error": "缺少提醒 ID"})
		return
	}

	if err := services.DeleteReminder(reminderID, userID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "提醒已删除",
	})
}
