package handlers

import (
	"context"
	"fmt"
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

// AssignmentsHandler 作业处理器
type AssignmentsHandler struct{}

// NewAssignmentsHandler 创建作业处理器
func NewAssignmentsHandler() *AssignmentsHandler {
	return &AssignmentsHandler{}
}

// GetStandardAssignments 获取标准作业列表
func (h *AssignmentsHandler) GetStandardAssignments(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "error": "用户未登录"})
		return
	}

	log.Printf("用户 %s 请求获取作业列表", userID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// 从数据库获取课程数据
	tasks, err := services.GetUserCourseData(ctx, userID)
	if err != nil {
		log.Printf("获取课程数据失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "获取作业列表失败"})
		return
	}

	// 获取已完成和已删除的作业ID
	completedIDs, _ := services.GetCompletedAssignmentIDs(ctx, userID)
	deletedIDs, _ := services.GetDeletedAssignmentIDs(ctx, userID)

	completedSet := make(map[string]bool)
	deletedSet := make(map[string]bool)
	for _, id := range completedIDs {
		completedSet[id] = true
	}
	for _, id := range deletedIDs {
		deletedSet[id] = true
	}

	// 转换数据格式 - 初始化为空数组而不是 nil
	formattedTasks := make([]models.Assignment, 0)
	homeworkCount := 0
	testCount := 0

	for _, task := range tasks {
		taskID := task.TaskID

		// 跳过已删除的任务
		if deletedSet[taskID] {
			continue
		}

		assignment := models.Assignment{
			ID:      taskID,
			Subject: task.Subject,
			Type:    task.Type,
			Details: models.AssignmentDetails{
				Task:           task.Title,
				Deadline:       task.Deadline,
				URL:            task.URL,
				CanSubmit:      true,
				IsGroup:        false,
				DetailsContent: task.Details,
			},
			Completed: completedSet[taskID],
			HasTasks:  true,
			TaskCount: 1,
		}
		formattedTasks = append(formattedTasks, assignment)

		if task.Type == "homework" {
			homeworkCount++
		} else {
			testCount++
		}
	}

	stats := models.AssignmentStats{
		HomeworkCount: homeworkCount,
		TestsCount:    testCount,
		TotalCount:    len(formattedTasks),
	}

	log.Printf("从数据库为用户 %s 返回 %d 个作业/测试项目", userID, len(formattedTasks))

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"tasks":   formattedTasks,
		"total":   len(formattedTasks),
		"stats":   stats,
		"source":  "database",
	})
}

// MarkAssignmentComplete 标记作业为已完成
func (h *AssignmentsHandler) MarkAssignmentComplete(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "error": "用户未登录"})
		return
	}

	assignmentID := c.Param("id")
	log.Printf("用户 %s 标记作业 %s 为已完成", userID, assignmentID)

	var req struct {
		Title   string `json:"title"`
		Subject string `json:"subject"`
	}
	c.ShouldBindJSON(&req)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	objID, _ := primitive.ObjectIDFromHex(userID)

	collection := database.GetCollection(database.AssignmentStatusCollection)

	// 检查是否已经存在状态
	var existing models.AssignmentStatus
	err := collection.FindOne(ctx, bson.M{
		"user_id":       objID,
		"assignment_id": assignmentID,
	}).Decode(&existing)

	now := utils.GetBeijingTime()

	if err == nil {
		// 更新现有状态
		_, err = collection.UpdateOne(ctx,
			bson.M{"_id": existing.ID},
			bson.M{"$set": bson.M{
				"status":     "completed",
				"title":      req.Title,
				"subject":    req.Subject,
				"updated_at": now,
			}},
		)
	} else {
		// 创建新状态
		status := models.AssignmentStatus{
			UserID:       objID,
			AssignmentID: assignmentID,
			Title:        req.Title,
			Subject:      req.Subject,
			Status:       "completed",
			CreatedAt:    now,
			UpdatedAt:    now,
		}
		_, err = collection.InsertOne(ctx, status)
	}

	if err != nil {
		log.Printf("标记作业完成失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "标记失败"})
		return
	}

	log.Printf("作业 %s 标记完成成功", assignmentID)
	c.JSON(http.StatusOK, gin.H{"success": true, "message": "作业已标记为完成"})
}

// MarkAssignmentUncomplete 撤销作业完成状态
func (h *AssignmentsHandler) MarkAssignmentUncomplete(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "error": "用户未登录"})
		return
	}

	assignmentID := c.Param("id")
	log.Printf("用户 %s 撤销作业 %s 的完成状态", userID, assignmentID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	objID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.AssignmentStatusCollection)

	_, err := collection.DeleteOne(ctx, bson.M{
		"user_id":       objID,
		"assignment_id": assignmentID,
		"status":        "completed",
	})

	if err != nil {
		log.Printf("撤销作业完成失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "撤销失败"})
		return
	}

	log.Printf("作业 %s 撤销完成成功", assignmentID)
	c.JSON(http.StatusOK, gin.H{"success": true, "message": "已撤销完成状态"})
}

// DeleteAssignment 删除作业
func (h *AssignmentsHandler) DeleteAssignment(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "error": "用户未登录"})
		return
	}

	assignmentID := c.Param("id")
	log.Printf("用户 %s 删除作业 %s", userID, assignmentID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	objID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.AssignmentStatusCollection)

	now := utils.GetBeijingTime()
	status := models.AssignmentStatus{
		UserID:       objID,
		AssignmentID: assignmentID,
		Status:       "deleted",
		CreatedAt:    now,
		UpdatedAt:    now,
	}

	// 使用upsert
	_, err := collection.UpdateOne(ctx,
		bson.M{"user_id": objID, "assignment_id": assignmentID},
		bson.M{"$set": bson.M{
			"status":     "deleted",
			"updated_at": now,
		}},
		nil,
	)

	if err != nil {
		// 如果不存在则插入
		_, err = collection.InsertOne(ctx, status)
		if err != nil {
			log.Printf("删除作业失败: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "删除失败"})
			return
		}
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "作业已删除"})
}

// RestoreAssignment 恢复作业
func (h *AssignmentsHandler) RestoreAssignment(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "error": "用户未登录"})
		return
	}

	assignmentID := c.Param("id")
	log.Printf("用户 %s 恢复作业 %s", userID, assignmentID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	objID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.AssignmentStatusCollection)

	_, err := collection.DeleteOne(ctx, bson.M{
		"user_id":       objID,
		"assignment_id": assignmentID,
		"status":        "deleted",
	})

	if err != nil {
		log.Printf("恢复作业失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "恢复失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "作业已恢复"})
}

// GetDeletedAssignments 获取已删除的作业（回收站）
func (h *AssignmentsHandler) GetDeletedAssignments(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "error": "用户未登录"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	objID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.AssignmentStatusCollection)

	cursor, err := collection.Find(ctx, bson.M{
		"user_id": objID,
		"status":  "deleted",
	})

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "获取回收站失败"})
		return
	}
	defer cursor.Close(ctx)

	var deletedItems []models.AssignmentStatus
	if err := cursor.All(ctx, &deletedItems); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "解析数据失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"items":   deletedItems,
		"count":   len(deletedItems),
	})
}

// RefreshAssignments 刷新作业数据（异步）
func (h *AssignmentsHandler) RefreshAssignments(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "error": "用户未登录"})
		return
	}

	log.Printf("用户 %s 请求刷新作业数据", userID)

	// 异步刷新
	go services.RefreshUserData(userID)

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "正在刷新数据...",
	})
}

// RefreshAssignmentsSync 同步刷新作业数据
func (h *AssignmentsHandler) RefreshAssignmentsSync(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "error": "用户未登录"})
		return
	}

	log.Printf("用户 %s 请求同步刷新作业数据", userID)

	// 同步刷新
	count, err := services.RefreshUserData(userID)
	if err != nil {
		log.Printf("刷新数据失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "数据刷新完成",
		"count":   count,
	})
}

// GetCompletedAssignments 获取已完成的作业
func (h *AssignmentsHandler) GetCompletedAssignments(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "error": "用户未登录"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	objID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.AssignmentStatusCollection)

	cursor, err := collection.Find(ctx, bson.M{
		"user_id": objID,
		"status":  "completed",
	})

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "获取已完成作业失败"})
		return
	}
	defer cursor.Close(ctx)

	var completedItems []models.AssignmentStatus
	if err := cursor.All(ctx, &completedItems); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "解析数据失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"items":   completedItems,
		"count":   len(completedItems),
	})
}

// PermanentDeleteAssignment 永久删除作业
func (h *AssignmentsHandler) PermanentDeleteAssignment(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "error": "用户未登录"})
		return
	}

	assignmentID := c.Param("id")
	log.Printf("用户 %s 永久删除作业 %s", userID, assignmentID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	objID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.AssignmentStatusCollection)

	_, err := collection.DeleteOne(ctx, bson.M{
		"user_id":       objID,
		"assignment_id": assignmentID,
	})

	if err != nil {
		log.Printf("永久删除作业失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "删除失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"success": true, "message": "作业已永久删除"})
}

// RemindAssignment 发送作业提醒
func (h *AssignmentsHandler) RemindAssignment(c *gin.Context) {
	userID := middleware.GetUserID(c)
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"success": false, "error": "用户未登录"})
		return
	}

	assignmentID := c.Param("id")
	log.Printf("用户 %s 请求提醒作业 %s", userID, assignmentID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	objID, err := primitive.ObjectIDFromHex(userID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "error": "无效的用户ID"})
		return
	}

	// 检查作业是否已完成
	completedIDs, _ := services.GetCompletedAssignmentIDs(ctx, userID)
	for _, id := range completedIDs {
		if id == assignmentID {
			c.JSON(http.StatusBadRequest, gin.H{"success": false, "error": "该作业已完成，无需提醒"})
			return
		}
	}

	// 检查作业是否已删除
	deletedIDs, _ := services.GetDeletedAssignmentIDs(ctx, userID)
	for _, id := range deletedIDs {
		if id == assignmentID {
			c.JSON(http.StatusBadRequest, gin.H{"success": false, "error": "该作业已删除，无法提醒"})
			return
		}
	}

	// 从数据库查询作业信息
	courseDataCollection := database.GetCollection(database.CourseDataCollection)
	var assignment struct {
		Subject  string `bson:"subject"`
		Title    string `bson:"title"`
		Deadline string `bson:"deadline"`
		Type     string `bson:"type"`
		Details  string `bson:"details"`
	}

	err = courseDataCollection.FindOne(ctx, bson.M{
		"user_id": objID,
		"task_id": assignmentID,
	}).Decode(&assignment)

	if err != nil {
		log.Printf("作业 %s 不存在于数据库中: %v", assignmentID, err)
		c.JSON(http.StatusNotFound, gin.H{"success": false, "error": "作业不存在"})
		return
	}

	// 获取用户邮箱
	usersCollection := database.GetCollection(database.UsersCollection)
	var user struct {
		Email string `bson:"email"`
	}
	err = usersCollection.FindOne(ctx, bson.M{"_id": objID}).Decode(&user)
	if err != nil || user.Email == "" {
		c.JSON(http.StatusBadRequest, gin.H{"success": false, "error": "未找到用户邮箱，请在设置中配置邮箱"})
		return
	}

	// 解析截止时间
	var dueTime time.Time
	if assignment.Deadline != "" {
		if t, err := time.Parse(time.RFC3339, assignment.Deadline); err == nil {
			dueTime = t
		} else if t, err := time.Parse("2006-01-02T15:04:05", assignment.Deadline); err == nil {
			dueTime = t
		}
	}

	// 格式化截止时间显示
	deadlineDisplay := assignment.Deadline
	if !dueTime.IsZero() {
		deadlineDisplay = dueTime.Format("2006年01月02日 15:04:05")
	}

	// 生成提醒类型文字
	assignmentType := "作业"
	if assignment.Type == "test" {
		assignmentType = "测试"
	}

	// 解析前端传来的提醒配置
	var requestData struct {
		ReminderConfig struct {
			Type     string  `json:"type"`     // instant, 1h, 3h, 6h, 12h, custom-hours-before, custom-hours-after, custom-datetime
			Hours    float64 `json:"hours"`    // 小时数
			Timing   string  `json:"timing"`   // before 或 after
			Datetime string  `json:"datetime"` // 自定义时间 YYYY-MM-DDTHH:mm
		} `json:"reminderConfig"`
	}
	c.ShouldBindJSON(&requestData)
	reminderConfig := requestData.ReminderConfig

	// 计算计划发送时间
	now := time.Now()
	scheduledTime := now
	scheduleDesc := "立即"

	rtype := reminderConfig.Type
	if rtype == "" {
		rtype = "instant"
	}

	switch rtype {
	case "instant":
		scheduledTime = now
		scheduleDesc = "立即"

	case "1h", "3h", "6h", "12h":
		presetHours := map[string]float64{"1h": 1, "3h": 3, "6h": 6, "12h": 12}
		hours := presetHours[rtype]
		timing := reminderConfig.Timing
		if timing == "" {
			timing = "before"
		}

		if timing == "after" {
			scheduledTime = now.Add(time.Duration(hours * float64(time.Hour)))
			scheduleDesc = fmt.Sprintf("%.0f小时后", hours)
		} else if !dueTime.IsZero() {
			scheduledTime = dueTime.Add(-time.Duration(hours * float64(time.Hour)))
			scheduleDesc = fmt.Sprintf("截止前%.0f小时", hours)
		} else {
			scheduledTime = now.Add(time.Duration(hours * float64(time.Hour)))
			scheduleDesc = fmt.Sprintf("%.0f小时后", hours)
		}

	case "custom-hours-before":
		hours := reminderConfig.Hours
		if hours <= 0 {
			hours = 1
		}
		if !dueTime.IsZero() {
			scheduledTime = dueTime.Add(-time.Duration(hours * float64(time.Hour)))
			scheduleDesc = fmt.Sprintf("截止前%.0f小时", hours)
		} else {
			scheduledTime = now.Add(time.Duration(hours * float64(time.Hour)))
			scheduleDesc = fmt.Sprintf("%.0f小时后", hours)
		}

	case "custom-hours-after":
		hours := reminderConfig.Hours
		if hours <= 0 {
			hours = 1
		}
		scheduledTime = now.Add(time.Duration(hours * float64(time.Hour)))
		scheduleDesc = fmt.Sprintf("%.0f小时后", hours)

	case "custom-datetime":
		if reminderConfig.Datetime != "" {
			// 解析自定义时间 (格式: YYYY-MM-DDTHH:mm)
			if t, err := time.ParseInLocation("2006-01-02T15:04", reminderConfig.Datetime, time.Local); err == nil {
				scheduledTime = t
				scheduleDesc = t.Format("2006-01-02 15:04")
			} else {
				log.Printf("解析自定义时间失败: %v", err)
				scheduledTime = now
				scheduleDesc = "立即"
			}
		}

	default:
		scheduledTime = now
		scheduleDesc = "立即"
	}

	// 生成提醒消息
	subject := fmt.Sprintf("BUCT课程提醒 - %s提醒", assignmentType)
	content := fmt.Sprintf(`
		<p><strong>⚠️ %s提醒</strong></p>
		<p><strong>科目:</strong> %s</p>
		<p><strong>标题:</strong> %s</p>
		<p><strong>截止时间:</strong> %s</p>
		<p><strong>提醒时间:</strong> %s</p>
	`, assignmentType, assignment.Subject, assignment.Title, deadlineDisplay, scheduleDesc)

	// 判断是立即发送还是定时发送
	if scheduledTime.Before(now) || scheduledTime.Sub(now) < time.Minute {
		// 立即发送
		err = services.SendReminderEmail(user.Email, subject, content)
		if err != nil {
			log.Printf("发送提醒邮件失败: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "邮件发送失败，请检查邮箱配置"})
			return
		}

		// 记录到数据库
		scheduledRemindersCollection := database.GetCollection("scheduled_reminders")
		_, err = scheduledRemindersCollection.InsertOne(ctx, bson.M{
			"user_id":        objID,
			"type":           "assignment",
			"target_id":      assignmentID,
			"email":          user.Email,
			"message":        content,
			"scheduled_time": now,
			"status":         "sent",
			"created_at":     now,
			"updated_at":     now,
			"sent_at":        now,
		})
		if err != nil {
			log.Printf("记录提醒到数据库失败: %v", err)
		}

		log.Printf("已立即发送提醒到: %s", user.Email)
		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"message": fmt.Sprintf("提醒已立即发送：%s - %s", assignment.Subject, assignment.Title),
			"detail": gin.H{
				"schedule": "now",
				"email":    user.Email,
			},
		})
	} else {
		// 定时发送 - 插入到 scheduled_reminders 表，由 scheduler 处理
		scheduledRemindersCollection := database.GetCollection("scheduled_reminders")
		_, err = scheduledRemindersCollection.InsertOne(ctx, bson.M{
			"user_id":        objID,
			"type":           "assignment",
			"target_id":      assignmentID,
			"email":          user.Email,
			"subject":        subject,
			"message":        content,
			"scheduled_time": scheduledTime,
			"status":         "scheduled",
			"created_at":     now,
			"updated_at":     now,
		})
		if err != nil {
			log.Printf("保存定时提醒失败: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"success": false, "error": "保存定时提醒失败"})
			return
		}

		log.Printf("已创建定时提醒，计划 %s 发送到: %s", scheduleDesc, user.Email)
		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"message": fmt.Sprintf("已设置%s提醒（%s）：%s - %s", assignmentType, scheduleDesc, assignment.Subject, assignment.Title),
			"assignment": gin.H{
				"subject":       assignment.Subject,
				"task":          assignment.Title,
				"deadline":      deadlineDisplay,
				"type":          assignmentType,
				"reminder_time": scheduleDesc,
			},
		})
	}
}
