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
	"go.mongodb.org/mongo-driver/mongo/options"
)

// AdminHandler 管理员处理器
type AdminHandler struct{}

// NewAdminHandler 创建管理员处理器
func NewAdminHandler() *AdminHandler {
	return &AdminHandler{}
}

// GetUsers 获取所有用户
func (h *AdminHandler) GetUsers(c *gin.Context) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	collection := database.GetCollection(database.UsersCollection)

	opts := options.Find().SetProjection(bson.M{
		"password_hash": 0,
		"s_password":    0,
	})

	cursor, err := collection.Find(ctx, bson.M{}, opts)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "获取用户列表失败"})
		return
	}
	defer cursor.Close(ctx)

	var users []models.User
	if err := cursor.All(ctx, &users); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "解析数据失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"users":   users,
		"count":   len(users),
	})
}

// GetUserDetail 获取用户详情
func (h *AdminHandler) GetUserDetail(c *gin.Context) {
	userID := c.Param("id")
	userObjID, err := primitive.ObjectIDFromHex(userID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "error": "无效的用户ID"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	collection := database.GetCollection(database.UsersCollection)

	var user models.User
	opts := options.FindOne().SetProjection(bson.M{
		"password_hash": 0,
		"s_password":    0,
	})

	if err := collection.FindOne(ctx, bson.M{"_id": userObjID}, opts).Decode(&user); err != nil {
		c.JSON(http.StatusNotFound, gin.H{"success": false, "error": "用户不存在"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"user":    user,
	})
}

// UpdateUser 更新用户
func (h *AdminHandler) UpdateUser(c *gin.Context) {
	userID := c.Param("id")
	userObjID, err := primitive.ObjectIDFromHex(userID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "error": "无效的用户ID"})
		return
	}

	var req struct {
		IsAdmin *bool `json:"is_admin"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "error": "请求格式错误"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	collection := database.GetCollection(database.UsersCollection)

	updateData := bson.M{"updated_at": utils.GetBeijingTime()}
	if req.IsAdmin != nil {
		updateData["is_admin"] = *req.IsAdmin
	}

	_, err = collection.UpdateOne(ctx,
		bson.M{"_id": userObjID},
		bson.M{"$set": updateData},
	)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "更新失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "用户更新成功"})
}

// DeleteUser 删除用户
func (h *AdminHandler) DeleteUser(c *gin.Context) {
	userID := c.Param("id")
	userObjID, err := primitive.ObjectIDFromHex(userID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "error": "无效的用户ID"})
		return
	}

	// 不能删除自己
	currentUserID := middleware.GetUserID(c)
	if userID == currentUserID {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "error": "不能删除自己"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	collection := database.GetCollection(database.UsersCollection)

	result, err := collection.DeleteOne(ctx, bson.M{"_id": userObjID})
	if err != nil || result.DeletedCount == 0 {
		c.JSON(http.StatusNotFound, gin.H{"success": false, "error": "用户不存在"})
		return
	}

	// 同时删除用户的相关数据
	go cleanupUserData(userID)

	log.Printf("管理员删除了用户: %s", userID)
	c.JSON(http.StatusOK, gin.H{"success": true, "message": "用户已删除"})
}

// cleanupUserData 清理用户相关数据
func cleanupUserData(userID string) {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	userObjID, _ := primitive.ObjectIDFromHex(userID)

	// 删除课程数据
	database.GetCollection(database.CourseDataCollection).DeleteMany(ctx, bson.M{"user_id": userObjID})

	// 删除作业状态
	database.GetCollection(database.AssignmentStatusCollection).DeleteMany(ctx, bson.M{"user_id": userObjID})

	// 删除待办事项
	database.GetCollection(database.TodosCollection).DeleteMany(ctx, bson.M{"user_id": userObjID})

	// 删除提醒
	database.GetCollection(database.ScheduledRemindersCollection).DeleteMany(ctx, bson.M{"user_id": userObjID})

	log.Printf("已清理用户 %s 的相关数据", userID)
}

// GetSystemStats 获取系统统计
func (h *AdminHandler) GetSystemStats(c *gin.Context) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// 统计各集合的文档数
	usersCount, _ := database.GetCollection(database.UsersCollection).CountDocuments(ctx, bson.M{})
	coursesCount, _ := database.GetCollection(database.CourseDataCollection).CountDocuments(ctx, bson.M{})
	todosCount, _ := database.GetCollection(database.TodosCollection).CountDocuments(ctx, bson.M{})
	remindersCount, _ := database.GetCollection(database.ScheduledRemindersCollection).CountDocuments(ctx, bson.M{})

	// 今日注册用户数
	today := time.Now().Truncate(24 * time.Hour)
	todayUsers, _ := database.GetCollection(database.UsersCollection).CountDocuments(ctx, bson.M{
		"created_at": bson.M{"$gte": today},
	})

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"stats": gin.H{
			"total_users":     usersCount,
			"today_users":     todayUsers,
			"total_courses":   coursesCount,
			"total_todos":     todosCount,
			"total_reminders": remindersCount,
		},
	})
}
