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
	"go.mongodb.org/mongo-driver/mongo/options"
)

// CourseDataHandler 课程数据处理器
type CourseDataHandler struct{}

// NewCourseDataHandler 创建课程数据处理器
func NewCourseDataHandler() *CourseDataHandler {
	return &CourseDataHandler{}
}

// GetStatus 获取课程数据状态
func (h *CourseDataHandler) GetStatus(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未登录"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	objID, _ := primitive.ObjectIDFromHex(userID)

	// 获取课程数据 - 检查是否有任何课程数据
	collection := database.GetCollection(database.CourseDataCollection)
	
	// 计算数据数量
	count, err := collection.CountDocuments(ctx, bson.M{"user_id": objID})
	if err != nil || count == 0 {
		c.JSON(http.StatusOK, gin.H{
			"success":            true,
			"has_data":           false,
			"last_update":        nil,
			"next_auto_refresh":  nil,
			"hours_until_refresh": nil,
		})
		return
	}

	// 获取最近更新时间
	var latestData struct {
		UpdatedAt time.Time `bson:"updated_at"`
	}
	
	opts := options.FindOne().SetSort(bson.D{{Key: "updated_at", Value: -1}})
	err = collection.FindOne(ctx, bson.M{"user_id": objID}, opts).Decode(&latestData)
	
	var lastUpdate *time.Time
	if err == nil && !latestData.UpdatedAt.IsZero() {
		lastUpdate = &latestData.UpdatedAt
	}

	// 计算下次刷新时间（假设每12小时刷新一次）
	var hoursUntilRefresh *float64
	var nextAutoRefresh *time.Time
	if lastUpdate != nil {
		nextRefresh := lastUpdate.Add(12 * time.Hour)
		nextAutoRefresh = &nextRefresh
		hoursLeft := time.Until(nextRefresh).Hours()
		if hoursLeft < 0 {
			hoursLeft = 0
		}
		hoursUntilRefresh = &hoursLeft
	}

	c.JSON(http.StatusOK, gin.H{
		"success":             true,
		"has_data":            count > 0,
		"last_update":         lastUpdate,
		"next_auto_refresh":   nextAutoRefresh,
		"hours_until_refresh": hoursUntilRefresh,
	})
}

// Refresh 刷新课程数据
func (h *CourseDataHandler) Refresh(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "未登录"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// 检查用户是否设置了学号和密码
	objID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.UsersCollection)
	var user models.User
	if err := collection.FindOne(ctx, bson.M{"_id": objID}).Decode(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"error":   "用户不存在",
		})
		return
	}

	if user.StudentID == "" || user.SPassword == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"error":   "请先设置学号和密码",
		})
		return
	}

	// 同步执行刷新任务
	count, err := services.RefreshUserData(userID)
	if err != nil {
		log.Printf("刷新课程数据失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success":    true,
		"message":    "数据刷新成功",
		"count":      count,
		"updated_at": utils.GetBeijingTime().Format(time.RFC3339),
	})
}
