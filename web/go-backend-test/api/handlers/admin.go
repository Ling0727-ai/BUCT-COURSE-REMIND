package handlers

import (
	"context"
	"net/http"
	"strconv"
	"time"

	"github.com/Ling0727-ai/go-buct-course-backend/models"
	"github.com/Ling0727-ai/go-buct-course-backend/models/User"
	"github.com/Ling0727-ai/go-buct-course-backend/scheduler"
	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
)

// adminRequired 检查当前用户是否为管理员，对应 Python admin_required 装饰器
func adminRequired(c *gin.Context) bool {
	userID, ok := getUserID(c)
	if !ok {
		return false
	}
	user, err := User.Repository.GetUserByID(userID)
	if err != nil || user == nil || !user.IsAdmin {
		c.JSON(http.StatusForbidden, gin.H{"error": "需要管理员权限"})
		return false
	}
	return true
}

// AdminTriggerCleanup 手动触发调度器立即执行一轮刷新
// 对应 Python POST /api/admin/cleanup/trigger
func AdminTriggerCleanup(c *gin.Context) {
	if !adminRequired(c) {
		return
	}

	// 用调度器单例在后台执行一次全量刷新
	go scheduler.GetScheduler().TriggerRefresh()

	c.JSON(http.StatusOK, gin.H{
		"success":   true,
		"message":   "清理/刷新任务已触发",
		"timestamp": time.Now().Format(time.RFC3339),
	})
}

// AdminGetCompletedAssignments 分页列出所有已完成作业记录
// 对应 Python GET /api/admin/completed-assignments
func AdminGetCompletedAssignments(c *gin.Context) {
	if !adminRequired(c) {
		return
	}

	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "50"))
	if page < 1 {
		page = 1
	}
	if limit < 1 || limit > 200 {
		limit = 50
	}
	skip := int64((page - 1) * limit)

	client, err := models.ConnectToDB()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "数据库连接失败"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	col := client.Database("buct-course").Collection("assignment_status")
	filter := bson.M{"status": "completed"}
	total, _ := col.CountDocuments(ctx, filter)

	// 联表查询 users，对应 Python aggregate $lookup
	pipeline := bson.A{
		bson.M{"$match": filter},
		bson.M{"$lookup": bson.M{
			"from":         "users",
			"localField":   "user_id",
			"foreignField": "_id",
			"as":           "user_info",
		}},
		bson.M{"$project": bson.M{
			"assignment_id":      1,
			"assignment_title":   1,
			"assignment_subject": 1,
			"status_time":        1,
			"expires_at":         1,
			"username":           bson.M{"$arrayElemAt": bson.A{"$user_info.username", 0}},
			"user_email":         bson.M{"$arrayElemAt": bson.A{"$user_info.email", 0}},
		}},
		bson.M{"$sort": bson.M{"status_time": -1}},
		bson.M{"$skip": skip},
		bson.M{"$limit": int64(limit)},
	}

	cursor, err := col.Aggregate(ctx, pipeline)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "查询失败"})
		return
	}
	defer cursor.Close(ctx)

	var records []map[string]interface{}
	if err = cursor.All(ctx, &records); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "解析数据失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"records": records,
		"pagination": gin.H{
			"page":  page,
			"limit": limit,
			"total": total,
			"pages": (int(total) + limit - 1) / limit,
		},
		"timestamp": time.Now().Format(time.RFC3339),
	})
}

// AdminGetSystemStatus 获取系统状态信息
// 对应 Python GET /api/admin/system/status
func AdminGetSystemStatus(c *gin.Context) {
	if !adminRequired(c) {
		return
	}

	client, err := models.ConnectToDB()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "数据库连接失败"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	db := client.Database("buct-course")
	users, _ := db.Collection("users").CountDocuments(ctx, bson.M{})
	completedAssignments, _ := db.Collection("assignment_status").CountDocuments(ctx, bson.M{"status": "completed"})
	verificationCodes, _ := db.Collection("verification_codes").CountDocuments(ctx, bson.M{})
	scheduledReminders, _ := db.Collection("scheduled_reminders").CountDocuments(ctx, bson.M{"status": "scheduled"})

	s := scheduler.GetScheduler()
	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"system_status": gin.H{
			"database_stats": gin.H{
				"users":                 users,
				"completed_assignments": completedAssignments,
				"verification_codes":    verificationCodes,
				"scheduled_reminders":   scheduledReminders,
			},
			"scheduler": gin.H{
				"running": s.IsRunning(),
			},
			"server_time": time.Now().Format(time.RFC3339),
		},
	})
}
