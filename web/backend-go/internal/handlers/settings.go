package handlers

import (
	"context"
	"log"
	"net/http"
	"time"

	"buct-course-remind/internal/database"
	"buct-course-remind/internal/middleware"
	"buct-course-remind/internal/models"
	"buct-course-remind/internal/utils"

	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

// SettingsHandler 设置处理器
type SettingsHandler struct{}

// NewSettingsHandler 创建设置处理器
func NewSettingsHandler() *SettingsHandler {
	return &SettingsHandler{}
}

// GetSettings 获取设置
func (h *SettingsHandler) GetSettings(c *gin.Context) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	collection := database.GetCollection(database.SettingsCollection)

	cursor, err := collection.Find(ctx, bson.M{})
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取设置失败"})
		return
	}
	defer cursor.Close(ctx)

	settings := make(map[string]interface{})
	for cursor.Next(ctx) {
		var result bson.M
		if err := cursor.Decode(&result); err != nil {
			continue
		}
		key := result["key"].(string)
		settings[key] = result["value"]
	}

	// 设置默认值
	if _, ok := settings["notification_email"]; !ok {
		settings["notification_email"] = ""
	}

	c.JSON(http.StatusOK, settings)
}

// SaveSettings 保存设置
func (h *SettingsHandler) SaveSettings(c *gin.Context) {
	var data map[string]interface{}
	if err := c.ShouldBindJSON(&data); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	collection := database.GetCollection(database.SettingsCollection)
	now := utils.GetBeijingTime()

	for key, value := range data {
		if key == "notification_email" {
			_, err := collection.UpdateOne(ctx,
				bson.M{"key": key},
				bson.M{"$set": bson.M{
					"key":        key,
					"value":      value,
					"updated_at": now,
				}},
				nil,
			)
			if err != nil {
				// 尝试插入
				collection.InsertOne(ctx, bson.M{
					"key":        key,
					"value":      value,
					"updated_at": now,
				})
			}
		}
	}

	log.Println("设置保存成功")
	c.JSON(http.StatusOK, gin.H{"message": "设置保存成功"})
}

// GetEmailSettings 获取邮箱设置
func (h *SettingsHandler) GetEmailSettings(c *gin.Context) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := database.GetCollection(database.SettingsCollection)

	var result bson.M
	err := collection.FindOne(ctx, bson.M{"key": "notification_email"}).Decode(&result)

	email := ""
	if err == nil && result["value"] != nil {
		email = result["value"].(string)
	}

	c.JSON(http.StatusOK, gin.H{"to_email": email})
}

// SaveEmailSettings 保存邮箱设置
func (h *SettingsHandler) SaveEmailSettings(c *gin.Context) {
	var req struct {
		ToEmail string `json:"to_email"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	// 验证邮箱格式
	if req.ToEmail != "" && !containsAt(req.ToEmail) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "邮箱格式不正确"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	collection := database.GetCollection(database.SettingsCollection)
	now := utils.GetBeijingTime()

	_, err := collection.UpdateOne(ctx,
		bson.M{"key": "notification_email"},
		bson.M{"$set": bson.M{
			"key":        "notification_email",
			"value":      req.ToEmail,
			"updated_at": now,
		}},
		nil,
	)

	if err != nil {
		collection.InsertOne(ctx, bson.M{
			"key":        "notification_email",
			"value":      req.ToEmail,
			"updated_at": now,
		})
	}

	log.Printf("邮箱设置保存成功: %s", req.ToEmail)
	c.JSON(http.StatusOK, gin.H{"message": "邮箱设置保存成功"})
}

func containsAt(s string) bool {
	for _, c := range s {
		if c == '@' {
			return true
		}
	}
	return false
}

// UserSettingsHandler 用户设置处理器
type UserSettingsHandler struct{}

// NewUserSettingsHandler 创建用户设置处理器
func NewUserSettingsHandler() *UserSettingsHandler {
	return &UserSettingsHandler{}
}

// GetUserSettings 获取用户设置
func (h *UserSettingsHandler) GetUserSettings(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未登录"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	objID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.UsersCollection)

	var user models.User
	err := collection.FindOne(ctx, bson.M{"_id": objID}).Decode(&user)
	if err != nil {
		c.JSON(http.StatusOK, gin.H{
			"auto_reminder":      true,
			"reminder_hours":     24,
			"email_notification": true,
		})
		return
	}

	// 返回用户相关的设置，使用默认值如果未设置
	autoReminder := user.AutoReminder
	reminderHours := user.ReminderHours
	emailNotification := user.EmailNotification

	// 设置默认值
	if reminderHours <= 0 {
		reminderHours = 24
	}
	// 如果从未设置过（新用户），启用自动提醒
	if !autoReminder && reminderHours == 24 {
		autoReminder = true
		emailNotification = true
	}

	c.JSON(http.StatusOK, gin.H{
		"auto_reminder":      autoReminder,
		"reminder_hours":     reminderHours,
		"email_notification": emailNotification,
	})
}

// SaveUserSettings 保存用户设置
func (h *UserSettingsHandler) SaveUserSettings(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未登录"})
		return
	}

	var settings struct {
		AutoReminder      *bool    `json:"auto_reminder"`
		ReminderHours     *float64 `json:"reminder_hours"`
		EmailNotification *bool    `json:"email_notification"`
	}
	if err := c.ShouldBindJSON(&settings); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	objID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.UsersCollection)

	// 构建更新字段
	updateFields := bson.M{
		"updated_at": time.Now(),
	}
	if settings.AutoReminder != nil {
		updateFields["auto_reminder"] = *settings.AutoReminder
	}
	if settings.ReminderHours != nil {
		updateFields["reminder_hours"] = *settings.ReminderHours
	}
	if settings.EmailNotification != nil {
		updateFields["email_notification"] = *settings.EmailNotification
	}

	_, err := collection.UpdateOne(ctx, bson.M{"_id": objID}, bson.M{"$set": updateFields})
	if err != nil {
		log.Printf("保存用户设置失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "保存失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "设置保存成功"})
}
