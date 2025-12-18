package scheduler

import (
	"context"
	"log"
	"sync"
	"time"

	"buct-course-remind/internal/database"
	"buct-course-remind/internal/models"
	"buct-course-remind/internal/services"
	"buct-course-remind/internal/utils"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

// CourseDataScheduler 课程数据定时刷新调度器
type CourseDataScheduler struct {
	running              bool
	mutex                sync.Mutex
	refreshInterval      time.Duration
	reminderCheckInterval time.Duration
	autoReminderInterval  time.Duration
	stopChan             chan struct{}
}

var schedulerInstance *CourseDataScheduler

// GetScheduler 获取调度器实例
func GetScheduler() *CourseDataScheduler {
	if schedulerInstance == nil {
		schedulerInstance = &CourseDataScheduler{
			refreshInterval:       12 * time.Hour,
			reminderCheckInterval: 5 * time.Second,
			autoReminderInterval:  1 * time.Hour,
			stopChan:              make(chan struct{}),
		}
	}
	return schedulerInstance
}

// InitScheduler 初始化调度器
func InitScheduler() {
	scheduler := GetScheduler()
	scheduler.Start()
}

// Start 启动调度器
func (s *CourseDataScheduler) Start() {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	if s.running {
		log.Println("调度器已经在运行中")
		return
	}

	s.running = true
	go s.run()
	log.Println("课程数据定时刷新调度器已启动")
}

// Stop 停止调度器
func (s *CourseDataScheduler) Stop() {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	if !s.running {
		return
	}

	s.running = false
	close(s.stopChan)
	log.Println("课程数据定时刷新调度器已停止")
}

// run 调度器主循环
func (s *CourseDataScheduler) run() {
	refreshTicker := time.NewTicker(s.refreshInterval)
	reminderTicker := time.NewTicker(s.reminderCheckInterval)
	autoReminderTicker := time.NewTicker(s.autoReminderInterval)

	defer refreshTicker.Stop()
	defer reminderTicker.Stop()
	defer autoReminderTicker.Stop()

	for {
		select {
		case <-s.stopChan:
			return

		case <-refreshTicker.C:
			s.refreshAllUsers()

		case <-reminderTicker.C:
			s.processDueReminders()

		case <-autoReminderTicker.C:
			s.checkAndCreateAutoReminders()
		}
	}
}

// refreshAllUsers 刷新所有需要刷新的用户数据
func (s *CourseDataScheduler) refreshAllUsers() {
	log.Println("开始检查需要刷新数据的用户")

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	users := s.getUsersNeedRefresh(ctx)
	if len(users) == 0 {
		return
	}

	log.Printf("发现 %d 个用户需要刷新数据", len(users))

	for _, userID := range users {
		if !s.running {
			break
		}

		if count, err := services.RefreshUserData(userID); err != nil {
			log.Printf("刷新用户 %s 数据失败: %v", userID, err)
		} else {
			log.Printf("刷新用户 %s 数据成功，共 %d 条", userID, count)
		}

		// 每个用户之间间隔2秒
		time.Sleep(2 * time.Second)
	}
}

// getUsersNeedRefresh 获取需要刷新数据的用户列表
func (s *CourseDataScheduler) getUsersNeedRefresh(ctx context.Context) []string {
	collection := database.GetCollection(database.UsersCollection)

	cursor, err := collection.Find(ctx, bson.M{
		"student_id": bson.M{"$exists": true, "$nin": []interface{}{nil, ""}},
		"s_password": bson.M{"$exists": true, "$nin": []interface{}{nil, ""}},
	})
	if err != nil {
		log.Printf("查询用户失败: %v", err)
		return nil
	}
	defer cursor.Close(ctx)

	var usersNeedRefresh []string
	currentTime := utils.GetBeijingTime()

	for cursor.Next(ctx) {
		var user models.User
		if err := cursor.Decode(&user); err != nil {
			continue
		}

		userID := user.ID.Hex()

		// 检查最后更新时间
		lastUpdate := getLastUpdateTime(ctx, userID)
		if lastUpdate == nil {
			// 从未更新过，需要刷新
			usersNeedRefresh = append(usersNeedRefresh, userID)
		} else {
			// 检查是否超过12小时
			if currentTime.Sub(*lastUpdate) >= s.refreshInterval {
				usersNeedRefresh = append(usersNeedRefresh, userID)
			}
		}
	}

	return usersNeedRefresh
}

// getLastUpdateTime 获取用户课程数据的最后更新时间
func getLastUpdateTime(ctx context.Context, userID string) *time.Time {
	objID, err := primitive.ObjectIDFromHex(userID)
	if err != nil {
		return nil
	}

	collection := database.GetCollection(database.CourseDataCollection)

	var result struct {
		UpdatedAt time.Time `bson:"updated_at"`
	}

	err = collection.FindOne(ctx, bson.M{"user_id": objID}).Decode(&result)
	if err != nil {
		return nil
	}

	return &result.UpdatedAt
}

// processDueReminders 处理到期的定时提醒
func (s *CourseDataScheduler) processDueReminders() {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	collection := database.GetCollection(database.ScheduledRemindersCollection)
	currentTime := utils.GetBeijingTime()

	// 查询到期的提醒（status 为 scheduled 且 scheduled_time <= 当前时间）
	cursor, err := collection.Find(ctx, bson.M{
		"status":         "scheduled",
		"scheduled_time": bson.M{"$lte": currentTime},
	})
	if err != nil {
		log.Printf("查询到期提醒失败: %v", err)
		return
	}
	defer cursor.Close(ctx)

	for cursor.Next(ctx) {
		var reminder struct {
			ID            primitive.ObjectID `bson:"_id"`
			UserID        primitive.ObjectID `bson:"user_id"`
			Email         string             `bson:"email"`
			Subject       string             `bson:"subject"`
			Message       string             `bson:"message"`
			TargetID      string             `bson:"target_id"`
			ScheduledTime time.Time          `bson:"scheduled_time"`
		}
		if err := cursor.Decode(&reminder); err != nil {
			log.Printf("解析提醒数据失败: %v", err)
			continue
		}

		// 获取用户邮箱（优先使用记录中的邮箱）
		email := reminder.Email
		if email == "" {
			email = getUserEmail(ctx, reminder.UserID.Hex())
		}
		if email == "" {
			log.Printf("用户 %s 没有邮箱，跳过提醒", reminder.UserID.Hex())
			continue
		}

		// 发送提醒邮件
		subject := reminder.Subject
		if subject == "" {
			subject = "⚠️ 作业提醒"
		}
		content := reminder.Message
		if content == "" {
			content = "您有一个作业需要完成，请及时处理。"
		}

		if err := services.SendReminderEmail(email, subject, content); err != nil {
			log.Printf("发送提醒邮件失败: %v", err)
			// 标记为失败
			collection.UpdateOne(ctx,
				bson.M{"_id": reminder.ID},
				bson.M{"$set": bson.M{
					"status":     "failed",
					"error":      err.Error(),
					"updated_at": currentTime,
				}},
			)
			continue
		}

		// 标记为已发送
		collection.UpdateOne(ctx,
			bson.M{"_id": reminder.ID},
			bson.M{"$set": bson.M{
				"status":     "sent",
				"sent_at":    currentTime,
				"updated_at": currentTime,
			}},
		)

		log.Printf("已发送定时提醒邮件: %s -> %s", reminder.TargetID, email)
	}
}

// checkAndCreateAutoReminders 检查并创建自动提醒
func (s *CourseDataScheduler) checkAndCreateAutoReminders() {
	log.Println("检查需要自动提醒的作业")
	
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// 获取所有用户（检查是否启用自动提醒）
	usersCollection := database.GetCollection(database.UsersCollection)
	cursor, err := usersCollection.Find(ctx, bson.M{
		"email": bson.M{"$exists": true, "$ne": ""},
	})
	if err != nil {
		log.Printf("查询用户失败: %v", err)
		return
	}
	defer cursor.Close(ctx)

	for cursor.Next(ctx) {
		var user models.User
		if err := cursor.Decode(&user); err != nil {
			continue
		}

		// 检查用户是否启用了自动提醒（默认启用）
		// 如果 auto_reminder 字段不存在或为 true，则启用
		autoReminder := true
		if !user.AutoReminder && user.ReminderHours > 0 {
			// 明确设置为 false
			autoReminder = false
		}

		if !autoReminder {
			continue
		}

		// 获取用户自定义的提醒时间，默认24小时
		reminderHours := user.ReminderHours
		if reminderHours <= 0 {
			reminderHours = 24
		}

		s.checkUserAutoRemindersWithHours(ctx, user.ID.Hex(), reminderHours)
	}
}

// checkUserAutoRemindersWithHours 检查单个用户的自动提醒（使用自定义提醒时间）
func (s *CourseDataScheduler) checkUserAutoRemindersWithHours(ctx context.Context, userID string, reminderHours float64) {
	// 获取用户的课程数据
	tasks, err := services.GetUserCourseData(ctx, userID)
	if err != nil {
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

	currentTime := utils.GetBeijingTime()
	// reminderHours 使用传入的参数值

	for _, task := range tasks {
		// 跳过已完成或已删除的作业
		if completedSet[task.TaskID] || deletedSet[task.TaskID] {
			continue
		}

		// 解析截止时间（支持多种格式）
		var deadline time.Time
		var parseErr error

		// 尝试 ISO 格式 2025-12-23T12:59:00
		deadline, parseErr = time.Parse("2006-01-02T15:04:05", task.Deadline)
		if parseErr != nil {
			// 尝试 RFC3339 格式
			deadline, parseErr = time.Parse(time.RFC3339, task.Deadline)
		}
		if parseErr != nil {
			// 尝试简单格式 2006-01-02 15:04
			deadline, parseErr = time.Parse("2006-01-02 15:04", task.Deadline)
		}
		if parseErr != nil {
			// 尝试简单格式 2006-01-02 15:04:05
			deadline, parseErr = time.Parse("2006-01-02 15:04:05", task.Deadline)
		}
		if parseErr != nil {
			continue
		}

		// 计算提醒时间（截止时间前 reminderHours 小时）
		reminderTime := deadline.Add(-time.Duration(reminderHours) * time.Hour)

		// 如果提醒时间已过（已经在截止前24小时内），但截止时间还没到，立即创建提醒
		if reminderTime.Before(currentTime) && deadline.After(currentTime) {
			// 检查是否已经创建了提醒
			if !reminderExists(ctx, userID, task.TaskID) {
				createReminder(ctx, userID, task, currentTime)
				log.Printf("创建紧急自动提醒: %s - %s (截止: %s)", task.Subject, task.Title, deadline.Format("2006-01-02 15:04"))
			}
		} else if reminderTime.After(currentTime) && reminderTime.Before(currentTime.Add(24*time.Hour)) {
			// 如果提醒时间在未来且在24小时内，创建定时提醒
			if !reminderExists(ctx, userID, task.TaskID) {
				createReminder(ctx, userID, task, reminderTime)
			}
		}
	}
}

// getUserEmail 获取用户邮箱
func getUserEmail(ctx context.Context, userID string) string {
	objID, err := primitive.ObjectIDFromHex(userID)
	if err != nil {
		return ""
	}

	collection := database.GetCollection(database.UsersCollection)
	var user models.User
	if err := collection.FindOne(ctx, bson.M{"_id": objID}).Decode(&user); err != nil {
		return ""
	}

	return user.Email
}

// formatReminderContent 格式化提醒内容
func formatReminderContent(reminder models.ScheduledReminder) string {
	return "<p><strong>科目：</strong>" + reminder.Subject + "</p>" +
		"<p><strong>作业：</strong>" + reminder.Title + "</p>" +
		"<p><strong>提醒时间：</strong>" + reminder.ReminderTime.Format("2006-01-02 15:04") + "</p>"
}

// reminderExists 检查提醒是否已存在
func reminderExists(ctx context.Context, userID, assignmentID string) bool {
	objID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.ScheduledRemindersCollection)

	count, err := collection.CountDocuments(ctx, bson.M{
		"user_id":       objID,
		"assignment_id": assignmentID,
		"sent":          false,
	})

	return err == nil && count > 0
}

// createReminder 创建提醒
func createReminder(ctx context.Context, userID string, task models.CourseData, reminderTime time.Time) {
	objID, _ := primitive.ObjectIDFromHex(userID)
	collection := database.GetCollection(database.ScheduledRemindersCollection)

	reminder := models.ScheduledReminder{
		UserID:       objID,
		AssignmentID: task.TaskID,
		Title:        task.Title,
		Subject:      task.Subject,
		ReminderTime: reminderTime,
		Sent:         false,
		Type:         "auto",
		CreatedAt:    utils.GetBeijingTime(),
	}

	if _, err := collection.InsertOne(ctx, reminder); err != nil {
		log.Printf("创建提醒失败: %v", err)
	} else {
		log.Printf("已创建自动提醒: %s - %s", task.Subject, task.Title)
	}
}
