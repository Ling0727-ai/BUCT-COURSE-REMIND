package handlers

import (
	"context"
	"log"
	"net/http"
	"time"

	"buct-course-remind/internal/database"
	"buct-course-remind/internal/middleware"
	"buct-course-remind/internal/models"
	"buct-course-remind/internal/services"
	"buct-course-remind/internal/utils"

	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

// ReminderHandler 提醒处理器
type ReminderHandler struct{}

// NewReminderHandler 创建提醒处理器
func NewReminderHandler() *ReminderHandler {
	return &ReminderHandler{}
}

// CreateReminder 创建提醒
func (h *ReminderHandler) CreateReminder(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "error": "用户未登录"})
		return
	}

	var req struct {
		AssignmentID string    `json:"assignment_id" binding:"required"`
		Title        string    `json:"title"`
		Subject      string    `json:"subject"`
		ReminderTime time.Time `json:"reminder_time" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "error": "请求格式错误"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	userObjID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.ScheduledRemindersCollection)

	// 检查是否已存在相同提醒
	count, _ := collection.CountDocuments(ctx, bson.M{
		"user_id":       userObjID,
		"assignment_id": req.AssignmentID,
		"sent":          false,
	})

	if count > 0 {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "error": "该作业已设置提醒"})
		return
	}

	reminder := models.ScheduledReminder{
		UserID:       userObjID,
		AssignmentID: req.AssignmentID,
		Title:        req.Title,
		Subject:      req.Subject,
		ReminderTime: req.ReminderTime,
		Sent:         false,
		Type:         "manual",
		CreatedAt:    utils.GetBeijingTime(),
	}

	result, err := collection.InsertOne(ctx, reminder)
	if err != nil {
		log.Printf("创建提醒失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "创建提醒失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success":     true,
		"message":     "提醒创建成功",
		"reminder_id": result.InsertedID.(primitive.ObjectID).Hex(),
	})
}

// GetReminders 获取用户的提醒列表
func (h *ReminderHandler) GetReminders(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "error": "用户未登录"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	userObjID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.ScheduledRemindersCollection)

	cursor, err := collection.Find(ctx, bson.M{
		"user_id": userObjID,
		"sent":    false,
	})
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "获取提醒失败"})
		return
	}
	defer cursor.Close(ctx)

	var reminders []models.ScheduledReminder
	if err := cursor.All(ctx, &reminders); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "解析数据失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success":   true,
		"reminders": reminders,
		"count":     len(reminders),
	})
}

// DeleteReminder 删除提醒
func (h *ReminderHandler) DeleteReminder(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "error": "用户未登录"})
		return
	}

	reminderID := c.Param("id")
	reminderObjID, err := primitive.ObjectIDFromHex(reminderID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "error": "无效的提醒ID"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	userObjID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.ScheduledRemindersCollection)

	result, err := collection.DeleteOne(ctx, bson.M{
		"_id":     reminderObjID,
		"user_id": userObjID,
	})

	if err != nil || result.DeletedCount == 0 {
		c.JSON(http.StatusNotFound, gin.H{"success": false, "error": "提醒不存在"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "提醒已删除"})
}

// SendTestReminder 发送测试提醒
func (h *ReminderHandler) SendTestReminder(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "error": "用户未登录"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// 获取用户邮箱
	userObjID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.UsersCollection)

	var user models.User
	if err := collection.FindOne(ctx, bson.M{"_id": userObjID}).Decode(&user); err != nil {
		c.JSON(http.StatusNotFound, gin.H{"success": false, "error": "用户不存在"})
		return
	}

	if user.Email == "" {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "error": "用户未设置邮箱"})
		return
	}

	// 发送测试邮件
	subject := "BUCT课程提醒 - 测试邮件"
	content := "<p>这是一封测试邮件，用于验证邮件提醒功能是否正常工作。</p>" +
		"<p>如果您收到此邮件，说明邮件提醒功能配置正确！</p>"

	if err := services.SendReminderEmail(user.Email, subject, content); err != nil {
		log.Printf("发送测试邮件失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "发送测试邮件失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "测试邮件已发送到 " + user.Email,
	})
}
