package handlers

import (
	"context"
	"net/http"
	"time"

	"github.com/Ling0727-ai/go-buct-course-backend/config"
	"github.com/Ling0727-ai/go-buct-course-backend/models"
	"github.com/Ling0727-ai/go-buct-course-backend/services"
	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/mongo/options"
)

const settingsCollection = "settings"

// GetSettings 获取系统设置，对应 Python GET /api/settings
func GetSettings(c *gin.Context) {
	client, err := models.ConnectToDB()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "数据库连接失败"})
		return
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	cursor, err := client.Database("REDACTED_MONGO_USER").Collection(settingsCollection).Find(ctx, map[string]interface{}{})
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取设置失败"})
		return
	}
	defer cursor.Close(ctx)

	result := gin.H{"notification_email": ""}
	for cursor.Next(ctx) {
		var doc struct {
			Key   string      `bson:"key"`
			Value interface{} `bson:"value"`
		}
		if err = cursor.Decode(&doc); err == nil {
			result[doc.Key] = doc.Value
		}
	}
	c.JSON(http.StatusOK, result)
}

// SaveSettings 保存系统设置，对应 Python POST /api/settings
func SaveSettings(c *gin.Context) {
	var body map[string]interface{}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}
	client, err := models.ConnectToDB()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "数据库连接失败"})
		return
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	col := client.Database("REDACTED_MONGO_USER").Collection(settingsCollection)
	for key, val := range body {
		if key != "notification_email" {
			continue
		}
		col.UpdateOne(ctx,
			map[string]interface{}{"key": key},
			map[string]interface{}{"$set": map[string]interface{}{"value": val, "updated_at": time.Now()}},
			options.Update().SetUpsert(true),
		)
	}
	c.JSON(http.StatusOK, gin.H{"message": "设置保存成功"})
}

// GetEmailSettings 获取邮箱通知设置，对应 Python GET /api/settings/email
func GetEmailSettings(c *gin.Context) {
	client, err := models.ConnectToDB()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "数据库连接失败"})
		return
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var doc struct {
		Value string `bson:"value"`
	}
	_ = client.Database("REDACTED_MONGO_USER").Collection(settingsCollection).FindOne(ctx,
		map[string]interface{}{"key": "notification_email"},
	).Decode(&doc)

	c.JSON(http.StatusOK, gin.H{"to_email": doc.Value})
}

// SaveEmailSettings 保存邮箱通知设置，对应 Python POST /api/settings/email
func SaveEmailSettings(c *gin.Context) {
	var body struct {
		ToEmail string `json:"to_email"`
	}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误"})
		return
	}
	if body.ToEmail != "" && !services.EmailRegexp.MatchString(body.ToEmail) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "邮箱格式不正确"})
		return
	}
	client, err := models.ConnectToDB()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "数据库连接失败"})
		return
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	_, err = client.Database("REDACTED_MONGO_USER").Collection(settingsCollection).UpdateOne(ctx,
		map[string]interface{}{"key": "notification_email"},
		map[string]interface{}{"$set": map[string]interface{}{"value": body.ToEmail, "updated_at": time.Now()}},
		options.Update().SetUpsert(true),
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "保存失败"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"message": "邮箱设置保存成功"})
}

// HealthCheck 健康检查端点，对应 Python GET /api/health
func HealthCheck(c *gin.Context) {
	dbStatus := "healthy"
	client, err := models.ConnectToDB()
	if err != nil {
		dbStatus = "unhealthy: " + err.Error()
	} else {
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
		defer cancel()
		if pingErr := client.Ping(ctx, nil); pingErr != nil {
			dbStatus = "unhealthy: " + pingErr.Error()
		}
	}

	mailConfigured := config.Mail != nil && config.Mail.IsReady()
	status := "healthy"
	statusCode := http.StatusOK
	if dbStatus != "healthy" {
		status = "unhealthy"
		statusCode = http.StatusServiceUnavailable
	}
	c.JSON(statusCode, gin.H{
		"status":          status,
		"database":        dbStatus,
		"mail_configured": mailConfigured,
		"services": gin.H{
			"verification_code":   "available",
			"user_registration":   "available",
			"user_authentication": "available",
		},
	})
}

// GetStats 获取全局统计信息，对应 Python GET /api/stats
func GetStats(c *gin.Context) {
	client, err := models.ConnectToDB()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "数据库连接失败"})
		return
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	db := client.Database("REDACTED_MONGO_USER")
	now := time.Now()

	totalAssignments, _ := db.Collection("course_data").CountDocuments(ctx,
		map[string]interface{}{"type": "homework"})
	totalTests, _ := db.Collection("course_data").CountDocuments(ctx,
		map[string]interface{}{"type": "test"})
	urgentAssignments, _ := db.Collection("course_data").CountDocuments(ctx,
		map[string]interface{}{"deadline": map[string]interface{}{"$lte": now.Add(48 * time.Hour).Format(time.RFC3339)}})

	c.JSON(http.StatusOK, gin.H{
		"total_assignments":  totalAssignments,
		"total_tests":        totalTests,
		"urgent_assignments": urgentAssignments,
		"total_items":        totalAssignments + totalTests,
		"timestamp":          now.Format(time.RFC3339),
	})
}
