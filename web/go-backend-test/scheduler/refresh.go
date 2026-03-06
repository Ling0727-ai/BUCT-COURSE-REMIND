package scheduler

import (
	"context"
	"log"
	"time"

	"github.com/Ling0727-ai/go-buct-course-backend/models"
	"github.com/Ling0727-ai/go-buct-course-backend/models/CourseData"
	"github.com/Ling0727-ai/go-buct-course-backend/scraper"
	"go.mongodb.org/mongo-driver/bson"
)

// run 调度器主循环，对应 Python _run_scheduler
func (s *CourseDataScheduler) run() {
	log.Println("[scheduler] 调度器已启动")

	reminderTicker := time.NewTicker(ReminderCheckInterval)
	autoReminderTicker := time.NewTicker(AutoReminderCheckInterval)
	refreshTicker := time.NewTicker(RefreshInterval)
	defer reminderTicker.Stop()
	defer autoReminderTicker.Stop()
	defer refreshTicker.Stop()

	// semaphore：同一时刻最多 1 个 processDueReminders 在运行，防止 goroutine 堆积
	reminderSem := make(chan struct{}, 1)
	// semaphore：同一时刻最多 1 个 checkAndCreateAutoReminders 在运行
	autoSem := make(chan struct{}, 1)

	// 启动时先检查一次：只刷新"从未更新过"或"距上次超12h"的用户
	s.runRefreshCycle()

	// 启动时先检查一次自动提醒
	go func() {
		select {
		case autoSem <- struct{}{}:
			defer func() { <-autoSem }()
			if err := checkAndCreateAutoReminders(); err != nil {
				log.Printf("[scheduler] 启动时检查自动提醒异常: %v", err)
			}
		default:
			// 已有一个在运行，跳过
		}
	}()

	for {
		select {
		case <-s.stopCh:
			log.Println("[scheduler] 调度器已停止")
			return

		case <-refreshTicker.C:
			s.runRefreshCycle()

		case <-reminderTicker.C:
			// 非阻塞尝试获取 semaphore，拿不到说明上一轮还没跑完，直接跳过
			go func() {
				select {
				case reminderSem <- struct{}{}:
					defer func() { <-reminderSem }()
					if err := processDueReminders(); err != nil {
						log.Printf("[scheduler] 处理到期提醒异常: %v", err)
					}
				default:
					log.Println("[scheduler] 上一轮提醒处理尚未完成，跳过本次")
				}
			}()

		case <-autoReminderTicker.C:
			go func() {
				select {
				case autoSem <- struct{}{}:
					defer func() { <-autoSem }()
					if err := checkAndCreateAutoReminders(); err != nil {
						log.Printf("[scheduler] 检查自动提醒异常: %v", err)
					}
				default:
					log.Println("[scheduler] 上一轮自动提醒检查尚未完成，跳过本次")
				}
			}()
		}
	}
}

// runRefreshCycle 执行一轮全量用户数据刷新，对应 Python 主循环中对 _get_users_need_refresh 的调用
func (s *CourseDataScheduler) runRefreshCycle() {
	users, err := getUsersNeedRefresh()
	if err != nil {
		log.Printf("[scheduler] 获取待刷新用户列表失败: %v", err)
		return
	}
	if len(users) == 0 {
		return
	}

	log.Printf("[scheduler] 发现 %d 个用户需要刷新数据", len(users))
	for _, userID := range users {
		select {
		case <-s.stopCh:
			return
		default:
		}
		if err := refreshUserData(userID); err != nil {
			log.Printf("[scheduler] 刷新用户 %s 数据失败: %v", userID, err)
		}
		time.Sleep(UserRefreshGap)
	}
}

// getUsersNeedRefresh 获取需要刷新数据的用户列表
// 对应 Python _get_users_need_refresh
func getUsersNeedRefresh() ([]string, error) {
	client, err := models.ConnectToDB()
	if err != nil {
		return nil, err
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// 查询有学号和密码的用户，对应 Python users.find({student_id, s_password exist})
	col := client.Database("buct-course").Collection("users")
	cursor, err := col.Find(ctx, bson.M{
		"student_id": bson.M{"$exists": true, "$nin": bson.A{nil, ""}},
		"s_password": bson.M{"$exists": true, "$nin": bson.A{nil, ""}},
	})
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	courseRepo := CourseData.Repository
	threshold := RefreshInterval

	var needRefresh []string
	for cursor.Next(ctx) {
		var user struct {
			ID string `bson:"_id"`
		}
		if err = cursor.Decode(&user); err != nil {
			continue
		}

		lastUpdate, err := courseRepo.GetLastUpdateTimeByUserID(user.ID)
		if err != nil || lastUpdate.IsZero() {
			needRefresh = append(needRefresh, user.ID)
			continue
		}
		if time.Since(lastUpdate) >= threshold {
			needRefresh = append(needRefresh, user.ID)
		}
	}
	return needRefresh, cursor.Err()
}

// refreshUserData 刷新指定用户的课程数据，对应 Python _refresh_user_data
func refreshUserData(userID string) error {
	log.Printf("[scheduler] 开始自动刷新用户 %s 的课程数据", userID)

	s := scraper.GetScraper()
	result, err := s.GetPendingTasks(userID)
	if err != nil {
		return err
	}

	tasks := make([]CourseData.TaskInput, 0, len(result.Tasks))
	for _, t := range result.Tasks {
		tasks = append(tasks, CourseData.TaskInput{
			Subject:  t.Subject,
			Title:    t.Title,
			Deadline: t.Deadline,
			Details:  t.Details,
			Url:      t.URL,
			Type:     t.Type,
		})
	}

	courseRepo := CourseData.Repository
	saved, err := courseRepo.SaveUserCourseData(userID, tasks)
	if err != nil {
		return err
	}

	log.Printf("[scheduler] 用户 %s 自动刷新完成，保存 %d 条数据", userID, saved)
	return nil
}
