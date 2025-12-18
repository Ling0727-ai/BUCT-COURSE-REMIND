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

// TodosHandler 待办事项处理器
type TodosHandler struct{}

// NewTodosHandler 创建待办事项处理器
func NewTodosHandler() *TodosHandler {
	return &TodosHandler{}
}

// GetTodos 获取待办事项列表
func (h *TodosHandler) GetTodos(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "用户未登录", "success": false})
		return
	}

	includeCompleted := c.Query("include_completed") == "true"

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	objID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.TodosCollection)

	filter := bson.M{
		"user_id": objID,
		"deleted": bson.M{"$ne": true},
	}

	if !includeCompleted {
		filter["completed"] = false
	}

	opts := options.Find().SetSort(bson.D{
		{Key: "priority", Value: -1},
		{Key: "due_date", Value: 1},
		{Key: "created_at", Value: -1},
	})

	cursor, err := collection.Find(ctx, filter, opts)
	if err != nil {
		log.Printf("获取待办列表失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "获取待办列表失败",
			"success": false,
		})
		return
	}
	defer cursor.Close(ctx)

	var todos []models.Todo
	if err := cursor.All(ctx, &todos); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "解析数据失败",
			"success": false,
		})
		return
	}

	// 转换为响应格式 - 初始化为空数组而不是 nil
	todoResponses := make([]models.TodoResponse, 0)
	for _, todo := range todos {
		todoResponses = append(todoResponses, todo.ToResponse())
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"todos":   todoResponses,
		"count":   len(todoResponses),
	})
}

// CreateTodo 创建待办事项
func (h *TodosHandler) CreateTodo(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "用户未登录", "success": false})
		return
	}

	var req models.CreateTodoRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "待办标题不能为空", "success": false})
		return
	}

	// 验证优先级
	priority := req.Priority
	if priority != "low" && priority != "medium" && priority != "high" {
		priority = "medium"
	}

	// 计算截止日期
	var dueDate *time.Time
	var estimatedHours *float64

	if req.Hours != nil && *req.Hours > 0 {
		hours := *req.Hours
		estimatedHours = &hours
		due := utils.GetBeijingTime().Add(time.Duration(hours * float64(time.Hour)))
		dueDate = &due
	} else if req.DueDate != nil && *req.DueDate != "" {
		parsed, err := time.Parse(time.RFC3339, *req.DueDate)
		if err == nil {
			dueDate = &parsed
		}
	} else {
		// 默认24小时
		hours := 24.0
		estimatedHours = &hours
		due := utils.GetBeijingTime().Add(24 * time.Hour)
		dueDate = &due
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	objID, _ := primitive.ObjectIDFromHex(userID)
	now := utils.GetBeijingTime()

	todo := models.Todo{
		UserID:         objID,
		Title:          req.Title,
		Description:    req.Description,
		Priority:       priority,
		DueDate:        dueDate,
		EstimatedHours: estimatedHours,
		Completed:      false,
		Deleted:        false,
		CreatedAt:      now,
		UpdatedAt:      now,
	}

	collection := database.GetCollection(database.TodosCollection)
	result, err := collection.InsertOne(ctx, todo)
	if err != nil {
		log.Printf("创建待办事项失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "创建待办事项失败",
			"success": false,
		})
		return
	}

	log.Printf("用户 %s 创建待办事项: %s", userID, req.Title)
	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "待办事项创建成功",
		"todo_id": result.InsertedID.(primitive.ObjectID).Hex(),
	})
}

// UpdateTodo 更新待办事项
func (h *TodosHandler) UpdateTodo(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "用户未登录", "success": false})
		return
	}

	todoID := c.Param("id")
	todoObjID, err := primitive.ObjectIDFromHex(todoID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的待办ID", "success": false})
		return
	}

	var req models.UpdateTodoRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请求格式错误", "success": false})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	userObjID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.TodosCollection)

	// 检查待办是否存在
	var existing models.Todo
	err = collection.FindOne(ctx, bson.M{
		"_id":     todoObjID,
		"user_id": userObjID,
	}).Decode(&existing)

	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "待办事项不存在", "success": false})
		return
	}

	// 准备更新数据
	updateData := bson.M{"updated_at": utils.GetBeijingTime()}

	if req.Title != nil && *req.Title != "" {
		updateData["title"] = *req.Title
	}
	if req.Description != nil {
		updateData["description"] = req.Description
	}
	if req.Priority != nil {
		if *req.Priority == "low" || *req.Priority == "medium" || *req.Priority == "high" {
			updateData["priority"] = *req.Priority
		}
	}
	if req.Hours != nil && *req.Hours > 0 {
		hours := *req.Hours
		updateData["estimated_hours"] = hours
		due := utils.GetBeijingTime().Add(time.Duration(hours * float64(time.Hour)))
		updateData["due_date"] = due
	}
	if req.DueDate != nil && *req.DueDate != "" {
		parsed, err := time.Parse(time.RFC3339, *req.DueDate)
		if err == nil {
			updateData["due_date"] = parsed
		}
	}
	if req.Completed != nil {
		updateData["completed"] = *req.Completed
		if *req.Completed {
			now := utils.GetBeijingTime()
			updateData["completed_at"] = now
		} else {
			updateData["completed_at"] = nil
		}
	}

	_, err = collection.UpdateOne(ctx,
		bson.M{"_id": todoObjID},
		bson.M{"$set": updateData},
	)

	if err != nil {
		log.Printf("更新待办事项失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "更新失败", "success": false})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "待办事项更新成功"})
}

// DeleteTodo 删除待办事项
func (h *TodosHandler) DeleteTodo(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "用户未登录", "success": false})
		return
	}

	todoID := c.Param("id")
	todoObjID, err := primitive.ObjectIDFromHex(todoID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的待办ID", "success": false})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	userObjID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.TodosCollection)

	now := utils.GetBeijingTime()
	_, err = collection.UpdateOne(ctx,
		bson.M{"_id": todoObjID, "user_id": userObjID},
		bson.M{"$set": bson.M{
			"deleted":    true,
			"deleted_at": now,
			"updated_at": now,
		}},
	)

	if err != nil {
		log.Printf("删除待办事项失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "删除失败", "success": false})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "待办事项已删除"})
}

// CompleteTodo 完成待办事项
func (h *TodosHandler) CompleteTodo(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "用户未登录", "success": false})
		return
	}

	todoID := c.Param("id")
	todoObjID, err := primitive.ObjectIDFromHex(todoID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的待办ID", "success": false})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	userObjID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.TodosCollection)

	now := utils.GetBeijingTime()
	_, err = collection.UpdateOne(ctx,
		bson.M{"_id": todoObjID, "user_id": userObjID},
		bson.M{"$set": bson.M{
			"completed":    true,
			"completed_at": now,
			"updated_at":   now,
		}},
	)

	if err != nil {
		log.Printf("完成待办事项失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "操作失败", "success": false})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "待办事项已完成"})
}

// UncompleteTodo 撤销完成待办事项
func (h *TodosHandler) UncompleteTodo(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "用户未登录", "success": false})
		return
	}

	todoID := c.Param("id")
	todoObjID, err := primitive.ObjectIDFromHex(todoID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的待办ID", "success": false})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	userObjID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.TodosCollection)

	now := utils.GetBeijingTime()
	_, err = collection.UpdateOne(ctx,
		bson.M{"_id": todoObjID, "user_id": userObjID},
		bson.M{"$set": bson.M{
			"completed":    false,
			"completed_at": nil,
			"updated_at":   now,
		}},
	)

	if err != nil {
		log.Printf("撤销完成待办事项失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "操作失败", "success": false})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "已撤销完成状态"})
}

// GetDeletedTodos 获取已删除的待办事项
func (h *TodosHandler) GetDeletedTodos(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "用户未登录", "success": false})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	userObjID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.TodosCollection)

	cursor, err := collection.Find(ctx, bson.M{
		"user_id": userObjID,
		"deleted": true,
	})
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取数据失败", "success": false})
		return
	}
	defer cursor.Close(ctx)

	var todos []models.Todo
	if err := cursor.All(ctx, &todos); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "解析数据失败", "success": false})
		return
	}

	var todoResponses []models.TodoResponse
	for _, todo := range todos {
		todoResponses = append(todoResponses, todo.ToResponse())
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"todos":   todoResponses,
		"count":   len(todoResponses),
	})
}

// RestoreTodo 恢复待办事项
func (h *TodosHandler) RestoreTodo(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "用户未登录", "success": false})
		return
	}

	todoID := c.Param("id")
	todoObjID, err := primitive.ObjectIDFromHex(todoID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的待办ID", "success": false})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	userObjID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.TodosCollection)

	now := utils.GetBeijingTime()
	_, err = collection.UpdateOne(ctx,
		bson.M{"_id": todoObjID, "user_id": userObjID},
		bson.M{"$set": bson.M{
			"deleted":    false,
			"deleted_at": nil,
			"updated_at": now,
		}},
	)

	if err != nil {
		log.Printf("恢复待办事项失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "恢复失败", "success": false})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "待办事项已恢复"})
}

// PermanentDeleteTodo 永久删除待办事项
func (h *TodosHandler) PermanentDeleteTodo(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "用户未登录", "success": false})
		return
	}

	todoID := c.Param("id")
	todoObjID, err := primitive.ObjectIDFromHex(todoID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的待办ID", "success": false})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	userObjID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.TodosCollection)

	_, err = collection.DeleteOne(ctx, bson.M{
		"_id":     todoObjID,
		"user_id": userObjID,
	})

	if err != nil {
		log.Printf("永久删除待办事项失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "删除失败", "success": false})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "待办事项已永久删除"})
}
